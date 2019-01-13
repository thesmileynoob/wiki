# -*- coding: utf-8 -*-
import os
import time
import json

import wasabi
import flask

from wiki.page import *  # TODO only import needed stuff
from wiki.settings import get_setting, Setting

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


@flask_app.route('/wiki/<int:id>')
def view_page(id):
    page = get_page(id=id)
    rev = page.get_last_rev()

    ctx = {
        'v_title': page.title,  # Tab title
        'v_page_id': page.id,
        'v_page_title': page.title,
        'v_timestamp': time.ctime(rev.timestamp),
        'v_body': rev.body
    }

    return flask.render_template('page.html', **ctx)


@flask_app.route('/new')
def view_new_page():
    """ Add a new page """
    ctx = {'v_title': 'New Page'}
    return flask.render_template('newpage.html', **ctx)


@flask_app.route('/edit/<int:id>')
def view_edit_page(id):
    page = get_page(id=id)
    if not page:
        ctx = {
            'v_title': f'Edit Page {id}',
            'v_message': f'Page {id} does not exist'
        }
        return flask.redirect('redirect.html', v_message='Invalid page')

    rev = page.get_last_rev()
    ctx = {
        'v_title': f'Edit Page {id}',
        'v_page_id': page.id,
        'v_page_title': page.title,
        'v_page_note': page.note,
        'v_rev_body': rev.body
    }
    return flask.render_template('editpage.html', **ctx)


@flask_app.route('/wiki/<title>')
def api_search_page(title):
    page = get_page(title=title)
    if page:
        return flask.redirect(flask.url_for('view_page'), id=page.id)
    else:
        ctx = {
            'v_title': 'Page not found',
            'v_message': f"Page '{title}' not found"
        }
        return flask.redirect('redirect.html', **ctx)


@flask_app.route('/api/new', methods=['POST'])
def api_new_page():
    # Save page and redirect
    r = flask.request

    page_title = r.form.get('page_title', '').strip()
    page_note = r.form.get('page_note', '').strip()
    rev_body = r.form.get('rev_body', '').strip()

    # TODO frontend validation
    if not page_title:
        raise Exception('TitleError: empty title')
    if not rev_body:
        raise Exception('RevisionError: empty revision')

    page = create_page(page_title, page_note)
    rev = Revision()
    rev.body = rev_body
    rev.timestamp = int(time.time())
    page.add_revision(rev)

    return flask.redirect(flask.url_for('view_page', id=page.id))


@flask_app.route('/api/edit/<int:id>', methods=['POST'])
def api_edit_page(id):
    r = flask.request
    page_id = r.form.get('page_id', '')
    page_title = r.form.get('page_title', '').strip()
    page_note = r.form.get('page_note', '').strip()
    rev_body = r.form.get('rev_body', '').strip()

    # TODO Check for changes

    page = get_page(id=id)
    rev = Revision()
    rev.body = rev_body
    rev.timestamp = int(time.time())
    page.add_revision(rev)

    return flask.redirect(flask.url_for('view_page', id=id))


@flask_app.route('/delete/<int:id>')
def api_page_delete(id):
    del_page_by_id(id)
    ctx = {
        'v_title': f'Delete Page {id}',
        'v_message': f'Successful'
    }
    return flask.render_template('redirect.html',  **ctx)


@flask_app.route('/generate')
def api_generate_pages():
    gen_dummy_pages()
    return flask.redirect(flask.url_for('view_homepage'))


flask_app.run()
