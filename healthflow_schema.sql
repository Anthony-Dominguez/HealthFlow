-- HealthFlow+ Database Schema
-- PostgreSQL with pgvector extension (Supabase)
-- Version: 1.0

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE document_type AS ENUM (
    'lab_report',
    'medication_list',
    'discharge_summary',
    'imaging_report',
    'prescription',
    'insurance_card',
    'insurance_eob',
    'vaccination_record',
    'allergy_list',
    'care_plan',
    'visit_summary',
    'referral',
    'voice_note',
    'other'
);

CREATE TYPE processing_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'partially_completed'
);

CREATE TYPE entity_type AS ENUM (
    'medication',
    'lab_result',
    'diagnosis',
    'symptom',
    'doctor',
    'appointment',
    'procedure',
    'allergy',
    'vital_sign',
    'immunization'
);

CREATE TYPE event_type AS ENUM (
    'lab_completed',
    'medication_started',
    'medication_ended',
    'symptom_logged',
    'appointment_scheduled',
    'appointment_completed',
    'procedure_completed',
    'diagnosis_received',
    'document_uploaded',
    'vital_recorded',
    'immunization_received'
);

CREATE TYPE message_role AS ENUM (
    'user',
    'assistant',
    'system'
);

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users table (extends Supabase auth.users)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    date_of_birth DATE,
    phone_number TEXT,
    profile_data JSONB DEFAULT '{}'::jsonb,
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE users IS 'User profiles extending Supabase authentication';
COMMENT ON COLUMN users.profile_data IS 'Additional profile information (gender, address, emergency contact, etc.)';
COMMENT ON COLUMN users.preferences IS 'User preferences (notifications, timezone, language, etc.)';

-- ============================================================================
-- DOCUMENTS
-- ============================================================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- File information
    file_name TEXT NOT NULL,
    storage_path TEXT NOT NULL, -- Supabase Storage path
    mime_type TEXT NOT NULL,
    file_size BIGINT NOT NULL, -- bytes

    -- Document classification
    document_type document_type NOT NULL,
    document_subtype TEXT, -- Additional granularity (e.g., 'CBC' for lab_report)

    -- Processing
    processing_status processing_status NOT NULL DEFAULT 'pending',
    processing_error TEXT,
    extracted_text TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Dates
    document_date DATE, -- Actual date of the document (e.g., lab date)
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE documents IS 'Uploaded healthcare documents with metadata and processing status';
COMMENT ON COLUMN documents.storage_path IS 'Reference to file in Supabase Storage bucket';
COMMENT ON COLUMN documents.extracted_text IS 'Full extracted text from OCR/parsing';
COMMENT ON COLUMN documents.metadata IS 'Additional metadata (OCR confidence, source, provider info, etc.)';
COMMENT ON COLUMN documents.document_date IS 'Date from document content (not upload date)';

-- ============================================================================
-- MEDICAL ENTITIES
-- ============================================================================

CREATE TABLE medical_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,

    -- Entity classification
    entity_type entity_type NOT NULL,

    -- Flexible entity data (varies by type)
    entity_data JSONB NOT NULL,

    -- Temporal information
    entity_date DATE, -- Date of the entity (lab date, prescription date, etc.)
    entity_end_date DATE, -- For ranges (medication end, appointment duration)

    -- Extraction metadata
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    extraction_confidence DECIMAL(3,2), -- 0.00 to 1.00
    is_verified BOOLEAN DEFAULT FALSE, -- User-verified accuracy

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE medical_entities IS 'Structured medical data extracted from documents';
COMMENT ON COLUMN medical_entities.entity_data IS 'Type-specific fields stored as JSON (see documentation for schemas)';
COMMENT ON COLUMN medical_entities.extraction_confidence IS 'AI extraction confidence score';
COMMENT ON COLUMN medical_entities.is_verified IS 'User has confirmed accuracy';

-- Example entity_data structures (documented):
COMMENT ON COLUMN medical_entities.entity_data IS
'Entity type schemas:
- medication: {name, dosage, frequency, route, prescriber, pharmacy, refills, ndc_code}
- lab_result: {test_name, value, unit, reference_range, is_critical, lab_name, ordering_physician}
- diagnosis: {icd10_code, condition_name, onset_date, diagnosed_by, severity}
- symptom: {symptom_name, severity, duration, body_location, notes}
- doctor: {name, specialty, npi, phone, address, facility}
- appointment: {provider, location, reason, status, duration_minutes}
- procedure: {procedure_name, cpt_code, provider, facility, notes}
- allergy: {allergen, reaction, severity, onset_date, verified_date}
- vital_sign: {type, value, unit, measurement_location}
- immunization: {vaccine_name, cvx_code, lot_number, manufacturer, site, route}';

-- ============================================================================
-- TIMELINE
-- ============================================================================

CREATE TABLE timeline_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,

    -- Event classification
    event_type event_type NOT NULL,
    title TEXT NOT NULL,
    description TEXT,

    -- Temporal information
    event_date DATE NOT NULL, -- Date without time
    event_timestamp TIMESTAMPTZ, -- Precise timestamp if available

    -- Additional data
    metadata JSONB DEFAULT '{}'::jsonb,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- User interaction
    is_starred BOOLEAN DEFAULT FALSE,
    user_notes TEXT,

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE timeline_events IS 'Unified timeline of all health events';
COMMENT ON COLUMN timeline_events.metadata IS 'Event-specific additional data';

-- Join table for timeline events and medical entities (many-to-many)
CREATE TABLE timeline_event_entities (
    timeline_event_id UUID NOT NULL REFERENCES timeline_events(id) ON DELETE CASCADE,
    medical_entity_id UUID NOT NULL REFERENCES medical_entities(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (timeline_event_id, medical_entity_id)
);

COMMENT ON TABLE timeline_event_entities IS 'Links timeline events to their related medical entities';

-- ============================================================================
-- VOICE LOGS
-- ============================================================================

CREATE TABLE voice_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL, -- Auto-created document

    -- Audio file
    audio_storage_path TEXT NOT NULL,
    audio_format TEXT, -- wav, mp3, m4a, etc.
    duration_seconds INTEGER,

    -- Transcription
    transcribed_text TEXT,
    transcription_confidence DECIMAL(3,2),
    transcription_language TEXT DEFAULT 'en',

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Temporal
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE voice_logs IS 'Voice-recorded symptom journals and notes';
COMMENT ON COLUMN voice_logs.metadata IS 'Additional data (device, location, extracted symptoms, etc.)';

-- ============================================================================
-- EMBEDDINGS & RAG
-- ============================================================================

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Chunk content
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL, -- Order within document

    -- Chunking metadata
    token_count INTEGER,
    char_count INTEGER,

    -- Context
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(document_id, chunk_index)
);

COMMENT ON TABLE document_chunks IS 'Document chunks for embedding generation';
COMMENT ON COLUMN document_chunks.metadata IS 'Chunk metadata (section_title, page_number, context, etc.)';

CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_id UUID NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Vector embedding
    embedding_vector vector(1536), -- OpenAI ada-002 or similar (adjust dimension as needed)

    -- Model information
    embedding_model TEXT NOT NULL, -- e.g., 'text-embedding-ada-002'
    model_version TEXT,

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(chunk_id, embedding_model)
);

COMMENT ON TABLE embeddings IS 'Vector embeddings for semantic search';
COMMENT ON COLUMN embeddings.embedding_vector IS 'Vector dimension should match embedding model (1536 for ada-002, 768 for sentence-transformers)';

-- ============================================================================
-- CHAT SYSTEM
-- ============================================================================

CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Session info
    title TEXT,
    summary TEXT, -- AI-generated summary

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Temporal
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE chat_sessions IS 'Chat conversation sessions with AI agent';

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Message content
    role message_role NOT NULL,
    content TEXT NOT NULL,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    token_count INTEGER,

    -- Model information (for assistant messages)
    model_name TEXT,
    model_version TEXT,

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE chat_messages IS 'Individual messages within chat sessions';
COMMENT ON COLUMN chat_messages.metadata IS 'Message metadata (tool_calls, function_results, citations, etc.)';

-- Join table for chat message references to documents and entities
CREATE TABLE chat_message_references (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,

    -- Reference targets (one must be non-null)
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    medical_entity_id UUID REFERENCES medical_entities(id) ON DELETE CASCADE,

    -- Context
    reference_type TEXT, -- 'source', 'citation', 'context', etc.
    relevance_score DECIMAL(3,2), -- 0.00 to 1.00

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (document_id IS NOT NULL OR medical_entity_id IS NOT NULL)
);

COMMENT ON TABLE chat_message_references IS 'Links chat messages to referenced documents and entities';

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Documents
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_document_type ON documents(document_type);
CREATE INDEX idx_documents_processing_status ON documents(processing_status);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at DESC);
CREATE INDEX idx_documents_document_date ON documents(document_date DESC NULLS LAST);
CREATE INDEX idx_documents_user_date ON documents(user_id, document_date DESC NULLS LAST);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);
CREATE INDEX idx_documents_metadata ON documents USING GIN(metadata);

-- Full-text search on extracted text
CREATE INDEX idx_documents_extracted_text_fts ON documents USING GIN(to_tsvector('english', extracted_text));

-- Medical Entities
CREATE INDEX idx_entities_user_id ON medical_entities(user_id);
CREATE INDEX idx_entities_document_id ON medical_entities(document_id);
CREATE INDEX idx_entities_entity_type ON medical_entities(entity_type);
CREATE INDEX idx_entities_entity_date ON medical_entities(entity_date DESC NULLS LAST);
CREATE INDEX idx_entities_user_type ON medical_entities(user_id, entity_type);
CREATE INDEX idx_entities_user_date ON medical_entities(user_id, entity_date DESC NULLS LAST);
CREATE INDEX idx_entities_data ON medical_entities USING GIN(entity_data);
CREATE INDEX idx_entities_verified ON medical_entities(is_verified) WHERE is_verified = TRUE;

-- Specific entity_data searches (examples for common queries)
CREATE INDEX idx_entities_medication_name ON medical_entities
    USING GIN((entity_data->'name') gin_trgm_ops)
    WHERE entity_type = 'medication';

CREATE INDEX idx_entities_lab_test_name ON medical_entities
    USING GIN((entity_data->'test_name') gin_trgm_ops)
    WHERE entity_type = 'lab_result';

-- Timeline Events
CREATE INDEX idx_timeline_user_id ON timeline_events(user_id);
CREATE INDEX idx_timeline_document_id ON timeline_events(document_id);
CREATE INDEX idx_timeline_event_type ON timeline_events(event_type);
CREATE INDEX idx_timeline_event_date ON timeline_events(event_date DESC);
CREATE INDEX idx_timeline_user_date ON timeline_events(user_id, event_date DESC);
CREATE INDEX idx_timeline_starred ON timeline_events(user_id, is_starred) WHERE is_starred = TRUE;
CREATE INDEX idx_timeline_tags ON timeline_events USING GIN(tags);

-- Timeline Event Entities (join table)
CREATE INDEX idx_timeline_entities_event ON timeline_event_entities(timeline_event_id);
CREATE INDEX idx_timeline_entities_entity ON timeline_event_entities(medical_entity_id);

-- Voice Logs
CREATE INDEX idx_voice_logs_user_id ON voice_logs(user_id);
CREATE INDEX idx_voice_logs_document_id ON voice_logs(document_id);
CREATE INDEX idx_voice_logs_recorded_at ON voice_logs(recorded_at DESC);

-- Full-text search on transcribed text
CREATE INDEX idx_voice_logs_transcribed_text_fts ON voice_logs USING GIN(to_tsvector('english', transcribed_text));

-- Document Chunks
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_user_id ON document_chunks(user_id);
CREATE INDEX idx_chunks_doc_index ON document_chunks(document_id, chunk_index);

-- Full-text search on chunks
CREATE INDEX idx_chunks_text_fts ON document_chunks USING GIN(to_tsvector('english', chunk_text));

-- Embeddings (CRITICAL for performance)
CREATE INDEX idx_embeddings_chunk_id ON embeddings(chunk_id);
CREATE INDEX idx_embeddings_user_id ON embeddings(user_id);

-- IVFFlat index for vector similarity search (adjust lists parameter based on data size)
-- lists = rows/1000 is a good starting point (e.g., 100 for 100K rows)
CREATE INDEX idx_embeddings_vector_cosine ON embeddings
    USING ivfflat (embedding_vector vector_cosine_ops)
    WITH (lists = 100);

-- Alternative: HNSW index (if using pgvector 0.5.0+) - better recall, slower build
-- CREATE INDEX idx_embeddings_vector_hnsw ON embeddings
--     USING hnsw (embedding_vector vector_cosine_ops);

-- Chat Sessions
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_started_at ON chat_sessions(started_at DESC);
CREATE INDEX idx_chat_sessions_last_message ON chat_sessions(last_message_at DESC);

-- Chat Messages
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX idx_chat_messages_session_created ON chat_messages(session_id, created_at);

-- Chat Message References
CREATE INDEX idx_chat_refs_message_id ON chat_message_references(chat_message_id);
CREATE INDEX idx_chat_refs_document_id ON chat_message_references(document_id) WHERE document_id IS NOT NULL;
CREATE INDEX idx_chat_refs_entity_id ON chat_message_references(medical_entity_id) WHERE medical_entity_id IS NOT NULL;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON medical_entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_timeline_updated_at BEFORE UPDATE ON timeline_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voice_logs_updated_at BEFORE UPDATE ON voice_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update last_message_at when new message is added
CREATE OR REPLACE FUNCTION update_chat_session_last_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions
    SET last_message_at = NEW.created_at
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_session_last_message AFTER INSERT ON chat_messages
    FOR EACH ROW EXECUTE FUNCTION update_chat_session_last_message();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE timeline_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE timeline_event_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_message_references ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id);

-- Documents policies
CREATE POLICY "Users can view own documents"
    ON documents FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own documents"
    ON documents FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own documents"
    ON documents FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own documents"
    ON documents FOR DELETE
    USING (auth.uid() = user_id);

-- Medical entities policies
CREATE POLICY "Users can view own entities"
    ON medical_entities FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own entities"
    ON medical_entities FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own entities"
    ON medical_entities FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own entities"
    ON medical_entities FOR DELETE
    USING (auth.uid() = user_id);

-- Timeline policies
CREATE POLICY "Users can view own timeline"
    ON timeline_events FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own timeline events"
    ON timeline_events FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own timeline events"
    ON timeline_events FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own timeline events"
    ON timeline_events FOR DELETE
    USING (auth.uid() = user_id);

-- Timeline event entities policies
CREATE POLICY "Users can view own timeline entity links"
    ON timeline_event_entities FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM timeline_events
            WHERE id = timeline_event_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage own timeline entity links"
    ON timeline_event_entities FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM timeline_events
            WHERE id = timeline_event_id AND user_id = auth.uid()
        )
    );

-- Voice logs policies (similar pattern)
CREATE POLICY "Users can view own voice logs"
    ON voice_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own voice logs"
    ON voice_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own voice logs"
    ON voice_logs FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own voice logs"
    ON voice_logs FOR DELETE
    USING (auth.uid() = user_id);

-- Document chunks policies
CREATE POLICY "Users can view own chunks"
    ON document_chunks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chunks"
    ON document_chunks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own chunks"
    ON document_chunks FOR DELETE
    USING (auth.uid() = user_id);

-- Embeddings policies
CREATE POLICY "Users can view own embeddings"
    ON embeddings FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own embeddings"
    ON embeddings FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own embeddings"
    ON embeddings FOR DELETE
    USING (auth.uid() = user_id);

-- Chat sessions policies
CREATE POLICY "Users can view own chat sessions"
    ON chat_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat sessions"
    ON chat_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own chat sessions"
    ON chat_sessions FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own chat sessions"
    ON chat_sessions FOR DELETE
    USING (auth.uid() = user_id);

-- Chat messages policies
CREATE POLICY "Users can view own chat messages"
    ON chat_messages FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat messages"
    ON chat_messages FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Chat message references policies
CREATE POLICY "Users can view own message references"
    ON chat_message_references FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM chat_messages
            WHERE id = chat_message_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage own message references"
    ON chat_message_references FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM chat_messages
            WHERE id = chat_message_id AND user_id = auth.uid()
        )
    );

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to search documents and entities by embedding similarity
CREATE OR REPLACE FUNCTION search_by_embedding(
    query_embedding vector(1536),
    query_user_id UUID,
    match_threshold DECIMAL DEFAULT 0.7,
    match_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    chunk_text TEXT,
    similarity DECIMAL,
    document_name TEXT,
    document_type document_type,
    document_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.chunk_id,
        dc.document_id,
        dc.chunk_text,
        ROUND((1 - (e.embedding_vector <=> query_embedding))::numeric, 3) AS similarity,
        d.file_name AS document_name,
        d.document_type,
        d.document_date
    FROM embeddings e
    JOIN document_chunks dc ON e.chunk_id = dc.id
    JOIN documents d ON dc.document_id = d.id
    WHERE e.user_id = query_user_id
        AND 1 - (e.embedding_vector <=> query_embedding) > match_threshold
    ORDER BY e.embedding_vector <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION search_by_embedding IS 'Semantic search using cosine similarity on embeddings';

-- Function to get user timeline with filters
CREATE OR REPLACE FUNCTION get_user_timeline(
    query_user_id UUID,
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL,
    event_types event_type[] DEFAULT NULL,
    limit_count INTEGER DEFAULT 50,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    event_id UUID,
    event_type event_type,
    title TEXT,
    description TEXT,
    event_date DATE,
    event_timestamp TIMESTAMPTZ,
    document_id UUID,
    document_name TEXT,
    entity_count INTEGER,
    is_starred BOOLEAN,
    tags TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        te.id AS event_id,
        te.event_type,
        te.title,
        te.description,
        te.event_date,
        te.event_timestamp,
        te.document_id,
        d.file_name AS document_name,
        COUNT(tee.medical_entity_id)::INTEGER AS entity_count,
        te.is_starred,
        te.tags
    FROM timeline_events te
    LEFT JOIN documents d ON te.document_id = d.id
    LEFT JOIN timeline_event_entities tee ON te.id = tee.timeline_event_id
    WHERE te.user_id = query_user_id
        AND (start_date IS NULL OR te.event_date >= start_date)
        AND (end_date IS NULL OR te.event_date <= end_date)
        AND (event_types IS NULL OR te.event_type = ANY(event_types))
    GROUP BY te.id, d.file_name
    ORDER BY te.event_date DESC, te.event_timestamp DESC NULLS LAST
    LIMIT limit_count
    OFFSET offset_count;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_user_timeline IS 'Retrieve user timeline with optional filtering';

-- Function to get entity summary by type
CREATE OR REPLACE FUNCTION get_entity_summary(
    query_user_id UUID
)
RETURNS TABLE (
    entity_type entity_type,
    total_count BIGINT,
    verified_count BIGINT,
    latest_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        me.entity_type,
        COUNT(*)::BIGINT AS total_count,
        COUNT(*) FILTER (WHERE me.is_verified)::BIGINT AS verified_count,
        MAX(me.entity_date) AS latest_date
    FROM medical_entities me
    WHERE me.user_id = query_user_id
    GROUP BY me.entity_type
    ORDER BY me.entity_type;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_entity_summary IS 'Get summary statistics of medical entities by type';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for recent documents with processing status
CREATE VIEW recent_documents_summary AS
SELECT
    d.id,
    d.user_id,
    d.file_name,
    d.document_type,
    d.processing_status,
    d.document_date,
    d.uploaded_at,
    COUNT(DISTINCT me.id) AS entity_count,
    COUNT(DISTINCT dc.id) AS chunk_count,
    d.file_size
FROM documents d
LEFT JOIN medical_entities me ON d.id = me.document_id
LEFT JOIN document_chunks dc ON d.id = dc.document_id
GROUP BY d.id
ORDER BY d.uploaded_at DESC;

COMMENT ON VIEW recent_documents_summary IS 'Summary view of documents with entity and chunk counts';

-- View for medications currently active
CREATE VIEW active_medications AS
SELECT
    me.id,
    me.user_id,
    me.entity_data->>'name' AS medication_name,
    me.entity_data->>'dosage' AS dosage,
    me.entity_data->>'frequency' AS frequency,
    me.entity_date AS start_date,
    me.entity_end_date AS end_date,
    me.document_id,
    d.file_name AS source_document
FROM medical_entities me
LEFT JOIN documents d ON me.document_id = d.id
WHERE me.entity_type = 'medication'
    AND (me.entity_end_date IS NULL OR me.entity_end_date >= CURRENT_DATE)
ORDER BY me.entity_date DESC;

COMMENT ON VIEW active_medications IS 'Currently active medications';

-- ============================================================================
-- GRANTS (adjust based on your Supabase setup)
-- ============================================================================

-- Grant appropriate permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
