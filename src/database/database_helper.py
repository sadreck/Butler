from src.libs.components.repo import RepoComponent
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import PollStatus, WorkflowStatus, RepoStatus, GitHubRefType


class DatabaseHelper:
    def next_repo_to_fulfill(self, count: int) -> RepoComponent | list[RepoComponent] | None:
        sql = f"""
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
                r.archive		AS repo_archive
            FROM workflows      w
            JOIN repositories   r ON r.id = w.repo_id
            JOIN organisations  o ON o.id = r.org_id
            WHERE
                w.status = :workflow_status
                AND r.status = :repo_status
                AND r.poll_status = :repo_poll_status
            GROUP BY r.id
            ORDER BY r.id
            LIMIT {int(count)}
        """

        rows = self.select(
            sql,
            {
                'workflow_status': WorkflowStatus.NONE,
                'repo_status': RepoStatus.NONE,
                'repo_poll_status': PollStatus.SCANNED
            }
        )
        if len(rows) == 0:
            return None
        elif count == 1:
            return RepoComponent.from_dict(rows[0])
        return [RepoComponent.from_dict(row) for row in rows]

    def next_repo_to_scan(self, count: int) -> RepoComponent | list[RepoComponent] | None:
        sql = f"""
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
                r.archive		AS repo_archive
            FROM repositories r
            JOIN organisations o ON o.id = r.org_id
            WHERE r.poll_status = :poll_status
            ORDER BY o.name, r.name, r.ref
            LIMIT {int(count)}
        """

        rows = self.select(sql, {'poll_status': PollStatus.PENDING})
        if len(rows) == 0:
            return None
        elif count == 1:
            return RepoComponent.from_dict(rows[0])
        return [RepoComponent.from_dict(row) for row in rows]

    def next_workflow_to_download(self, count: int) -> WorkflowComponent | list[WorkflowComponent] | None:
        sql = f"""
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
                w.contents      AS workflow_contents
            FROM workflows      w
            JOIN repositories   r ON r.id = w.repo_id
            JOIN organisations  o ON o.id = r.org_id
            WHERE
                w.status = :status
            LIMIT {int(count)}
        """

        rows = self.select(sql, {'status': WorkflowStatus.NONE})
        if len(rows) == 0:
            return None
        elif count == 1:
            return WorkflowComponent.from_dict(rows[0])
        return [WorkflowComponent.from_dict(row) for row in rows]

    def next_to_process(self, count: int) -> WorkflowComponent | list[WorkflowComponent] | None:
        sql = f"""
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
                w.contents      AS workflow_contents
            FROM workflows w
            JOIN repositories   r ON r.id = w.repo_id
            JOIN organisations  o ON o.id = r.org_id
            WHERE
                w.status = :status
            ORDER BY r.id
            LIMIT {int(count)}
        """

        rows = self.select(sql, {'status': WorkflowStatus.DOWNLOADED})
        if len(rows) == 0:
            return None
        elif count == 1:
            return WorkflowComponent.from_dict(rows[0])
        return [WorkflowComponent.from_dict(row) for row in rows]

    def next_commit_to_resolve(self, count: int) -> RepoComponent | list[RepoComponent] | None:
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
                r.archive		AS repo_archive
            FROM repositories r
            JOIN organisations o ON o.id = r.org_id
            WHERE
                r.ref_type = :ref_type
                AND r.resolved_ref_type = :resolved_ref_type
            ORDER BY o.name, r.name, r.ref
            LIMIT {int(count)}
        """

        rows = self.select(sql, {'ref_type': GitHubRefType.COMMIT, 'resolved_ref_type': GitHubRefType.UNKNOWN})
        if len(rows) == 0:
            return None
        elif count == 1:
            return RepoComponent.from_dict(rows[0])
        return [RepoComponent.from_dict(row) for row in rows]

    def get_full_workflow_from_id(self, workflow_id: int) -> WorkflowComponent | None:
        sql = """
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
                w.data			        AS workflow_data,
                w.contents			    AS workflow_contents
            FROM workflows w
            JOIN repositories r ON r.id = w.repo_id
            JOIN organisations o ON o.id = r.org_id
            WHERE
                w.id = :workflow_id
        """
        rows = self.select(sql, {'workflow_id': workflow_id})
        if len(rows) == 0:
            return None
        return WorkflowComponent.from_dict(rows[0])
