# -*- coding: utf-8 -*-
import os
import time

import wasabi
import flask

from sqlalchemy.orm.exc import NoResultFound

from wiki import config
from wiki.page import Page, Revision, new_session

log = wasabi.Printer()
flask_app = flask.Flask('Wiki')
flask_app.config['DEBUG'] = True


@flask_app.route('/')
def homepage_view():
    session = new_session()

    pages = session.query(Page).all()
    num_pages = len(pages)
    num_revs = session.query(Revision).count()
    check = 0
    for page in pages:
        page.revcount = len(page.revisions)
        check += page.revcount

    abandoned = num_revs - check
    session.close()

    log.info(f"{num_pages} pages")
    return flask.render_template('home.html', num_pages=num_pages,
                                 pages=pages, num_revs=num_revs,
                                 abandoned = abandoned)


@flask_app.route('/wiki/<title>')
def page_view(title):
    session = new_session()

    title = Page.format_title(title)
    try:
        page = session.query(Page).filter_by(title=title).one()
    except NoResultFound:
        return 'No match found'
        # TODO Handle this!

    rev = page.revisions[0]

    session.close()

    return flask.render_template(
        'page.html',
        page_id=page.id,
        title=Page.pretty_title(page.title),
        content=rev.content)


@flask_app.route('/delete/<int:id>')
def page_delete(id):
    session = new_session()
    try:
        page = session.query(Page).filter_by(id=id).one()
        del page.revisions
        del page
        msg = f'Page(id: {id}) deleted successfully'
    except NoResultFound:
        msg = f'Delete Failed- Page(id: {id}) doesnt exist!'
    finally:
        session.commit()
        session.close()

    return flask.render_template('redirect.html',
                                 title=f'Delete Page {id}', message=msg)


@flask_app.route('/todo')
def todo_view():
    return flask.render_template('todo.html')


@flask_app.route('/settings')
def settings():
    return flask.render_template('settings.html')


@flask_app.route('/add', methods=['GET', 'POST'])
def add_page_view():
    """ Add a new page """
    r = flask.request
    if r.method == 'GET':
        # Display the add form
        return flask.render_template('add_page.html', title='Add Page')
    else:
        # Save the form and show a little modal maybe
        page_title = r.form.get('page_title', '').strip()
        page_flags = r.form.get('page_flags', '').strip()
        page_note = r.form.get('page_note', '').strip()

        rev_content = r.form.get('rev_content', '').strip()
        rev_note = r.form.get('rev_note', '').strip()

        if not page_title:
            raise Exception('TitleError: empty title')
        if not rev_content:
            raise Exception('RevisionError: empty revision')

        # page
        page = Page()
        page.title = Page.format_title(page_title)
        page.note = page_note
        page.flags = Page.format_flags(page_flags)

        # Revision
        rev = Revision()
        rev.content = rev_content
        rev.note = rev_note
        rev.timestamp = int(time.time())

        create_new_page(page, rev)

        return flask.redirect(flask.url_for('page_view',
                                            title=Page.format_title(page_title)))


def create_new_page(page: Page, revision: Revision):
    """ save's a new page to db """
    session = new_session()
    if page.revisions:
        log.fail('create_new_page: Page already exists!: ', page)
        raise Exception('Page already exists!')
    page.revisions.append(revision)
    session.add(page)
    session.commit()
    session.close()


@flask_app.route('/generate')
def generate_pages():
    """ Generate dummy pages for testing """

    with open('static/dummy_data.txt', 'r') as f:
        data = f.read()

    pages = data.split('======')
    assert len(pages) == 3

    p1 = Page(title=Page.format_title('wiki'))
    p1.revisions.append(Revision(content=pages[0]))

    p2 = Page(title=Page.format_title('Website'))
    p2.revisions.append(Revision(content=pages[1]))

    p3 = Page(title=Page.format_title('stock market'))
    p3.revisions.append(Revision(content=pages[2]))

    session = new_session()
    session.add_all([p1, p2, p3])
    session.commit()
    session.close()

    log.good('Pages generated successfully')
    return flask.redirect(flask.url_for('homepage_view'))


flask_app.run()
