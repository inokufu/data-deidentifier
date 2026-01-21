from abc import ABC, abstractmethod

from logger import LoggerContract


class EngineFactoryContract(ABC):
    """Contract for engine factories."""

    @classmethod
    @abstractmethod
    def warmup(cls, logger: LoggerContract) -> None:
        """Pre-load all NLP engines and models at application startup.

        This method eagerly initializes the engines, loading language models
        into memory. Call this during application startup to avoid cold-start
        latency on the first API request.

        Args:
            logger: Logger instance for logging information.
        """
        raise NotImplementedError
