from app.logging import get_logger
from pygit2 import Repository as gitrepo

from yaml import safe_load as yaml_safe_load

__all__ = ("get_repo", "get_workdir", "get_path", 'get_schema')

logger = get_logger(__name__)

class SchemaRepository:
    def __init__(self, repo, branch, path):
        self.repo   = gitrepo(repo)
        self.branch = self.repo.branches[branch]
        self.path   = path
        # logger.info(f"Starting Schema() with repo: {repo}")

    def get_workdir(self):
        return self.repo.workdir

    def get_path(self):
        return self.repo.path 

    def get_schema(self):
        print(f"Using branch {self.branch.branch_name}")
        if not self.branch.is_checked_out():
            print(f"Checking out branch {self.branch.branch_name}")
            ref = self.repo.lookup_reference(self.branch.name)
            self.repo.checkout(ref)
        schema_path = self.get_workdir() + "schemas/system_profile/v1.yaml"
        schema_dict = yaml_safe_load(open(schema_path))
        return schema_dict

    def close(self):
        self._kafka_consumer.close()

