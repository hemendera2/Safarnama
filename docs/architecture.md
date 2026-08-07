# Safarnama - Architecture Overview

## 1. Clean Architecture
Safarnama is built using a layered architecture to ensure separation of concerns:

- **Entities (Models)**: SQLAlchemy models defining the core travel domain.
- **Repositories**: Data access logic (abstraction over SQLAlchemy).
- **Services**: Business logic (e.g., Discovery scoring, Ingestion pipeline).
- **Controllers (Blueprints)**: Versioned REST endpoints.

## 2. Geo-Hierarchy Data Model
The platform uses a 6-tier geographic model:
`Country` -> `State` -> `District` -> `City` -> `Village` -> `Place`

## 3. Observability Stack
- **Logging**: Structured JSON logs via `src/utils/logger.py`.
- **Metrics**: Prometheus metrics exposed via `/metrics`.
- **Tracing**: Request-ID propagation via `X-Request-Id` headers.
- **Health**: `/health` endpoint for readiness/liveness checks.

## 4. Security
- **JWT**: Stateless authentication with role-based access.
- **Talisman**: Automatic security headers (HSTS, XSS protection).
- **Limiter**: IP-based rate limiting to prevent abuse.

## 5. Performance
- Indexed coordinate searches for O(log N) bounding-box lookups.
- Eager loading (`joinedload`) to solve the N+1 query problem.
