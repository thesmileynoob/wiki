# -*- coding: utf-8 -*-
import os
import time
import json

import wasabi
import flask

from sqlalchemy.orm.exc import NoResultFound

from wiki.models import Page, Revision
from wiki.page import *

log = wasabi.Printer()
flask_app = flask.Flask('Wiki')
flask_app.debug = True
flask_app.env = 'development'


@flask_app.route('/')
def view_homepage():
    pages = get_all_pages()

    check = 0
    num_revs = 0
    for page in pages:
        page.revcount = page.get_rev_count()
        check += page.revcount
        num_revs += page.revcount
    abandoned = num_revs - check

    ctx = {
        'v_pages': pages,
        'v_num_pages': len(pages),
        'v_num_revs': num_revs,
        'v_num_abandoned': abandoned,
    }

    return flask.render_template('home.html', **ctx)


@flask_app.route('/settings')
def view_settings():
    return flask.render_template('settings.html')


@flask_app.route('/wiki/<title>')
def api_search_page(title):
    ctx = get_page_by_title(title)
    # TODO pagenotfound!
    return flask.render_template('page.html', **ctx)


@flask_app.route('/wiki/<int:id>')
def view_page(id):
    ctx = get_page_by_id(id)
    return flask.render_template('page.html', **ctx)


@flask_app.route('/new')
def view_new_page():
    """ Add a new page """
    ctx = {'v_title': 'New Page'}
    return flask.render_template('newpage.html', **ctx)


@flask_app.route('/edit/<int:id>')
def view_edit_page(id):
    with new_session() as session:
        try:
            page: Page = session.query(Page).filter_by(id=id).one()
            latestrev: Revision = page.revisions[-1]
            ctx = {
                'v_title': f'Edit Page {id}',
                'v_page_id': page.id,
                'v_page_title': Page.pretty_title(page.title),
                'v_page_note': page.note or "",
                'v_rev_content': latestrev.content
            }
            return flask.render_template('editpage.html', **ctx)
        except NoResultFound:
            ctx = {
                'v_title': f'Edit Page {id}',
                'v_message': f'Page {id} does not exist'
            }
            return flask.render_template('redirect.html',  **ctx)


@flask_app.route('/api/new', methods=['POST'])
def api_new_page():
    # Save page and redirect
    r = flask.request

    page_title = r.form.get('page_title', '').strip()
    page_note = r.form.get('page_note', '').strip()
    rev_content = r.form.get('rev_content', '').strip()

    # TODO frontend validation
    if not page_title:
        raise Exception('TitleError: empty title')
    if not rev_content:
        raise Exception('RevisionError: empty revision')

    id = create_new_page(page_title, page_note, rev_content)

    return flask.redirect(flask.url_for('view_page', id=id))


@flask_app.route('/api/edit/<int:id>', methods=['POST'])
def api_edit_page(id):
    r = flask.request
    page_id = r.form.get('page_id', '')
    page_title = r.form.get('page_title', '').strip()
    page_note = r.form.get('page_note', '').strip()
    rev_content = r.form.get('rev_content', '').strip()

    with new_session() as session:
        page = session.query(Page).filter_by(id=id).one()

        page.title = Page.format_title(page_title)
        page.note = page_note

        rev = Revision()
        rev.content = rev_content
        rev.timestamp = int(time.time())

        page.revisions.append(rev)

        session.commit()

    return flask.redirect(flask.url_for('view_page', id=id))


@flask_app.route('/delete/<int:id>')
def api_page_delete(id):
    ctx = del_page_by_id(id)
    return flask.render_template('redirect.html',  **ctx)


@flask_app.route('/generate')
def api_generate_pages():
    gen_dummy_pages()
    return flask.redirect(flask.url_for('view_homepage'))


flask_app.run()
