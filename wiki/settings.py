import time
import sqlite3

from contextlib import contextmanager

from .page import new_session


_SETTINGS = {
    'theme': ['light', 'dark'],
}


def _setup():
    SQL = """ 
    CREATE TABLE IF NOT EXISTS settings (
        name TEXT NOT NULL,
        value TEXT NOT NULL,
        PRIMARY KEY (name),
        UNIQUE (name)
    );
    """
    with new_session() as cur:
        cur.execute(SQL)
        for name, value in _SETTINGS.items():
            SQL = """INSERT OR IGNORE INTO settings 
            (name, value) VALUES (?,?)
            """
            cur.execute(SQL, (name, value[0]))


def _setting_exists(name: str) -> bool:
    return name in _SETTINGS.keys()


def _setting_is_valid(name: str, value: str) -> bool:
    assert _setting_exists(name), "ERROR: FIX THIS!"
    return value in _SETTINGS[name]


class Setting:
    def __init__(self, name: str, value: str):
        if not _setting_exists(name):
            raise Exception('Unknown setting: ' + name)
        if not _setting_is_valid(name, value):
            msg = 'Invalid setting value: ' + value
            msg += '\n  Possible values: {' + \
                ','.join(_SETTINGS[name]) + '}'
            raise Exception(msg)

        self.name: str = name
        self.value: str = value

    def save(self):
        with new_session() as cur:
            SQL = "UPDATE settings SET name=?, value=? WHERE name=?"
            cur.execute(SQL, (self.name, self.value, self.name))

    def from_row(row):
        assert row
        return Setting(row[0], row[1])


def get_setting(name: str) -> Setting:
    assert _setting_exists(name), "Invalid setting name"
    with new_session() as cur:
        SQL = "SELECT * FROM settings WHERE name=?"
        row = cur.execute(SQL, (name,)).fetchone()
        return Setting.from_row(row)


def get_setting_values(name: str) -> [str]:
    assert _setting_exists(name), "Invalid setting name"
    with new_session() as cur:
        SQL = "SELECT * FROM settings WHERE name=?"
        row = cur.execute(SQL, (name,)).fetchone()
        return Setting.from_row(row)


_setup()
