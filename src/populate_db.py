import logging

from db.session import SessionLocal
from db.init_db import init_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate() -> None:
    """
    Populate DB with initial data.
    """
    db = SessionLocal()
    init_db(db)


def main() -> None:
    logger.info("(API) Populating DB with initial data...")
    populate()
    logger.info("(API) Initial data created.")


if __name__ == "__main__":
    main()
