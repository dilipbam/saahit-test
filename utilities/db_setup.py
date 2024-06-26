import os

from alembic.util import CommandError
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

from utilities.schemas import all_bases
from utilities.schemas.models import Base

# importing path of alembic.ini file may neeed changes
ALEMBIC_INI_PATH = os.path.join(os.path.dirname(__file__), "alembic.ini")


def database_factory(DB_URL):
    # Create the engine
    engine = create_engine(DB_URL)

    # Reflect the changes in models to the database metadata
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Bind the metadata to the engine
    Base.metadata.bind = engine

    # Create all tables that don't exist in the database
    for base in all_bases:
        Base.metadata.create_all(engine, checkfirst=True)

    # Create a session maker
    Session = sessionmaker(autoflush=False, bind=engine)
    return Session


# def run_migrations():
#     """ Run Alembic migrations """
#     # Path to the alembic.ini file
#
#     # Run migration commands
#     config = Config(ALEMBIC_INI_PATH)
#     command.revision(config, autogenerate=True, message="Automatic migration")
#     command.upgrade(config, "head")

def run_migrations():
    """ Run Alembic migrations """
    # Run migration commands
    config = Config(ALEMBIC_INI_PATH)
    try:
        command.revision(config, autogenerate=True, message="Automatic migration")
        command.upgrade(config, "head")
    except CommandError as e:
        print(f"Error occurred during migration: {e}")
        try:
            # Generate a new migration script reflecting the deletion
            command.revision(config, autogenerate=True, message="Reflect deletion of record")
            # Apply the new migration script
            command.upgrade(config, "head")
        except CommandError as e:
            print(f"Error occurred during migration: {e}")


if __name__ == "__main__":
    run_migrations()
