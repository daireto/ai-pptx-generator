"""Main module for the API."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

from src import config
from src.definitions import PPTX_MEDIA_TYPE
from src.generation_service import GenerationService
from src.logger import logger

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['GET'],
    allow_headers=['*'],
)
app.mount('/static', StaticFiles(directory='src/static'), name='static')


@app.get('/api/generate')
def generate(topic: str) -> StreamingResponse:
    """Generate a PowerPoint presentation for the given topic.

    Parameters
    ----------
    topic : str
        Topic to generate the presentation for.

    Returns
    -------
    StreamingResponse
        Stream of SSE events.

    """
    service = GenerationService()
    return StreamingResponse(
        service.generate_and_stream(topic),
        media_type='text/event-stream',
    )


@app.get('/api/download/{file_id}')
def download(file_id: str) -> FileResponse:
    """Download the generated file.

    Parameters
    ----------
    file_id : str
        ID of the file to download.

    Returns
    -------
    FileResponse
        File response.

    """
    if not file_id:
        logger.error('File ID is missing')
        raise HTTPException(status_code=400, detail='ID de archivo no proporcionado')

    pptx_filepath = config.TEMP_FOLDER / file_id
    if not pptx_filepath.exists():
        logger.error(f'File {pptx_filepath} not found')
        raise HTTPException(status_code=404, detail='Archivo no encontrado')

    def cleanup() -> None:
        pptx_filepath.unlink(missing_ok=True)
        logger.info(f'File {pptx_filepath} deleted')

    return FileResponse(
        pptx_filepath,
        media_type=PPTX_MEDIA_TYPE,
        filename=config.RESPONSE_FILENAME,
        background=BackgroundTask(cleanup),
    )


@app.get('/')
def serve_frontend() -> FileResponse:
    """Serve the frontend.

    Returns
    -------
    FileResponse
        File response.

    """
    return FileResponse('src/static/index.html')
