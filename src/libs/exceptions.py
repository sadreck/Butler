class InvalidCommandLine(Exception):
    pass

class DatabaseException(Exception):
    pass

class DatabaseRecordMissing(DatabaseException):
    pass

class InvalidRepoFormat(Exception):
    pass

class InvalidOrgFormat(Exception):
    pass

class MissingComponentDetails(Exception):
    pass

class UnknownWorkflowType(Exception):
    pass

class DatabaseVersionMismatch(DatabaseException):
    pass

class InvalidCustomQueryFile(Exception):
    pass
