PRAGMA foreign_keys = ON;

CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    repository_uri TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE metadata_configurations (
    metadata_configuration_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    storage_profile TEXT NOT NULL CHECK (storage_profile IN ('broad', 'essential')),
    encryption_scope TEXT NOT NULL CHECK (encryption_scope IN (
        'environment', 'full_database', 'selected_fields', 'none'
    )),
    backups_encrypted INTEGER NOT NULL CHECK (backups_encrypted IN (0, 1)),
    encryption_method TEXT,
    key_reference TEXT,
    decision_reason TEXT NOT NULL,
    decided_by_person_id TEXT REFERENCES people(person_id),
    effective_at TEXT NOT NULL,
    supersedes_configuration_id TEXT REFERENCES metadata_configurations(metadata_configuration_id),
    CHECK (encryption_scope = 'none' OR encryption_method IS NOT NULL),
    CHECK (key_reference IS NULL OR encryption_scope <> 'none'),
    UNIQUE (project_id, effective_at)
);

CREATE TABLE knowledge_items (
    knowledge_item_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    external_id TEXT NOT NULL,
    item_type TEXT NOT NULL,
    source_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (project_id, external_id)
);

CREATE TABLE knowledge_relations (
    knowledge_relation_id TEXT PRIMARY KEY,
    source_item_id TEXT NOT NULL REFERENCES knowledge_items(knowledge_item_id),
    target_item_id TEXT NOT NULL REFERENCES knowledge_items(knowledge_item_id),
    relation_type TEXT NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    created_at TEXT NOT NULL,
    CHECK (source_item_id <> target_item_id),
    UNIQUE (source_item_id, target_item_id, relation_type, valid_from)
);

CREATE TABLE architecture_graphs (
    graph_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    version_id TEXT REFERENCES versions(version_id),
    cycle_id TEXT REFERENCES development_cycles(cycle_id),
    graph_scope TEXT NOT NULL CHECK (graph_scope IN ('global', 'subsystem', 'component')),
    status TEXT NOT NULL CHECK (status IN ('draft', 'approved', 'superseded')),
    canonical_source TEXT NOT NULL DEFAULT 'metadata',
    source_reference TEXT,
    created_at TEXT NOT NULL,
    supersedes_graph_id TEXT REFERENCES architecture_graphs(graph_id)
);

CREATE TABLE graph_nodes (
    graph_node_id TEXT PRIMARY KEY,
    graph_id TEXT NOT NULL REFERENCES architecture_graphs(graph_id),
    stable_id TEXT NOT NULL,
    node_type TEXT NOT NULL CHECK (node_type IN ('component', 'document', 'data', 'tool', 'agent', 'environment', 'orchestrator')),
    name TEXT NOT NULL,
    execution_mode TEXT CHECK (execution_mode IS NULL OR execution_mode IN ('deterministic', 'prompt_ai', 'agentic_ai', 'hybrid')),
    owner_reference TEXT,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE (graph_id, stable_id)
);

CREATE TABLE graph_edges (
    graph_edge_id TEXT PRIMARY KEY,
    graph_id TEXT NOT NULL REFERENCES architecture_graphs(graph_id),
    source_node_id TEXT NOT NULL REFERENCES graph_nodes(graph_node_id),
    target_node_id TEXT NOT NULL REFERENCES graph_nodes(graph_node_id),
    relation_type TEXT NOT NULL CHECK (relation_type IN ('flows_to', 'depends_on', 'contracts_with', 'owns', 'validates', 'derives', 'authorizes', 'orchestrates')),
    contract_reference TEXT,
    ordinal INTEGER NOT NULL CHECK (ordinal > 0),
    UNIQUE (graph_id, source_node_id, target_node_id, relation_type),
    CHECK (source_node_id <> target_node_id)
);

CREATE TABLE projection_definitions (
    projection_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    name TEXT NOT NULL,
    output_type TEXT NOT NULL,
    output_path TEXT,
    query_text TEXT NOT NULL,
    template_uri TEXT,
    template_sha256 TEXT,
    projection_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (project_id, name, projection_version)
);

CREATE TABLE people (
    person_id TEXT PRIMARY KEY,
    pseudonym TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    created_at TEXT NOT NULL,
    retired_at TEXT
);

CREATE TABLE environments (
    environment_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    fingerprint_sha256 TEXT NOT NULL UNIQUE,
    hardware_json TEXT NOT NULL DEFAULT '{}',
    operating_system TEXT,
    runtime_json TEXT NOT NULL DEFAULT '{}',
    dependencies_json TEXT NOT NULL DEFAULT '{}',
    configuration_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE versions (
    version_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    version TEXT NOT NULL,
    commit_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (project_id, version),
    UNIQUE (project_id, commit_hash)
);

CREATE TABLE development_cycles (
    cycle_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES versions(version_id),
    parent_cycle_id TEXT REFERENCES development_cycles(cycle_id),
    cycle_type TEXT NOT NULL CHECK (cycle_type IN (
        'feature', 'bugfix', 'refactoring', 'documentation', 'data_change',
        'security', 'release', 'other'
    )),
    objective TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    conclusion TEXT,
    limitations TEXT,
    created_by_person_id TEXT REFERENCES people(person_id)
);

CREATE TABLE test_definitions (
    test_definition_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    external_id TEXT NOT NULL,
    test_type TEXT NOT NULL CHECK (test_type IN (
        'functional', 'data', 'performance', 'security', 'migration',
        'recovery', 'accessibility', 'human_review', 'other'
    )),
    title TEXT NOT NULL,
    source_document TEXT NOT NULL,
    source_revision TEXT,
    requirement_reference TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (project_id, external_id, source_revision)
);

CREATE TABLE test_run_groups (
    run_group_id TEXT PRIMARY KEY,
    cycle_id TEXT NOT NULL REFERENCES development_cycles(cycle_id),
    purpose TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    conclusion TEXT,
    limitations TEXT
);

CREATE TABLE test_runs (
    test_run_id TEXT PRIMARY KEY,
    run_group_id TEXT NOT NULL REFERENCES test_run_groups(run_group_id),
    test_definition_id TEXT REFERENCES test_definitions(test_definition_id),
    environment_id TEXT NOT NULL REFERENCES environments(environment_id),
    attempt_number INTEGER NOT NULL CHECK (attempt_number > 0),
    status TEXT NOT NULL CHECK (status IN (
        'passed', 'failed', 'skipped', 'inconclusive', 'error'
    )),
    started_at TEXT NOT NULL,
    completed_at TEXT,
    duration_ms REAL CHECK (duration_ms IS NULL OR duration_ms >= 0),
    method TEXT NOT NULL,
    load_description TEXT,
    dataset_reference TEXT,
    conclusion TEXT,
    limitations TEXT,
    executed_by_person_id TEXT REFERENCES people(person_id),
    supersedes_test_run_id TEXT REFERENCES test_runs(test_run_id),
    UNIQUE (run_group_id, test_definition_id, environment_id, attempt_number)
);

CREATE TABLE test_results (
    test_result_id TEXT PRIMARY KEY,
    test_run_id TEXT NOT NULL REFERENCES test_runs(test_run_id),
    case_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN (
        'passed', 'failed', 'skipped', 'inconclusive', 'error'
    )),
    expected_summary TEXT,
    observed_summary TEXT,
    error_code TEXT,
    duration_ms REAL CHECK (duration_ms IS NULL OR duration_ms >= 0),
    created_at TEXT NOT NULL
);

CREATE TABLE performance_metrics (
    metric_id TEXT PRIMARY KEY,
    test_run_id TEXT NOT NULL REFERENCES test_runs(test_run_id),
    metric_name TEXT NOT NULL,
    unit TEXT NOT NULL,
    sample_count INTEGER CHECK (sample_count IS NULL OR sample_count >= 0),
    mean_value REAL,
    median_value REAL,
    standard_deviation REAL,
    p50_value REAL,
    p95_value REAL,
    p99_value REAL,
    confidence_level REAL,
    confidence_interval_low REAL,
    confidence_interval_high REAL,
    minimum_value REAL,
    maximum_value REAL,
    baseline_metric_id TEXT REFERENCES performance_metrics(metric_id),
    relative_change REAL,
    big_o TEXT,
    algorithm_parameters_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    UNIQUE (test_run_id, metric_name, unit)
);

CREATE TABLE resource_measurements (
    resource_measurement_id TEXT PRIMARY KEY,
    test_run_id TEXT NOT NULL REFERENCES test_runs(test_run_id),
    resource_type TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    aggregation TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE human_evaluations (
    human_evaluation_id TEXT PRIMARY KEY,
    cycle_id TEXT NOT NULL REFERENCES development_cycles(cycle_id),
    test_run_id TEXT REFERENCES test_runs(test_run_id),
    evaluator_person_id TEXT REFERENCES people(person_id),
    criterion TEXT NOT NULL,
    scale TEXT,
    score REAL,
    conclusion TEXT NOT NULL,
    limitations TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE version_reviews (
    version_review_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES versions(version_id),
    cycle_id TEXT REFERENCES development_cycles(cycle_id),
    evaluator_person_id TEXT REFERENCES people(person_id),
    score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    overall_comment TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN (
        'approved', 'approved_with_reservations', 'correction_requested',
        'evolution_requested', 'refactoring_requested', 'rejected'
    )),
    scope_summary TEXT,
    limitations TEXT,
    reviewed_at TEXT NOT NULL
);

CREATE TABLE version_review_entries (
    review_entry_id TEXT PRIMARY KEY,
    version_review_id TEXT NOT NULL REFERENCES version_reviews(version_review_id),
    entry_type TEXT NOT NULL CHECK (entry_type IN (
        'positive', 'negative', 'improvement', 'observation'
    )),
    ordinal INTEGER NOT NULL CHECK (ordinal > 0),
    content TEXT NOT NULL,
    UNIQUE (version_review_id, entry_type, ordinal)
);

CREATE TABLE review_findings (
    review_finding_id TEXT PRIMARY KEY,
    version_review_id TEXT NOT NULL REFERENCES version_reviews(version_review_id),
    finding_type TEXT NOT NULL CHECK (finding_type IN ('bug', 'feature', 'refactor')),
    area TEXT,
    score INTEGER CHECK (score IS NULL OR score BETWEEN 0 AND 100),
    problem_or_absence TEXT NOT NULL,
    comment TEXT,
    improvement TEXT,
    impact TEXT,
    perceived_priority TEXT,
    preserved_behavior TEXT,
    formalized_knowledge_item_id TEXT REFERENCES knowledge_items(knowledge_item_id),
    created_at TEXT NOT NULL
);

CREATE TABLE review_ingestions (
    review_ingestion_id TEXT PRIMARY KEY,
    version_review_id TEXT NOT NULL REFERENCES version_reviews(version_review_id),
    source_path TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    expected_finding_count INTEGER NOT NULL CHECK (expected_finding_count >= 0),
    persisted_finding_count INTEGER NOT NULL CHECK (persisted_finding_count >= 0),
    persisted_at TEXT NOT NULL,
    verified_at TEXT,
    source_cleared_at TEXT,
    UNIQUE (source_path, source_sha256),
    CHECK (source_cleared_at IS NULL OR verified_at IS NOT NULL),
    CHECK (verified_at IS NULL OR expected_finding_count = persisted_finding_count)
);

CREATE TABLE change_requests (
    change_request_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    version_id TEXT REFERENCES versions(version_id),
    request_type TEXT NOT NULL CHECK (request_type IN ('bug', 'feature', 'refactor')),
    source_path TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    title TEXT NOT NULL,
    requested_by_person_id TEXT REFERENCES people(person_id),
    created_at TEXT NOT NULL,
    formalized_knowledge_item_id TEXT REFERENCES knowledge_items(knowledge_item_id),
    UNIQUE (project_id, source_path, source_sha256)
);

CREATE TABLE change_proposals (
    proposal_id TEXT PRIMARY KEY,
    change_request_id TEXT NOT NULL REFERENCES change_requests(change_request_id),
    status TEXT NOT NULL CHECK (status IN (
        'draft', 'discussing', 'awaiting_approval', 'approved', 'rejected', 'superseded'
    )),
    created_at TEXT NOT NULL
);

CREATE TABLE proposal_revisions (
    proposal_revision_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL REFERENCES change_proposals(proposal_id),
    revision_number INTEGER NOT NULL CHECK (revision_number > 0),
    content_sha256 TEXT NOT NULL,
    source_path TEXT NOT NULL,
    source_commit TEXT,
    authored_by_person_id TEXT REFERENCES people(person_id),
    created_at TEXT NOT NULL,
    supersedes_revision_id TEXT REFERENCES proposal_revisions(proposal_revision_id),
    UNIQUE (proposal_id, revision_number),
    UNIQUE (proposal_id, content_sha256)
);

CREATE TABLE proposal_feedback (
    proposal_feedback_id TEXT PRIMARY KEY,
    proposal_revision_id TEXT NOT NULL REFERENCES proposal_revisions(proposal_revision_id),
    decision TEXT NOT NULL CHECK (decision IN (
        'approved', 'partially_agreed', 'revision_requested', 'rejected'
    )),
    source_sha256 TEXT NOT NULL,
    source_commit TEXT,
    provided_by_person_id TEXT REFERENCES people(person_id),
    created_at TEXT NOT NULL
);

CREATE TABLE proposal_approvals (
    proposal_approval_id TEXT PRIMARY KEY,
    proposal_revision_id TEXT NOT NULL REFERENCES proposal_revisions(proposal_revision_id),
    approved_content_sha256 TEXT NOT NULL,
    approved_by_person_id TEXT NOT NULL REFERENCES people(person_id),
    approved_at TEXT NOT NULL,
    revoked_at TEXT,
    revocation_reason TEXT,
    UNIQUE (proposal_revision_id),
    CHECK (revoked_at IS NULL OR revocation_reason IS NOT NULL)
);

CREATE TABLE artifacts (
    artifact_id TEXT PRIMARY KEY,
    cycle_id TEXT REFERENCES development_cycles(cycle_id),
    test_run_id TEXT REFERENCES test_runs(test_run_id),
    artifact_type TEXT NOT NULL,
    uri TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    media_type TEXT,
    sensitivity TEXT NOT NULL DEFAULT 'internal',
    encryption_method TEXT,
    key_reference TEXT,
    created_at TEXT NOT NULL,
    CHECK (cycle_id IS NOT NULL OR test_run_id IS NOT NULL)
);

CREATE INDEX idx_versions_project_created
    ON versions(project_id, created_at);
CREATE INDEX idx_knowledge_items_project_type
    ON knowledge_items(project_id, item_type);
CREATE INDEX idx_knowledge_relations_source_type
    ON knowledge_relations(source_item_id, relation_type);
CREATE INDEX idx_knowledge_relations_target_type
    ON knowledge_relations(target_item_id, relation_type);
CREATE INDEX idx_graphs_project_created
    ON architecture_graphs(project_id, created_at);
CREATE INDEX idx_graph_nodes_graph_type
    ON graph_nodes(graph_id, node_type, execution_mode);
CREATE INDEX idx_graph_edges_source_type
    ON graph_edges(source_node_id, relation_type);
CREATE INDEX idx_graph_edges_target_type
    ON graph_edges(target_node_id, relation_type);
CREATE INDEX idx_cycles_version_type
    ON development_cycles(version_id, cycle_type);
CREATE INDEX idx_definitions_project_type
    ON test_definitions(project_id, test_type);
CREATE INDEX idx_groups_cycle_started
    ON test_run_groups(cycle_id, started_at);
CREATE INDEX idx_runs_group_status
    ON test_runs(run_group_id, status);
CREATE INDEX idx_runs_definition_environment
    ON test_runs(test_definition_id, environment_id, started_at);
CREATE INDEX idx_results_run_status
    ON test_results(test_run_id, status);
CREATE INDEX idx_metrics_run_name
    ON performance_metrics(test_run_id, metric_name);
CREATE INDEX idx_resources_run_type
    ON resource_measurements(test_run_id, resource_type);
CREATE INDEX idx_evaluations_cycle_criterion
    ON human_evaluations(cycle_id, criterion);
CREATE INDEX idx_version_reviews_version_date
    ON version_reviews(version_id, reviewed_at);
CREATE INDEX idx_review_entries_review_type
    ON version_review_entries(version_review_id, entry_type, ordinal);
CREATE INDEX idx_review_findings_review_type
    ON review_findings(version_review_id, finding_type);
CREATE INDEX idx_change_requests_project_type
    ON change_requests(project_id, request_type, created_at);
CREATE INDEX idx_proposals_request_status
    ON change_proposals(change_request_id, status);
CREATE INDEX idx_proposal_revisions_proposal_number
    ON proposal_revisions(proposal_id, revision_number);
CREATE INDEX idx_proposal_feedback_revision_date
    ON proposal_feedback(proposal_revision_id, created_at);
CREATE INDEX idx_artifacts_run_type
    ON artifacts(test_run_id, artifact_type);

CREATE VIEW test_run_summary AS
SELECT
    g.run_group_id,
    c.cycle_id,
    v.version,
    v.commit_hash,
    COUNT(r.test_run_id) AS total_runs,
    SUM(CASE WHEN r.status = 'passed' THEN 1 ELSE 0 END) AS passed_runs,
    SUM(CASE WHEN r.status = 'failed' THEN 1 ELSE 0 END) AS failed_runs,
    SUM(CASE WHEN r.status = 'skipped' THEN 1 ELSE 0 END) AS skipped_runs,
    SUM(CASE WHEN r.status = 'inconclusive' THEN 1 ELSE 0 END) AS inconclusive_runs,
    SUM(CASE WHEN r.status = 'error' THEN 1 ELSE 0 END) AS error_runs
FROM test_run_groups g
JOIN development_cycles c ON c.cycle_id = g.cycle_id
JOIN versions v ON v.version_id = c.version_id
LEFT JOIN test_runs r ON r.run_group_id = g.run_group_id
GROUP BY g.run_group_id, c.cycle_id, v.version, v.commit_hash;

CREATE VIEW approved_proposal_revisions AS
SELECT
    p.proposal_id,
    pr.proposal_revision_id,
    pr.revision_number,
    pr.content_sha256,
    pa.approved_at,
    pa.approved_by_person_id
FROM proposal_approvals pa
JOIN proposal_revisions pr
  ON pr.proposal_revision_id = pa.proposal_revision_id
JOIN change_proposals p ON p.proposal_id = pr.proposal_id
WHERE pa.revoked_at IS NULL
  AND pa.approved_content_sha256 = pr.content_sha256;

CREATE VIEW version_review_comparison AS
SELECT
    p.project_id,
    p.name AS project_name,
    v.version,
    v.commit_hash,
    vr.version_review_id,
    vr.score,
    vr.overall_comment,
    vr.decision,
    vr.reviewed_at,
    LAG(vr.score) OVER (
        PARTITION BY p.project_id ORDER BY vr.reviewed_at, vr.version_review_id
    ) AS previous_score,
    vr.score - LAG(vr.score) OVER (
        PARTITION BY p.project_id ORDER BY vr.reviewed_at, vr.version_review_id
    ) AS score_change
FROM version_reviews vr
JOIN versions v ON v.version_id = vr.version_id
JOIN projects p ON p.project_id = v.project_id;

CREATE TRIGGER prevent_architecture_graphs_update
BEFORE UPDATE ON architecture_graphs
BEGIN
    SELECT RAISE(ABORT, 'architecture_graphs are append-only');
END;

CREATE TRIGGER prevent_architecture_graphs_delete
BEFORE DELETE ON architecture_graphs
BEGIN
    SELECT RAISE(ABORT, 'architecture_graphs are append-only');
END;

CREATE TRIGGER prevent_graph_nodes_update
BEFORE UPDATE ON graph_nodes
BEGIN
    SELECT RAISE(ABORT, 'graph_nodes are append-only');
END;

CREATE TRIGGER prevent_graph_nodes_delete
BEFORE DELETE ON graph_nodes
BEGIN
    SELECT RAISE(ABORT, 'graph_nodes are append-only');
END;

CREATE TRIGGER prevent_graph_edges_update
BEFORE UPDATE ON graph_edges
BEGIN
    SELECT RAISE(ABORT, 'graph_edges are append-only');
END;

CREATE TRIGGER prevent_graph_edges_delete
BEFORE DELETE ON graph_edges
BEGIN
    SELECT RAISE(ABORT, 'graph_edges are append-only');
END;

CREATE TRIGGER prevent_metadata_configurations_update
BEFORE UPDATE ON metadata_configurations
BEGIN
    SELECT RAISE(ABORT, 'metadata_configurations are append-only');
END;

CREATE TRIGGER prevent_metadata_configurations_delete
BEFORE DELETE ON metadata_configurations
BEGIN
    SELECT RAISE(ABORT, 'metadata_configurations are append-only');
END;

CREATE TRIGGER prevent_version_reviews_update
BEFORE UPDATE ON version_reviews
BEGIN
    SELECT RAISE(ABORT, 'version_reviews are append-only');
END;

CREATE TRIGGER prevent_version_reviews_delete
BEFORE DELETE ON version_reviews
BEGIN
    SELECT RAISE(ABORT, 'version_reviews are append-only');
END;

CREATE TRIGGER prevent_review_entries_update
BEFORE UPDATE ON version_review_entries
BEGIN
    SELECT RAISE(ABORT, 'version_review_entries are append-only');
END;

CREATE TRIGGER prevent_review_entries_delete
BEFORE DELETE ON version_review_entries
BEGIN
    SELECT RAISE(ABORT, 'version_review_entries are append-only');
END;

CREATE TRIGGER prevent_review_findings_update
BEFORE UPDATE ON review_findings
BEGIN
    SELECT RAISE(ABORT, 'review_findings are append-only');
END;

CREATE TRIGGER prevent_review_findings_delete
BEFORE DELETE ON review_findings
BEGIN
    SELECT RAISE(ABORT, 'review_findings are append-only');
END;

CREATE TRIGGER validate_proposal_approval_hash
BEFORE INSERT ON proposal_approvals
WHEN NEW.approved_content_sha256 <> (
    SELECT content_sha256
    FROM proposal_revisions
    WHERE proposal_revision_id = NEW.proposal_revision_id
)
BEGIN
    SELECT RAISE(ABORT, 'approval hash must match the exact proposal revision');
END;

CREATE TRIGGER require_explicit_approved_feedback
BEFORE INSERT ON proposal_approvals
WHEN NOT EXISTS (
    SELECT 1
    FROM proposal_feedback
    WHERE proposal_revision_id = NEW.proposal_revision_id
      AND decision = 'approved'
)
BEGIN
    SELECT RAISE(ABORT, 'explicit approved feedback is required');
END;

CREATE TRIGGER prevent_proposal_revisions_update
BEFORE UPDATE ON proposal_revisions
BEGIN
    SELECT RAISE(ABORT, 'proposal_revisions are append-only');
END;

CREATE TRIGGER prevent_proposal_revisions_delete
BEFORE DELETE ON proposal_revisions
BEGIN
    SELECT RAISE(ABORT, 'proposal_revisions are append-only');
END;

CREATE TRIGGER prevent_proposal_feedback_update
BEFORE UPDATE ON proposal_feedback
BEGIN
    SELECT RAISE(ABORT, 'proposal_feedback is append-only');
END;

CREATE TRIGGER prevent_proposal_feedback_delete
BEFORE DELETE ON proposal_feedback
BEGIN
    SELECT RAISE(ABORT, 'proposal_feedback is append-only');
END;

CREATE TRIGGER prevent_test_runs_update
BEFORE UPDATE ON test_runs
BEGIN
    SELECT RAISE(ABORT, 'test_runs are append-only');
END;

CREATE TRIGGER prevent_test_runs_delete
BEFORE DELETE ON test_runs
BEGIN
    SELECT RAISE(ABORT, 'test_runs are append-only');
END;

CREATE TRIGGER prevent_test_results_update
BEFORE UPDATE ON test_results
BEGIN
    SELECT RAISE(ABORT, 'test_results are append-only');
END;

CREATE TRIGGER prevent_test_results_delete
BEFORE DELETE ON test_results
BEGIN
    SELECT RAISE(ABORT, 'test_results are append-only');
END;

CREATE TRIGGER prevent_performance_metrics_update
BEFORE UPDATE ON performance_metrics
BEGIN
    SELECT RAISE(ABORT, 'performance_metrics are append-only');
END;

CREATE TRIGGER prevent_performance_metrics_delete
BEFORE DELETE ON performance_metrics
BEGIN
    SELECT RAISE(ABORT, 'performance_metrics are append-only');
END;
