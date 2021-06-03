
import sqlite3
import fnmatch
import os

import config
import recipedb
import mdproc


def init_db(db):

    with open('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()


def vprint(text, verbose):

    if verbose:
        print(text)


def make_dicts(cursor, row):

    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def reindex(verbose=False):

    need_init = not os.path.exists(config.DATABASE)

    db = sqlite3.connect(config.DATABASE)
    if need_init:
        init_db(db)
    db.row_factory = make_dicts

    vprint('\n\nConnect to \'{}\''.format(config.DATABASE), verbose)
    recipedb.empty(db)
    count = 0

    for root, dirnames, filenames in os.walk(config.CONTENT_ROOT):
        for filename in fnmatch.filter(filenames, '*.md'):
            if not filename.startswith('__'):
                mdfile = os.path.join(root, filename)
                vprint('Add \'{}\''.format(mdfile), verbose)
                _, meta = mdproc.get_html(mdfile)
                recipedb.add_recipe(db, mdfile=mdfile, meta=meta)
                count += 1
    db.close()
    vprint('\nTotal: {}\n\n'.format(count), verbose)


if __name__ == '__main__':
    reindex(verbose=True)
