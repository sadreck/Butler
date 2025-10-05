from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import WorkflowType
from src.libs.exceptions import InvalidRepoFormat


def test_workflow_component():
    try:
        workflow = WorkflowComponent('actions')
        assert False
    except InvalidRepoFormat:
        assert True
    except Exception:
        assert False

    workflow = WorkflowComponent('actions/checkout')
    assert workflow.repo.org.name == 'actions'
    assert workflow.repo.name == 'checkout'
    assert workflow.repo.ref == ''
    assert workflow.path == ''
    assert workflow.type == WorkflowType.ACTION

    workflow = WorkflowComponent('actions/checkout@v1')
    assert workflow.repo.org.name == 'actions'
    assert workflow.repo.name == 'checkout'
    assert workflow.repo.ref == 'v1'
    assert workflow.path == ''
    assert workflow.type == WorkflowType.ACTION

    workflow = WorkflowComponent('actions/workflows/.github/workflows/ci.yaml@main')
    assert workflow.repo.org.name == 'actions'
    assert workflow.repo.name == 'workflows'
    assert workflow.repo.ref == 'main'
    assert workflow.path == '.github/workflows/ci.yaml'
    assert workflow.type == WorkflowType.WORKFLOW

    workflow = WorkflowComponent('actions/workflows/some/action@main')
    assert workflow.repo.org.name == 'actions'
    assert workflow.repo.name == 'workflows'
    assert workflow.repo.ref == 'main'
    assert workflow.path == 'some/action'
    assert workflow.type == WorkflowType.ACTION
