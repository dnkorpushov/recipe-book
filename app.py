import sqlite3
import fnmatch
import os
from sqlite3.dbapi2 import DateFromTicks

from flask import Flask, redirect
from flask import render_template
from flask import g
from flask.globals import request

import config
import mdproc
import recipedb

app = Flask(__name__)

SITE_TITLE = config.SITE_TITLE

def get_db():

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                    for idx, value in enumerate(row))

    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(config.DATABASE)
    db.row_factory = make_dicts

    return db


def init_db():

    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.teardown_appcontext
def close_connection(exception):

    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():

    page_title = SITE_TITLE
    with app.app_context():
        db = get_db()
        last_recipes = recipedb.get_last_recipes(db, 10)
        tag_list_popular = recipedb.get_taglist_popular(db, 15)

    return render_template('index.html', tag_list_popular=tag_list_popular, 
                            last_recipes=last_recipes, page_title=page_title)


@app.route('/reindex')
def reindex():

    with app.app_context():
        db = get_db()
        recipedb.empty(db)
        for root, dirnames, filenames in os.walk(config.CONTENT_ROOT):
            for filename in fnmatch.filter(filenames, '*.md'):
                if not filename.startswith('__'):
                    mdfile = os.path.join(root, filename)
                    _, meta = mdproc.get_html(mdfile)
                    recipedb.add_recipe(db, mdfile=mdfile, meta=meta)

    return redirect('/')


@app.route('/recipes')
def view_recipelist():
    page_title = 'Список рецептов' + ' | ' + SITE_TITLE
    with app.app_context():
        db = get_db()
        recipe_list = recipedb.get_recipes(db)

    return render_template('recipelist.html', title='Список рецептов', recipe_list=recipe_list,
                            page_title=page_title)    


@app.route('/recipe/<rowid>')
def view_recipe(rowid):
    
    with app.app_context():
        db = get_db()
        mdfile = recipedb.get_recipe(db, rowid)
        html, meta = mdproc.get_display_html(mdfile)
        page_title = meta['title'] + ' | ' + SITE_TITLE
        
    return render_template('recipe.html', recipe=html, page_title=page_title)


@app.route('/tags')
def view_taglist():
    page_title = 'Все метки' + ' | ' + SITE_TITLE
    with app.app_context():
        db = get_db()
        tag_list = recipedb.get_taglist(db)
    
    return render_template('taglist.html', tag_list=tag_list, page_title=page_title)


@app.route('/tag/<tag>', defaults={'title': None})
@app.route('/tag/<tag>/<title>')
def view_tag(tag, title):

    with app.app_context():
        db = get_db()
        recipe_list = recipedb.get_recipes_for_tag(db, tag)
        if title is None:
            title = 'Метка: {}'.format(tag)
        page_title = title + ' | ' + SITE_TITLE
    
    return render_template('recipelist.html', title=title, recipe_list=recipe_list,
                            page_title=page_title)


@app.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'POST':
        search_str = request.form['search']

    with app.app_context():
        db = get_db()
        recipe_list = recipedb.search(db, search_str)
    title = 'Поиск: {}'.format(search_str)
    page_title = title + ' | ' + SITE_TITLE
    
    return render_template('recipelist.html', title=title, recipe_list=recipe_list,
                            page_title=page_title)
