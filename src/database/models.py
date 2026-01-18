from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text, Integer, Boolean


Base = declarative_base()


class OrganisationModel(Base):
    __tablename__ = 'organisations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, default='', index=True)
    poll_status = Column(Integer, default=0, index=False)
    status = Column(Integer, default=0, index=True)

class RepositoryModel(Base):
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, default=0, index=True)
    redirect_id = Column(Integer, default=0, index=True)
    name = Column(String, default='', index=True)
    default_branch = Column(String, default='', index=True)
    ref = Column(String, default='', index=True)
    ref_type = Column(Integer, default=0, index=True)
    ref_commit = Column(String, default='')
    ref_old_name = Column(String, default='', index=True)
    resolved_ref = Column(String, default='', index=True)
    resolved_ref_type = Column(Integer, default=0, index=True)
    visibility = Column(Integer, default=0, index=True)
    poll_status = Column(Integer, default=0, index=False)
    status = Column(Integer, default=0, index=True)
    stars = Column(Integer, default=0, index=True)
    fork = Column(Boolean, default=False, index=True)
    archive = Column(Boolean, default=False, index=True)

class WorkflowModel(Base):
    __tablename__ = 'workflows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_id = Column(Integer, default=0, index=True)
    redirect_id = Column(Integer, default=0, index=True)
    path = Column(String, default='')
    type = Column(Integer, default=0, index=True)
    contents = Column(Text)
    data = Column(Text)
    status = Column(Integer, default=0, index=True)

class WorkflowRelationshipModel(Base):
    __tablename__ = 'workflow_relationships'

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, default=0, index=True)
    child_id = Column(Integer, default=0, index=True)

class WorkflowDataModel(Base):
    __tablename__ = 'workflow_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, default=0, index=True)
    property = Column(String, default='', index=True)
    name = Column(String, default='', index=True)
    value = Column(Text, default='', index=True)

class JobModel(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, default=0, index=True)
    name = Column(String, default='')
    shortname = Column(String, default='', index=True)

class JobDataModel(Base):
    __tablename__ = 'job_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, default=0, index=True)
    property = Column(String, default='', index=True)
    name = Column(String, default='', index=True)
    value = Column(Text, default='', index=True)

class StepModel(Base):
    __tablename__ = 'steps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, default=0, index=True)
    step_number = Column(Integer, default=0, index=True)

class StepDataModel(Base):
    __tablename__ = 'step_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    step_id = Column(Integer, default=0, index=True)
    property = Column(String, default='', index=True)
    name = Column(String, default='', index=True)
    value = Column(Text, default='', index=True)

class VariableModel(Base):
    __tablename__ = 'variables'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_data_id = Column(Integer, default=0, index=True)
    job_data_id = Column(Integer, default=0, index=True)
    step_data_id = Column(Integer, default=0, index=True)
    name = Column(String, default='', index=True)

class VariableValueMappingModel(Base):
    __tablename__ = 'variables_value_mapping'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Integer, default=0, index=True)
    type_join_id = Column(Integer, default=0, index=True)
    group_type = Column(Integer, default=0, index=True)
    name = Column(String, default='', index=True)
    value = Column(String, default='', index=True)

class ConfigModel(Base):
    __tablename__ = 'config'

    name = Column(String, primary_key=True, index=True)
    value = Column(String, default='', index=True)
