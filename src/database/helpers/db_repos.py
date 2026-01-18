from sqlalchemy import func, update
from src.database.helpers.db_base import DBBase
from src.database.models import RepositoryModel
from src.libs.components.repo import RepoComponent
from src.libs.constants import RepoStatus, PollStatus, GitHubRefType
from src.libs.exceptions import MissingComponentDetails


class DBRepo(DBBase):
    def find(self, org_id: int, name: str, ref: str | None) -> RepositoryModel | None:
        if ref is None or len(ref) == 0:
            return self.session.query(RepositoryModel).filter(
                RepositoryModel.org_id == org_id,
                func.lower(RepositoryModel.name) == func.lower(name)
            ).first()
        return self.session.query(RepositoryModel).filter(
            RepositoryModel.org_id == org_id,
            func.lower(RepositoryModel.name) == func.lower(name),
            RepositoryModel.ref == ref
        ).first()

    def get(self, id: int) -> RepositoryModel | None:
        return self.session.query(RepositoryModel).filter(
            RepositoryModel.id == id
        ).first()

    def create(self, repo: RepoComponent) -> RepositoryModel:
        if repo.org.id == 0:
            raise MissingComponentDetails("Missing component details: repo.org.id")

        record = self.find(repo.org.id, repo.name, repo.ref)
        if not record:
            record = RepositoryModel(
                org_id=repo.org.id,
                name=repo.name,
                default_branch=repo.default_branch,
                ref=repo.ref,
                ref_type=repo.ref_type,
                ref_commit=repo.ref_commit,
                ref_old_name=repo.ref_old_name,
                resolved_ref=repo.resolved_ref,
                resolved_ref_type=repo.resolved_ref_type,
                visibility=repo.visibility,
                status=repo.status,
                poll_status=repo.poll_status,
                redirect_id=repo.redirect_id,
                stars=repo.stars,
                fork=repo.fork,
                archive=repo.archive,
            )
            self.add(record)
            self.save()
        return record

    def set_status(self, id: int, status: RepoStatus) -> None:
        statement = update(RepositoryModel).where(
            RepositoryModel.id == id
        ).values(status=status)
        self.update_statement(statement)

    def set_poll_status(self, id: int, poll_status: PollStatus) -> None:
        statement = update(RepositoryModel).where(
            RepositoryModel.id == id
        ).values(poll_status=poll_status)
        self.update_statement(statement)

    def update(self, repo: RepoComponent) -> None:
        if repo.id == 0:
            raise MissingComponentDetails("Missing component details: repo.id")

        statement = update(RepositoryModel).where(
            RepositoryModel.id == repo.id
        ).values(
            org_id=repo.org.id,
            name=repo.name,
            default_branch=repo.default_branch,
            ref=repo.ref,
            ref_type=repo.ref_type,
            ref_commit=repo.ref_commit,
            ref_old_name=repo.ref_old_name,
            resolved_ref=repo.resolved_ref,
            resolved_ref_type=repo.resolved_ref_type,
            visibility=repo.visibility,
            status=repo.status,
            poll_status=repo.poll_status,
            stars=repo.stars,
            fork=repo.fork,
            archive=repo.archive,
        )
        self.update_statement(statement)

    def set_ref_resolved_fields(self, id: int, resolved_ref: str, resolved_ref_type: GitHubRefType) -> None:
        statement = update(RepositoryModel).where(
            RepositoryModel.id == id
        ).values(resolved_ref=resolved_ref, resolved_ref_type=resolved_ref_type)
        self.update_statement(statement)

    def count(self) -> int:
        return self.session.query(RepositoryModel).count()
