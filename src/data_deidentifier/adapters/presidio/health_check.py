from typing import override

from logger import LoggerContract

from data_deidentifier.adapters.presidio.engines import PresidioEngineFactory
from data_deidentifier.domain.contracts.health_check import HealthCheckContract
from data_deidentifier.domain.types.health_check_result import HealthCheckResult


class PresidioHealthChecker(HealthCheckContract):
    """Presidio implementation of analyzer health checks."""

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the Presidio analyzer health checker.

        Args:
            logger: Logger for logging events
        """
        self.logger = logger

    @override
    def check_readiness(self) -> HealthCheckResult:
        checks = {}
        is_healthy = True

        try:
            analyzer = PresidioEngineFactory.get_analyzer_engine()
            supported_entities = analyzer.get_supported_entities()

            # If we have supported entities, it means that model is loaded.
            if not supported_entities:
                checks["analyzer"] = {
                    "status": "not_ready",
                    "message": "No entities supported - model may not be loaded",
                }
                is_healthy = False
            else:
                checks["analyzer"] = {
                    "status": "ok",
                    "supported_entities_count": len(supported_entities),
                    "engine": "presidio",
                }

        except Exception as e:
            self.logger.exception(
                message="Failed to check analyzer readiness",
                exc=e,
            )
            checks["analyzer"] = {
                "status": "error",
                "message": "Failed to check analyzer health",
                "error": str(e),
            }
            is_healthy = False

        return HealthCheckResult(
            is_healthy=is_healthy,
            checks=checks,
        )
