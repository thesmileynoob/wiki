# -*- coding: utf-8 -*-
import os

import wasabi
import flask
import jinja2

from wiki import config
from wiki.page import Page, Revision, new_session

log = wasabi.Printer()
flask_app = flask.Flask('Wiki')
jenv = jinja2.Environment(
    loader=jinja2.PackageLoader(__name__, config.TEMPLATE_DIR),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)


@flask_app.route('/')
def homepage():
    session = new_session()
    page = session.query(Page).filter_by(id=1).one()
    rev = page.revisions[0]
    session.close()

    homepage = jenv.get_template('homepage.html')
    return homepage.render(title=page.title, content=rev.content)


@flask_app.route('/todo')
def todo():
    template = jenv.get_template('todo.html')
    return template.render()


@flask_app.route('/settings')
def settings():
    template = jenv.get_template('settings.html')
    return template.render()


@flask_app.route('/generate')
def generate_pages():
    """ Generate dummy pages for testing """

    if os.path.exists(config.DBNAME):
        return f"Pages already present. Delete {config.DBNAME} to regenerate pages."

    with open('static/dummy_data.txt', 'r') as f:
        data = f.read()

    pages = data.split('======')
    assert len(pages) == 3

    p1 = Page(title='Wiki')
    r1 = Revision(content=pages[0])

    p2 = Page(title='Website')
    r2 = Revision(content=pages[1])

    p3 = Page(title='Stock_Market')
    r3 = Revision(content=pages[2])

    session = new_session()

    session.add(p1)
    session.add(p2)
    session.add(p3)
    session.commit()

    p1.revisions.append(r1)
    p2.revisions.append(r2)
    p3.revisions.append(r3)

    session.commit()

    session.close()

    log.good('Pages generated successfully')
    return 'OK'


flask_app.run()
