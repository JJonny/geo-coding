I have a Flask + Celery + Redis + PostgreSQL web application called "geo-coding".

## Current Architecture
- Distance calculation: Python `geopy.distance.great_circle()`
- DB table `geo_app.tasks` with fields: id (uuid), status (varchar), distances (json)
- Two endpoints:
  - `POST /api/calculateDistance` — accepts CSV with lat/lon coordinates, sends points to external service, saves results to DB
  - `GET /api/getResult/<task_id>` — returns task result

## Goal
Refactor the project to use **PostgreSQL + PostGIS** for distance calculation instead of Python geopy.

## What I need
1. **Analyze** the current codebase and identify all places where `great_circle` or any distance calculation logic is used
2. **Create a migration plan** (step-by-step, no code yet) covering:
   - Enabling PostGIS extension
   - Schema changes: replace `distances (json)` with proper PostGIS geometry columns OR keep json but compute via PostGIS SQL
   - New SQL query using `ST_Distance(geography, geography)` or `ST_DistanceSphere` to replace geopy
   - Changes to Celery task logic
   - Any index recommendations (e.g. GIST index on geometry columns)
3. **Highlight risks** and backward compatibility concerns
4. **Ask me clarifying questions** before writing any code

## Constraints
- Keep the existing API contract (same request/response format)
- Celery + Redis architecture stays the same
- Minimize downtime — prefer additive migrations

Please start with reading the project structure and relevant files, then present the migration plan.

Use Alembic for schema migration, add PostGIS extension check