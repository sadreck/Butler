import os

from src.libs.components.repo import RepoComponent
from src.libs.instances.workflow import WorkflowInstance
from src.libs.utils import Utils


def _load_asset_file(path: str) -> dict:
    file = os.path.join(Utils.get_tests_assets_folder(), path)
    return Utils.load_yaml(Utils.read_file(file))

def test_local_checkout():
    workflow = WorkflowInstance(_load_asset_file('microsoft/workflow_local_checkout.yaml'), RepoComponent('microsoft/vscode@main'))
    assert workflow.name == 'Author Verified'
    assert len(workflow.jobs) == 1
    job = workflow.jobs[0]
    assert job.shortname == 'main'
    assert len(job.steps) == 3
    assert job.step(1).name == 'Checkout Actions'
    assert job.step(1).uses == 'actions/checkout@v4'
    assert job.step(3).name == 'Run Author Verified'
    assert job.step(3).uses == 'microsoft/vscode-github-triage-actions/author-verified@stable'
    assert job.step(4) is None
