# Data deidentifier

[![Python](https://img.shields.io/badge/Python-FFD43B?logo=python)](https://www.python.org/)
![License](https://img.shields.io/badge/MIT-red?logo=opensourceinitiative)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-E6F0FF?logo=githubactions)](https://github.com/features/actions)
[![Pytest](https://img.shields.io/badge/pytest-E6F7FF?logo=pytest)](https://docs.pytest.org/)
[![EditorConfig](https://img.shields.io/badge/EditorConfig-333333?logo=editorconfig)](https://editorconfig.org/)
[![Rye](https://img.shields.io/badge/Rye-000000?logo=rye)](https://rye.astral.sh/)
[![Ruff](https://img.shields.io/badge/Ruff-3A3A3A?logo=ruff)](https://docs.astral.sh/ruff/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-40332E?logo=pre-commit)](https://pre-commit.com/)
[![Makefile](https://img.shields.io/badge/Makefile-427819?logo=gnu)](https://www.gnu.org/software/make/manual/make.html)
[![MkDocs](https://img.shields.io/badge/MkDocs-526CFE?logo=markdown)](https://www.mkdocs.org/)

<!-- TOC -->
* [Data deidentifier](#data-deidentifier)
  * [Overview](#overview)
    * [Key Features](#key-features)
    * [Supported Entity Types](#supported-entity-types)
    * [Available Methods and Operators](#available-methods-and-operators)
  * [Setup and installation](#setup-and-installation)
    * [With Docker](#with-docker)
      * [Prerequisites](#prerequisites)
      * [Development Environment](#development-environment)
      * [Quick Start (Without volumes or Traefik)](#quick-start-without-volumes-or-traefik)
      * [Production Environment](#production-environment)
    * [With Rye](#with-rye)
    * [Prerequisites](#prerequisites-1)
    * [Installation](#installation)
  * [Usage](#usage)
    * [Text Anonymization](#text-anonymization)
    * [Structured Data Anonymization](#structured-data-anonymization)
    * [Text Pseudonymization](#text-pseudonymization)
    * [Entity Enrichment](#entity-enrichment)
  * [Development](#development)
    * [API Documentation](#api-documentation)
    * [Code Formatting and Linting](#code-formatting-and-linting)
    * [Development Commands](#development-commands)
    * [Environment Variables](#environment-variables)
    * [Architecture](#architecture)
  * [Contributing](#contributing)
  * [License](#license)
<!-- TOC -->

## Overview

A comprehensive solution for anonymizing and pseudonymizing personally
identifiable information (PII) in both textual and structured data. Built on
Microsoft Presidio, this API provides enterprise-grade data deidentification
with configurable operators and methods.

### Key Features

- **Text & Structured Data Processing** - Support for plain text and JSON
- **Flexible Anonymization** - Multiple operators: replace, redact, mask, hash,
  encrypt
- **Consistent Pseudonymization** - Random number, counter, and cryptographic
  hash methods. Maintains consistency within a single request.
- **Production Ready** - Thread-safe, scalable FastAPI service with
  comprehensive error handling

### Supported Entity Types

`PERSON`, `EMAIL_ADDRESS`, `PHONE_NUMBER`, `CREDIT_CARD`, `IP_ADDRESS`,
`LOCATION`, `DATE_TIME`, `URL`.

### Available Methods and Operators

**Anonymization Operators:**

- `replace` - Replace with generic placeholders
- `redact` - Remove entirely
- `mask` - Masking with character
- `hash` - Cryptographic hash
- `encrypt` - Encryption

**Pseudonymization Methods:**

- `random_number` - Cryptographically secure random pseudonyms
- `counter` - Sequential numbering
- `crypto_hash` - BLAKE2b-based pseudonyms

## Setup and installation

You can run the application either directly with **Rye** or using **Docker**.

1. Clone the repository
2. Set up environment variables:
   Create a `.env` file in the project root by copying `.env.default`:
   ```
   cp .env.default .env
   ```
   You can then modify the variables in `.env` as needed.

### With Docker

The application is containerized using Docker, with a robust and flexible
deployment strategy that leverages:

- Docker for containerization with a multi-environment support (dev and prod)
  using Docker Compose profiles
- Traefik as a reverse proxy and load balancer, with built-in SSL/TLS support
  via Let's Encrypt, and a dashboard in dev environment.
- Gunicorn as the production-grade WSGI HTTP server, with configurable worker
  processes and threads, and dynamic scaling based on system resources.

#### Prerequisites

- Docker and Docker Compose installed on your machine.

#### Development Environment

Build and run the development environment:

```
docker compose --profile dev up --build
```

The API will be available at : `http://ddi.localhost`

Traefik Dashboard will be available at : `http://traefik.ddi.localhost`

#### Quick Start (Without volumes or Traefik)

For a quick test without full stack:

```
docker build --target dev-standalone -t ddi:dev-standalone .
docker run --env-file .env -p 8005:8005 ddi:dev-standalone
```

Note: This version won't reflect source code changes in real-time.

#### Production Environment

Configure production-specific settings, then build and run the production
environment:

```
docker compose --profile prod up --build
```

### With Rye

### Prerequisites

- Python 3.13 or higher
- [Rye](https://rye.astral.sh) for dependency management

### Installation

1. Install Rye, see https://rye.astral.sh/guide/installation/

2. **Install dependencies**
   ```bash
   make init
   ```

3. **Start the server**
   ```bash
   make start
   ```

The API will be available at `http://localhost:8005`.

## Usage

### Text Anonymization

```bash
curl -X POST "http://localhost:8005/anonymize/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Doe lives in New York and his email is john@example.com",
    "operator": "replace"
  }'
```

Response:

```json
{
  "anonymized_text": "<PERSON> lives in <LOCATION> and his email is <EMAIL_ADDRESS>",
  "detected_entities": [
    {
      "type": "PERSON",
      "start": 0,
      "end": 8,
      "score": 0.85,
      "text": "John Doe"
    },
    {
      "type": "LOCATION",
      "start": 18,
      "end": 26,
      "score": 0.85,
      "text": "New York"
    },
    {
      "type": "EMAIL_ADDRESS",
      "start": 44,
      "end": 60,
      "score": 1.0,
      "text": "john@example.com"
    }
  ]
}
```

### Structured Data Anonymization

```bash
curl -X POST "http://localhost:8005/anonymize/structured" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "user": {
        "name": "Alice Johnson",
        "email": "alice@company.com",
        "address": "123 Main St, Boston"
      }
    },
    "operator": "mask",
    "operator_params": {
      "masking_char":"*",
      "chars_to_mask":999
    }
  }'
```

Response:

```json
{
  "anonymized_data": {
    "user": {
      "name": "*************",
      "email": "*****************",
      "address": "*******************"
    }
  },
  "detected_fields": {
    "user.name": "PERSON",
    "user.email": "EMAIL_ADDRESS",
    "user.address": "LOCATION"
  }
}
```

### Text Pseudonymization

```bash
curl -X POST "http://localhost:8005/pseudonymize/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Doe was born on January 24, 1985, and Jane Smith lives in 221B Baker Street London",
    "method": "counter"
  }'
```

Response:

```json
{
  "pseudonymized_text": "<PERSON_2> was born on <DATE_TIME_1>, and <PERSON_1> lives in <LOCATION_1>",
  "detected_entities": [
    {
      "type": "PERSON",
      "start": 0,
      "end": 8,
      "score": 0.85,
      "text": "John Doe"
    },
    {
      "type": "DATE_TIME",
      "start": 21,
      "end": 37,
      "score": 0.85,
      "text": "January 24, 1985"
    },
    {
      "type": "PERSON",
      "start": 43,
      "end": 53,
      "score": 0.85,
      "text": "Jane Smith"
    },
    {
      "type": "LOCATION",
      "start": 63,
      "end": 87,
      "score": 0.85,
      "text": "221B Baker Street London"
    }
  ]
}
```

### Entity Enrichment

Configure external services to add contextual information to pseudonyms, by
entity type:

```bash
# In .env file
ENRICHMENT_CONFIGURATIONS='{
  "LOCATION": {
    "type": "http",
    "url": "http://your-geo-service.example.com/enrich"
  }
}'
```

To transform, for example, `<LOCATION_123>` into
`<LOCATION_123> (United Kingdom)` when the service returns country information.

## Development

### API Documentation

Once the server is running, you can access the interactive API documentation:

- Swagger UI: Available at `/docs`
- ReDoc: Available at `/redoc`

These interfaces provide detailed information about all available endpoints,
request/response schemas, and allow you to test the API directly from your
browser.

### Code Formatting and Linting

The project uses [Ruff](https://docs.astral.sh/ruff/) for linting and
formatting, with [pre-commit](https://pre-commit.com/) hooks for automated
quality checks. Code documentation is built
with [MkDocs](https://www.mkdocs.org/)
and Material theme.

### Development Commands

Key commands for development:

```bash
make help              # Display all available commands
make init              # Initialize project (first installation)
make start             # Start application
make check             # Run all checks (precommit + test)
make format            # Format code
make lint              # Run linting checks
make docs-serve        # Serve project documentation locally
```

### Environment Variables

| Variable                               | Description                                                   | Required | Default Value      | Possible Values                                 |
|----------------------------------------|---------------------------------------------------------------|----------|--------------------|-------------------------------------------------|
| **Application Configuration**          |                                                               |          |                    |                                                 |
| `DEFAULT_LANGUAGE`                     | Default language for text analysis                            | No       | `en`               | `en`                                            |
| `DEFAULT_MINIMUM_SCORE`                | Default confidence threshold                                  | No       | `0.5`              | `0.0` to `1.0`                                  |
| `DEFAULT_ANONYMIZATION_OPERATOR`       | Default anonymization method                                  | No       | `replace`          | `replace`, `redact`, `mask`, `hash`, `encrypt`  |
| `DEFAULT_PSEUDONYMIZATION_METHOD`      | Default pseudonymization method                               | No       | `random_number`    | `random_number`, `counter`, `crypto_hash`       |
| `ENRICHMENT_CONFIGURATIONS`            | Entity enrichment service configs                             | No       | `{}`               | JSON object                                     |
| **Environment Configuration**          |                                                               |          |                    |                                                 |
| `ENVIRONMENT`                          | Affects error handling and logging throughout the application | No       | `development`      | `development`, `production`                     |
| `LOG_LEVEL`                            | Minimum logging level                                         | No       | `info`             | `debug`, `info`, `warning`, `error`, `critical` |
| **Internal Application Configuration** |                                                               |          |                    |                                                 |
| `APP_INTERNAL_HOST`                    | Host for internal application binding                         | No       | `0.0.0.0`          | Valid host/IP                                   |
| `APP_INTERNAL_PORT`                    | Port for internal application binding                         | No       | `8005`             | Any valid port                                  |
| **External Routing Configuration**     |                                                               |          |                    |                                                 |
| `APP_EXTERNAL_HOST`                    | External hostname for the application                         | Yes      | `ddi.localhost`    | Valid hostname                                  |
| `APP_EXTERNAL_PORT`                    | External port for routing (dev env only)                      | No       | `80`               | Any valid port                                  |
| **Traefik Configuration**              |                                                               |          |                    |                                                 |
| `TRAEFIK_RELEASE`                      | Traefik image version                                         | No       | `v3.4.4`           | Valid Traefik version                           |
| `LETS_ENCRYPT_EMAIL`                   | Email for Let's Encrypt certificate                           | Yes      | `test@example.com` | Valid email                                     |
| **Performance Configuration**          |                                                               |          |                    |                                                 |
| `WORKERS_COUNT`                        | Number of worker processes                                    | No       | `4`                | Positive integer                                |
| `THREADS_PER_WORKER`                   | Number of threads per worker                                  | No       | `2`                | Positive integer                                |

Refer to `.env.default` for a complete list of configurable environment variables and their default values.

### Architecture

The project follows **Domain-Driven Design** principles with clean separation of
concerns:

```
├── domain/                # Core business logic
│   ├── contracts/         # Abstract interfaces
│   ├── services/          # Application services
│   ├── types/             # Domain models and enums
│   └── exceptions.py      # Domain exceptions
├── adapters/              # External integrations
│   ├── api/               # FastAPI routes and schemas
│   ├── presidio/          # Microsoft Presidio integration
│   └── infrastructure/    # Config, HTTP client, enrichment
```

## Contributing

We welcome contributions to this project! Please see
the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to
contribute, including:

- How to set up your development environment
- Coding standards and style guidelines
- Pull request process
- Testing requirements

## License

This project is licensed under the MIT License - see the LICENSE file for
details.
