from src.tests.mock_response import MockResponse


def default() -> dict:
    return {
        '/rate_limit': MockResponse('rate_limit.json', None, 200),
        '/users/microsoft': MockResponse('accounts/microsoft.json', None, 200),
        '/users/sadreck': MockResponse('accounts/sadreck.json', None, 200),
        '/users/does-not-exist-tests': MockResponse('accounts/does-not-exist-tests.json', None, 404),
        '/repos/microsoft/vscode': MockResponse('microsoft/fulfillment-vscode.json', None, 200),
        '/repos/microsoft/vscode/git/ref/heads/main': MockResponse('microsoft/fulfillment-vscode-ref-heads-main.json', None, 200),
        '/repos/microsoft/vscode/git/ref/tags/1.100.0': MockResponse('microsoft/fulfillment-vscode-ref-tags-1.100.0.json', None, 200),
        '/repos/microsoft/vscode/commits/19c72e4d24fe4ac9a7fc7b8161a3a852246282a2': MockResponse('microsoft/fulfillment-vscode-ref-commits-19c72e4d.json', None, 200),
        '/repos/microsoft/vscode/git/ref/heads/1.100.0': MockResponse('microsoft/fulfillment-vscode-ref-heads-1.100.0.json', None, 404),
        '/repos/microsoft/vscode/git/ref/heads/19c72e4d24fe4ac9a7fc7b8161a3a852246282a2': MockResponse('microsoft/fulfillment-vscode-ref-heads-19c72e4d.json', None, 404),
        '/repos/microsoft/vscode/git/ref/tags/19c72e4d24fe4ac9a7fc7b8161a3a852246282a2': MockResponse('microsoft/fulfillment-vscode-ref-tags-19c72e4d.json', None, 404),
        '/repos/aws-actions/configure-aws-credentials': MockResponse('aws-actions/repo-aws-creds.json', None, 200),
        '/repos/aws-actions/configure-aws-credentials/commits/5579c002bb4778aa43395ef1df492868a9a1c83f': MockResponse('aws-actions/fulfillment-aws-creds-commits.json', None, 422),
        '/repos/aws-actions/configure-aws-credentials/git/ref/heads/5579c002bb4778aa43395ef1df492868a9a1c83f': MockResponse('aws-actions/fulfillment-aws-creds-ref-heads.json', None, 404),
        '/repos/aws-actions/configure-aws-credentials/git/ref/tags/5579c002bb4778aa43395ef1df492868a9a1c83f': MockResponse('aws-actions/fulfillment-aws-creds-ref-tags.json', None, 404),
        '/repos/aws-actions/configure-aws-credentials/git/tags/5579c002bb4778aa43395ef1df492868a9a1c83f': MockResponse('aws-actions/fulfillment-aws-creds-git-tags.json', None, 200),
        '/repos/aws-actions/configure-aws-credentials/branches/5579c002bb4778aa43395ef1df492868a9a1c83f': MockResponse('aws-actions/fulfillment-aws-creds-git-tags.json', None, 404),
        '/orgs/microsoft/repos': MockResponse('microsoft/microsoft-page-1-contents.json', 'microsoft/microsoft-page-1-headers.json', 200),
        '/organizations/6154722/repos?per_page=10&sort=full_name&page=2': MockResponse('microsoft/microsoft-page-2-contents.json', 'microsoft/microsoft-page-2-headers.json', 200),
        '/organizations/6154722/repos?per_page=10&sort=full_name&page=3': MockResponse('microsoft/microsoft-page-3-contents.json', None, 200),
        '/repos/microsoft/vscode/contents/.github/workflows': MockResponse('microsoft/vscode-ls-workflows.json', None, 200),
        '/repos/microsoft/vscode/contents/.github/workflows-meh': MockResponse('microsoft/vscode-ls-workflows-not-found.json', None, 404),
        'https://raw.githubusercontent.com/microsoft/vscode/main/.github/workflows/telemetry.yml': MockResponse('microsoft/file-vscode-telemetry.yml', None, 200, is_json_contents=False),
        '/repos/microsoft/vscode/contents/.github/workflows/telemetry.yml?ref=main': MockResponse('microsoft/file-vscode-telemetry.json', None, 200),
        'https://raw.githubusercontent.com/microsoft/vscode/main/.github/workflows/telemetry-does-not-exist.yml': MockResponse('microsoft/file-vscode-telemetry-does-not-exist.json', None, 404),
        '/repos/actions/checkout/contents/action.yml?ref=v4': MockResponse('actions/checkout-v4.json', None, 200),
        '/repos/ossf/scorecard-action/contents/action.yml?ref=main': MockResponse('ossf/scorecard-action-404.json', None, 404),
        '/repos/ossf/scorecard-action/contents/action.yaml?ref=main': MockResponse('ossf/scorecard-action-main.json', None, 200),
        '/repos/microsoft/vscode/contents/action.yml?ref=main': MockResponse('microsoft/action-yml-404.json', None, 404),
        '/repos/microsoft/vscode/contents/action.yaml?ref=main': MockResponse('microsoft/action-yaml-404.json', None, 404),
        '/repos/microsoft/vscode/contents/Dockerfile?ref=main': MockResponse('microsoft/action-yaml-404.json', None, 404),
        '/repos/spotify/beam/contents/.github/actions/cancel-workflow-runs': MockResponse('spotify/beam-action.json', None, 200),
        '/repos/microsoft/vscode/tags': MockResponse('microsoft/tags-page-1.json', 'microsoft/tags-page-1-headers.json', 200),
        '/repositories/41881900/tags?per_page=10&page=2': MockResponse('microsoft/tags-page-2.json', None, 200),
        '/repos/microsoft/vscode/branches': MockResponse('microsoft/branches-page-1.json', 'microsoft/branches-page-1-headers.json', 200),
        '/repositories/41881900/branches?per_page=10&page=2': MockResponse('microsoft/branches-page-2.json', None, 200)
    }

def download_vscode() -> dict:
    return {
        '/rate_limit': MockResponse('rate_limit.json', None, 200),
        '/repos/microsoft/vscode/contents/.github/workflows': MockResponse('vscode-download/892f4e116195aedff0de1d6d7588fd76.contents.json', 'vscode-download/892f4e116195aedff0de1d6d7588fd76.headers.json', 200, is_json_contents=True),
        '/repos/microsoft/vscode': MockResponse('vscode-download/f5faff61819877c0da6afeccf1fd3c8b.contents.json', 'vscode-download/f5faff61819877c0da6afeccf1fd3c8b.headers.json', 200, is_json_contents=True),
        '/repos/microsoft/vscode/git/ref/heads/main': MockResponse('vscode-download/095c1955551c5577e8d699bc8c09fc27.contents.json', 'vscode-download/095c1955551c5577e8d699bc8c09fc27.headers.json', 200, is_json_contents=True),
        'https://raw.githubusercontent.com/microsoft/vscode/refs/heads/main/.github/workflows/copilot-setup-steps.yml': MockResponse('vscode-download/3948b8bdc82dc947ffdc4c2b673d4b81.contents.json', 'vscode-download/3948b8bdc82dc947ffdc4c2b673d4b81.headers.json', 200, is_json_contents=False),
        '/repos/actions/checkout': MockResponse('vscode-download/c345337398ea8c1a15bdaf7e722deae0.contents.json', 'vscode-download/c345337398ea8c1a15bdaf7e722deae0.headers.json', 200, is_json_contents=True),
        '/repos/actions/checkout/git/ref/heads/v5': MockResponse('vscode-download/c7878066c016a3a303020ac4715c1768.contents.json', 'vscode-download/c7878066c016a3a303020ac4715c1768.headers.json', 404, is_json_contents=True),
        '/repos/actions/checkout/git/ref/tags/v5': MockResponse('vscode-download/063f45e95f4e09e8403e248372ff5555.contents.json', 'vscode-download/063f45e95f4e09e8403e248372ff5555.headers.json', 200, is_json_contents=True),
        'https://raw.githubusercontent.com/actions/checkout/refs/tags/v5/action.yml': MockResponse('vscode-download/42a1150ef36f03038e8565f6292c7006.contents.json', 'vscode-download/42a1150ef36f03038e8565f6292c7006.headers.json', 200, is_json_contents=False),
        '/repos/actions/setup-node': MockResponse('vscode-download/6d15b6455836628bf1c55cf80261461d.contents.json', 'vscode-download/6d15b6455836628bf1c55cf80261461d.headers.json', 200, is_json_contents=True),
        '/repos/actions/setup-node/git/ref/heads/v6': MockResponse('vscode-download/356017b26b7f59175fa6037f54dee751.contents.json', 'vscode-download/356017b26b7f59175fa6037f54dee751.headers.json', 404, is_json_contents=True),
        '/repos/actions/setup-node/git/ref/tags/v6': MockResponse('vscode-download/f7620e4fe6a0cf98a8fd9a39f5ab0057.contents.json', 'vscode-download/f7620e4fe6a0cf98a8fd9a39f5ab0057.headers.json', 200, is_json_contents=True),
        'https://raw.githubusercontent.com/actions/setup-node/refs/tags/v6/action.yml': MockResponse('vscode-download/efc66b8d4fb488a21854e02f3e547af4.contents.json', 'vscode-download/efc66b8d4fb488a21854e02f3e547af4.headers.json', 200, is_json_contents=False),
        '/repos/actions/cache': MockResponse('vscode-download/c575cb06fa7fd1f94ce6d09833190bc5.contents.json', 'vscode-download/c575cb06fa7fd1f94ce6d09833190bc5.headers.json', 200, is_json_contents=True),
        '/repos/actions/cache/git/ref/heads/v4': MockResponse('vscode-download/14f542de73a332596fc782d58123706d.contents.json', 'vscode-download/14f542de73a332596fc782d58123706d.headers.json', 404, is_json_contents=True),
        '/repos/actions/cache/git/ref/tags/v4': MockResponse('vscode-download/54955d07cc05701c8c7fed1eb0c79100.contents.json', 'vscode-download/54955d07cc05701c8c7fed1eb0c79100.headers.json', 200, is_json_contents=True),
        'https://raw.githubusercontent.com/actions/cache/refs/tags/v4/restore/action.yml': MockResponse('vscode-download/0e71032eaeba7e8a8500ef85797ab873.contents.json', 'vscode-download/0e71032eaeba7e8a8500ef85797ab873.headers.json', 200, is_json_contents=False),
    }

def missing_org() -> dict:
    return {
        '/rate_limit': MockResponse('rate_limit.json', None, 200),
        '/repos/microsoft-does-not-exist/vscode': MockResponse('missing-org/d178ee9f5e15c1dcaf28a0c83009ef49.contents.json', 'missing-org/d178ee9f5e15c1dcaf28a0c83009ef49.headers.json', 404, is_json_contents=True)
    }

def missing_repo() -> dict:
    return {
        '/rate_limit': MockResponse('rate_limit.json', None, 200),
        '/repos/microsoft/vscode-does-not-exist': MockResponse('missing-repo/4c760c01c050d1c10f898ae320f493e2.contents.json', 'missing-repo/4c760c01c050d1c10f898ae320f493e2.headers.json', 404, is_json_contents=True)
    }

def missing_workflow() -> dict:
    return {
        '/rate_limit': MockResponse('rate_limit.json', None, 200),
        '/repos/microsoft/vscode': MockResponse('missing-workflow/f5faff61819877c0da6afeccf1fd3c8b.contents.json', 'missing-workflow/f5faff61819877c0da6afeccf1fd3c8b.headers.json', 200, is_json_contents=True),
        '/repos/microsoft/vscode/contents/.github/workflows': MockResponse('missing-workflow/892f4e116195aedff0de1d6d7588fd76.contents.json', 'missing-workflow/892f4e116195aedff0de1d6d7588fd76.headers.json', 200, is_json_contents=True)
    }

def renamed_branch() -> dict:
    return {
        '/rate_limit': MockResponse('rate_limit.json', None, 200),
        '/repos/apache/datafusion-ballista-python': MockResponse('renamed-branch/8dba132e5d6abcdde29d98d10a6323df.contents.json', 'renamed-branch/8dba132e5d6abcdde29d98d10a6323df.headers.json', 200, is_json_contents=True),
        '/repos/apache/datafusion-ballista-python/contents/.github/workflows': MockResponse('renamed-branch/a0254d55b1e61c3229c653bb7db2a093.contents.json', 'renamed-branch/a0254d55b1e61c3229c653bb7db2a093.headers.json', 200, is_json_contents=True),
        '/repos/apache/datafusion-ballista-python/git/ref/heads/main': MockResponse('renamed-branch/1e9a58184cc250207159843c72ed2f92.contents.json', 'renamed-branch/1e9a58184cc250207159843c72ed2f92.headers.json', 200, is_json_contents=True),
        'https://raw.githubusercontent.com/apache/datafusion-ballista-python/refs/heads/main/.github/workflows/comment_bot.yml': MockResponse('renamed-branch/41b65cda9ec4daad515c1c351705b475.contents.json', 'renamed-branch/41b65cda9ec4daad515c1c351705b475.headers.json', 200, is_json_contents=False),
        '/repos/actions/checkout': MockResponse('renamed-branch/c345337398ea8c1a15bdaf7e722deae0.contents.json', 'renamed-branch/c345337398ea8c1a15bdaf7e722deae0.headers.json', 200, is_json_contents=True),
        '/repos/actions/checkout/git/ref/heads/v3': MockResponse('renamed-branch/54e484559d13e8739fef07bed948e671.contents.json', 'renamed-branch/54e484559d13e8739fef07bed948e671.headers.json', 404, is_json_contents=True),
        '/repos/actions/checkout/git/ref/tags/v3': MockResponse('renamed-branch/440d5faed64d079de7a5eb451fc61229.contents.json', 'renamed-branch/440d5faed64d079de7a5eb451fc61229.headers.json', 200, is_json_contents=True),
        'https://raw.githubusercontent.com/actions/checkout/refs/tags/v3/action.yml': MockResponse('renamed-branch/1cd627ad8103122b8d401d14778ca085.contents.json', 'renamed-branch/1cd627ad8103122b8d401d14778ca085.headers.json', 200, is_json_contents=False),
        '/repos/actions/setup-python': MockResponse('renamed-branch/a6e321dd2857909af294ea0ea21fe461.contents.json', 'renamed-branch/a6e321dd2857909af294ea0ea21fe461.headers.json', 200, is_json_contents=True),
        '/repos/actions/setup-python/git/ref/heads/v4': MockResponse('renamed-branch/36709eaed054d434610ce30503662170.contents.json', 'renamed-branch/36709eaed054d434610ce30503662170.headers.json', 404, is_json_contents=True),
        '/repos/actions/setup-python/git/ref/tags/v4': MockResponse('renamed-branch/fad741232c02c57495320552cd87c6cb.contents.json', 'renamed-branch/fad741232c02c57495320552cd87c6cb.headers.json', 200, is_json_contents=True),
        'https://raw.githubusercontent.com/actions/setup-python/refs/tags/v4/action.yml': MockResponse('renamed-branch/6d919f506747457496e7f2d52b02565a.contents.json', 'renamed-branch/6d919f506747457496e7f2d52b02565a.headers.json', 200, is_json_contents=False),
        '/repos/r-lib/actions': MockResponse('renamed-branch/fb680e14d53bf432419b0a5d7e66a985.contents.json', 'renamed-branch/fb680e14d53bf432419b0a5d7e66a985.headers.json', 200, is_json_contents=True),
        '/repos/r-lib/actions/git/ref/heads/master': MockResponse('renamed-branch/6fcafd98283e88c2c071dcdac336bfaf.contents.json', 'renamed-branch/6fcafd98283e88c2c071dcdac336bfaf.headers.json', 404, is_json_contents=True),
        '/repos/r-lib/actions/git/ref/tags/master': MockResponse('renamed-branch/cb8bb0e1d9f531f6e2716ac66f02a71c.contents.json', 'renamed-branch/cb8bb0e1d9f531f6e2716ac66f02a71c.headers.json', 404, is_json_contents=True),
        '/repos/r-lib/actions/commits/master': MockResponse('renamed-branch/be910c06d84c6b6b3586592364660579.contents.json', 'renamed-branch/be910c06d84c6b6b3586592364660579.headers.json', 422, is_json_contents=True),
        '/repos/r-lib/actions/branches/master': MockResponse('renamed-branch/d46809292ab844a8913e575b19343edb.contents.json', 'renamed-branch/d46809292ab844a8913e575b19343edb.headers.json', 200, is_json_contents=True),
        'https://raw.githubusercontent.com/r-lib/actions/refs/heads/old/pr-fetch/action.yml': MockResponse('renamed-branch/4a34602832492229e4204735871f81ee.contents.json', 'renamed-branch/4a34602832492229e4204735871f81ee.headers.json', 200, is_json_contents=False),
        'https://raw.githubusercontent.com/r-lib/actions/refs/heads/old/pr-push/action.yml': MockResponse('renamed-branch/53d58299e719befbcf9afa4e8e3b6193.contents.json', 'renamed-branch/53d58299e719befbcf9afa4e8e3b6193.headers.json', 200, is_json_contents=False)
    }
