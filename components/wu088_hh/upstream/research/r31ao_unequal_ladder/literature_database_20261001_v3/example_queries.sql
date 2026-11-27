-- Read-only examples; run against the successor SQLite DB.
SELECT source_id,title,acquisition_status,acquired_representation,remaining_gap FROM source_catalog ORDER BY source_id;
SELECT * FROM v_current_missing;
SELECT * FROM v_source_files WHERE source_id IN ('P04','P06','C12');
SELECT * FROM v_failed_attempts WHERE source_id='P04';
SELECT source_id,version_requested,version_acquired,raw_source_acquired,authority_role FROM code_version_policy;
SELECT source_id,title FROM catalog_search WHERE catalog_search MATCH 'Petras';
SELECT section_id,heading,snippet(report_search,2,'[',']','…',25) FROM report_search WHERE report_search MATCH 'Petras';
-- Both listed content parts form one backup set, not individual per-file mirrors.
SELECT * FROM v_payload_backup_sets WHERE asset_id='P04-R2-A1';
SELECT * FROM original_research_database_status;
