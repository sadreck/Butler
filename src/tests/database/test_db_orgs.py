from src.database.database import Database
from src.libs.components.org import OrgComponent
from src.libs.constants import PollStatus, RepoStatus


def test_db_orgs(database: Database):
    org = OrgComponent('microsoft')
    org.poll_status = PollStatus.PENDING
    microsoft = database.orgs().create(org)

    assert microsoft.poll_status == PollStatus.PENDING
    assert microsoft.status == RepoStatus.NONE
    assert microsoft.name == 'microsoft'
    assert microsoft.id == 1

    # Try to find it by all-caps name.
    microsoft2 = database.orgs().find('MICROSOFT')
    assert microsoft.id == microsoft2.id

    # Try to re-create with an all-caps name.
    org = OrgComponent('MICROSOFT')
    microsoft2 = database.orgs().create(org)
    assert microsoft.id == microsoft2.id

    # Fetch by id.
    microsoft2 = database.orgs().get(microsoft.id)
    assert microsoft.id == microsoft2.id

    org = OrgComponent('aws')
    aws = database.orgs().create(org)
    assert aws.id == 2
    assert aws.poll_status == PollStatus.NONE

    database.orgs().set_poll_status(aws.id, PollStatus.SCANNED)
    database.orgs().set_status(aws.id, RepoStatus.MISSING)

    database.refresh_record(aws)
    assert aws.poll_status == PollStatus.SCANNED
    assert aws.status == RepoStatus.MISSING
