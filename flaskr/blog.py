from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename 
import os
from flaskr.auth import login_required
from flaskr.db import get_db
from base64 import b64encode

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

#decorating our create function with login_required which takes a view as input - wrapper is just shortcut to direct to login page if not logged in - two methods listed here
#if we're posting, execute a DB command to post the blog entry; otherwise render the create template
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        if 'file' in request.files:
            file=request.files['file']
            data =file.read()
        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            if file:
                render_file = render_picture(data)
                db.execute(
                    'INSERT INTO post (title, body, author_id, pic)'
                    ' VALUES (?, ?, ?, ?)',
                    (title, body, g.user['id'], render_file))
            else:
                db.execute(
                    'INSERT INTO post (title, body, author_id)'
                    ' VALUES (?, ?, ?)',
                    (title, body, g.user['id']))
            db.commit()
            
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')
#m123
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)
    
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

def render_picture(data):
    render_pic = b64encode(data).decode('ascii') 
    return render_pic

@bp.route('/<int:id>/details', methods=('GET',))
@login_required
def detail(id):
    post = get_post(id)
    return render_template('blog/detail.html', post=post)
