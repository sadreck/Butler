class DBBase:
    _session: any = None
    _auto_commit: bool = False

    @property
    def session(self):
        return self._session

    def __init__(self, session: any, auto_commit: bool):
        self._session = session
        self._auto_commit = auto_commit

    def save(self) -> None:
        self.session.flush()
        if self._auto_commit:
            self.session.commit()

    def add(self, record: any) -> None:
        self.session.add(record)

    def update_statement(self, statement: any) -> int:
        result = self.session.execute(statement)
        self.save()
        return result.rowcount
