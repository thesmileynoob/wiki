# -*- coding: utf-8 -*-
import wasabi
import flask
import jinja2

from wiki import settings
from wiki import page

log = wasabi.Printer()
flask_app = flask.Flask('Wiki')
jenv = jinja2.Environment(
    loader=jinja2.PackageLoader(__name__, settings.TEMPLATE_DIR),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)


@flask_app.route('/')
def homepage():
    template = jenv.get_template('homepage.html')
    return template.render(title='Lorem Ipsum', name='akshay')


@flask_app.route('/todo')
def todo():
    template = jenv.get_template('todo.html')
    return template.render()


@flask_app.route('/settings')
def settings():
    template = jenv.get_template('settings.html')
    return template.render()


flask_app.run()
