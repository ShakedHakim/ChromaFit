from repository import ColorRepository, MockItemRepository, SqliteColorRepository


class RepositoryFactory:
    """Creates ColorRepository instances from a type name."""

    @staticmethod
    def create(repo_type: str, **kwargs) -> ColorRepository:
        """Return a repository for the given type ("sqlite" or "mock").

        For "sqlite", accepts an optional db_path (default "chromafit.db").
        Raises ValueError if repo_type is not recognized.
        """
        if repo_type == "sqlite":
            return SqliteColorRepository(kwargs.get("db_path", "chromafit.db"))
        if repo_type == "mock":
            return MockItemRepository()
        raise ValueError(
            f"Unknown repository type: '{repo_type}'. Expected 'sqlite' or 'mock'."
        )
