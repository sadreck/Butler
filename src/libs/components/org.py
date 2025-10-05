from src.database.models import OrganisationModel
from src.libs.components.base import BaseComponent
from src.libs.constants import PollStatus, RepoStatus
from src.libs.exceptions import InvalidOrgFormat


class OrgComponent(BaseComponent):
    _id: int = 0
    _name: str = None
    _poll_status: PollStatus = PollStatus.NONE
    _status: RepoStatus = RepoStatus.NONE

    @property
    def id(self) -> int:
        return self._id or 0

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def name(self):
        return self._name or ''

    @property
    def poll_status(self) -> PollStatus:
        return self._poll_status or PollStatus.NONE

    @poll_status.setter
    def poll_status(self, value: PollStatus):
        self._poll_status = value

    @property
    def status(self) -> RepoStatus:
        return self._status or RepoStatus.NONE

    @status.setter
    def status(self, value: RepoStatus):
        self._status = value

    def __init__(self, name: str):
        info = self._parse_component(name)
        if len(info['org']) == 0:
            raise InvalidOrgFormat('Invalid org component name')
        self._name = info['org']

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_model(cls, org: OrganisationModel):
        instance = cls(org.name)
        instance.id = org.id
        instance.poll_status = org.poll_status
        instance.status = org.status

        return instance
