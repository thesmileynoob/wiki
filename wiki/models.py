import json
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# Internals
DBNAME = 'data.db'
_Base = declarative_base()
# engine = create_engine(f"sqlite:///:memory:", echo=True)
_engine = create_engine(f"sqlite:///{DBNAME}")
# Flag for creating tables
_invoked_once = False


@contextmanager
def new_session():
    """ Context manager for sessions """
    global _invoked_once
    if not _invoked_once:
        # Create tables lazily
        _Base.metadata.create_all(_engine)
        _invoked_once = True

    Session = sessionmaker(bind=_engine)
    instance = Session()
    yield instance
    instance.close()


class Page(_Base):
    __tablename__ = 'pages'

    id: int = Column(Integer, primary_key=True)
    title: str = Column(Text, unique=True, nullable=False)
    note: str = Column(Text)

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

    def get_last_rev(self):
        with new_session() as sess:
            rev = sess.query(Revision).filter_by(page_id=self.id).one()
            return rev

    def get_all_revs(self):
        with new_session() as sess:
            revs = sess.query(Revision).filter_by(page_id=self.id).all()
            return revs
    
    def get_rev_count(self):
        with new_session() as sess:
            return sess.query(Revision).filter_by(page_id=self.id).count()


class Revision(_Base):
    __tablename__ = 'revisions'

    id: int = Column(Integer, primary_key=True)
    page_id: int = Column(Integer, ForeignKey('pages.id'))
    content: str = Column(Text, nullable=False)
    timestamp: int = Column(Integer, nullable=False)  # Unix epoch

    def __repr__(self):
        return f"<Rev(id: {self.id}, pid: {self.page_id}, content: '{self.content[:50]}')>"


"""
class TodoList(_Base):
    __tablename__ = 'todo_list'

    id: int = Column(Integer, primary_key=True)
    timestamp: int = Column(Integer, nullable=False)
    title: str = Column(Text, unique=True, nullable=False)

    items = relationship('TodoItem',
                         back_populates='todo_list', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return f"<TodoList(id: {self.id}, title: '{self.title}')>"


class TodoItem(_Base):
    __tablename__ = 'todo_items'

    id: int = Column(Integer, primary_key=True)
    list_id: int = Column(Integer, ForeignKey('todo_list.id'))
    content: str = Column(Text, nullable=False)
    timestamp: int = Column(Integer, nullable=False)  # Unix epoch

    todo_list: TodoList = relationship('TodoList', back_populates='items')

    def __repr__(self):
        return f"<TodoItem(id: {self.id}, lid: {self.list_id}, content: '{self.content[:50]}')>"

"""
