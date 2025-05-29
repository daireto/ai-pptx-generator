"""PPTX generation service."""

import json
import uuid
from collections.abc import Generator
from typing import Literal

from src import config
from src.definitions import FIX_JSON_TIMES
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
        self._pptx_generator = PPTXGenerator(
            pixabay_api_key=config.PIXABAY_API_KEY,
        )

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
                yield self._build_event_message(chunk_content, msg_type='chunk')

            logger.info('Extracting JSON...')
            extracted_json = extract_json_from_text(json_response)

            for i in range(FIX_JSON_TIMES):
                if extracted_json:
                    try:
                        logger.info('Testing extracted JSON...')
                        self._pptx_generator.test_json(extracted_json)
                        break
                    except Exception as e:
                        logger.error(f'JSON test failed: {e}')

                logger.info(f'Fixing JSON... (try {i + 1}/{FIX_JSON_TIMES})')
                yield self._build_event_message('FIX-JSON-STEP', msg_type='step')
                fixed_json = ''
                for chunk in self._json_generator.fix_json(json_response):
                    chunk_content = chunk.choices[0].delta.content or ''
                    fixed_json += chunk_content
                    yield self._build_event_message(chunk_content, msg_type='chunk')

                logger.info('Extracting fixed JSON...')
                extracted_json = extract_json_from_text(fixed_json)
                yield self._build_event_message('FIX-JSON-CLEAN', msg_type='step')

            if not extracted_json:
                yield self._build_event_message('FIX-JSON-FAILED', msg_type='step')
                logger.error(f'Failed to extract JSON after {FIX_JSON_TIMES} tries.')
                return

            yield self._build_event_message('FILE-GEN-STEP', msg_type='step')
            logger.info(f'Generating presentation: {output_file}')
            self._pptx_generator.generate(extracted_json, str(output_file))
            logger.info(f'Presentation generated: {output_file}')
            yield self._build_event_message(
                f'FILE-GEN-DONE:{file_id}',
                msg_type='step',
            )

        except Exception as e:  # noqa: BLE001
            logger.error(f'Error generating presentation: {e}')
            yield self._build_event_message(f'FILE-GEN-ERROR:{e}', msg_type='step')

    def _build_event_message(
        self, msg: str, msg_type: Literal['chunk', 'step']
    ) -> str:
        content = json.dumps(
            {'type': msg_type, 'message': msg},
            ensure_ascii=False,
        )
        return f'data: {content}\n\n'

    def _client_factory(self) -> LLMClient:
        provider = config.INFERENCE_PROVIDER.lower().strip()
        if provider == 'novita':
            return NovitaClient(config.NOVITA_API_KEY, config.MODEL_NAME)
        if provider == 'huggingface':
            return HuggingFaceClient(
                config.HUGGINGFACE_API_KEY, config.MODEL_NAME
            )
        raise InvalidInferenceProviderError(provider)
