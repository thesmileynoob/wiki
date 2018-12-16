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
    categories: [int]
    flags: str
    notes: str
    body: Body

Category:
    id: int
    name: str
    desc: str
    notes: str


Revision:
    id: int
    Content: str (main text, appendices)
    notes: str
"""

Base = declarative_base()
engine = create_engine(f"sqlite:///{config.DBNAME}")
# engine = create_engine(f"sqlite:///:memory:", echo=True)


class Page(Base):
    __tablename__ = 'pages'

    id: int = Column(Integer, primary_key=True)
    title: str = Column(String, unique=True)
    flags: str = Column(String, comment='Comma separated strings')
    categories: int = Column(String, comment='Comma seperated category ids')
    notes: str = Column(String)

    # List of revisions of this page
    revisions = relationship('Revision', back_populates='page')

    def __repr__(self):
        return f"<Page(id: {self.id}, title: '{self.title}')>"


class Category(Base):
    __tablename__ = 'categories'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, unique=True)
    desc: str = Column(String, comment='A short description of the category')
    notes: str = Column(String)

    def __repr__(self):
        return f"<Category(id: {self.id}, name: '{self.name}')>"


class Revision(Base):
    __tablename__ = 'revisions'

    id: int = Column(Integer, primary_key=True)
    page_id: int = Column(Integer, ForeignKey('pages.id'))
    content: str = Column(String)
    timestamp: int = Column(Integer)  # Unix epoch
    notes: str = Column(String)

    page: Page = relationship('Page', back_populates='revisions')

    def __repr__(self):
        return f"< Rev(id: {self.id}, pid: {self.page_id}, content: '{self.content}') >"


# Create the tables if they do not exist already
Base.metadata.create_all(engine)

# TODO Delet this


def api_test(pagename):
    Session = sessionmaker(bind=engine)
    session = Session()
    page = Page(title=pagename)
    r1 = Revision(page_id=1, content='first revision')

    session.add(page)
    session.add(r1)
    session.commit()

    r2 = Revision(page_id=1, content='second revision')

    page.revisions.append(r2)  # HOLY SMOKES THIS WORKS!!!
    session.commit()

    session.close()
