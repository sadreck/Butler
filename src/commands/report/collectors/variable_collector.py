import os
from src.commands.report.helpers.variable_results import VariableResults
from src.commands.report.collector_base import CollectorBase
from src.libs.components.workflow import WorkflowComponent


class VariableCollector(CollectorBase):
    def generate_output_paths(self):
        self.outputs['html']['variables'] = {
            'title': 'Variables',
            'path': os.path.join(self.output_path, f'{self.org.name}-variables.html')
        }

        self.outputs['csv']['variables'] = {
            'title': 'Variables and Secrets',
            'path': os.path.join(self.output_path, f'{self.org.name}-variables-and-secrets.csv')
        }

        self.outputs['csv']['variables-workflows'] = {
            'title': 'Variables and Secrets Workflows',
            'path': os.path.join(self.output_path, f'{self.org.name}-variables-and-secrets-workflows.csv')
        }

    def run(self) -> bool:
        data = {
            'org': self.org.name,
            'results': VariableResults()
        }

        self.log.info(f"Searching for workflow variables & secrets")
        workflows_results = self._get_workflow_variables(self.org.id)

        self.log.info(f"Searching for job variables & secrets")
        jobs_results = self._get_job_variables(self.org.id)

        self.log.info(f"Searching for step variables & secrets")
        steps_results = self._get_step_variables(self.org.id)

        self.log.info(f"Processing {len(workflows_results)} workflow results")
        for result in workflows_results:
            workflow = WorkflowComponent.from_dict(result)
            instance = data['results'].get_or_create(workflow, result['variable_name'])

        self.log.info(f"Processing {len(jobs_results)} job results")
        for result in jobs_results:
            workflow = WorkflowComponent.from_dict(result)
            instance = data['results'].get_or_create(workflow, result['variable_name'])

        self.log.info(f"Processing {len(steps_results)} step results")
        for result in steps_results:
            workflow = WorkflowComponent.from_dict(result)
            instance = data['results'].get_or_create(workflow, result['variable_name'])

        self._export(data)
        return True

    def _export(self, data: dict) -> None:
        if 'html' in self.export_formats:
            html_file = self.outputs['html']['variables']['path']
            self.log.info(f"Saving HTML output to {html_file}")
            self.render('variables', 'Variables', data, html_file)

        if 'csv' in self.export_formats:
            self.write_to_csv(
                self.outputs['csv']['variables']['path'],
                data['results'].csv_for_variables(self.org.name)
            )

            self.write_to_csv(
                self.outputs['csv']['variables-workflows']['path'],
                data['results'].csv_for_workflows()
            )

    def _get_workflow_variables(self, org_id: int) -> list:
        sql = """
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
                w.data			AS workflow_data,
                w.contents      AS workflow_contents,
                v.name			AS variable_name
            FROM organisations o
            JOIN repositories r ON r.org_id = o.id
            JOIN workflows w ON w.repo_id = r.id
            JOIN workflow_data wd ON wd.workflow_id = w.id
            JOIN variables v ON v.workflow_data_id = wd.id
            WHERE
                o.id = :org_id
                AND (LOWER(v.name) LIKE 'secrets.%' OR LOWER(v.name) LIKE 'vars.%')
                AND LOWER(v.name) NOT LIKE '%.github_token'
                AND LOWER(v.name) NOT LIKE '%.gh_token'
                AND LOWER(v.name) NOT LIKE '%.token'
        """
        return self.database.select(sql, {'org_id': org_id})

    def _get_job_variables(self, org_id: int) -> list:
        sql = """
            SELECT
                o.id			AS org_id,
                o.name			AS org_name,
                r.id			AS repo_id,
                r.visibility	AS repo_visibility,
                r.name			AS repo_name,
                r.ref			AS repo_ref,
                r.ref_type		AS repo_ref_type,
                r.resolved_ref	AS repo_resolved_ref,
                r.resolved_ref_type	AS repo_resolved_ref_type,
                r.ref_commit	AS repo_ref_commit,
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
                w.data			AS workflow_data,
                w.contents      AS workflow_contents,
                j.name          AS job_name,
                j.shortname     AS job_shortname,
                v.name			AS variable_name
            FROM organisations o
            JOIN repositories r ON r.org_id = o.id
            JOIN workflows w ON w.repo_id = r.id
            JOIN jobs j ON j.workflow_id = w.id
            JOIN job_data jd ON jd.job_id = j.id
            JOIN variables v ON v.job_data_id = jd.id
            WHERE
                o.id = :org_id
                AND (LOWER(v.name) LIKE 'secrets.%' OR LOWER(v.name) LIKE 'vars.%')
                AND LOWER(v.name) NOT LIKE '%.github_token'
                AND LOWER(v.name) NOT LIKE '%.gh_token'
                AND LOWER(v.name) NOT LIKE '%.token'
        """
        return self.database.select(sql, {'org_id': org_id})

    def _get_step_variables(self, org_id: int) -> list:
        sql = """
            SELECT
                o.id			AS org_id,
                o.name			AS org_name,
                r.id			AS repo_id,
                r.visibility	AS repo_visibility,
                r.name			AS repo_name,
                r.ref			AS repo_ref,
                r.ref_type		AS repo_ref_type,
                r.resolved_ref	AS repo_resolved_ref,
                r.resolved_ref_type	AS repo_resolved_ref_type,
                r.ref_commit	AS repo_ref_commit,
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
                w.data			AS workflow_data,
                w.contents      AS workflow_contents,
                j.name          AS job_name,
                j.shortname     AS job_shortname,
                s.step_number	AS step_number,
                v.name			AS variable_name
            FROM organisations o
            JOIN repositories r ON r.org_id = o.id
            JOIN workflows w ON w.repo_id = r.id
            JOIN jobs j ON j.workflow_id = w.id
            JOIN steps s ON s.job_id = j.id
            JOIN step_data sd ON sd.step_id = s.id
            JOIN variables v ON v.step_data_id = sd.id
            WHERE
                o.id = :org_id
                AND (LOWER(v.name) LIKE 'secrets.%' OR LOWER(v.name) LIKE 'vars.%')
                AND LOWER(v.name) NOT LIKE '%.github_token'
                AND LOWER(v.name) NOT LIKE '%.gh_token'
                AND LOWER(v.name) NOT LIKE '%.token'
        """
        return self.database.select(sql, {'org_id': org_id})
