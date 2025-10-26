import json
from sqlalchemy import and_, or_
from sqlalchemy import func, update
from src.database.helpers.db_base import DBBase
from src.database.models import WorkflowModel, WorkflowRelationshipModel, WorkflowDataModel
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import WorkflowStatus, WorkflowType
from src.libs.exceptions import MissingComponentDetails


class DBWorkflow(DBBase):
    def find(self, repo_id: int, path: str) -> WorkflowModel | None:
        return self.session.query(WorkflowModel).filter(
            WorkflowModel.repo_id == repo_id,
            func.lower(WorkflowModel.path) == func.lower(path)
        ).first()

    def create(self, workflow: WorkflowComponent) -> WorkflowModel:
        if workflow.repo.id == 0:
            raise MissingComponentDetails("Missing component details: workflow.repo.id")
        elif workflow.repo.org.id == 0:
            raise MissingComponentDetails("Missing component details: workflow.repo.org.id")

        record = self.find(workflow.repo.id, workflow.path)
        if not record:
            record = WorkflowModel(
                repo_id=workflow.repo.id,
                redirect_id=workflow.redirect_id,
                path=workflow.path,
                type=workflow.type,
                contents=workflow.contents,
                data=workflow.data_string,
                status=workflow.status
            )
            self.add(record)
            self.save()
        return record

    def update_status(self, id: int, status: WorkflowStatus) -> None:
        if id == 0:
            raise MissingComponentDetails("Missing workflow component details: id")

        statement = update(WorkflowModel).where(
            WorkflowModel.id == id
        ).values(
            status=status
        )
        self.update_statement(statement)

    def update_type(self, id: int, type: WorkflowType) -> None:
        if id == 0:
            raise MissingComponentDetails("Missing workflow component details: id")

        statement = update(WorkflowModel).where(
            WorkflowModel.id == id
        ).values(
            type=type
        )
        self.update_statement(statement)

    def update_type_and_path(self, workflow: WorkflowComponent) -> None:
        if workflow.id == 0:
            raise MissingComponentDetails("Missing workflow component details: id")

        statement = update(WorkflowModel).where(
            WorkflowModel.id == workflow.id
        ).values(
            type=workflow.type,
            path=workflow.path
        )
        self.update_statement(statement)

    def update_contents(self, id: int, contents: str, data: dict | str | None) -> None:
        if id == 0:
            raise MissingComponentDetails("Missing workflow component details: id")

        if not data:
            data = {}

        statement = update(WorkflowModel).where(
            WorkflowModel.id == id
        ).values(
            contents=contents,
            data=json.dumps(data)
        )
        self.update_statement(statement)

    def update_redirect_id(self, id: int, redirect_id: int) -> None:
        if id == 0:
            raise MissingComponentDetails("Missing workflow component details: id")
        elif redirect_id == 0:
            raise MissingComponentDetails("Missing workflow component details: redirect_id")

        statement = update(WorkflowModel).where(
            WorkflowModel.id == id
        ).values(
            redirect_id=redirect_id
        )
        self.update_statement(statement)

    def link_workflows(self, parent_workflow: WorkflowComponent, child_workflow: WorkflowComponent) -> bool:
        if parent_workflow.id == 0:
            raise MissingComponentDetails("Missing parent workflow component details: id")
        elif parent_workflow.id == 0:
            raise MissingComponentDetails("Missing child workflow component details: id")

        if self.session.query(WorkflowRelationshipModel).filter_by(parent_id=parent_workflow.id, child_id=child_workflow.id).scalar():
            return True

        relationship = WorkflowRelationshipModel(parent_id=parent_workflow.id, child_id=child_workflow.id)
        self.add(relationship)
        self.save()
        return True

    def set_data(self, id: int, property: str, data: any) -> None:
        if isinstance(data, dict):
            for name, value in data.items():
                item = WorkflowDataModel(workflow_id=id, property=property, name=name, value=str(value))
                self.add(item)
        elif isinstance(data, list):
            for value in data:
                item = WorkflowDataModel(workflow_id=id, property=property, name='', value=str(value))
                self.add(item)
        else:
            item = WorkflowDataModel(workflow_id=id, property=property, name='', value=str(data))
            self.add(item)
        self.save()

    def delete_data(self, id: int) -> None:
        self.session.query(WorkflowDataModel).filter_by(workflow_id=id).delete()
        self.save()

    def find_next_data(self, workflow_data_id: int, count: int) -> list[WorkflowDataModel] | None:
        return (self.session.query(WorkflowDataModel)
                .filter(
                    and_(
                        WorkflowDataModel.id > workflow_data_id,
                        or_(
                            WorkflowDataModel.property == 'env',
                            WorkflowDataModel.value.like('%{{%')
                        )
                    )
                ).order_by(WorkflowDataModel.id).limit(count).all()
            )

    def count(self) -> int:
        return self.session.query(WorkflowModel).count()
