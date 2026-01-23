from abc import ABC, abstractmethod

from data_deidentifier.domain.types.health_check_result import HealthCheckResult


class HealthCheckContract(ABC):
    """Contract for health check operations."""

    @abstractmethod
    def check_readiness(self) -> HealthCheckResult:
        """Check if the application is ready to serve requests.

        This verifies that all critical dependencies are initialized and working.

        Returns:
            HealthCheckResult with the status of each check
        """
        raise NotImplementedError
