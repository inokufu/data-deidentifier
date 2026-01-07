"""Entry point for running the application."""

import os

import uvicorn


def main() -> None:
    """Run the FastAPI application."""
    uvicorn.run(
        "data_deidentifier.adapters.api.main:app",
        host=os.getenv("APP_INTERNAL_HOST", "0.0.0.0"),  # noqa: S104
        port=int(os.getenv("APP_INTERNAL_PORT", "8005")),
        reload=True,
    )


if __name__ == "__main__":
    main()
