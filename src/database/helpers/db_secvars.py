from sqlalchemy import func
from src.libs.constants import SecretVariableVisibility
from src.libs.components.secvar import SecretVariableComponent
from src.database.helpers.db_base import DBBase
from src.database.models import SecretsVariablesModel, SecretsVariablesReposModel


class DBSecretsAndVariables(DBBase):
    def find(self, repo_id: int, category: int, type: int, name: str) -> SecretsVariablesModel | None:
        return self.session.query(SecretsVariablesModel).filter(
            SecretsVariablesModel.repo_id == repo_id,
            SecretsVariablesModel.category == category,
            SecretsVariablesModel.type == type,
            func.lower(SecretsVariablesModel.name) == func.lower(name)
        ).first()

    def create(self, repo_id: int, secvar: SecretVariableComponent) -> SecretsVariablesModel:
        record = self.find(repo_id, secvar.category, secvar.type, secvar.name)
        if not record:
            record = SecretsVariablesModel(repo_id=repo_id)
            record.category = secvar.category
            record.type = secvar.type
            record.name = secvar.name
            record.value = secvar.value
            record.visibility = secvar.visibility
            record.created_at = secvar.created_at
            record.updated_at = secvar.updated_at
            self.add(record)
            self.save()

            if secvar.visibility == SecretVariableVisibility.SELECTED:
                for repo in secvar.repos:
                    repo_record = SecretsVariablesReposModel(secret_variable_id=record.id, repo_id=repo.id)
                    self.add(repo_record)
                self.save()

        return record
