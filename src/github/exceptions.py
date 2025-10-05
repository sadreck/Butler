class GitHubException(Exception):
    pass

class ApiRateLimitExceeded(GitHubException):
    pass

class TooManyRequests(GitHubException):
    pass

class NoValidAccessToken(GitHubException):
    pass

class OrgNotFound(GitHubException):
    pass

class HttpAccessBlocked(GitHubException):
    pass

class HttpEmptyRepo(GitHubException):
    pass

class HttpNotFound(GitHubException):
    pass

class HttpNoCommitFound(GitHubException):
    pass

class HttpInvalidState(GitHubException):
    pass

class HttpInvalidRequest(GitHubException):
    pass

class HttpTooManyRequests(GitHubException):
    pass

class HttpUnknownError(GitHubException):
    pass

class AccountNotFound(GitHubException):
    pass

class UnknownAccountType(GitHubException):
    pass

class RepoNotFound(GitHubException):
    pass

class RefNotFound(GitHubException):
    pass

class ErrorDownloadingFile(GitHubException):
    pass
