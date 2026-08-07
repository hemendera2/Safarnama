# Changelog - Safarnama

## [v0.1.0-alpha.1] - 2026-08-08

### 🚀 Initial Alpha Core
- **Knowledge Graph**: Node-Edge relationship model for India's offbeat travel spots.
- **Intelligence Engine**: Weighted ranking system for discovery (Photography, Adventure, Seasonality).
- **Explainability**: Human-readable recommendation reasons ("✨ Top-rated for Monsoon").
- **Trust Layer**: Provenance tracking with confidence scores and source attribution.
- **Analytics**: Instrumented user event tracking (Searches, Clicks, Bookmarks).
- **Discovery UI**: Interactive map-based dashboard with curated collections.

### 🛠️ Infrastructure
- **Clean Architecture**: Decoupled API, Service, Repository, and Model layers.
- **Database**: SQLite (V2 Schema) with Alembic migrations and performance indexes.
- **Security**: JWT Authentication, RBAC (Traveler, Admin), Rate Limiting, and Security Headers.
- **Observability**: Structured JSON logging and Prometheus metrics.

### 🧪 Known Issues
- Geofencing is simulated via bounding boxes (Full PostGIS migration scheduled for M2 expansion).
- Admin dashboard requires manual token entry for this alpha build.
