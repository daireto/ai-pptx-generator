"""Custom exceptions."""


class InvalidInferenceProviderError(Exception):
    """Invalid inference provider."""

    def __init__(self, provider: str) -> None:
        """Initialize the exception.

        Parameters
        ----------
        provider : str
            Name of the invalid provider.

        """
        super().__init__(f'Invalid inference provider: {provider!r}')
