from sqlalchemy import func
from src.database.helpers.db_base import DBBase
from src.database.models import ConfigModel


class DBConfig(DBBase):
    def get(self, name: str, default: any = None) -> ConfigModel:
        record = self.session.query(ConfigModel).filter(
            func.lower(ConfigModel.name) == func.lower(name)
        ).first()
        return record.value if record else default

    def set(self, name: str, value: str | int) -> None:
        record = self.get(name)
        if not record:
            record = ConfigModel(name=name, value=value)
            self.add(record)
        record.value = value
        self.save()

    def delete(self, name: str) -> None:
        self.session.query(ConfigModel).filter_by(
            func.lower(ConfigModel.name) == func.lower(name)
        ).delete()
        self.save()
