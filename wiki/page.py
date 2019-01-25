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


def _setup():
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
        self.revs: [Revision] = []

    def __repr__(self):
        return f"<Page(id: {self.id}, title: '{self.title}', revcount: {{ len(self.revs) }})>"

    def add_revision(self, rev: Revision):
        self.revs.insert(0, rev)
        SQL = """
        INSERT INTO revisions (page_id, timestamp, body)
        VALUES (?, ?, ?)
        """
        with new_session() as cur:
            cur.execute(SQL, (self.id, rev.timestamp, rev.body))
            rev.id = cur.lastrowid

    def last_rev(self) -> Revision:
        return self.revs[0]

    def body(self) -> str:
        return self.last_rev().body

    def timestamp(self) -> str:
        return time.ctime(self.last_rev().timestamp)

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
    """ return page by id with its revs attached """
    with new_session() as cur:
        if id:
            SQL = "SELECT * FROM pages WHERE id=?"
            row = cur.execute(SQL, (id,)).fetchone()
        elif title:
            SQL = "SELECT * FROM pages WHERE title LIKE ?"
            row = cur.execute(SQL, (title,)).fetchone()
        else:
            assert 0, "This shouldn't happen"

        if not row:
            return None

        page =  Page.from_row(row)
        page.revs = _get_page_revs(page.id)
        return page


def _get_page_revs(pid: int) -> [Revision]:
    """ return a list of all revisions of page in desc ord """
    SQL = "SELECT * FROM revisions WHERE page_id=? ORDER BY timestamp DESC"
    with new_session() as cur:
        res = cur.execute(SQL, (pid, )).fetchall()
        if not res:
            assert 0, "No revs found: pid=" + str(id)
        return [Revision.from_row(row) for row in res]


def get_all_pages() -> [Page]:
    with new_session() as cur:
        pids = cur.execute("SELECT id FROM PAGES").fetchall()
        if not pids:
            return []
        else:
            return [get_page(pid[0]) for pid in pids]


def get_page_index() -> [(int, str)]:
    """ return the list of tuple(id, title) of all pages """
    SQL = "SELECT id, title FROM pages"
    with new_session() as cur:
        rows = cur.execute(SQL).fetchall()
        if not rows:
            return []
        else:
            return [(row[0], row[1]) for row in rows]


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
    sep = ';;;;;'
    bodies = data.split(sep)
    assert len(bodies) == 4

    titles = ['wiki', 'Website', 'Stock Market', 'Markdown']

    for i, title in enumerate(titles):
        page = create_page(title, '')
        rev = Revision()
        rev.body = bodies[i]
        rev.timestamp = int(time.time())
        page.add_revision(rev)

    print('Pages generated successfully')


# Create all tables
_setup()
