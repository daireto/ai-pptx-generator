"""PPTX generation service."""

import json
import uuid
from collections.abc import Generator

from src import config
from src.exceptions import InvalidInferenceProviderError
from src.json_generator import JSONGenerator
from src.llm_client import HuggingFaceClient, LLMClient, NovitaClient
from src.logger import logger
from src.pptx_generator import PPTXGenerator
from src.utils import extract_json_from_text


class GenerationService:
    """Service for generating a PowerPoint presentation."""

    def __init__(self) -> None:
        """Initialize the service."""
        client = self._client_factory()
        self._json_generator = JSONGenerator(client)
        self._pptx_generator = PPTXGenerator(pixabay_api_key=config.PIXABAY_API_KEY)

    def generate_and_stream(self, topic: str) -> Generator[str, None, None]:
        """Generate a PowerPoint presentation and stream the results.

        Parameters
        ----------
        topic : str
            Topic to generate the presentation for.

        Yields
        ------
        Generator[str, None, None]
            Stream of SSE events.

        """
        file_id = str(uuid.uuid4())
        output_file = config.TEMP_FOLDER / file_id

        try:
            logger.info('Starting generation of JSON...')
            json_response = ''
            for chunk in self._json_generator.generate_json(topic):
                chunk_content = chunk.choices[0].delta.content or ''
                json_response += chunk_content
                yield self._build_event_message(chunk_content)

            logger.info('Extracting JSON...')
            extracted_json = extract_json_from_text(json_response)

            for i in range(3):
                if extracted_json:
                    try:
                        logger.info('Testing extracted JSON...')
                        if self._pptx_generator.test_json(extracted_json):
                            break
                    except Exception as e:  # noqa: BLE001
                        logger.error(f'JSON test failed: {e}')

                logger.info(f'Fixing JSON... (try {i + 1}/3)')
                yield self._build_event_message('\nFIX-JSON-STEP\n')
                fixed_json = ''
                for chunk in self._json_generator.fix_json(json_response):
                    chunk_content = chunk.choices[0].delta.content or ''
                    fixed_json += chunk_content
                    yield self._build_event_message(chunk_content)

                logger.info('Extracting fixed JSON...')
                extracted_json = extract_json_from_text(fixed_json)
                yield self._build_event_message('\nFIX-JSON-CLEAN\n')

            if not extracted_json:
                yield self._build_event_message('\nFIX-JSON-FAILED\n')
                logger.error('Failed to extract JSON after 2 tries.')
                return

            yield self._build_event_message('\nPPTX-GEN-STEP\n')
            logger.info(f'Generating PowerPoint presentation: {output_file}')
            self._pptx_generator.generate(extracted_json, str(output_file))
            logger.info(f'PowerPoint presentation generated: {output_file}')
            yield self._build_event_message(f'\nPPTX-GEN-DONE:{file_id}\n')

        except Exception as e:  # noqa: BLE001
            logger.error(f'Error generating PowerPoint: {e}')
            yield self._build_event_message(f'\nPPTX-GEN-ERROR:{e}\n')

    def _build_event_message(self, content: str) -> str:
        return f'data: {json.dumps({"content": content}, ensure_ascii=False)}\n\n'

    def _client_factory(self) -> LLMClient:
        provider = config.INFERENCE_PROVIDER.lower().strip()
        if provider == 'novita':
            return NovitaClient(config.NOVITA_API_KEY, config.MODEL_NAME)
        if provider == 'huggingface':
            return HuggingFaceClient(config.HUGGINGFACE_API_KEY, config.MODEL_NAME)
        raise InvalidInferenceProviderError(provider)
