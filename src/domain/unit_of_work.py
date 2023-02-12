from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException

from repository import Repository


class UnitOfWork:
    """
    Maintains a list of objects affected by a business
    transaction and coordinates the writing out of changes
    and the resolution of concurrency problems.


    Args:
        session (Session): The database session object.
        repositories (list[Repository]): Collection of the abstract interfaces for database
    """

    def __init__(self, session: Session):
        self.session = session
        self.repositories: list[Repository] = []

    def add_repository(self, repository: Repository):
        self.repositories.append(repository)

    def commit(self):
        try:
            for repository in self.repositories:
                repository.persist()
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status_code=406, detail="Data integrity error")
