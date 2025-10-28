import pytest


@pytest.mark.parametrize('mock_requests_get', ['default'], indirect=True)
def test_get_org_repos(client, mock_requests_get):
    all_repos = [
        '.github', '.Net-Interactive-Kernels-ADS', '.NET-Modernization-In-a-Day', '0xDeCA10B',
        '2019-ignite-circuit-playground', '2023iotlevelup', '25-days-of-serverless', '2LCS', '3-in-1-dock', '30daysof',
        '50BusinessAssignmentsLog', 'A-CLIP', 'A-TALE-OF-THREE-CITIES', 'aaai21-copy-that', 'aad-app-credential-tools',
        'aad-hybrid-lab', 'aadb2c-starter-kit', 'AADConnectConfigDocumenter', 'aad_b2c_webview', 'AaronLocker',
        'ABAP-SDK-for-Azure', 'abap2git', 'ability-attributes', 'abledom', 'abstrakt', 'aca-dev-day',
        'academic-knowledge-exploration-services-utilities', 'AcademicContent', 'acc', 'acc-vm-engine'
    ]
    for batch in client.get_org_repos('microsoft', True, True):
        for repo in batch:
            if repo.name in all_repos:
                all_repos.remove(repo.name)

    assert len(all_repos) == 0

    no_archive_fork_repos = [
        '.github', '.Net-Interactive-Kernels-ADS', '0xDeCA10B', '2023iotlevelup', '2LCS', '30daysof',
        '50BusinessAssignmentsLog', 'A-CLIP', 'A-TALE-OF-THREE-CITIES', 'aaai21-copy-that', 'aad-app-credential-tools',
        'aad-hybrid-lab', 'aadb2c-starter-kit', 'AADConnectConfigDocumenter', 'aad_b2c_webview', 'AaronLocker',
        'ABAP-SDK-for-Azure', 'abap2git', 'ability-attributes', 'abledom', 'aca-dev-day',
        'academic-knowledge-exploration-services-utilities', 'AcademicContent', 'acc', 'acc-vm-engine'
    ]
    for batch in client.get_org_repos('microsoft', False, False):
        for repo in batch:
            if repo.name in no_archive_fork_repos:
                no_archive_fork_repos.remove(repo.name)

    assert len(no_archive_fork_repos) == 0
