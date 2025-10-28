import pytest
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import RepoVisibility


@pytest.mark.parametrize('mock_requests_get', ['default'], indirect=True)
def test_download(client, mock_requests_get):
    component = WorkflowComponent('spotify/beam/.github/actions/cancel-workflow-runs@master')
    component.repo.visibility = RepoVisibility.PUBLIC
    submodule = client.get_submodule(component)
    assert submodule is not None
    assert isinstance(submodule, WorkflowComponent)
    assert str(submodule) == 'potiuk/cancel-workflow-runs@953e057dc81d3458935a18d1184c386b0f6b5738'
