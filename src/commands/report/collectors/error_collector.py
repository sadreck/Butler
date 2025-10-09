import os
from src.commands.report.helpers.error_results import ErrorResults
from src.commands.report.collector_base import CollectorBase
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import WorkflowStatus


class ErrorCollector(CollectorBase):
    def run(self) -> bool:
        data = {
            'org': self.org.name,
            'results': ErrorResults(),
        }
        output_file = os.path.join(self.output_path, 'errors.html')

        self.log.info('Searching for errors')
        error_results = self._get_errors(self.org.id)

        self.log.info(f"Processing {len(error_results)} results")
        for result in error_results:
            parent_dict = {
                key.replace("parent_", "", 1): value
                for key, value in result.items()
                if key.startswith("parent_")
            }
            workflow_error = WorkflowComponent.from_dict(result, False)
            workflow_parent = WorkflowComponent.from_dict(parent_dict, False)

            instance = data['results'].get_or_create(workflow_error, workflow_parent)

        self.log.info(f"Rendering output to {output_file}")
        output = self.render('error', 'Errors', data, output_file)
        return True

    def _get_errors(self, org_id: int) -> list:
        sql = f"""
            SELECT
                o.id			AS org_id,
                o.name			AS org_name,
                r.id			AS repo_id,
                r.visibility	AS repo_visibility,
                r.name			AS repo_name,
                r.ref			AS repo_ref,
                r.ref_type		AS repo_ref_type,
                r.ref_commit	AS repo_ref_commit,
                r.resolved_ref	AS repo_resolved_ref,
                r.resolved_ref_type	AS repo_resolved_ref_type,
                r.status		AS repo_status,
                r.poll_status	AS repo_poll_status,
                r.redirect_id	AS repo_redirect_id,
                r.stars         AS repo_stars,
                r.fork          AS repo_fork,
                r.archive		AS repo_archive,
                w.id			AS workflow_id,
                w.redirect_id	AS workflow_redirect_id,
                w.path			AS workflow_path,
                w.type			AS workflow_type,
                w.status		AS workflow_status,
                
                o2.id			AS parent_org_id,
                o2.name			AS parent_org_name,
                r2.id			AS parent_repo_id,
                r2.visibility	AS parent_repo_visibility,
                r2.name			AS parent_repo_name,
                r2.ref			AS parent_repo_ref,
                r2.ref_type		AS parent_repo_ref_type,
                r2.resolved_ref	AS parent_repo_resolved_ref,
                r2.resolved_ref_type	AS parent_repo_resolved_ref_type,
                r2.ref_commit	AS parent_repo_ref_commit,
                r2.status		AS parent_repo_status,
                r2.poll_status	AS parent_repo_poll_status,
                r2.redirect_id	AS parent_repo_redirect_id,
                r2.stars        AS parent_repo_stars,
                r2.fork         AS parent_repo_fork,
                r2.archive		AS parent_repo_archive,
                w2.id			AS parent_workflow_id,
                w2.redirect_id	AS parent_workflow_redirect_id,
                w2.path			AS parent_workflow_path,
                w2.type			AS parent_workflow_type,
                w2.status		AS parent_workflow_status
            FROM workflows w
            JOIN repositories r ON r.id = w.repo_id
            JOIN organisations o ON o.id = r.org_id
            JOIN (
                WITH RECURSIVE transitive(parent_id, child_id, depth) AS (
                  SELECT parent_id, child_id, 1
                  FROM workflow_relationships
                  UNION
                  SELECT t.parent_id, wr.child_id, t.depth + 1
                  FROM transitive AS t
                  JOIN workflow_relationships AS wr
                    ON wr.parent_id = t.child_id
                )
                SELECT parent_id, child_id, depth
                FROM transitive
                ORDER BY parent_id
            ) wr ON wr.child_id = w.id
            JOIN workflows w2 ON w2.id = wr.parent_id
            JOIN repositories r2 ON r2.id = w2.repo_id
            JOIN organisations o2 ON o2.id = r2.org_id
            WHERE
                w.status IN(:error, :missing)
                AND o2.id = :org_id
                AND NOT (LOWER(o.name) = 'github' AND LOWER(w.path) LIKE 'action/%')
        """

        return self.database.select(sql, {'org_id': org_id, 'error': WorkflowStatus.ERROR, 'missing': WorkflowStatus.MISSING})
