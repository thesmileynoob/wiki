# -*- coding: utf-8 -*-
import os
import time
import json

import wasabi
import flask

from sqlalchemy.orm.exc import NoResultFound

from wiki.models import Page, Revision, TodoItem, TodoList
from wiki.page import *

log = wasabi.Printer()
flask_app = flask.Flask('Wiki')
flask_app.config['DEBUG'] = True


@flask_app.route('/')
def homepage_view():
    ctx = get_all_pages()
    # TODO Generate context here itself
    return flask.render_template('home.html', **ctx)


@flask_app.route('/wiki/<title>')
def page_view(title):
    ctx = get_page_by_title(title)
    return flask.render_template('page.html', **ctx)


@flask_app.route('/delete/<int:id>')
def page_delete(id):
    ctx = del_page_by_id(id)
    return flask.render_template('redirect.html',  **ctx)


def todo_get():
    # return json string response for todos
    with new_session() as sess:
        # return string json representation
        todo_items = sess.query(TodoItem).all()
        todo_lists = sess.query(TodoList).all()

        result = {
            'lists': [],
            'items': []
        }

        for item in todo_items:
            result['items'].append({
                'id': item.id,
                'list_id': item.list_id,
                'content': item.content,
                'timestamp': item.timestamp
            })
        for item in todo_lists:
            result['lists'].append({
                'id': item.id,
                'title': item.title,
                'timestamp': item.timestamp,
            })
    return json.dumps(result)


@flask_app.route('/todo', methods=['GET', 'POST'])
def todo_view():
    with new_session() as sess:
        todo_lists = sess.query(TodoList).all()
        todo_items = sess.query(TodoItem).all()

    # ['list1']
    ctx = {
        'todo_lists': todo_lists,
        'todo_items': todo_items
    }

    todo_items = []

    req = flask.request
    if req.method == 'POST':
        # return status json response
        item = req.form.get('title')
        # create item
        # if ok, update context
    elif req.method == 'DELETE':
        # TODO impl
        pass
    else:
        raise NotImplementedError
    return flask.render_template('todo.html', **ctx)


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

        create_new_page(page_title, page_note, rev_content)

        return flask.redirect(
            flask.url_for('page_view', title=Page.format_title(page_title)))


@flask_app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_page_view(id):
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
            flask.url_for('page_view', title=Page.format_title(page_title)))


@flask_app.route('/generate')
def generate_pages():
    gen_dummy_pages()
    return flask.redirect(flask.url_for('homepage_view'))


flask_app.run()
