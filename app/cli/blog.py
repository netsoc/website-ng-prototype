from datetime import datetime
import sys
from os import path
import tempfile
import subprocess

from html2text import html2text
import markdown
import tzlocal

from .. import db
from ..models import User, BlogPost
from . import CLIError

timezone = tzlocal.get_localzone()
md = markdown.Markdown(output_format='html5')

def eprint(msg):
    print(msg, file=sys.stderr)
def pretty_authors(post):
    return ', '.join(map(lambda u: u.name, post.authors))
def pretty_time(time):
    return time.strftime('%x at %X %Z')
def find_or_make_users(users):
    obj_users = []
    for name in users:
        u = User.query.filter_by(name=name).first()
        if not u:
            u = User(name=name)
            db.session.add(u)
        obj_users.append(u)
    db.session.commit()
    return obj_users
def get_post(id):
    post = BlogPost.query\
            .filter_by(id=id)\
            .first()
    if not post:
        raise CLIError(f'Post #{id} not found')
    return post

def list(args):
    query = BlogPost.query\
            .order_by(BlogPost.edited.asc() if args.reverse else BlogPost.edited.desc())
    if args.limit != 0:
        query = query.limit(args.limit)

    for post in query:
        print(f'#{post.id}: "{post.title}" by {pretty_authors(post)} (last modified on {pretty_time(post.edited)})')

def get(args):
    post = get_post(args.id)

    eprint(f'Title: {post.title}')
    eprint(f'Author(s): {pretty_authors(post)}')
    eprint(f'Created: on {pretty_time(post.time)}')
    if post.edited != post.time:
        eprint(f'Last edited: on {pretty_time(post.edited)}')

    if args.html:
        content = post.html
    elif post.markdown:
        content = post.markdown
    elif args.force_markdown:
        eprint('Converting HTML to Markdown...')
        content = html2text(post.html)
    else:
        eprint('Warning: Markdown unavailable, showing HTML')
        content = post.html

    print(content)

def delete(args):
    post = get_post(args.id)
    db.session.delete(post)
    db.session.commit()
    print(f'Post #{post.id} deleted')

def new(args):
    extension = '.html' if args.html else '.md'
    with tempfile.NamedTemporaryFile(mode='r', prefix='post-', suffix=extension) as tmp_post:
        ctime = path.getmtime(tmp_post.name)
        # Open the user's editor of choice to type the contents of the post
        subprocess.call([args.editor, tmp_post.name])

        # Will only happen if the user didn't save at all
        if path.getmtime(tmp_post.name) == ctime:
            print('Post cancelled')
            return

        content = tmp_post.read()

    authors = find_or_make_users(args.authors)
    time = datetime.now(tz=timezone)
    post = BlogPost(
        title=args.title,
        time=time,
        edited=time,
        authors=authors,
    )

    if args.html:
        post.html = content
    else:
        post.markdown = content
        post.html = md.convert(content)

    db.session.add(post)
    db.session.commit()
    print(f'Created post #{post.id}')
