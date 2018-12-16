# -*- coding: utf-8 -*-
import os

import wasabi
import flask
# import jinja2

from wiki import config
from wiki.page import Page, Revision, new_session

log = wasabi.Printer()
flask_app = flask.Flask('Wiki')

# jenv = jinja2.Environment(
#     loader=jinja2.PackageLoader(__name__, config.TEMPLATE_DIR),
#     autoescape=jinja2.select_autoescape(['html', 'xml'])
# )


@flask_app.route('/')
def homepage():
    session = new_session()
    pages = session.query(Page).all()
    num_pages = len(pages)
    session.close()
    log.warn(f"{num_pages} pages")
    # homepage = jenv.get_template('home.html')
    # return homepage.render(num_pages=num_pages, pages=pages)
    return flask.render_template('home.html', num_pages=num_pages,
                                 pages=pages)


@flask_app.route('/wiki/<title>')
def page_view(title):
    session = new_session()
    page = session.query(Page).filter_by(title=title).one()
    if not page:
        return 'No match found'
    rev = page.revisions[0]
    session.close()

    # homepage = jenv.get_template('page.html')
    # return homepage.render(title=page.title, content=rev.content)
    return flask.render_template('page.html', title=page.title,
                                 content=rev.content)


@flask_app.route('/todo')
def todo():
    return flask.render_template('todo.html')


@flask_app.route('/settings')
def settings():
    return flask.render_template('settings.html')


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
