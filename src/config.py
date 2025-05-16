"""Config."""

from pathlib import Path

from starlette.config import Config
from starlette.datastructures import Secret

config = Config('.env')

DEBUG = config('DEBUG', cast=bool, default=False)

TEMP_FOLDER = Path(config('TEMP_FOLDER', cast=str, default='temp'))
TEMP_FOLDER.mkdir(exist_ok=True)

RESOURCES_FOLDER = config('RESOURCES_FOLDER', cast=str, default='src/resources')
RESPONSE_FILENAME = config('RESPONSE_FILENAME', cast=str, default='Presentation.pptx')

MODEL_NAME = config('MODEL_NAME', cast=str, default='qwen/qwen2.5-7b-instruct')
INFERENCE_PROVIDER = config('INFERENCE_PROVIDER', cast=str, default='novita')

HUGGINGFACE_API_KEY = config('HUGGINGFACE_API_KEY', cast=Secret, default=Secret(''))
NOVITA_API_KEY = config('NOVITA_API_KEY', cast=Secret, default=Secret(''))
PIXABAY_API_KEY = config('PIXABAY_API_KEY', cast=Secret, default=Secret(''))
