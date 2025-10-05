from src.libs.components.org import OrgComponent
from src.libs.constants import PollStatus, RepoStatus
from src.libs.exceptions import InvalidOrgFormat


def test_org_component():
    try:
        org = OrgComponent('')
        assert False
    except InvalidOrgFormat:
        assert True
    except Exception:
        return False

    org = OrgComponent('microsoft')
    assert org.name == 'microsoft'
    assert org.id == 0
    assert org.poll_status == PollStatus.NONE
    assert org.status == RepoStatus.NONE

    org = OrgComponent('microsoft/vscode')
    assert org.name == 'microsoft'

    org = OrgComponent('microsoft/vscode@main')
    assert org.name == 'microsoft'
