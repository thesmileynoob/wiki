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
    with new_session() as session:

        pages = session.query(Page).all()
        num_revs = session.query(Revision).count()

        check = 0
        for page in pages:
            page.revcount = len(page.revisions)
            check += page.revcount
        abandoned = num_revs - check

        ctx = {
            'v_pages': pages,
            'v_num_pages': len(pages),
            'v_num_revs': num_revs,
            'v_num_abandoned': abandoned,
        }

    return flask.render_template('home.html', **ctx)


@flask_app.route('/wiki/<title>')
def page_view(title):
    with new_session() as session:

        title = Page.format_title(title)
        try:
            page = session.query(Page).filter_by(title=title).one()
        except NoResultFound:
            return 'No match found'
            # TODO Handle this!

        rev = page.revisions[0]  # latest revision

        ctx = {
            'v_page_id': page.id,
            'v_pretty_title': Page.pretty_title(page.title),
            'v_content': rev.content
        }

    return flask.render_template('page.html', **ctx)


@flask_app.route('/delete/<int:id>')
def page_delete(id):
    with new_session() as session:
        try:
            page = session.query(Page).filter_by(id=id).one()
            session.delete(page)  # delete page and its revs
            msg = f'Page(id: {id}) deleted successfully'
        except NoResultFound:
            msg = f'Delete Failed- Page(id: {id}) doesnt exist!'
        finally:
            session.commit()

        ctx = {
            'v_title': f'Delete Page {id}',
            'v_message': msg
        }

    return flask.render_template('redirect.html',  **ctx)


@flask_app.route('/todo')
def todo_view():
    return flask.render_template('todo.html')


@flask_app.route('/settings')
def settings():
    return flask.render_template('settings.html')


# TODO rename to /new
@flask_app.route('/add', methods=['GET', 'POST'])
def add_page_view():
    """ Add a new page """
    r = flask.request

    if r.method == 'GET':
        # Display the add form
        ctx = {'v_title': 'New Page'}
        return flask.render_template('add_page.html', **ctx)

    elif r.method == 'POST':
        # Save the form and show a little modal maybe
        page_title = r.form.get('page_title', '').strip()
        page_note = r.form.get('page_note', '').strip()
        rev_content = r.form.get('rev_content', '').strip()

        # TODO frontend validation
        if not page_title:
            raise Exception('TitleError: empty title')
        if not rev_content:
            raise Exception('RevisionError: empty revision')

        with new_session() as session:
            # page
            page = Page()
            page.title = Page.format_title(page_title)
            page.note = page_note

            # Revision
            rev = Revision()
            rev.content = rev_content
            rev.timestamp = int(time.time())

            if page.revisions:
                log.fail('create_new_page: Page already exists!: ', page)
                raise Exception('Page already exists!')
            page.revisions.append(rev)
            session.add(page)
            session.commit()

        return flask.redirect(
            flask.url_for('page_view', title=Page.format_title(page_title)))


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

    with new_session() as session:
        session.add_all([p1, p2, p3])
        session.commit()

    log.good('Pages generated successfully')
    return flask.redirect(flask.url_for('homepage_view'))


flask_app.run()
