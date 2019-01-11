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
flask_app.config['DEBUG'] = True


@flask_app.route('/')
def view_homepage():
    ctx = get_all_pages()
    # TODO Generate context here itself
    return flask.render_template('home.html', **ctx)


@flask_app.route('/settings')
def view_settings():
    return flask.render_template('settings.html')


@flask_app.route('/wiki/<title>')
def view_page(title):
    ctx = get_page_by_title(title)
    return flask.render_template('page.html', **ctx)


# TODO rename to /new
@flask_app.route('/add', methods=['GET', 'POST'])
def view_add_page():
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

        create_new_page(page_title, page_note, rev_content)

        return flask.redirect(
            flask.url_for('view_page', title=Page.format_title(page_title)))


@flask_app.route('/edit/<int:id>', methods=['GET', 'POST'])
def view_edit_page(id):
    if flask.request.method == 'GET':
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
                return flask.render_template('edit_page.html', **ctx)
            except NoResultFound:
                ctx = {
                    'v_title': f'Edit Page {id}',
                    'v_message': f'Page {id} does not exist'
                }
                return flask.render_template('redirect.html',  **ctx)

    elif flask.request.method == 'POST':
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

        return flask.redirect(
            flask.url_for('view_page', title=Page.format_title(page_title)))


@flask_app.route('/delete/<int:id>')
def api_page_delete(id):
    ctx = del_page_by_id(id)
    return flask.render_template('redirect.html',  **ctx)


@flask_app.route('/generate')
def api_generate_pages():
    gen_dummy_pages()
    return flask.redirect(flask.url_for('view_homepage'))


flask_app.run()
