"""LLM client."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from huggingface_hub import InferenceClient
from openai import OpenAI
from starlette.datastructures import Secret

from src.definitions import NOVITA_BASE_URL


class LLMClient(ABC):
    """LLM client interface."""

    def __init__(self, api_token: Secret, repo_id: str) -> None:
        """Initialize the LLM client.

        Parameters
        ----------
        api_token : Secret
            API token for the LLM provider.
        repo_id : str
            Repository ID for the LLM model.

        """
        self._api_token = api_token
        self._repo_id = repo_id
        self.set_client()

    @abstractmethod
    def set_client(self) -> None: ...  # noqa: D102

    @abstractmethod
    def get_completion(self, prompt: str, max_tokens: int = 16384) -> Iterable[Any]: ...  # noqa: D102


class NovitaClient(LLMClient):
    """LLM client for Novita."""

    def set_client(self) -> None:
        """Set the client for the LLM provider."""
        self.__client = OpenAI(
            base_url=NOVITA_BASE_URL,
            api_key=str(self._api_token),
        )

    def get_completion(self, prompt: str, max_tokens: int = 16384) -> Iterable[Any]:
        """Get a completion from the LLM provider.

        Parameters
        ----------
        prompt : str
            Prompt to send to the LLM provider.
        max_tokens : int, optional
            Maximum number of tokens to generate, by default 16384.

        Returns
        -------
        Iterable[Any]
            Stream of tokens.

        """
        return self.__client.chat.completions.create(
            model=self._repo_id,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True,
            max_tokens=max_tokens,
            temperature=0.1,
        )


class HuggingFaceClient(LLMClient):
    """LLM client for Hugging Face."""

    def set_client(self) -> None:
        """Set the client for the LLM provider."""
        self.__client = InferenceClient(
            model=self._repo_id,
            token=str(self._api_token),
            provider='hf-inference',
        )

    def get_completion(self, prompt: str, max_tokens: int = 16384) -> Iterable[Any]:
        """Get a completion from the LLM provider.

        Parameters
        ----------
        prompt : str
            Prompt to send to the LLM provider.
        max_tokens : int, optional
            Maximum number of tokens to generate, by default 16384

        Returns
        -------
        Iterable[Any]
            Stream of tokens.

        """
        return self.__client.chat_completion(
            model=self._repo_id,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True,
            max_tokens=max_tokens,
            temperature=0.1,
        )
