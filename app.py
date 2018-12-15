# -*- coding: utf-8 -*-
import wasabi
import flask
import jinja2



TEMPLATE_DIR = 'static/templates'

log = wasabi.Printer()
# TODO Change __name__ used in flask and jenv
flask_app = flask.Flask(__name__)

# jinja2 Environment
# TODO Change __name__ used in flask and jenv
jenv = jinja2.Environment(
    loader=jinja2.PackageLoader(__name__, TEMPLATE_DIR),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

# routes

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
