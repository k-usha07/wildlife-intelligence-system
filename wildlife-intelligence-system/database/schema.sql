-- ============================================================================
-- Wildlife Population Intelligence System — Milestone 1 database schema
-- PostgreSQL 15+ with PostGIS extension
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ----------------------------------------------------------------------------
-- Roles & Users (Auth / RBAC)
-- ----------------------------------------------------------------------------

CREATE TABLE roles (
    id          SMALLSERIAL PRIMARY KEY,
    name        VARCHAR(40) UNIQUE NOT NULL,   -- admin, researcher, conservation_officer, forest_department
    description VARCHAR(255)
);

INSERT INTO roles (name, description) VALUES
    ('admin',                'Full platform administration'),
    ('researcher',           'Wildlife Researcher'),
    ('conservation_officer', 'Conservation Officer'),
    ('forest_department',    'Forest Department Officer');

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name       VARCHAR(120) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role_id         SMALLINT NOT NULL REFERENCES roles(id),
    organization    VARCHAR(150),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_role ON users(role_id);

-- ----------------------------------------------------------------------------
-- Monitoring Sites
-- ----------------------------------------------------------------------------

CREATE TYPE habitat_type AS ENUM (
    'forest', 'grassland', 'wetland', 'desert', 'coastal', 'marine', 'mountain', 'other'
);

CREATE TABLE monitoring_sites (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(150) NOT NULL,
    habitat_type    habitat_type NOT NULL DEFAULT 'other',
    protected_area  VARCHAR(150),
    location        GEOGRAPHY(POINT, 4326) NOT NULL,   -- GPS coordinates
    elevation_m     NUMERIC(8,2),
    description     TEXT,
    created_by       UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_monitoring_sites_location ON monitoring_sites USING GIST(location);
CREATE INDEX idx_monitoring_sites_habitat ON monitoring_sites(habitat_type);

-- ----------------------------------------------------------------------------
-- Devices (camera traps / audio sensors / drones)
-- ----------------------------------------------------------------------------

CREATE TYPE device_type AS ENUM ('camera_trap', 'audio_sensor', 'drone', 'environmental_sensor');
CREATE TYPE device_status AS ENUM ('active', 'inactive', 'maintenance', 'lost');

CREATE TABLE devices (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_code       VARCHAR(50) UNIQUE NOT NULL,   -- e.g. CT-014
    device_type       device_type NOT NULL,
    monitoring_site_id UUID NOT NULL REFERENCES monitoring_sites(id) ON DELETE CASCADE,
    status            device_status NOT NULL DEFAULT 'active',
    installed_at      DATE,
    last_maintained_at DATE,
    notes             TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_devices_site ON devices(monitoring_site_id);
CREATE INDEX idx_devices_status ON devices(status);

-- ----------------------------------------------------------------------------
-- Surveys
-- ----------------------------------------------------------------------------

CREATE TYPE survey_status AS ENUM ('planned', 'active', 'completed', 'cancelled');

CREATE TABLE surveys (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name          VARCHAR(150) NOT NULL,
    objective     TEXT,
    owner_id      UUID NOT NULL REFERENCES users(id),
    status        survey_status NOT NULL DEFAULT 'planned',
    start_date    DATE NOT NULL,
    end_date      DATE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_surveys_owner ON surveys(owner_id);
CREATE INDEX idx_surveys_status ON surveys(status);

-- Many-to-many: a survey covers one or more monitoring sites
CREATE TABLE survey_sites (
    survey_id           UUID NOT NULL REFERENCES surveys(id) ON DELETE CASCADE,
    monitoring_site_id  UUID NOT NULL REFERENCES monitoring_sites(id) ON DELETE CASCADE,
    PRIMARY KEY (survey_id, monitoring_site_id)
);

-- ----------------------------------------------------------------------------
-- Media assets (raw uploads: camera trap / drone images, audio recordings)
-- ----------------------------------------------------------------------------

CREATE TYPE media_type AS ENUM ('image', 'audio', 'video');

CREATE TABLE media_assets (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    survey_id           UUID NOT NULL REFERENCES surveys(id) ON DELETE CASCADE,
    monitoring_site_id  UUID NOT NULL REFERENCES monitoring_sites(id),
    device_id           UUID REFERENCES devices(id),
    media_type          media_type NOT NULL,
    storage_path        VARCHAR(500) NOT NULL,   -- local path or S3/Azure blob URI
    captured_at         TIMESTAMPTZ,
    uploaded_by          UUID REFERENCES users(id),
    uploaded_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    file_size_bytes      BIGINT,
    processing_status    VARCHAR(30) NOT NULL DEFAULT 'pending'  -- pending/processing/done/failed (Milestone 2+ AI pipeline)
);

CREATE INDEX idx_media_survey ON media_assets(survey_id);
CREATE INDEX idx_media_site ON media_assets(monitoring_site_id);
CREATE INDEX idx_media_status ON media_assets(processing_status);

-- ----------------------------------------------------------------------------
-- Observations (species detections — schema ready for Milestone 2 AI output)
-- ----------------------------------------------------------------------------

CREATE TABLE observations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_asset_id  UUID NOT NULL REFERENCES media_assets(id) ON DELETE CASCADE,
    species_name    VARCHAR(150),           -- NULL until Milestone 2 classification runs
    confidence      NUMERIC(5,4),           -- 0.0000 - 1.0000
    is_endangered   BOOLEAN DEFAULT FALSE,
    count_estimate  INTEGER,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_observations_media ON observations(media_asset_id);
CREATE INDEX idx_observations_species ON observations(species_name);

-- ----------------------------------------------------------------------------
-- Audit log
-- ----------------------------------------------------------------------------

CREATE TABLE audit_log (
    id          BIGSERIAL PRIMARY KEY,
    user_id     UUID REFERENCES users(id),
    action      VARCHAR(100) NOT NULL,
    entity      VARCHAR(100),
    entity_id   UUID,
    metadata    JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_entity ON audit_log(entity, entity_id);
