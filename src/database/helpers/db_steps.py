from sqlalchemy import and_, or_
from src.database.helpers.db_base import DBBase
from src.database.models import StepModel, StepDataModel
from src.libs.exceptions import MissingComponentDetails


class DBStep(DBBase):
    def find(self, job_id: int, number: int) -> StepModel | None:
        return self.session.query(StepModel).filter(
            StepModel.job_id == job_id,
            StepModel.step_number == number
        ).first()

    def create(self, job_id: int, number: int) -> StepModel:
        if job_id == 0:
            raise MissingComponentDetails("No job_id passed to step model")
        elif number <= 0:
            raise ValueError("Step number cannot be <= 0")

        record = self.find(job_id, number)
        if not record:
            record = StepModel(job_id=job_id, step_number=number)
            self.add(record)
            self.save()
        return record

    def set_data(self, id: int, property: str, data: any) -> None:
        if isinstance(data, dict):
            for name, value in data.items():
                item = StepDataModel(step_id=id, property=property, name=name, value=str(value))
                self.add(item)
        elif isinstance(data, list):
            for value in data:
                item = StepDataModel(step_id=id, property=property, name='', value=str(value))
                self.add(item)
        else:
            item = StepDataModel(step_id=id, property=property, name='', value=str(data))
            self.add(item)
        self.save()

    def delete_data(self, id: int) -> None:
        self.session.query(StepDataModel).filter_by(step_id=id).delete()
        self.save()

    def find_next_data(self, step_data_id: int, count: int) -> StepDataModel | None:
        return (self.session.query(StepDataModel)
                .filter(
                    and_(
                        StepDataModel.id > step_data_id,
                        or_(
                            StepDataModel.property == 'env',
                            StepDataModel.value.like('%{{%')
                        )
                    )
                ).order_by(StepDataModel.id).limit(count).all()
            )

    def count(self) -> int:
        return self.session.query(StepModel).count()

    def stepdata_count(self) -> int:
        return self.session.query(StepDataModel).count()