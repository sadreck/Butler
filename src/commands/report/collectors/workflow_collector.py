import os
from src.commands.report.helpers.workflow_results import WorkflowResults
from src.commands.report.collector_base import CollectorBase
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import WorkflowStatus


class WorkflowCollector(CollectorBase):
    _shortname = 'workflows'

    def generate_output_paths(self):
        self.outputs['html']['workflows'] = {
            'title': 'Workflows',
            'path': os.path.join(self.output_path, f'{self.org.name}-workflows.html'),
            'file': f'{self.org.name}-workflows.html'
        }

        self.outputs['csv']['workflows'] = {
            'title': 'Workflows',
            'path': os.path.join(self.output_path, f'{self.org.name}-workflows.csv'),
            'file': f'{self.org.name}-workflows.csv'
        }

    def run(self) -> bool:
        data = {
            'org': self.org.name,
            'results': WorkflowResults()
        }

        self.log.info('Searching for workflows')
        workflow_results = self._get_workflows(self.org.id)

        self.log.info(f"Processing {len(workflow_results)} results")
        for result in workflow_results:
            workflow = WorkflowComponent.from_dict(result, False)

            instance = data['results'].get_or_create(workflow, result['job_count'], result['triggers'])
            if instance['instance'].status == WorkflowStatus.MISSING:
                # Get additional info.
                self.log.debug(f"Getting additional information for {instance['instance']}")
                parent_workflows = self._get_caller_workflows(instance['instance'].id)
                for parent_workflow in parent_workflows:
                    data['results'].add_missing_workflows(workflow, parent_workflow)

        self._export(data)
        self.outputs['info'] = {
            'workflows': data['results'].count('workflows'),
            'actions': data['results'].count('actions'),
        }
        return True

    def _export(self, data: dict) -> None:
        if 'html' in self.export_formats:
            html_file = self.outputs['html']['workflows']['path']
            self.log.info(f"Saving HTML output to {html_file}")
            self.render('workflows', 'Workflows', data, html_file)

        if 'csv' in self.export_formats:
            self.write_to_csv(
                self.outputs['csv']['workflows']['path'],
                data['results'].for_csv()
            )

    def _get_caller_workflows(self, workflow_id: int) -> list:
        sql = f"""
            SELECT
                parent_id
            FROM (
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
            ) wr
            WHERE wr.child_id = :child_id
        """

        workflows = []
        results = self.database.select(sql, {'child_id': workflow_id})
        for result in results:
            workflow = self.database.get_full_workflow_from_id(result['parent_id'])
            if workflow:
                workflows.append(workflow)
        return workflows

    def _get_workflows(self, org_id: int) -> list:
        sql = f"""
            SELECT
                o.id			        AS org_id,
                o.name			        AS org_name,
                r.id			        AS repo_id,
                r.visibility	        AS repo_visibility,
                r.name			        AS repo_name,
                r.ref			        AS repo_ref,
                r.ref_type		        AS repo_ref_type,
                r.ref_commit	        AS repo_ref_commit,
                r.resolved_ref	        AS repo_resolved_ref,
                r.resolved_ref_type	    AS repo_resolved_ref_type,
                r.status		        AS repo_status,
                r.poll_status	        AS repo_poll_status,
                r.redirect_id	        AS repo_redirect_id,
                r.stars                 AS repo_stars,
                r.fork                  AS repo_fork,
                r.archive		        AS repo_archive,
                w.id			        AS workflow_id,
                w.redirect_id	        AS workflow_redirect_id,
                w.path			        AS workflow_path,
                w.type			        AS workflow_type,
                w.status		        AS workflow_status,
                COALESCE(js.total, 0)   AS job_count,
                COALESCE(event_triggers.triggers, '')   AS triggers
            FROM workflows w
            JOIN repositories r ON r.id = w.repo_id
            JOIN organisations o ON o.id = r.org_id
            LEFT JOIN (
                SELECT
                    j.workflow_id,
                    COUNT(j.id) AS total
                FROM jobs j
                GROUP BY j.workflow_id
            ) js ON js.workflow_id = w.id
            LEFT JOIN (
                SELECT
                    wd.workflow_id,
                    GROUP_CONCAT(value, ',') AS triggers
                FROM workflow_data wd
                WHERE
                    wd.property = 'on'
                    AND LENGTH(wd.value) > 0
                GROUP BY wd.workflow_id
                ORDER BY wd.value
            ) event_triggers ON event_triggers.workflow_id = w.id
            WHERE
                o.id = :org_id
        """

        return self.database.select(sql, {'org_id': org_id})
