from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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


Body:
    id: int
    revision: int
    Content (main text, appendices)
    notes: str
"""

class Page:
    def __init__(self):
        self.id: int = 0 # Permanant
        self.title: str = "" # Camel_Case
        self.flags: str = "" # ??
        self.categories: int = 0 # ForeignKey(Category.id)
        self.notes: str = ""

class Category:
    def __init__(self):
        self.id: int = 0 # permanant
        self.name: str = ""
        self.desc: str = "" # description
        self.notes: str = ""

class Body:
    def __init__(self):
        self.id: int = 0 # permanant
        self.page_id: int = 0 # Foreign key
        self.content: str = ""
        self.revision: int = 0  # Increseases by 1 every edit
        self.timestamp: int = 0 # Unix epoch
        self.notes: str = ""
