# PulseOps

### Incident & Service Reliability Platform

A backend platform for managing production incidents and service reliability.

```text
Alerts
  ↓
Correlation & Deduplication
  ↓
Incidents
  ↓
Responder Assignment
  ↓
Investigation
  ↓
Escalation
  ↓
Resolution
  ↓
Audit & Reliability Metrics
```

PulseOps is a production-oriented backend built around real-world engineering problems: idempotency, concurrency, background processing, state management, failure recovery, observability, and system design.

---

## Problem

When a production service starts failing, engineering teams need to quickly answer:

- What broke? How severe is it? Which service is affected?
- Who is handling the incident? What changed?
- What actions have already been taken? Is the situation improving?
- When was the incident resolved?

That information is normally scattered across monitoring systems, logs, deployments, tickets, and chat tools. PulseOps centralizes it: alerts come in, get correlated into incidents, get assigned to responders, get tracked through resolution, and every action is recorded and measured.

## Goals

- Reliable alert ingestion
- Alert deduplication and correlation
- Incident lifecycle management
- On-call responder assignment
- Automated escalation
- Asynchronous notification processing
- Idempotent operations
- Concurrency-safe workflows
- Auditability
- Rate limiting
- Caching
- Structured logging
- Metrics and observability
- Production-oriented database design

---

## Features

### Alert Ingestion

```
POST /api/v1/alerts
```

```json
{
  "service": "payment-service",
  "environment": "production",
  "severity": "critical",
  "source": "prometheus",
  "metric": "error_rate",
  "value": 18.7,
  "threshold": 5.0,
  "timestamp": "..."
}
```

Incoming alerts are validated and checked against existing incidents. Each alert either belongs to an existing incident or opens a new one — alerts are never inserted blindly.

### Alert Deduplication & Correlation

Multiple alerts for the same underlying failure produce one incident, not several:

```
10:00  Payment API error rate 20%
10:01  Payment API error rate 21%
10:02  Payment API error rate 19%
10:03  Payment API error rate 22%

                ↓

        One Incident
             │
      ┌──────┼──────┐
      ↓      ↓      ↓
   Alert 1 Alert 2 Alert 3 ...
```

Alerts are correlated using a deterministic fingerprint:

```
hash(
    service +
    environment +
    alert_type +
    relevant_labels
)
```

Redis stores fingerprints for fast lookup, so the ingestion path stays cheap even under high alert volume.

### Incident Management

```
OPEN → ACKNOWLEDGED → INVESTIGATING → MITIGATED → RESOLVED
```

```
POST   /incidents
GET    /incidents
GET    /incidents/{id}
PATCH  /incidents/{id}
POST   /incidents/{id}/acknowledge
POST   /incidents/{id}/resolve
```

The service layer enforces valid state transitions and rejects the rest:

```
OPEN → ACKNOWLEDGED       ✅
OPEN → RESOLVED           ❌
RESOLVED → INVESTIGATING  ❌
```

### On-Call & Assignment

```
Team                    Users                Services
 ├── Backend             ├── Engineer          ├── Payment API
 ├── Infrastructure       ├── Team Lead          ├── Authentication API
 └── Payments             └── Manager            └── Order Service
```

```
Alert → Identify service → Identify owning team → Find on-call engineer → Assign incident
```

```
GET  /on-call/current
POST /incidents/{id}/assign
POST /incidents/{id}/escalate
```

### Escalation

Critical incidents escalate automatically when they go unacknowledged:

```
Critical Incident → Engineer Notified → No ack (5 min) → Escalate
                                                               ↓
                                              Team Lead → No response → Engineering Manager
```

Escalation runs asynchronously through Celery workers rather than inline in the request path, so a slow notification never blocks alert ingestion.

### Notifications

```
Incident Created → Notification Job → Queue → Worker → Email / Webhook
```

Notifications are dispatched outside the request/response cycle. Email and webhooks ship first; Slack/Teams integrations are planned.

### Idempotency

External monitoring systems retry requests when they don't receive a response in time. Every alert submission carries an idempotency key, so retries resolve to a single logical operation instead of duplicate incidents:

```
Idempotency-Key: abc123
```

```
3 requests → same idempotency key → 1 logical operation
```

### Rate Limiting

The ingestion endpoint is rate-limited per API key using Redis:

```
1000 requests / minute / API key
```

### Audit Logging

Every meaningful action — create, acknowledge, assign, resolve — is written to an audit trail:

```json
{
  "actor": "user_123",
  "action": "INCIDENT_RESOLVED",
  "entity": "incident_456",
  "timestamp": "...",
  "metadata": {}
}
```

### Observability

- Request IDs, structured logging
- Request latency & error metrics
- Health checks, Prometheus metrics, OpenTelemetry tracing

```
GET /health
GET /health/live
GET /health/ready
```

---

## Architecture

PulseOps starts as a modular monolith rather than a microservices split.

```
                    External Systems
                          │
                          ▼
                  ┌────────────────┐
                  │ Alert Ingestion│
                  │      API       │
                  └───────┬────────┘
                          │
                          ▼
                 Validation & Auth
                          │
                          ▼
              Deduplication / Correlation
                          │
                          ▼
                  ┌───────────────┐
                  │   PostgreSQL  │
                  └───────┬───────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
          ┌────────┐             ┌──────────┐
          │ Redis  │             │ Job Queue│
          └────────┘             └────┬─────┘
                                       │
                                       ▼
                                  ┌────────┐
                                  │ Worker │
                                  │(Celery)│
                                  └───┬────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                          ▼
                  Notifications              Escalation
```

Nginx sits in front of the FastAPI application as a reverse proxy in production.

## Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3.12 |
| Package Manager | uv |
| API | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Cache | Redis |
| Background Jobs | Celery |
| Authentication | JWT / OAuth2 |
| Testing | pytest |
| Containerization | Docker |
| Reverse Proxy | Nginx |
| API Documentation | OpenAPI / Swagger |
| Linting / Formatting | Ruff |
| Type Checking | mypy |
| Metrics | Prometheus |
| Observability | OpenTelemetry |
| CI/CD | GitHub Actions |
| Deployment | AWS |

Each technology is introduced as the feature that needs it gets built — the stack doesn't front-load infrastructure the project doesn't use yet.

## Project Structure

```
pulseops/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── alerts.py
│   │       ├── incidents.py
│   │       ├── teams.py
│   │       ├── services.py
│   │       └── users.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   │
│   ├── db/
│   │   ├── models/
│   │   ├── session.py
│   │   └── migrations/
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │   ├── alert_service.py
│   │   ├── incident_service.py
│   │   ├── escalation_service.py
│   │   └── notification_service.py
│   │
│   ├── repositories/
│   │
│   ├── workers/
│   │
│   └── main.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── docs/
├── scripts/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
├── uv.lock
├── README.md
└── LICENSE
```

`repositories/` handles data access; `services/` holds business logic. The structure will grow as features land.

## Database Model

```
users · teams · services · on_call_schedules
alerts · incidents · incident_events · incident_assignments
notifications · audit_logs · idempotency_keys
```

```
Team
 ├── Users
 └── Services
       │
       ▼
     Alerts
       │
       ▼
    Incidents
       │
       ├── Assignments
       ├── Events
       ├── Notifications
       └── Audit Logs
```

PostgreSQL is the system of record: foreign keys, indexes, constraints, and transactions enforce consistency; UUIDs and JSONB are used where they fit, not by default.

## Alert Processing Flow

```
External Monitoring System
            │
            ▼
       POST /alerts
            │
            ▼
        Validation
            │
            ▼
     Idempotency Check
            │
            ▼
   Fingerprint Generation
            │
            ▼
 Deduplication / Correlation
            │
       ┌────┴────┐
       │         │
       ▼         ▼
 Existing     New Incident
 Incident         │
       │           ▼
       │       Create Incident
       │           │
       └─────┬─────┘
             ▼
        Store Alert
             │
             ▼
       Trigger Jobs
```

---

## Development Phases

### Phase 1 — Foundation
- [ ] FastAPI application
- [ ] PostgreSQL
- [ ] SQLAlchemy 2.0
- [ ] Alembic
- [ ] Docker
- [ ] Users, Teams, Services, Incidents

### Phase 2 — Authentication & Authorization
- [ ] JWT authentication
- [ ] OAuth2 integration
- [ ] Role-based access control (Admin, Engineer, Viewer)

### Phase 3 — Alert Ingestion
- [ ] Alert ingestion endpoint & validation
- [ ] Alert persistence & fingerprinting
- [ ] Deduplication & incident correlation

### Phase 4 — Redis
- [ ] Redis integration
- [ ] Incident caching
- [ ] Rate limiting
- [ ] Alert deduplication support
- [ ] Cache invalidation strategy

### Phase 5 — Background Processing
- [ ] Celery job queue & workers
- [ ] Notification jobs
- [ ] Escalation jobs
- [ ] Job retry handling

### Phase 6 — Reliability
- [ ] Idempotency
- [ ] Concurrency protection
- [ ] Retry strategies & dead-letter handling
- [ ] Worker failure recovery
- [ ] Duplicate notification prevention

### Phase 7 — Observability
- [ ] Structured logging & request IDs
- [ ] Metrics & health checks
- [ ] Prometheus integration
- [ ] OpenTelemetry tracing

### Phase 8 — Production
- [ ] Production Docker configuration
- [ ] CI/CD
- [ ] Cloud deployment behind Nginx
- [ ] HTTPS & environment configuration
- [ ] Database backups & production monitoring

---

## Engineering Focus

| Area | Design question it addresses |
|---|---|
| Idempotency | How the system behaves when an external service retries the same request |
| Concurrency | What happens when two identical alerts arrive at nearly the same time |
| Database Transactions | How incident creation and related writes stay consistent |
| State Machines | How invalid incident transitions are prevented |
| Background Processing | Why notifications and escalation run outside the HTTP request |
| Retry & Failure Handling | What happens when a worker crashes mid-job |
| Caching | Which data is cached and how invalidation works |
| Rate Limiting | How the system protects itself from high-volume alert traffic |
| Observability | How operators see what PulseOps itself is doing |
| Scalability | How the architecture holds up as alert volume grows |

## Future: Incident Intelligence

AI is not part of the initial build. The reliability platform is built and proven out first, without AI. A future, optional module adds AI-assisted incident investigation, kept architecturally separate from the core incident-management system:

```
Incident
   │
   ├── Logs
   ├── Alerts
   ├── Metrics
   └── Historical Incidents
             │
             ▼
          AI Layer
             │
       ┌─────┴─────┐
       ▼           ▼
Root-cause     Suggested
hypothesis     remediation
```

Planned capabilities:

- Root-cause hypotheses
- Relevant historical incidents
- Suggested investigation steps
- Suggested remediation
- Incident summaries

## Testing Strategy

```
tests/
├── unit/
│   ├── services/
│   ├── domain/
│   └── utilities/
│
└── integration/
    ├── api/
    ├── database/
    └── workers/
```

Coverage focuses on: valid/invalid incident transitions, duplicate alerts, concurrent alert ingestion, idempotent requests, authorization failures, database transaction failures, worker failures, retry behavior, and rate limiting.

---

## Project Status

**Status: Early Development** — the repository is currently being initialized. Items in the roadmap above are marked complete only after implementation and testing.