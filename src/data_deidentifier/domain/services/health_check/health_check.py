from logger import LoggerContract

from data_deidentifier.adapters.infrastructure.config.contract import ConfigContract
from data_deidentifier.domain.contracts.health_check import HealthCheckContract
from data_deidentifier.domain.types.health_check_result import HealthCheckResult


class HealthCheckService:
    """Service for checking application health and readiness.

    This service orchestrates health checks from various components
    without exposing implementation details.

    Currently, checks:
    - Entity analyzer readiness (Presidio + spaCy models)

    Future: Can be extended to check enrichment services, databases, etc.
    """

    def __init__(
        self,
        health_checker: HealthCheckContract,
        config: ConfigContract,
        logger: LoggerContract,
    ) -> None:
        """Initialize the health check service.

        Args:
            health_checker: Health checker contract
            config: The application configuration
            logger: Logger for logging events
        """
        self.health_checker = health_checker
        self.config = config
        self.logger = logger

    def check_readiness(self) -> HealthCheckResult:
        """Check if the application is ready to serve requests.

        Currently delegates to the analyzer health check.
        In the future, this method can aggregate multiple health checks
        (enrichment services, databases, caches, etc.)

        Returns:
            HealthCheckResult with status of each check
        """
        result = self.health_checker.check_readiness()

        if not result.is_healthy:
            self.logger.warning(
                "Application readiness check failed",
                {"checks": result.checks},
            )

        return HealthCheckResult(
            is_healthy=result.is_healthy,
            checks={
                "env": {
                    "log_level": self.config.get_log_level().name,
                    "environment": self.config.get_environment().name,
                },
                **result.checks,
            },
        )
