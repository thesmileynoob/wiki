# -*- coding: utf-8 -*-
import os
import shutil
import time
import json

import wasabi
import flask

from wiki.page import *  # TODO only import needed stuff
from wiki.settings import get_setting, Setting, get_setting_values
from wiki.backup import create_backup
from wiki.components import Context, Topbar, Sidebar, Link

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
        page.revcount = len(page.revs)
        check += page.revcount
        num_revs += page.revcount
    abandoned = num_revs - check

    ctx = Context()
    ctx.pages = pages
    ctx.num_pages = len(pages)
    ctx.num_revs = num_revs
    ctx.num_abandoned = abandoned # TODO clean this up

    return flask.render_template('home.html', ctx=ctx)


@flask_app.route('/wiki/<int:pid>')
def view_page(pid):
    page = get_page(pid)
    if not page:
        ctx = Context()
        return flask.render_template('notfound.html', ctx=ctx), 404

    ctx = Context()
    ctx.title = page.title

    ctx.topbar.add_link(Link('Edit', f'/edit/{page.id}'))
    ctx.topbar.add_link(Link('Info', f'/info/{page.id}'))
    ctx.topbar.add_link(Link('Delete', f'/delete/{page.id}'))

    ctx.page = page

    return flask.render_template('page.html', ctx=ctx)


@flask_app.route('/new')
def view_new_page():
    ctx = Context()
    ctx.title = 'New Page'
    ctx.action = '/api/new'

    return flask.render_template('newpage.html', ctx=ctx)


@flask_app.route('/edit/<int:pid>')
def view_edit_page(pid):
    page = get_page(pid)
    if not page:
        ctx = Context()
        ctx.title = 'Not Found: ID=' + str(pid)

        return flask.render_template('notfound.html', ctx=ctx), 404

    ctx = Context()
    ctx.title = f'Edit Page {pid}'
    ctx.action = '/api/edit/' + str(pid)
    ctx.page = page
    
    return flask.render_template('editpage.html', ctx=ctx)


@flask_app.route('/wiki/<title>')
def api_search_page(title: str):
    page = get_page(title=title)
    if page:
        return flask.redirect(flask.url_for('view_page', id=page.id))
    else:
        ctx = Context()
        ctx.title = page.title

        return flask.render_template('notfound.html', ctx=ctx), 404


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

    return flask.redirect(flask.url_for('view_page', pid=page.id))


@flask_app.route('/api/edit/<int:pid>', methods=['POST'])
def api_edit_page(pid):
    r = flask.request
    page_id = r.form.get('page_id', '')
    page_title = r.form.get('page_title', '').strip()
    page_note = r.form.get('page_note', '').strip()
    rev_body = r.form.get('rev_body', '').strip()

    # TODO Check for changes

    page = get_page(pid)
    rev = Revision()
    rev.body = rev_body
    rev.timestamp = int(time.time())
    page.add_revision(rev)

    return flask.redirect(flask.url_for('view_page', pid=pid))


@flask_app.route('/delete/<int:pid>')
def api_page_delete(pid):
    # TODO handle errors!
    del_page_by_id(pid)
    ctx = Context()
    ctx.title = f'Delete Page {pid}'
    ctx.message = 'Successful'

    return flask.render_template('redirect.html',  ctx=ctx)


@flask_app.route('/generate')
def api_generate_pages():
    gen_dummy_pages()
    return flask.redirect(flask.url_for('view_homepage'))


@flask_app.route('/backup')
def api_create_backup():
    ok = create_backup()
    if not ok:
        log.fail('Failed to create backup!')
        msg = 'Failed to create backup!'
    else:
        msg = 'Backup created successfully!'
    ctx = Context()
    ctx.title = 'Backup Created'
    ctx.message = msg

    return flask.render_template('redirect.html', ctx=ctx)


flask_app.run()
