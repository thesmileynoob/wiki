from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from . import config

Base = declarative_base()

# engine = create_engine(f"sqlite:///:memory:", echo=True)
_engine = create_engine(f"sqlite:///{config.DBNAME}")

_invoked_once = False
@contextmanager
def new_session():
    """ Context manager for sessions """
    global _invoked_once
    if not _invoked_once:
        Base.metadata.create_all(_engine)

    Session = sessionmaker(bind=_engine)
    instance = Session()
    yield instance
    instance.close()
