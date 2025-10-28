from sqlalchemy import func, update
from src.database.helpers.db_base import DBBase
from src.database.models import OrganisationModel
from src.libs.components.org import OrgComponent
from src.libs.constants import PollStatus, OrgStatus


class DBOrg(DBBase):
    def find(self, name: str) -> OrganisationModel | None:
        return self.session.query(OrganisationModel).filter(
            func.lower(OrganisationModel.name) == func.lower(name)
        ).first()

    def get(self, id: int) -> OrganisationModel | None:
        return self.session.query(OrganisationModel).filter(
            OrganisationModel.id == id
        ).first()

    def create(self, org: OrgComponent) -> OrganisationModel | None:
        record = self.find(org.name)
        if not record:
            record = OrganisationModel()
            record.name = org.name
            record.poll_status = org.poll_status
            self.add(record)
            self.save()
        return record

    def set_poll_status(self, id: int, poll_status: PollStatus) -> None:
        statement = update(OrganisationModel).where(
            OrganisationModel.id == id
        ).values(poll_status=poll_status)
        self.update_statement(statement)

    def set_status(self, id: int, status: OrgStatus) -> None:
        statement = update(OrganisationModel).where(
            OrganisationModel.id == id
        ).values(status=status)
        self.update_statement(statement)

    def count(self) -> int:
        return self.session.query(OrganisationModel).count()
