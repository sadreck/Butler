import os
from datetime import datetime
from src.commands.report.helpers.third_party_results import ThirdPartyResults
from src.commands.report.collector_base import CollectorBase
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import GitHubRefType


class ThirdPartyCollector(CollectorBase):
    _shortname = 'third_party'

    def generate_output_paths(self):
        self.outputs['html']['actions'] = {
            'title': 'Actions',
            'path': os.path.join(self.output_path, f'third-party-actions.html'),
            'file': f'third-party-actions.html'
        }

        self.outputs['csv']['actions'] = {
            'title': 'Actions',
            'path': os.path.join(self.output_path, f'third-party-actions.csv'),
            'file': f'third-party-actions.csv'
        }

    def run(self) -> bool:
        data = {
            'org': self.org.name,
            'results': ThirdPartyResults(
                self.config.get('trusted-orgs', []),
                self.config.get('deprecated-actions', [])
            ),
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.log.info('Searching for third party actions')
        third_party_results = self._get_third_party_actions(self.org.id)

        self.log.info(f"Processing {len(third_party_results)} results")
        for result in third_party_results:
            third_party_dict = self.extract_result_dict(result, "third_party_")
            workflow_parent = WorkflowComponent.from_dict(result, False)
            workflow_action = WorkflowComponent.from_dict(third_party_dict, False)

            instance = data['results'].get_or_create(workflow_action, workflow_parent, result['action_title'])

        self._export(data)
        self.outputs['info'] = {
            'count': data['results'].count('all')
        }
        return True

    def _export(self, data: dict) -> None:
        html_file = self.outputs['html']['actions']['path']
        self.log.info(f"Saving HTML output to {html_file}")
        self.render('third_party', 'Third Party Actions', data, html_file)

        self.write_to_csv(
            self.outputs['csv']['actions']['path'],
            data['results'].for_csv()
        )

    def _get_third_party_actions(self, org_id: int) -> list:
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
                
                o2.id			AS third_party_org_id,
                o2.name			AS third_party_org_name,
                r2.id			AS third_party_repo_id,
                r2.visibility	AS third_party_repo_visibility,
                r2.name			AS third_party_repo_name,
                r2.ref			AS third_party_repo_ref,
                r2.ref_type		AS third_party_repo_ref_type,
                r2.resolved_ref	AS third_party_repo_resolved_ref,
                r2.resolved_ref_type	AS third_party_repo_resolved_ref_type,
                r2.ref_commit	AS third_party_repo_ref_commit,
                r2.status		AS third_party_repo_status,
                r2.poll_status	AS third_party_repo_poll_status,
                r2.redirect_id	AS third_party_repo_redirect_id,
                r2.stars        AS third_party_repo_stars,
                r2.fork         AS third_party_repo_fork,
                r2.archive		AS third_party_repo_archive,
                w2.id			AS third_party_workflow_id,
                w2.redirect_id	AS third_party_workflow_redirect_id,
                w2.path			AS third_party_workflow_path,
                w2.type			AS third_party_workflow_type,
                w2.status		AS third_party_workflow_status,
                
                wt.depth		        AS action_depth,
                COALESCE(wd2.value, '') AS action_title
            FROM organisations o
            JOIN repositories r ON r.org_id = o.id
            JOIN workflows w ON w.repo_id = r.id
            JOIN workflow_tree wt ON wt.parent_id = w.id
            JOIN workflows w2 ON w2.id = wt.child_id
            JOIN repositories r2 ON r2.id = w2.repo_id
            JOIN organisations o2 ON o2.id = r2.org_id
            LEFT JOIN workflow_data wd2 ON wd2.workflow_id = w2.id AND wd2.property = 'name'
            WHERE
                o.id = :org_id
                AND o2.id != :org_id
                AND r2.ref_type != :unknown
        """

        return self.database.select(sql, {'org_id': org_id, 'unknown': GitHubRefType.UNKNOWN})
