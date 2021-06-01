import mdproc
import os


def get_recipes_for_tag(db, tag):

    cur = db.cursor().execute('select rowid, title from recipe_fts where rowid in (select distinct recipe_id from tag where tag=?) order by title', (tag,))
    rv = cur.fetchall()
    return rv


def get_recipes(db):

    cur = db.cursor().execute('select rowid, title from recipe_fts order by title')
    rv = cur.fetchall()
    return rv


def get_last_recipes(db, limit=10):

    cur = db.cursor().execute('select rowid, title from recipe_fts order by created desc limit ?', (limit,))
    rv = cur.fetchall()
    return rv


def get_recipe(db, rowid):

    mdfile = None
    cur = db.cursor().execute('select mdfile from recipe_fts where rowid=?', (rowid,))
    rv = cur.fetchall()
    if len(rv) > 0:
        mdfile = rv[0]['mdfile']
    return mdfile


def get_taglist_popular(db, limit=10):

    cur = db.cursor().execute('select tag, qty from (select tag, count(1) as qty from tag group by tag order by 2 DESC limit ?) order by 1', (limit,))
    rv = cur.fetchall()
    return rv


def get_taglist(db):

    cur = db.cursor().execute('select tag, count(1) as qty from tag group by tag order by tag')
    rv = cur.fetchall()
    return rv


def add_recipe(db, mdfile, meta):

    cur = db.cursor()
    text, _ = mdproc.get_text(mdfile)
    created = os.path.getctime(mdfile)

    cur.execute('insert into recipe_fts (title, tags, content, mdfile, created) values(?,?,?,?, ?)', 
                        (meta['title'],  ', '.join(meta['tags']).lower(), text, mdfile, created))
    rowid = cur.lastrowid
    for tag in meta['tags']:
        cur.execute('select count(1) as qty from tag where tag=? and recipe_id=?', (tag.lower(), rowid,))
        rv = cur.fetchall()
        if rv[0]['qty'] == 0:
            cur.execute('insert into tag values (?, ?)', (tag, rowid, ))

    db.commit()


def search(db, search_str):

    cur = db.cursor()
    cur.execute('select rowid, title from recipe_fts where recipe_fts match ? order by rank', 
                (search_str,))
    rv = cur.fetchall()
    return rv


def empty(db):

    db.cursor().execute('delete from tag')
    db.cursor().execute('delete from recipe_fts')
    db.commit()
