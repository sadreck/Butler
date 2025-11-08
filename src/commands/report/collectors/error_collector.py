import os
from datetime import datetime
from src.commands.report.collector_base import CollectorBase
from src.commands.report.helpers.error_results import ErrorResults
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import WorkflowStatus


class ErrorCollector(CollectorBase):
    _shortname = 'errors'

    def generate_output_paths(self):
        self.outputs['html']['errors'] = {
            'title': 'Errors',
            'path': os.path.join(self.output_path, f'errors.html'),
            'file': f'errors.html'
        }

        self.outputs['csv']['missing'] = {
            'title': 'Missing Actions',
            'path': os.path.join(self.output_path, f'missing-actions.csv'),
            'file': f'missing-actions.csv'
        }

        self.outputs['csv']['errors'] = {
            'title': 'Parsing Errors',
            'path': os.path.join(self.output_path, f'parsing-errors.csv'),
            'file': f'parsing-errors.csv'
        }

    def run(self) -> bool:
        data = {
            'org': self.org.name,
            'results': ErrorResults(),
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.log.info("Searching for missing actions")
        missing_actions = self._get_missing_actions(self.org.id)

        self.log.info("Searching for actions with errors")
        error_actions = self._get_error_actions(self.org.id)

        self.log.info(f"Processing {len(missing_actions)} calls to missing actions")
        for result in missing_actions:
            missing_dict = self.extract_result_dict(result, "missing_")
            missing_workflow = WorkflowComponent.from_dict(missing_dict, False)
            workflow = WorkflowComponent.from_dict(result, True)

            instance = data['results'].add_missing_workflow(workflow, missing_workflow)

        self.log.info(f"Processing {len(error_actions)} calls to actions with errors")
        for result in error_actions:
            error_dict = self.extract_result_dict(result, "error_")
            error_workflow = WorkflowComponent.from_dict(error_dict, True)
            workflow = WorkflowComponent.from_dict(result, True)

            instance = data['results'].add_error_workflow(workflow, error_workflow)

        self._export(data)
        self.outputs['info'] = {
            'missing': data['results'].count('missing'),
            'errors': data['results'].count('errors'),
        }
        return True

    def _export(self, data: dict) -> None:
        if 'html' in self.outputs:
            html_file = self.outputs['html']['errors']['path']
            self.log.info(f"Saving HTML output to {html_file}")
            self.render('errors', 'Errors', data, html_file)

        if 'csv' in self.outputs:
            self.write_to_csv(
                self.outputs['csv']['missing']['path'],
                data['results'].csv_for_missing()
            )

            self.write_to_csv(
                self.outputs['csv']['errors']['path'],
                data['results'].csv_for_errors()
            )

    def _get_error_actions(self, org_id: int) -> list:
        sql = """
            SELECT
                o.id			AS error_org_id,
                o.name			AS error_org_name,
                r.id			AS error_repo_id,
                r.visibility	AS error_repo_visibility,
                r.name			AS error_repo_name,
                r.ref			AS error_repo_ref,
                r.ref_type		AS error_repo_ref_type,
                r.resolved_ref	AS error_repo_resolved_ref,
                r.resolved_ref_type	AS error_repo_resolved_ref_type,
                r.ref_commit	AS error_repo_ref_commit,
                r.status		AS error_repo_status,
                r.poll_status	AS error_repo_poll_status,
                r.redirect_id	AS error_repo_redirect_id,
                r.stars         AS error_repo_stars,
                r.fork          AS error_repo_fork,
                r.archive		AS error_repo_archive,
                w.id			AS error_workflow_id,
                w.redirect_id	AS error_workflow_redirect_id,
                w.path			AS error_workflow_path,
                w.type			AS error_workflow_type,
                w.status		AS error_workflow_status,
                w.contents      AS error_workflow_contents,
                w.data          AS error_workflow_data,
                
                o2.id			AS org_id,
                o2.name			AS org_name,
                r2.id			AS repo_id,
                r2.visibility	AS repo_visibility,
                r2.name			AS repo_name,
                r2.ref			AS repo_ref,
                r2.ref_type		AS repo_ref_type,
                r2.resolved_ref	AS repo_resolved_ref,
                r2.resolved_ref_type	AS repo_resolved_ref_type,
                r2.ref_commit	AS repo_ref_commit,
                r2.status		AS repo_status,
                r2.poll_status	AS repo_poll_status,
                r2.redirect_id	AS repo_redirect_id,
                r2.stars         AS repo_stars,
                r2.fork          AS repo_fork,
                r2.archive		AS repo_archive,
                w2.id			AS workflow_id,
                w2.redirect_id	AS workflow_redirect_id,
                w2.path			AS workflow_path,
                w2.type			AS workflow_type,
                w2.status		AS workflow_status,
                w2.contents     AS workflow_contents,
                w2.data			AS workflow_data
            FROM workflows      w
            JOIN repositories   r ON r.id = w.repo_id
            JOIN organisations  o ON o.id = r.org_id
            JOIN workflow_tree  wt ON wt.child_id = w.id
            JOIN workflows      w2 ON w2.id = wt.parent_id
            JOIN repositories   r2 ON r2.id = w2.repo_id
            JOIN organisations  o2 ON o2.id = r2.org_id
            WHERE
                w.status = :error
                AND o.name != '_'
                AND o.name NOT LIKE '%/%'
                AND NOT (o.name = 'github' AND r.name = 'codeql-action')
                AND o2.id = :org_id
        """
        return self.database.select(sql, {'error': WorkflowStatus.ERROR, 'org_id': org_id})

    def _get_missing_actions(self, org_id: int) -> list:
        sql = """
            SELECT
                o.id			AS missing_org_id,
                o.name			AS missing_org_name,
                r.id			AS missing_repo_id,
                r.visibility	AS missing_repo_visibility,
                r.name			AS missing_repo_name,
                r.ref			AS missing_repo_ref,
                r.ref_type		AS missing_repo_ref_type,
                r.resolved_ref	AS missing_repo_resolved_ref,
                r.resolved_ref_type	AS missing_repo_resolved_ref_type,
                r.ref_commit	AS missing_repo_ref_commit,
                r.status		AS missing_repo_status,
                r.poll_status	AS missing_repo_poll_status,
                r.redirect_id	AS missing_repo_redirect_id,
                r.stars         AS missing_repo_stars,
                r.fork          AS missing_repo_fork,
                r.archive		AS missing_repo_archive,
                w.id			AS missing_workflow_id,
                w.redirect_id	AS missing_workflow_redirect_id,
                w.path			AS missing_workflow_path,
                w.type			AS missing_workflow_type,
                w.status		AS missing_workflow_status,
                
                o2.id			AS org_id,
                o2.name			AS org_name,
                r2.id			AS repo_id,
                r2.visibility	AS repo_visibility,
                r2.name			AS repo_name,
                r2.ref			AS repo_ref,
                r2.ref_type		AS repo_ref_type,
                r2.resolved_ref	AS repo_resolved_ref,
                r2.resolved_ref_type	AS repo_resolved_ref_type,
                r2.ref_commit	AS repo_ref_commit,
                r2.status		AS repo_status,
                r2.poll_status	AS repo_poll_status,
                r2.redirect_id	AS repo_redirect_id,
                r2.stars         AS repo_stars,
                r2.fork          AS repo_fork,
                r2.archive		AS repo_archive,
                w2.id			AS workflow_id,
                w2.redirect_id	AS workflow_redirect_id,
                w2.path			AS workflow_path,
                w2.type			AS workflow_type,
                w2.status		AS workflow_status,
                w2.contents     AS workflow_contents,
                w2.data			AS workflow_data
            FROM workflows      w
            JOIN repositories   r ON r.id = w.repo_id
            JOIN organisations  o ON o.id = r.org_id
            JOIN workflow_tree  wt ON wt.child_id = w.id
            JOIN workflows      w2 ON w2.id = wt.parent_id
            JOIN repositories   r2 ON r2.id = w2.repo_id
            JOIN organisations  o2 ON o2.id = r2.org_id
            WHERE
                w.status = :missing
                AND o.name != '_'
                AND o.name NOT LIKE '%/%'
                AND NOT (o.name = 'github' AND r.name = 'codeql-action')
                AND o2.id = :org_id
        """
        return self.database.select(sql, {'missing': WorkflowStatus.MISSING, 'org_id': org_id})
