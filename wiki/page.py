from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from . import config

"""
https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Layout
Represents a wiki page:

Page:
    id: int
    title: str
    flags: str
    notes: str
    body: Body

Revision:
    id: int
    Content: str (main text, appendices)
    notes: str
"""

# ORM Base class for mapped classes
Base = declarative_base()


class Page(Base):
    __tablename__ = 'pages'

    id: int = Column(Integer, primary_key=True)
    title: str = Column(String, unique=True)
    flags: str = Column(String, comment='csv')
    note: str = Column(String)

    # List of revisions of this page
    revisions = relationship('Revision', back_populates='page')

    def __repr__(self):
        return f"<Page(id: {self.id}, title: '{self.title}')>"

    @staticmethod
    def format_title(title: str):
        """ returns string formatted title as stored in the db """
        title = '_'.join(title.lower().split())
        return title

    @staticmethod
    def pretty_title(title: str) -> str:
        """ format page title in TitleCase """
        thetitle = ' '.join(title.split('_'))  # the sunken ship
        return thetitle.title()  # The Sunken Ship

    @staticmethod
    def format_flags(flags: any) -> str:
        """ flags must be string or [string] """
        if type(flags) not in [str, list]:
            raise TypeError("flags must be str or [str]")
        if type(flags) is str:
            flags = flags.split(',')
        flags = [x.strip().lower() for x in flags]
        return ', '.join(flags)


class Revision(Base):
    __tablename__ = 'revisions'

    id: int = Column(Integer, primary_key=True)
    page_id: int = Column(Integer, ForeignKey('pages.id'))
    content: str = Column(String)
    timestamp: int = Column(Integer)  # Unix epoch
    note: str = Column(String)

    page: Page = relationship('Page', back_populates='revisions')

    def __repr__(self):
        return f"<Rev(id: {self.id}, pid: {self.page_id}, content: '{self.content[:50]}')>"


# engine = create_engine(f"sqlite:///:memory:", echo=True)
engine = create_engine(f"sqlite:///{config.DBNAME}")

# Create the tables if they do not exist already
Base.metadata.create_all(engine)


@contextmanager
def new_session():
    """ Context manager for sessions. This is implemented only
    to simplify db access using the `with` statement """
    Session = sessionmaker(bind=engine)
    instance = Session()
    yield instance
    instance.close()
