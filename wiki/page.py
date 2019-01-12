import json
import time
import sqlite3
from contextlib import contextmanager

# Internals
DBNAME = 'data.db'


@contextmanager
def new_session():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    yield cur
    conn.commit()
    conn.close()


def setup_tables():
    SQL = """
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER,
        title TEXT NOT NULL,
        note TEXT,
        PRIMARY KEY (id)
        UNIQUE (title)
    );

    CREATE TABLE IF NOT EXISTS revisions (
        id INTEGER,
        page_id INTEGER NOT NULL,
        timestamp INTEGER NOT NULL,
        body TEXT NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (page_id) REFERENCES pages (id)
    );
    """
    with new_session() as cur:
        cur.executescript(SQL)


class Revision:
    __tablename__ = 'revisions'

    def __init__(self):
        self.id: int = 0
        self.page_id: int = 0
        self.timestamp: int = 0
        self.body: str = ''

    @staticmethod
    def from_row(row):
        assert row
        rev = Revision()
        rev.id = row[0]
        rev.page_id = row[1]
        rev.timestamp = row[2]
        rev.body = row[3]
        return rev


class Page:
    __tablename__ = 'pages'

    def __init__(self):
        self.id: int = 0  # PK
        self.title: str = ''  # Unique, notnull
        self.note: str = ''

    def __repr__(self):
        return f"<Page(id: {self.id}, title: '{self.title}')>"

    def add_revision(self, rev: Revision):
        SQL = """
        INSERT INTO revisions (page_id, timestamp, body)
        VALUES (?, ?, ?)
        """
        with new_session() as cur:
            cur.execute(SQL, (self.id, rev.timestamp, rev.body))
            rev.id = cur.lastrowid

    def get_last_rev(self):
        SQL = "SELECT * FROM revisions WHERE page_id=? ORDER BY timestamp DESC"
        with new_session() as cur:
            row = cur.execute(SQL, (self.id,)).fetchone()
            if row:
                return Revision.from_row(row)
            else:
                return None

    def get_rev_count(self):
        SQL = "SELECT COUNT(*) FROM revisions WHERE page_id=?"
        with new_session() as cur:
            res = cur.execute(SQL, (self.id,)).fetchone()
            return res[0]

    def get_all_revs(self):
        SQL = "SELECT * FROM revisions WHERE page_id=?"
        with new_session() as cur:
            rows = cur.execute(SQL).fetchall()
            if rows:
                revs = [Revision.from_row(row) for row in rows]
                return revs
            else:
                return []

    @staticmethod
    def from_row(row):
        assert row
        page = Page()
        page.id = row[0]
        page.title = row[1]
        page.note = row[2] or ''
        return page


def create_page(title: str, note: str) -> Page:
    with new_session() as cur:
        SQL = "INSERT INTO pages (title, note) VALUES (?, ?)"
        cur.execute(SQL, (title, note))
        id = cur.lastrowid

        assert id, "Couldn't get lastrowid"

        page = Page()
        page.id = id
        page.title = title
        page.note = note
        return page


def get_page(id: int = 0, title: str = '') -> Page:
    with new_session() as cur:
        if id:
            SQL = "SELECT * FROM pages WHERE id=?"
            row = cur.execute(SQL, (id,)).fetchone()
            if row:
                return Page.from_row(row)
        elif title:
            SQL = "SELECT * FROM pages WHERE title=?"
            row = cur.execute(SQL, (title,)).fetchone()
            if row:
                return Page.from_row(row)
        return None

def get_all_pages() -> [Page]:
    with new_session() as cur:
        rows = cur.execute("SELECT * FROM PAGES")
        if rows:
            pages = [Page.from_row(row) for row in rows]
            return pages
        else:
            return []


def del_page_by_id(id: int):
    page = get_page(id=id)
    assert page, "Page(id = %d) not found!" % id
    with new_session() as cur:
        cur.execute("DELETE FROM pages WHERE id=?", (id,))
        cur.execute("DELETE FROM revisions WHERE page_id=?",
                (id,))


def gen_dummy_pages():
    with open('static/dummy_data.txt', 'r') as f:
        data = f.read()
    bodies = data.split('======')
    assert len(bodies) == 3

    titles = ['wiki', 'Website', 'Stock Market']

    for i, title in enumerate(titles):
        page = create_page(title, '')
        rev = Revision()
        rev.body = bodies[i]
        rev.timestamp = int(time.time())
        page.add_revision(rev)

    print('Pages generated successfully')

# Create all tables
setup_tables()
