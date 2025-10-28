from enum import IntEnum


class WorkflowType(IntEnum):
    NONE = 0
    WORKFLOW = 1
    ACTION = 2
    DOCKER = 3

class WorkflowStatus(IntEnum):
    NONE = 0
    DOWNLOADED = 1
    PROCESSED = 2
    REDIRECT = 3
    ERROR = 4
    MISSING = 5
    SUBMODULE = 6

class RepoStatus(IntEnum):
    NONE = 0
    OK = 1
    MISSING = 2
    EMPTY = 3
    BLOCKED = 4
    COMMIT_MISSING = 5
    GIT_ERROR = 6
    INVALID_REQUEST = 7
    REDIRECT = 8
    NO_WORKFLOWS = 9
    UNKNOWN = 99

class OrgStatus(IntEnum):
    NONE = 0
    OK = 1
    MISSING = 2

class RepoVisibility(IntEnum):
    NONE = 0
    PUBLIC = 1
    PRIVATE = 2
    LOCAL = 3

class GitHubRefType(IntEnum):
    MISSING = -1
    UNKNOWN = 0
    BRANCH = 1
    TAG = 2
    COMMIT = 3

class PollStatus(IntEnum):
    NONE = 0
    PENDING = 1
    SCANNED = 2

class VariableMappingType(IntEnum):
    STEPS = 1
    JOBS = 2
    WORKFLOWS = 3

class VariableMappingGroupType(IntEnum):
    ENV = 1
    # INPUTS = 2
    # OUTPUTS = 3