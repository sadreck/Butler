import os.path

from src.libs.components.repo import RepoComponent
from src.libs.instances.workflow import WorkflowInstance
from src.libs.utils import Utils


def _load_runner_yaml(name: str) -> dict:
    file = os.path.join(Utils.get_tests_assets_folder(), 'runners', name)
    return Utils.load_yaml(Utils.read_file(file))

def test_basic():
    workflow = WorkflowInstance(_load_runner_yaml('basic.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    assert len(runners) == 1
    assert runners[0] == 'ubuntu-latest'

def test_basic_matrix():
    workflow = WorkflowInstance(_load_runner_yaml('matrix1.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    assert len(runners) == 12
    assert 'ubuntu-18.04' in runners
    assert 'ubuntu-20.04' in runners
    assert 'ubuntu-22.04' in runners
    assert 'ubuntu-2016' in runners
    assert 'ubuntu-2019' in runners
    assert 'ubuntu-2022' in runners
    assert 'windows-18.04' in runners
    assert 'windows-20.04' in runners
    assert 'windows-22.04' in runners
    assert 'windows-2016' in runners
    assert 'windows-2019' in runners
    assert 'windows-2022' in runners

def test_nested_matrix_dict():
    workflow = WorkflowInstance(_load_runner_yaml('matrix2.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    assert len(runners) == 4
    assert 'ubuntu-18.04' in runners
    assert 'ubuntu-20.04' in runners
    assert 'windows-2016' in runners
    assert 'windows-2019' in runners

def test_with_include():
    workflow = WorkflowInstance(_load_runner_yaml('matrix3.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    assert len(runners) == 4
    assert 'ubuntu-18.04' in runners
    assert 'ubuntu-20.04' in runners
    assert 'windows-2019' in runners
    assert 'windows-2022' in runners

def test_with_fromjson():
    workflow = WorkflowInstance(_load_runner_yaml('matrix4.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 0

def test_with_include2():
    workflow = WorkflowInstance(_load_runner_yaml('matrix5.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 3
    assert 'ubuntu-20.04' in runners
    assert 'ubuntu-22.04' in runners
    assert 'macos-latest' in runners

def test_nested_with_include():
    workflow = WorkflowInstance(_load_runner_yaml('matrix6.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 2
    assert 'macos-13' in runners
    assert 'macos-14' in runners

def test_with_fromjson_dict():
    workflow = WorkflowInstance(_load_runner_yaml('matrix7.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 0

def test_with_matrix_and_include():
    workflow = WorkflowInstance(_load_runner_yaml('matrix8.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 4
    assert 'macos-latest' in runners
    assert 'ubuntu-20.04' in runners
    assert 'ubuntu-latest' in runners
    assert 'windows-latest' in runners

def test_with_dynamic_includes():
    workflow = WorkflowInstance(_load_runner_yaml('matrix9.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 1
    assert 'ubuntu-latest' in runners

    workflow = WorkflowInstance(_load_runner_yaml('matrix10.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 0

def test_with_dynamic_runs_on():
    workflow = WorkflowInstance(_load_runner_yaml('matrix11.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 0

def test_matrix_double_nested():
    workflow = WorkflowInstance(_load_runner_yaml('matrix12.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 1
    assert 'windows-latest' in runners

def test_matrix_case_insensitive():
    workflow = WorkflowInstance(_load_runner_yaml('matrix13.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 2
    assert 'macos-latest' in runners
    assert 'ubuntu-latest' in runners

def test_with_nested_fromjson():
    workflow = WorkflowInstance(_load_runner_yaml('matrix14.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 0

def test_with_runs_com():
    workflow = WorkflowInstance(_load_runner_yaml('matrix15.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    # We don't parse that.
    assert len(runners) == 4
    assert 'macOS-10.15-X64' in runners
    assert 'macOS-11-ARM64' in runners
    assert 'runs-on.com' in runners
    assert 'ubuntu-22.04' in runners

def test_with_group():
    workflow = WorkflowInstance(_load_runner_yaml('matrix16.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    assert len(runners) == 1
    assert 'aws-general-8-plus' in runners

def test_with_empty_matrix():
    workflow = WorkflowInstance(_load_runner_yaml('matrix17.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    assert len(runners) == 2
    assert 'ubuntu-22.04' in runners
    assert 'windows-2022' in runners

def test_with_variable_list():
    workflow = WorkflowInstance(_load_runner_yaml('matrix18.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    assert len(runners) == 2
    assert 'ubuntu-latest' in runners
    assert 'ubuntu-24.04-arm' in runners

def test_with_array_runners():
    workflow = WorkflowInstance(_load_runner_yaml('matrix19.yaml'), RepoComponent('microsoft/vscode@main'))
    assert len(workflow.jobs) == 1
    runners = workflow.jobs[0].runners
    assert len(runners) == 2
    assert 'self-hosted' in runners
    assert 'ubuntu-latest' in runners