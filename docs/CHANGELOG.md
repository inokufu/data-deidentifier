# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-01-22

### Changed

- Simplify the multi-lingual options
- Add french language by default

## [1.1.0] - 2026-01-06

### Changed

- Migrated from Rye to uv
- Type checking with ty

## [1.0.0] - 2025-07-18

### Added

#### Core Features

- **Text Anonymization API** - REST endpoint `/anonymize/text` for anonymizing
  PII entities in plain text
- **Structured Data Anonymization API** - REST endpoint `/anonymize/structured`
  for anonymizing PII in JSON and DataFrame formats
- **Text Pseudonymization API** - REST endpoint `/pseudonymize/text` for
  generating consistent pseudonyms in text
- **Structured Data Pseudonymization API** - REST endpoint
  `/pseudonymize/structured` for pseudonymizing structured data

#### Anonymization Operators

- `REPLACE` - Replace detected entities with placeholder values
- `REDACT` - Remove or black out detected entities
- `MASK` - Partially mask detected entities
- `HASH` - Replace entities with cryptographic hashes
- `ENCRYPT` - Encrypt detected entities
- `PSEUDONYMIZE` - Generate consistent pseudonyms with optional enrichment

#### Pseudonymization Methods

- **Random Number Method** - Generate cryptographically secure random pseudonyms
  with intra-request consistency
- **Counter Method** - Sequential numbering with customizable start values
- **Crypto Hash Method** - BLAKE2b-based pseudonyms with optional salt for
  enhanced security

#### Entity Enrichment System

- **HTTP Enrichment Service** - External web service integration for adding
  contextual information to pseudonyms
- **Configurable Enrichment** - Per-entity-type enrichment configuration

#### Data Processing

- **Microsoft Presidio Integration** - Advanced PII detection and anonymization
- **JSON Support** - Nested structures with dot notation field paths
- **pandas DataFrame Support** - Native DataFrame processing

#### Infrastructure

- **FastAPI Framework** - Modern API with automatic OpenAPI documentation
- **Pydantic Models** - Strongly typed request/response schemas
- **Thread-Safe Engine Management** - Singleton pattern with lazy initialization
- **HTTP Client with Retry** - Exponential backoff for enrichment services
- **Comprehensive Error Handling** - Production-safe error responses

#### Configuration

- Environment variable configuration with defaults:
  - `DEFAULT_LANGUAGE` (default: "en")
  - `DEFAULT_MINIMUM_SCORE` (default: 0.5)
  - `DEFAULT_ANONYMIZATION_OPERATOR` (default: "replace")
  - `DEFAULT_PSEUDONYMIZATION_METHOD` (default: "random_number")
  - `ENRICHMENT_CONFIGURATIONS` - JSON enrichment service config

#### API Features

- **FastAPI Framework** - Modern, high-performance API with automatic OpenAPI
  documentation
- **Dependency Injection** - Clean separation of concerns with FastAPI's
  dependency injection
- **Request/Response Models** - Strongly typed request and response schemas with
  Pydantic
- **Error Handling** - Comprehensive exception handling with appropriate HTTP
  status codes
- **Logging Integration** - Structured logging with configurable log levels

#### Development Features

- **Domain-Driven Architecture** - Clean contracts and implementations
- **Type Safety** - Complete Python 3.13+ type annotations
- **Documentation** - Google-style docstrings with MkDocs integration
- **Quality Tools** - Pytest, Ruff formatter/linter, pre-commit hooks
- **Modern Tooling** - Rye dependency management, Uvicorn ASGI server
