from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug import secure_filename

from squeaker.auth import login_required
from squeaker.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def main():
	db=get_db()
	return render_template('blog/main.html')

@bp.route('/posts')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, attach, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
	
    reacts = db.execute(
        'SELECT r.id, react, created, author_id, username, post_id'
        ' FROM replies r JOIN user u ON r.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    """
    likes = db.execute(
		'SELECT l.id, liked, numlikes, author_id, post_id'
		'FROM postlikes l JOIN user u ON l.author_id = u.id'
	).fetchall()
    """
    return render_template('blog/index.html', posts=posts, reacts=reacts)
'''
class likes ():
    def liked():
    def unlike():
    def like():
'''
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        error = None
        title = request.form['title']
        body = request.form['body']
        attach = request.files['file']
        attach.save(secure_filename(attach.filename))
        

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, attach)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], attach)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')
	
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

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
	
	
	

@bp.route('/<int:id>/react', methods=('GET', 'POST'))
@login_required
def reaction(id):

    if request.method == 'POST':
        react = request.form['react']
        error = None


        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO replies (react, author_id, post_id)'
                ' VALUES (?, ?, ?)',
                (react, g.user['id'], id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
			
    return render_template('blog/reaction.html', post_id=id)
	
@bp.route('/account')	
def account():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/account.html', posts=posts)

@bp.route('/about')	
def about():
	db = get_db();
	abouts = db.execute(
        'SELECT p.id, abouts, author_id, created, username'
        ' FROM aboutuser p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
	
	return render_template('blog/about.html', abouts=abouts)
		
@bp.route('/aboutcreate', methods=('GET', 'POST'))
def about_create():

    if request.method == 'POST':
        about = request.form['about']
        error = None


        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO aboutuser(abouts, author_id)'
                'VALUES(?, ?)',
				(about, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.about'))
			
    return render_template('blog/about_create.html')

	
def return_home(id):
	return redirect(url_for('blog.index'))