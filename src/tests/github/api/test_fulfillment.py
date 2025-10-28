import pytest
from src.libs.components.repo import RepoComponent
from src.libs.constants import GitHubRefType, RepoStatus, RepoVisibility, WorkflowType


@pytest.mark.parametrize('mock_requests_get', ['default'], indirect=True)
def test_fulfillment_branch(client, mock_requests_get):
    component = RepoComponent('microsoft/vscode@main')
    client.fulfill_component(component)
    assert component.ref_type == GitHubRefType.BRANCH
    assert component.ref_commit == '509cc674f24d87a298d56518c318de67bda357cb'
    assert component.status == RepoStatus.OK
    assert component.visibility == RepoVisibility.PUBLIC

    component = RepoComponent('microsoft/vscode@1.100.0')
    client.fulfill_component(component)
    assert component.ref_type == GitHubRefType.TAG
    assert component.ref_commit == '19e0f9e681ecb8e5c09d8784acaa601316ca4571'
    assert component.status == RepoStatus.OK
    assert component.visibility == RepoVisibility.PUBLIC

    component = RepoComponent('microsoft/vscode@19c72e4d24fe4ac9a7fc7b8161a3a852246282a2')
    client.fulfill_component(component)
    assert component.ref_type == GitHubRefType.COMMIT
    assert component.ref_commit == '19c72e4d24fe4ac9a7fc7b8161a3a852246282a2'
    assert component.status == RepoStatus.OK
    assert component.visibility == RepoVisibility.PUBLIC

@pytest.mark.parametrize('mock_requests_get', ['default'], indirect=True)
def test_fulfillment_signed(client, mock_requests_get):
    # Sometimes the passed commit is a reference to a signed tag which is not directly accessible through the UI.
    # For example:
    #   aws-actions/configure-aws-credentials@5579c002bb4778aa43395ef1df492868a9a1c83f
    # That is the hash of the v4.0.2 tag which is e3dd6a429d7300a6a4c196c26e071d42e0343502.
    # However, when it's signed it's assigned a different hash.
    component = RepoComponent('aws-actions/configure-aws-credentials@5579c002bb4778aa43395ef1df492868a9a1c83f')
    client.fulfill_component(component)
    assert component.ref_type == GitHubRefType.TAG
    assert component.ref_commit == '5579c002bb4778aa43395ef1df492868a9a1c83f'
    assert component.status == RepoStatus.OK
    assert component.visibility == RepoVisibility.PUBLIC
