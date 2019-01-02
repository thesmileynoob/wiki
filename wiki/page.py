from .dbcommons import *


class Page(Base):
    __tablename__ = 'pages'

    id: int = Column(Integer, primary_key=True)
    title: str = Column(Text, unique=True, nullable=False)
    note: str = Column(Text)

    # NOTE: cascade is required for deletion to work!
    revisions = relationship(
            'Revision', back_populates='page', cascade='all, delete, delete-orphan')

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


class Revision(Base):
    __tablename__ = 'revisions'

    id: int = Column(Integer, primary_key=True)
    page_id: int = Column(Integer, ForeignKey('pages.id'))
    content: str = Column(Text, nullable=False)
    timestamp: int = Column(Integer, nullable=False)  # Unix epoch

    page: Page = relationship('Page', back_populates='revisions')

    def __repr__(self):
        return f"<Rev(id: {self.id}, pid: {self.page_id}, content: '{self.content[:50]}')>"


