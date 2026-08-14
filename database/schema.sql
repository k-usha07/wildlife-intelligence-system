-- ============================================================================
-- Wildlife Population Intelligence System — Full Database Schema
-- PostgreSQL 15+ with PostGIS extension
-- Milestones 1-4 complete
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ============================================================================
-- Roles & Users (Auth / RBAC)  — Milestone 1
-- ============================================================================
CREATE TABLE roles (
    id             5SERIAL PRIMARY KEY,
    name            VARCHAR(40) UNIQUE NOT NULL,   -- admin, researcher, conservation_officer, forest_department
    description     VARCHAR(255)
);

INSERT INTO roles (name, description) VALUES
    ('admin',               'Full platform administration'),
    ('researcher',          'Wildlife Researcher'),
    ('conservation_officer','Conservation Officer'),
    ('forest_department',   'Forest Department Officer');

!ECREATE TABLE users (
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


-- ============================================================================
-- Monitoring Sites  — Milestone 1
-- ============================================================================
CREATE TYPE habitat_type AS ENUM (
    'forest', 'grassland', 'wetland', 'desert',
    'coastal', 'marine', 'mountain', 'savanna', 'tundra', 'other'
);

CREATE TABLE monitoring_sites (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(150) NOT NULL,
    habitat_type    habitat_type NOT NULL DEFAULT 'other',
    protected_area  VARCHAR(150),
    location        GEOGRAPHY(POINT, 4326) NOT NULL,
    elevation_m     NUMERIC(8,2),
    description     TEXT,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_monitoring_sites_location ON monitoring_sites USING GIST(location);
CREATE INDEX idx_monitoring_sites_habitat  ON monitoring_sites(habitat_type);


-- ============================================================================
-- Devices (camera traps / audio sensors / drones)  — Milestone 1
-- ============================================================================
CREATE TYPE device_type   AS ENUM ('camera_trap', 'audio_sensor', 'drone', 'environmental_sensor', 'satellite');
CREATE TYPE device_status AS ENUM ('active', 'inactive', 'maintenance', 'lost');

CREATE TABLE devices (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_code         VARCHAR(50) UNIQUE NOT NULL,
    device_type         device_type NOT NULL,
    monitoring_site_id  UUID NOT NULL REFERENCES monitoring_sites(id) ON DELETE CASCADE,
    status              device_status NOT NULL DEFAULT 'active',
    installed_at        DATE,
    last_maintained_at  DATE,
    battery_level       NUMERIC(5,2),
    storage_remaining   NUMERIC(5,2),
    image_count         INTEGER DEFAULT 0,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_devices_site   ON devices(monitoring_site_id);
CREATE INDEX idx_devices_status ON devices(status);


-- ============================================================================
-- Surveys  — Milestone 1
-- ============================================================================
CREATE TYPE survey_status AS ENUM ('planned', 'active', 'completed', 'cancelled');

CREATE TABLE surveys (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(150) NOT NULL,
    objective   TEXT,
    owner_id    UUID NOT NULL REFERENCES users(id),
    status      survey_status NOT NULL DEFAULT 'planned',
    start_date  DATE NOT NULL,
    end_date    DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_surveys_owner  ON surveys(owner_id);
CREATE INDEX idx_surveys_status ON surveys(status);

CREATE TABLE survey_sites (
    survey_id          UUID NOT NULL REFERENCES surveys(id) ON DELETE CASCADE,
6  monitoring_site_id UUID NOT NULL REFERENCES monitoring_sites(id) ON DELETE CASCADE,
    PRIMARY KEY (survey_id, monitoring_site_id)
);


-- ============================================================================
-- Media assets (raw uploads)  — Milestone 1
-- ============================================================================
CREATE TYPE media_type AS ENUM ('image', 'audio', 'video');

CREATE TABLE media_assets (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    survey_id           UUID NOT NULL REFERENCES surveys(id) ON DELETE CASCADE,
    monitoring_site_id  UUID NOT NULL REFERENCES monitoring_sites(id),
    device_id           UUID REFERENCES devices(id),
    media_type          media_type NOT NULL,
    storage_path        VARCHAR(500) NOT NULL,
    captured_at         TIMESTAMPTZ,
    uploaded_by         UUID REFERENCES users(id),
    uploaded_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    file_size_bytes     BIGINT,
    processing_status   VARCHAR(30) NOT NULL DEFAULT 'pending'
);

CREATE INDEX idx_media_survey ON media_assets(survey_id);
CREATE INDEX idx_media_site   ON media_assets(monitoring_site_id);
CREATE INDEX idx_media_status ON media_assets(processing_status);


-- ============================================================================
-- Species  — Milestone 2
-- ============================================================================
CREATE TYPE conservation_status_enum AS ENUM (
    'LC',   -- Least Concern
    'NT',   -- Near Threatened
    'VU',   -- Vulnerable
    'EN',   -- Endangered
    'CR',   -- Critically Endangered
    'EW',   -- Extinct in Wild
    'EX',   -- Extinct
    'DD'    -- Data Deficient
);

CREATE TYPE species_group_enum AS ENUM (
    'mammals', 'birds', 'reptiles', 'amphibians', 'insects', 'marine_species'
);

CREATE TABLE species (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    common_name         VARCHAR(150) NOT NULL,
    scientific_name     VARCHAR(150) UNIQUE NOT NULL,
    species_group       species_group_enum NOT NULL,
    conservation_status conservation_status_enum NOT NULL DEFAULT 'LC',
    taxonomy_class      VARCHAR(100),
    taxonomy_order      VARCHAR(100),
    taxonomy_family     VARCHAR(100),
    taxonomy_genus      VARCHAR(100),
    population_estimate INTEGER,
    population_trend    VARCHAR(20),           -- increasing, stable, declining
    habitat_preference  VARCHAR(255),
    geographic_range    TEXT,
    is_endangered       BOOLEAN NOT NULL DEFAULT FALSE,
    is_migratory        BOOLEAN NOT NULL DEFAULT FALSE,
    description         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_species_group      ON species(species_group);
CREATE INDEX idx_species_status     ON species(conservation_status);
CREATE INDEX idx_species_endangered ON species(is_endangered);


-- ============================================================================
-- Observations (species detections)  — Milestone 1 (enhanced in Milestone 2)
-- ============================================================================
CREATE TABLE observations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_asset_id  UUID NOT NULL REFERENCES media_assets(id) ON DELETE CASCADE,
    species_id      UUID REFERENCES species(id),
    species_name    VARCHAR(150),              -- denormalised for quick filtering
    confidence      NUMERIC(5,4),             -- 0.0000 – 1.0000
    count_estimate  INTEGER DEFAULT 1,
    is_endangered   BOOLEAN DEFAULT FALSE,
    behavior        VARCHAR(100),
    notes           TEXT,
    is_verified     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_observations_media   ON observations(media_asset_id);
CREATE INDEX idx_observations_species ON observations(species_id);
CREATE INDEX idx_observations_name    ON observations(species_name);


-- ============================================================================
-- Population Estimates  — Milestone 3
-- ============================================================================
CREATE TABLE population_estimates (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    species_id              UUID NOT NULL REFERENCES species(id),
    survey_id               UUID NOT NULL REFERENCES surveys(id),
    estimated_population    INTEGER NOT NULL,
    density_per_km2         NUMERIC(10,4),
    confidence_interval_lower INTEGER,
    confidence_interval_upper INTEGER,
    estimation_method       VARCHAR(100),       -- distance_sampling, mark_recapture, camera_trap_rest
    area_km2                NUMERIC(10,2),
    observation_date        DATE NOT NULL,
    notes                   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_pop_est_species ON population_estimates(species_id);
CREATE INDEX idx_pop_est_survey  ON population_estimates(survey_id);


-- ============================================================================
-- Population Trends  — Milestone 3
-- ============================================================================
CREATE TABLE population_trends (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    species_id      UUID NOT NULL REFERENCES species(id),
    year            INTEGER NOT NULL,
    population_count INTEGER NOT NULL,
    growth_rate     NUMERIC(8,4),
    trend_direction VARCHAR(20),               -- increasing, stable, declining
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_pop_trend_species ON population_trends(species_id);


-- ============================================================================
-- Migration Records  — Milestone 3
-- ============================================================================
CREATE TABLE migration_records (
    id                  UUID4UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    species_id          UUID NOT NULL REFERENCES species(id),
    origin_latitude     NUMERIC(10,6),
    origin_longitude    NUMERIC(10,6),
    destination_latitude NUMERIC(10,6),
    destination_longitude NUMERIC(10,6),
    migration_date      DATE,
    distance_km         NUMERIC(10,2),
    direction           VARCHAR(50),
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_migration_species ON migration_records(species_id);


-- ============================================================================
-- Biodiversity Indices  — Milestone 2
-- ============================================================================
CREATE TABLE biodiversity_indices (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    survey_id       UUID NOT NULL REFERENCES surveys(id),
    shannon_index   NUMERIC(6,4),
    simpson_index   NUMERIC(6,4),
    species_richness INTEGER,
    evenness_index  NUMERIC(6,4),
    calculation_date DATE NOT NULL,
    area_km2        NUMERIC(10,2),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_biodiversity_survey ON biodiversity_indices(survey_id);


-- ============================================================================
-- Habitat Assessments  — Milestone 3
-- ============================================================================
CREATE TABLE habitat_assessments (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    survey_id               UUID NOT NULL REFERENCES surveys(id),
    habitat_type            VARCHAR(100),
    vegetation_cover_pct    NUMERIC(5,2),
    water_availability_score NUMERIC(4,2),
    food_availability_score  NUMERIC(4,2),
    human_disturbance_score  NUMERIC(4,2),
    fragmentation_index     NUMERIC(5,4) DEFAULT 0.0,
    overall_quality_score   NUMERIC(4,2),
    degradation_level       VARCHAR(50),
    suitability_score       NUMERIC(4,2),
    assessment_date         DATE NOT NULL,
    notes                   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_habitat_survey ON habitat_assessments(survey_id);


-- ============================================================================
-- Conservation Recommendations  — Milestone 3
-- ============================================================================
CREATE TABLE conservation_recommendations (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    species_id              UUID REFERENCES species(id),
    survey_id               UUID REFERENCES surveys(id),
    priority_level          VARCHAR(20),        -- critical, high, medium, low
    recommendation_type     VARCHAR(100),
    title                   VARCHAR(255) NOT NULL,
    description             TEXT NOT NULL,
    habitat_restoration     TEXT,
    protection_strategy     TEXT,
    resource_allocation     TEXT,
    implementation_timeline VARCHAR(100),
    status                  VARCHAR(20) DEFAULT 'pending',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_conservation_species ON conservation_recommendations(species_id);
CREATE INDEX idx_conservation_priority ON conservation_recommendations(priority_level);


-- ============================================================================
-- Ecosystem Health Scores  — Milestone 3
-- ============================================================================
CREATE TABLE ecosystem_health_scores (
    id                              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    survey_id                       UUID NOT NULL REFERENCES surveys(id),
    species_diversity_score         NUMERIC(4,2),     -- 30% weight
    population_stability_score      NUMERIC(4,2),     -- 25% weight
    habitat_quality_score           NUMERIC(4,2),     -- 20% weight
    endangered_species_score        NUMERIC(4,2),     -- 15% weight
    environmental_conditions_score  NUMERIC(4,2),     -- 10% weight
    overall_health_score            NUMERIC(4,2),
    conservation_status             VARCHAR(30),      -- Excellent, Healthy, Moderate Concern, Vulnerable, Critical
    assessment_date                 DATE NOT NULL,
    notes                           TEXT,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_health_survey ON ecosystem_health_scores(survey_id);


-- ============================================================================
-- Notifications.  — Milestone 4
-- ============================================================================
CREATE TYPE notification_priority AS ENUM ('critical', 'high', 'medium', 'low');
CREATE TYPE notification_type AS ENUM (
    'endangered_species_alert',
    'population_decline_alert',
    'habitat_degradation_alert',
    'monitoring_device_alert',
    'conservation_notification',
    'system_notification',
    'info'
);

CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id),
    title           VARCHAR(255) NOT NULL,
    message         TEXT NOT NULL,
    priority        notification_priority NOT NULL DEFAULT 'medium',
    type            notification_type NOT NULL DEFAULT 'info',
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    related_entity  VARCHAR(100),               -- e.g. 'species', 'survey', 'habitat_assessment'
    related_id      UUID,                       -- FK to the related entity
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_user     ON notifications(user_id);
CREATE INDEX idx_notifications_read     ON notifications(is_read);
CREATE INDEX idx_notifications_priority ON notifications(priority);


-- ============================================================================
-- Image Analysis Results  — Milestone 2
-- ============================================================================
CREATE TABLE image_analysis_results (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_asset_id      UUID NOT NULL REFERENCES media_assets(id) ON DELETE CASCADE,
    species_detected    JSONB,                  -- [{"species": "Lion", "count": 2, "confidence": 0.92}]
    bounding_boxes      JSONB,                  -- [{"x1":10,"y1":20,"x2":100,"y2":200}]
    image_quality       VARCHAR(20),            -- excellent, good, moderate, poor
    behaviors_detected  JSONB,                  -- ["ground_foraging", "group_behavior_Lion"]
    endangered_found    JSONB,                  -- ["Rhinoceros"]
    analysis_metadata   JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_image_analysis_media ON image_analysis_results(media_asset_id);


-- ============================================================================
-- Audio Analysis Results  — Milestone 2
-- ============================================================================
CREATE TABLE audio_analysis_results (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_asset_id      UUID NOT NULL REFERENCES media_assets(id) ON DELETE CASCADE,
    species_identified  JSONB,                  -- [{"species": "Owl", "confidence": 0.85, "call_type": "song"}]
    acoustic_events     JSONB,                  -- [{"start":0.5,"end":1.2,"type":"bird_call","freq":800}]
    noise_level         NUMERIC(8,6),
    duration_seconds    NUMERIC(10,2),
    analysis_metadata   JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audio_analysis_media ON audio_analysis_results(media_asset_id);


-- ============================================================================
-- Audit Log  — Milestone 1
-- ============================================================================
CREATE TABLE audit_log (
    id          BIGSERIAL PRIMARY KEY,
    user_id     UUID REFERENCES users(id),
    action      VARCHAR(100) NOT NULL,
    entity      VARCHAR(100),
    entity_id   UUID,
    metadata    JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_user   ON audit_log(user_id);
CREATE INDEX idx_audit_entity ON audit_log(entity, entity_id);