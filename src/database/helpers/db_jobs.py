from sqlalchemy import and_, or_
from src.database.helpers.db_base import DBBase
from src.database.models import JobModel, JobDataModel
from src.libs.exceptions import MissingComponentDetails


class DBJob(DBBase):
    def find(self, workflow_id: int, shortname: str) -> JobModel | None:
        return self.session.query(JobModel).filter(
            JobModel.workflow_id == workflow_id,
            JobModel.shortname == shortname
        ).first()

    def create(self, workflow_id: int, name: str, shortname: str) -> JobModel:
        if workflow_id == 0:
            raise MissingComponentDetails("No workflow_id passed to job model")
        elif not shortname or len(shortname) == 0:
            raise ValueError(f"Job shortname cannot be empty")

        record = self.find(workflow_id, shortname)
        if not record:
            record = JobModel(workflow_id=workflow_id, shortname=shortname, name=name)
            self.add(record)
            self.save()
        elif record and record.name.lower() != name.lower():
            record.name = name
            self.save()

        return record

    def set_data(self, id: int, property: str, data: any) -> None:
        if isinstance(data, dict):
            for name, value in data.items():
                item = JobDataModel(job_id=id, property=property, name=name, value=str(value))
                self.add(item)
        elif isinstance(data, list):
            for value in data:
                item = JobDataModel(job_id=id, property=property, name='', value=str(value))
                self.add(item)
        else:
            item = JobDataModel(job_id=id, property=property, name='', value=str(data))
            self.add(item)
        self.save()

    def delete_data(self, id: int) -> None:
        self.session.query(JobDataModel).filter_by(job_id=id).delete()
        self.save()

    def find_next_data(self, job_data_id: int, count: int) -> JobDataModel | None:
        return (self.session.query(JobDataModel)
                .filter(
                    and_(
                        JobDataModel.id > job_data_id,
                        or_(
                            JobDataModel.property == 'env',
                            JobDataModel.value.like('%{{%')
                        )
                    )
                ).order_by(JobDataModel.id).limit(count).all()
            )

    def count(self) -> int:
        return self.session.query(JobModel).count()
