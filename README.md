# TourEasy backend - Architecture & Design Documentation

> A DDD-lite FastAPI backend for a domestic tour marketplace in Azerbaijan. Locals find tours that depart from Baku
> and book them with a deposit; agencies list and manage their own tours. PostgreSQL stores all data.

This document covers the architecture, the patterns and decisions behind it, how to run the service, and the
endpoint reference. The architecture follows the Python/FastAPI port of
[Rovio.Matchmaking](https://github.com/TuralSuleymani/Rovio.Matchmaking): the same layers, shared kernel and
conventions.

**Status:** the agency module (domain, application, infrastructure, API) is implemented. The announcement (tour
listing) domain model exists; its service, repository and endpoints are next. See [Roadmap](#roadmap).

---

# Part 1: Architecture guide

## Table of Contents

- [Features](#features)
- [High-level diagram](#high-level-diagram)
- [Architecture diagram](#architecture-diagram)
- [Components diagram](#components-diagram)
- [Sequence diagrams](#sequence-diagrams)
- [Clean Architecture overview](#clean-architecture-overview)
- [Applied Domain-Driven Design patterns](#applied-domain-driven-design-patterns)
- [Applied design principles and patterns](#applied-design-principles-and-patterns)
- [Architectural decisions](#architectural-decisions)
- [Best practices applied](#best-practices-applied)
- [Technologies used](#technologies-used)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Quality checks](#quality-checks)
- [Failure model](#failure-model)
- [Roadmap](#roadmap)
- [Part 2: Endpoints reference](#part-2-endpoints-reference)

## Features

**Implemented**

- Agency registration; a new agency waits for admin verification before it can publish tours.
- Admin verification queue: verify, reject with a reason, suspend and reactivate agencies.
- Agency profile update (name, contact email) with partial `PATCH`.
- Every rule lives in the domain; expected failures come back as values with a stable error `code`.
- Layer boundaries enforced automatically with import-linter.

**Domain model ready, API next**

- Announcements (tour listings): title, description, photo gallery, itinerary, inclusions, meeting point,
  tour dates, price.

## High-level diagram

```mermaid
flowchart LR
    traveler[Traveler web app]
    agency[Agency dashboard]
    admin[Admin panel]
    api[TourEasy API<br/>FastAPI]
    db[(PostgreSQL)]

    traveler --> api
    agency --> api
    admin --> api
    api --> db
```

## Architecture diagram

Dependencies point inwards only. The domain knows nothing about FastAPI, SQLAlchemy, the database or `await`.

```mermaid
flowchart TD
    main[main.py<br/>composition root]
    api[api<br/>routers, request schemas, error mapping]
    infra[infrastructure<br/>SQLAlchemy rows, repositories, config]
    app[application<br/>services, ports, DTOs]
    domain[domain<br/>entities, value objects, rules]
    common[common<br/>Result, Id, Entity, DomainError]

    main --> api
    main --> infra
    api --> infra
    api --> app
    infra --> app
    infra --> domain
    app --> domain
    domain --> common
    app --> common
```

## Components diagram

```mermaid
flowchart LR
    subgraph api
        router[agency_router]
        unwrap[errors.unwrap]
    end
    subgraph application
        service[AgencyService]
        port[[IAgencyRepository]]
        dto[AgencyDto]
    end
    subgraph domain
        agency[Agency]
        vo[AgencyName<br/>ContactEmail]
    end
    subgraph infrastructure
        repo[AgencyRepository]
        row[AgencyRow]
        clock[SystemTimeProvider]
    end
    db[(PostgreSQL)]

    router --> service
    router --> unwrap
    service --> port
    service --> agency
    service --> dto
    agency --> vo
    repo -. implements .-> port
    repo --> row
    repo --> agency
    row --> db
    service --> clock
```

## Sequence diagrams

### Register an agency

```mermaid
sequenceDiagram
    participant C as Client
    participant R as agency_router
    participant S as AgencyService
    participant A as Agency
    participant P as AgencyRepository
    participant D as PostgreSQL

    C->>R: POST /api/v1/agencies {name, contact_email}
    R->>S: register(name, contact_email)
    S->>A: Agency.create(name, email, now)
    alt invalid input
        A-->>S: failure(DomainError)
        S-->>R: failure
        R-->>C: 400 {code, message}
    else valid
        A-->>S: success(Agency, PendingVerification)
        S->>P: add(agency)
        P->>D: INSERT + COMMIT
        S-->>R: success(AgencyDto)
        R-->>C: 201 + Location
    end
```

### Admin verifies an agency

```mermaid
sequenceDiagram
    participant C as Admin
    participant R as agency_router
    participant S as AgencyService
    participant P as AgencyRepository
    participant A as Agency

    C->>R: POST /api/v1/admin/agencies/{id}/verify
    R->>R: Id.parse(id) (400 invalid_id)
    R->>S: verify(id)
    S->>P: get(id)
    P-->>S: Agency.rehydrate(row) or None (404)
    S->>A: verify(now)
    alt not pending verification
        A-->>S: failure (409)
    else pending
        A-->>S: success, status = Active
        S->>P: update(agency)
        S-->>R: AgencyDto
        R-->>C: 200
    end
```

## Clean Architecture overview

| Layer | Package | Responsibility |
| --- | --- | --- |
| Shared kernel | `toureasy.common` | `Result`, typed `Id`, `Entity` base, `DomainError`, `ErrorType`, `TimeProvider` port |
| Domain | `toureasy.domain` | Entities, value objects, enums, error codes; every business rule. No I/O, no `await` |
| Application | `toureasy.application` | Use-case services, repository ports (`IAgencyRepository`), DTOs |
| Infrastructure | `toureasy.infrastructure` | SQLAlchemy row models, repository implementations, settings, system clock |
| API | `toureasy.api` | FastAPI routers, request schemas, `Result` → HTTP mapping, dependency wiring |
| Composition root | `toureasy.main` | Builds the app: settings, engine, session factory, routers |

## Applied Domain-Driven Design patterns

1. **Entities** with identity-based equality (`Entity[T]`): two agencies are equal when their ids are equal.
2. **Value objects** (`AgencyName`, `ContactEmail`, `Money`, `DateRange`, ...): immutable frozen dataclasses,
   compared by value, normalized on creation.
3. **Factory methods**: `create(...)` builds a new object and runs every rule; `rehydrate(...)` rebuilds an
   object loaded from storage without re-running rules.
4. **Typed ids**: `Id[Agency]` and `Id[Announcement]` cannot be mixed up.
5. **Behaviour on the entity**: status changes are methods (`verify`, `reject`, `suspend`, `reactivate`) that
   guard their own transitions, not setters.
6. **Domain errors as values**: rules return `Result` with a `DomainError` that carries an `ErrorType` and a
   stable `code`.
7. **Repositories as ports**: the application owns `IAgencyRepository`; infrastructure implements it.
8. **No aggregate root (deliberate)**: `Agency` and `Announcement` are independent entities linked by
   `agency_id`. See [Architectural decisions](#architectural-decisions).

## Applied design principles and patterns

1. **Ports and adapters**: services depend on interfaces (`IAgencyRepository`, `TimeProvider`), not on
   SQLAlchemy or the system clock.
2. **Repository**: the only place that reads or writes the database and commits.
3. **Result pattern**: expected failures travel as values; exceptions are reserved for bugs and corrupted data
   (`InvariantViolationError`).
4. **Dependency injection**: FastAPI `Depends` builds one `AsyncSession` and one service per request.
5. **Composition root**: `main.py` is the only module that knows every layer.
6. **Data mapper**: `AgencyRow` describes the table; `_to_values` and `_to_entity` translate to and from
   `Agency`.

## Architectural decisions

| Decision | Rationale |
| --- | --- |
| DDD-lite: no aggregate roots, no domain events, no CQRS | No invariant spans `Agency` and `Announcement` today. A root would force loading the agency on every announcement change and cause needless conflicts |
| Entities linked by id only (`Announcement.agency_id`) | Each entity has its own repository and can change independently |
| `Result` instead of exceptions for expected failures | Every failure path is explicit in signatures and easy to follow |
| HTTP status chosen only in `api/errors.py` | The domain and application never know about HTTP; `ErrorType` decides the status |
| Domain is synchronous, never calls `now()` | `async` is contagious and the clock is hidden state; services pass `now` from `TimeProvider` |
| Repository always calls `rehydrate`, never `create` | Loading must keep the stored id, status and timestamps, and must not fail on data saved under older rules |
| No creation token on entities | Kept simple; "only `create` and `rehydrate` call the constructor" is a convention |
| New agencies start as `PendingVerification` | The PRD requires admin verification of registration and tax ID before an agency publishes |
| State changes are action endpoints (`/verify`, `/suspend`) | Each transition is a domain method with its own rule, not a status field edit |
| One announcement = one departure, one `DateRange` | A new date is a new (duplicated) announcement; capacity belongs to the announcement |
| `Money` as `Decimal`, at most 2 decimal places | No float rounding; amounts with more decimals are rejected, not rounded |
| Tour dates as `date`, inclusive | Day precision is enough for domestic tours; the meeting time lives on `MeetingPoint` |
| Pydantic for DTOs and request schemas, not for the domain | The domain stays framework-free; the API returns DTOs directly |
| Layers checked by import-linter | Python has no compile-time module boundaries |

## Best practices applied

- Thin routers: parse input, call one service method, `unwrap` the result. No business conditions.
- Services hold no rules: load, call the entity, save only on success.
- Value objects normalize input (trim, collapse spaces, lower-case emails) so equal values compare equal.
- Settings come from `.env` (or real environment variables); no credentials in code.
- `expire_on_commit=False` on the session factory to avoid lazy loads after commit in async code.
- Type hints everywhere; mypy in strict mode; ruff for lint and import order.

## Technologies used

### Runtime & language

| Technology | Version |
| --- | --- |
| Python | 3.12 |
| PostgreSQL | 17 (Docker image) |
| uv | 0.9 (package and environment manager) |

### Production packages

| Package | Version | Used in |
| --- | --- | --- |
| fastapi | 0.142.4 | api |
| pydantic | 2.13.5 | application DTOs, api schemas |
| pydantic-settings | 2.15.0 | infrastructure config |
| sqlalchemy[asyncio] | 2.1.4 | infrastructure |
| asyncpg | 0.32.0 | infrastructure (PostgreSQL driver) |
| uvicorn | 0.54.0 | ASGI server |

### Development packages

| Package | Version | Purpose |
| --- | --- | --- |
| ruff | 0.16.10 | lint and import sorting |
| mypy | 2.4.0 | static type checking (strict) |
| import-linter | 2.15 | layer contract |
| pytest, pytest-asyncio, httpx, aiosqlite | see `uv.lock` | reserved for tests |

## Project structure

```text
backend/
├── compose.yaml                 # local PostgreSQL
├── pyproject.toml               # dependencies, ruff, mypy, import-linter
├── .env.example                 # copy to .env
└── src/toureasy/
    ├── main.py                  # composition root: create_app()
    ├── common/                  # shared kernel
    │   ├── entity.py, identity.py, result.py, time_provider.py
    │   └── errors/              # DomainError, ErrorType, CommonErrorCodes
    ├── domain/
    │   └── agency/
    │       ├── agency.py        # Agency entity
    │       ├── announcement.py  # Announcement entity (tour listing)
    │       ├── enums.py, errors.py
    │       └── value_objects/   # AgencyName, ContactEmail, Money, DateRange, ...
    ├── application/
    │   └── agency/
    │       ├── abstractions/agency_repository.py   # IAgencyRepository (port)
    │       ├── agency_service.py
    │       └── dtos.py
    ├── infrastructure/
    │   ├── config.py, database.py, system_time_provider.py
    │   └── agency/
    │       ├── agency_row.py           # SQLAlchemy model
    │       └── agency_repository.py    # AgencyRepository (adapter)
    └── api/
        ├── dependencies.py, errors.py
        └── agency/
            ├── agency_router.py
            └── schemas.py
```

## Getting started

Prerequisites: [uv](https://docs.astral.sh/uv/) and Docker.

```bash
# 1. Install dependencies into .venv
uv sync

# 2. Configure: DATABASE_URL is read from .env
cp .env.example .env

# 3. Start PostgreSQL (user, password and database are all "toureasy", port 5432)
docker compose up -d

# 4. Create the agencies table (once; there are no migrations yet)
docker exec -i toureasy-postgres psql -U toureasy -d toureasy -c "
CREATE TABLE agencies (
    id                   uuid         PRIMARY KEY,
    name                 varchar(200) NOT NULL,
    contact_email        varchar(254) NOT NULL,
    status               varchar(32)  NOT NULL,
    rejection_reason     varchar(500),
    created_at_utc       timestamptz  NOT NULL,
    last_modified_at_utc timestamptz  NOT NULL
);
CREATE INDEX ix_agencies_status_created_at_utc ON agencies (status, created_at_utc);"

# 5. Run the API
uv run uvicorn toureasy.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Stop the database with `docker compose down`; add `-v` to delete its data.

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `DATABASE_URL` | yes | none | SQLAlchemy async URL, e.g. `postgresql+asyncpg://toureasy:toureasy@localhost:5432/toureasy` |
| `DATABASE_ECHO` | no | `false` | Log every SQL statement |

## Quality checks

```bash
uv run ruff check src     # lint
uv run mypy               # strict type check
uv run lint-imports       # layer contract: api > infrastructure > application > domain > common
```

Automated tests are not part of the repository yet.

## Failure model

| Scenario | Behavior |
| --- | --- |
| Invalid input (empty name, bad email, missing reason) | `400` with the domain's error `code`; nothing is saved |
| Malformed path id | `400 invalid_id` |
| Malformed JSON or wrong field types | `422`, FastAPI's default validation response |
| Unknown agency | `404 agency_not_found` |
| Transition not allowed from the current status | `409` with a specific code; nothing is saved |
| Corrupted row in the database | `InvariantViolationError` from `rehydrate`; `500` |
| Database unavailable | Unhandled driver error; `500` |

## Roadmap

- Announcement service, repository and endpoints (create as draft, submit, moderate, pause, cancel, duplicate,
  archive), plus public search.
- Alembic migrations instead of the manual `CREATE TABLE`.
- Authentication and roles; admin endpoints are currently **unprotected**.
- Agency profile fields from the PRD: contact person, phone, tax ID (VÖEN), logo, description, social links.
- Reservations with a 10-minute seat hold and deposit payment.

---

# Part 2: Endpoints reference

All endpoints are under `/api/v1`. Bodies are JSON. Interactive docs: `/docs`.

## Endpoints overview

| Method | Path | Success | Errors |
| --- | --- | --- | --- |
| POST | `/api/v1/agencies` | 201 + `Location` | 400 |
| GET | `/api/v1/agencies/{agency_id}` | 200 | 400, 404 |
| PATCH | `/api/v1/agencies/{agency_id}` | 200 | 400, 404 |
| GET | `/api/v1/admin/agencies` | 200 | 400 |
| POST | `/api/v1/admin/agencies/{agency_id}/verify` | 200 | 400, 404, 409 |
| POST | `/api/v1/admin/agencies/{agency_id}/reject` | 200 | 400, 404, 409 |
| POST | `/api/v1/admin/agencies/{agency_id}/suspend` | 200 | 400, 404, 409 |
| POST | `/api/v1/admin/agencies/{agency_id}/reactivate` | 200 | 400, 404, 409 |

### Agency status transitions

```mermaid
stateDiagram-v2
    [*] --> PendingVerification: register
    PendingVerification --> Active: verify
    PendingVerification --> Rejected: reject (reason)
    Active --> Suspended: suspend
    Suspended --> Active: reactivate
```

## Agencies

### POST Register agency

`POST /api/v1/agencies`

```json
{
  "name": "Qəbələ Tur",
  "contact_email": "info@qebele.az"
}
```

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `name` | string | yes | trimmed, inner spaces collapsed, 1-200 characters |
| `contact_email` | string | yes | trimmed, lower-cased, valid email shape, at most 254 characters |

- `201 Created`: `AgencyDto` with `status = "PendingVerification"`; `Location: /api/v1/agencies/{id}`.
- `400`: `invalid_agency_name`, `invalid_contact_email`.

**AgencyDto**

```json
{
  "id": "3f2a9c1e5b7d4e8a9c217d4e5f6a8b90",
  "name": "Qəbələ Tur",
  "contact_email": "info@qebele.az",
  "status": "PendingVerification",
  "rejection_reason": null,
  "created_at_utc": "2026-10-09T09:00:00Z",
  "last_modified_at_utc": "2026-10-09T09:00:00Z"
}
```

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | UUID as 32 hex characters; path parameters accept it with or without dashes |
| `name` | string | normalized |
| `contact_email` | string | lower-cased |
| `status` | string | `PendingVerification`, `Active`, `Rejected`, `Suspended` |
| `rejection_reason` | string or null | set only when rejected |
| `created_at_utc` | datetime | UTC |
| `last_modified_at_utc` | datetime | UTC, changes on every successful update |

### GET Agency

`GET /api/v1/agencies/{agency_id}`

- `200`: `AgencyDto`.
- `400 invalid_id`, `404 agency_not_found`.

### PATCH Update agency

`PATCH /api/v1/agencies/{agency_id}`

```json
{
  "name": "Şəki Tur"
}
```

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | string | no | omitted = unchanged |
| `contact_email` | string | no | omitted = unchanged |

- `200`: updated `AgencyDto`.
- `400`: `invalid_id`, `invalid_agency_name`, `invalid_contact_email`. `404 agency_not_found`.

## Admin

> These endpoints have no authentication yet. Do not expose them publicly.

### GET List agencies

`GET /api/v1/admin/agencies?status=PendingVerification`

| Query | Type | Required | Notes |
| --- | --- | --- | --- |
| `status` | string | no | `PendingVerification`, `Active`, `Rejected`, `Suspended`; omitted = all |

- `200`: array of `AgencyDto`, oldest first (verification queue order).
- `400 invalid_agency_status`.

### POST Verify agency

`POST /api/v1/admin/agencies/{agency_id}/verify` (no body)

- `200`: `AgencyDto` with `status = "Active"`.
- `409 agency_not_pending_verification`.

### POST Reject agency

`POST /api/v1/admin/agencies/{agency_id}/reject`

```json
{
  "reason": "VÖEN could not be verified"
}
```

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `reason` | string | yes | trimmed, 1-500 characters |

- `200`: `AgencyDto` with `status = "Rejected"` and `rejection_reason`.
- `400 invalid_rejection_reason`, `409 agency_not_pending_verification`.

### POST Suspend agency

`POST /api/v1/admin/agencies/{agency_id}/suspend` (no body)

- `200`: `AgencyDto` with `status = "Suspended"`.
- `409`: `agency_already_suspended`, `agency_not_active`.

### POST Reactivate agency

`POST /api/v1/admin/agencies/{agency_id}/reactivate` (no body)

- `200`: `AgencyDto` with `status = "Active"`.
- `409`: `agency_already_active`, `agency_not_suspended`.

All admin endpoints with `{agency_id}` also return `400 invalid_id` and `404 agency_not_found`.

## Error responses

Every domain or application failure has the same shape:

```json
{
  "detail": {
    "code": "agency_not_pending_verification",
    "message": "Only an agency awaiting verification can be verified."
  }
}
```

Clients should switch on `code`, never on `message`.

| Status | `ErrorType` | Codes |
| --- | --- | --- |
| 400 | `BAD_REQUEST`, `VALIDATION` | `invalid_id`, `invalid_agency_name`, `invalid_contact_email`, `invalid_rejection_reason`, `invalid_agency_status` |
| 404 | `NOT_FOUND` | `agency_not_found` |
| 409 | `CONFLICT` | `agency_not_pending_verification`, `agency_not_active`, `agency_not_suspended`, `agency_already_suspended`, `agency_already_active` |
| 422 | (FastAPI) | malformed JSON or wrong field types |
| 429 / 503 / 500 | `TOO_MANY_REQUESTS` / `UNAVAILABLE` / `UNEXPECTED` | mapped, not used by agency endpoints yet |

## Quick curl examples

```bash
BASE=http://127.0.0.1:8000/api/v1

# register
curl -s -X POST $BASE/agencies -H "Content-Type: application/json" \
  -d '{"name": "Qəbələ Tur", "contact_email": "info@qebele.az"}'

# set ID to the "id" from the response
ID=3f2a9c1e5b7d4e8a9c217d4e5f6a8b90

curl -s $BASE/agencies/$ID
curl -s -X PATCH $BASE/agencies/$ID -H "Content-Type: application/json" -d '{"name": "Şəki Tur"}'

# admin
curl -s "$BASE/admin/agencies?status=PendingVerification"
curl -s -X POST $BASE/admin/agencies/$ID/verify
curl -s -X POST $BASE/admin/agencies/$ID/suspend
curl -s -X POST $BASE/admin/agencies/$ID/reactivate
curl -s -X POST $BASE/admin/agencies/$ID/reject -H "Content-Type: application/json" \
  -d '{"reason": "VÖEN could not be verified"}'
```
