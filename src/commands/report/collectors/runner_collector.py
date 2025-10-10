import os
from src.commands.report.helpers.runner_results import RunnerResults
from src.commands.report.collector_base import CollectorBase
from src.libs.components.workflow import WorkflowComponent


class RunnerCollector(CollectorBase):
    _shortname = 'runners'

    def generate_output_paths(self):
        self.outputs['html']['runners'] = {
            'title': 'Runners',
            'path': os.path.join(self.output_path, f'{self.org.name}-runners.html'),
            'file': f'{self.org.name}-runners.html'
        }

        self.outputs['csv']['runners'] = {
            'title': 'Runners',
            'path': os.path.join(self.output_path, f'{self.org.name}-runners.csv'),
            'file': f'{self.org.name}-runners.csv'
        }

        self.outputs['csv']['runners-workflows'] = {
            'title': 'Runners Workflows',
            'path': os.path.join(self.output_path, f'{self.org.name}-runners-workflows.csv'),
            'file': f'{self.org.name}-runners-workflows.csv'
        }

    def run(self) -> bool:
        data = {
            'org': self.org.name,
            'results': RunnerResults(
                self.config.get('supported_runners', []),
                self.config.get('unsupported_runners', [])
            )
        }

        self.log.info('Searching for runners')
        runners_results = self._get_runners(self.org.id)

        self.log.info(f"Processing {len(runners_results)} results")
        for result in runners_results:
            workflow = WorkflowComponent.from_dict(result)

            instance = data['results'].get_or_create(workflow, result['job_runner'])

        self._export(data)
        self.outputs['info'] = {
            'runners': data['results'].count,
            'self_hosted': data['results'].count_self_hosted,
        }
        return True

    def _export(self, data: dict) -> None:
        if 'html' in self.export_formats:
            html_file = self.outputs['html']['runners']['path']
            self.log.info(f"Saving HTML output to {html_file}")
            self.render('runners', 'Runners', data, html_file)

        if 'csv' in self.export_formats:
            self.write_to_csv(
                self.outputs['csv']['runners']['path'],
                data['results'].csv_for_runners(self.org.name)
            )

            self.write_to_csv(
                self.outputs['csv']['runners-workflows']['path'],
                data['results'].csv_for_workflows()
            )

    def _get_runners(self, org_id: int) -> list:
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
                jd.value		AS job_runner
            FROM organisations o
            JOIN repositories r ON r.org_id = o.id
            JOIN workflows w ON w.repo_id = r.id
            JOIN jobs j ON j.workflow_id = w.id
            JOIN job_data jd ON jd.job_id = j.id
            WHERE
                o.id = :org_id
                AND jd.property = 'runner'
                AND jd.value != 'labels'
                AND LENGTH(jd.value) > 0
        """
        return self.database.select(sql, {'org_id': org_id})