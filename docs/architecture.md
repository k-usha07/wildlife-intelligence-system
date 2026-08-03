# Architecture & Objectives — Milestone 1

## 1. Project objectives

Build an AI-powered platform that uses image recognition, acoustic analysis, computer
vision and machine learning to:

- Automatically identify wildlife species from camera-trap and drone images, and from
  audio recordings.
- Estimate population sizes and density, and track population trends over time.
- Monitor biodiversity and ecosystem/habitat health.
- Detect endangered species and raise alerts.
- Recommend conservation actions based on habitat and population data.

Primary users: Wildlife Researchers, Conservation Officers, Forest Department
Officers, and Administrators (see RBAC below).

## 2. Biodiversity monitoring workflow (Milestone 1 scope)

This is the operational loop the platform supports end-to-end starting in Milestone 1:

```
1. Admin/Conservation Officer registers a Monitoring Site
   (GPS coordinates, habitat type, protected area, device inventory)
        │
        ▼
2. Researcher creates a Survey against one or more Monitoring Sites
   (survey window, objective, assigned team)
        │
        ▼
3. Field devices (camera traps / audio sensors / drones) are registered
   and linked to a Monitoring Site
        │
        ▼
4. Researcher/field team uploads Images and Audio Recordings against
   a Survey + Monitoring Site + Device
        │
        ▼
5. (Milestone 2+) AI pipelines process uploads → species detections,
   acoustic events, population/biodiversity analytics
        │
        ▼
6. Observations accumulate into Observation History, feeding
   dashboards, alerts, and reports
```

Milestone 1 delivers steps 1–4 and 6 (data model + CRUD + auth), plus the storage
scaffolding (raw file storage path, DB tables) that the AI/ML engines in Milestones
2–3 will consume.

## 3. High-level architecture (Milestone 1 slice)

```
┌────────────────────┐        ┌───────────────────────────────────────────┐
│   React Frontend    │  HTTPS │              FastAPI Backend               │
│  (Vite + React      │◄──────►│  ┌───────────────────────────────────────┐ │
│   Router + Axios)    │  JWT   │  │  API Gateway / Routers                │ │
│                      │        │  │  /auth  /users  /surveys              │ │
│  - Login/Register    │        │  │  /monitoring-sites  /devices          │ │
│  - Role dashboards    │       │  │  /observations                        │ │
│  - Survey & site mgmt │       │  └───────────────────────────────────────┘ │
└────────────────────┘        │  ┌───────────────────────────────────────┐ │
                                │  │  Auth: JWT (access+refresh) + OAuth2  │ │
                                │  │  password flow, bcrypt hashing, RBAC  │ │
                                │  │  dependency (role checker)            │ │
                                │  └───────────────────────────────────────┘ │
                                │  ┌───────────────────────────────────────┐ │
                                │  │  SQLAlchemy ORM Models / Pydantic      │ │
                                │  │  Schemas                              │ │
                                │  └───────────────────────────────────────┘ │
                                └───────────────────┬───────────────────────┘
                                                     │
                                     ┌───────────────▼────────────────┐
                                     │  PostgreSQL + PostGIS           │
                                     │  (users, roles, surveys,        │
                                     │   monitoring_sites, devices,    │
                                     │   observations, media_assets)   │
                                     └──────────────────────────────────┘
                                                     │
                                     ┌───────────────▼────────────────┐
                                     │  Object storage (local volume   │
                                     │  in dev / S3-Azure Blob later)  │
                                     │  raw images & audio             │
                                     └──────────────────────────────────┘
```

This is the Milestone-1 subset of the full target architecture (see the original
architecture diagram in the project brief, page 2), which in later milestones adds
the AI/ML analytics layer (YOLOv8/TensorFlow/PyTorch for vision, YAMNet/BirdNET for
audio), the data lake, caching, and external integrations (GBIF, Sentinel Hub, GEE).

## 4. Roles & permissions (RBAC)

| Role                  | Can do in Milestone 1                                                        |
|------------------------|-------------------------------------------------------------------------------|
| `admin`                | Full access: manage users/roles, all sites, surveys, devices                 |
| `forest_department`    | Manage monitoring sites/devices in their protected areas, view all surveys   |
| `conservation_officer` | Create/manage surveys, view observations, manage devices                     |
| `researcher`           | Create surveys, register/browse monitoring sites, upload observations        |

Enforced via a FastAPI dependency (`require_roles(...)`) checked against the JWT's
`role` claim, backed by the `roles` and `users` tables.

## 5. Tech stack (Milestone 1)

- **Backend:** Python, FastAPI, SQLAlchemy 2.0, Pydantic v2, PostgreSQL + PostGIS,
  `python-jose` (JWT), `passlib[bcrypt]`, Alembic-ready structure
- **Frontend:** React 18 (Vite), React Router, Axios, plain CSS (design system tokens)
- **Infra:** Docker, Docker Compose
- **Dataset tooling:** Python scripts under `backend/app/datasets/` for Snapshot
  Serengeti, iNaturalist, BirdCLEF, Animal Kingdom, and GBIF

## 6. Data model summary

See [`database/schema.sql`](../database/schema.sql) for full DDL. Core entities:

- `roles`, `users` — auth + RBAC
- `monitoring_sites` — GPS-located sites (PostGIS `geography(Point)`), habitat type,
  protected area
- `devices` — camera traps / audio sensors / drones, linked to a monitoring site
- `surveys` — a monitoring campaign, owned by a researcher, linked to sites
- `survey_sites` — many-to-many join between surveys and monitoring sites
- `media_assets` — uploaded images/audio, linked to survey + site + device
- `observations` — placeholder for AI-derived detections (species, confidence),
  populated starting Milestone 2, but the table exists now so uploads have somewhere
  to land
- `audit_log` — basic action logging for traceability
