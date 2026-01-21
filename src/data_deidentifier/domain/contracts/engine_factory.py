from abc import ABC, abstractmethod


class EngineFactoryContract(ABC):
    """Contract for engine factories."""

    @classmethod
    @abstractmethod
    def warmup(cls) -> None:
        """Pre-load all NLP engines and models at application startup.

        This method eagerly initializes the engines, loading language models
        into memory. Call this during application startup to avoid cold-start
        latency on the first API request.
        """
        raise NotImplementedError
