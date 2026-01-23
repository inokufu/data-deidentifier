from dataclasses import dataclass


@dataclass
class HealthCheckResult:
    """Result of a health check.

    Attributes:
        is_healthy: Whether the system is healthy
        checks: Dictionary of individual check results
    """

    is_healthy: bool
    checks: dict[str, dict[str, str | int | bool]]
