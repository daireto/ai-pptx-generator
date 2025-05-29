"""JSON generator."""

from collections.abc import Iterable
from typing import Any

from src.definitions import ITEMS_COUNT
from src.llm_client import LLMClient
from src.logger import logger
from src.prompts import fix_prompt_template, generation_prompt_template
from src.resources import (
    json_example_minified_1,
    json_example_minified_2,
    json_schema_minified,
)


class JSONGenerator:
    """Ask a LLM to generate a JSON about a topic."""

    def __init__(self, client: LLMClient) -> None:
        """Initialize the JSONGenerator.

        Parameters
        ----------
        client : LLMClient
            Client for the LLM.

        """
        self.__client = client

    def generate_json(self, topic: str) -> Iterable[Any]:
        """Generate a JSON about a topic.

        Parameters
        ----------
        topic : str
            Topic to generate the JSON for.

        Returns
        -------
        Iterable[Any]
            Stream of tokens.

        """
        logger.info('Preparing generation prompt...')
        prompt = self._prepare_generation_prompt(topic)
        logger.info('Generating JSON...')
        return self._create_chat_completion(prompt)

    def fix_json(self, json: str) -> Iterable[Any]:
        """Fix a JSON to make it valid.

        Parameters
        ----------
        json : str
            JSON to fix.

        Returns
        -------
        Iterable[Any]
            Stream of tokens.

        """
        logger.info('Preparing fix prompt...')
        prompt = self._prepare_fix_prompt(json)
        logger.info('Fixing JSON...')
        return self._create_chat_completion(prompt)

    def _create_chat_completion(self, prompt: str) -> Iterable[Any]:
        """Create a chat completion.

        Parameters
        ----------
        prompt : str
            Prompt to send to the LLM.

        Returns
        -------
        Iterable[Any]
            Stream of tokens.

        """
        logger.info('Creating chat completion...')
        return self.__client.get_completion(prompt)

    def _prepare_generation_prompt(self, topic: str) -> str:
        return generation_prompt_template.format(
            topic=topic,
            json_schema_minified=json_schema_minified,
            json_example_minified_1=json_example_minified_1,
            json_example_minified_2=json_example_minified_2,
            count=ITEMS_COUNT,
        )

    def _prepare_fix_prompt(self, json: str) -> str:
        return fix_prompt_template.format(
            json=json,
            json_schema_minified=json_schema_minified,
            count=ITEMS_COUNT,
        )
