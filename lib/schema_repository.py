from app.logging import get_logger
from pygit2 import Repository as gitrepo

from yaml import safe_load as yaml_safe_load
# __all__ = ("get_repo")

logger = get_logger(__name__)

class SchemaRepository:
    def __init__(self, repo, branch, path):
        self.repo   = gitrepo(repo)
        self.branch = self.repo.branches[branch]
        self.path   = path
        logger.info(f"Starting Schema() with repo: {repo}")

    def get_workdir(self):
        return self.repo.workdir

    def get_path(self):
        return self.repo.path 

    def get_schema(self):
        if not self.branch.is_checked_out():
            ref = self.repo.lookup_reference(self.branch.name)
            self.repo.checkout(ref)
        schema_path = self.get_workdir() + "schemas/system_profile/v1.yaml"
        spec_dict = yaml_safe_load(open(schema_path))
        return spec_dict

    def close(self):
        self._kafka_consumer.close()

