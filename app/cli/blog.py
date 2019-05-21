import sys

from html2text import html2text

from .. import db
from ..models import BlogPost

def eprint(msg):
    print(msg, file=sys.stderr)
def pretty_authors(post):
    return ', '.join(map(lambda u: u.name, post.authors))
def pretty_time(time):
    return time.strftime('%x at %X %Z')

def list(args):
    query = db.session.query(BlogPost)\
            .order_by(BlogPost.edited.asc() if args.reverse else BlogPost.edited.desc())
    if args.limit != 0:
        query = query.limit(args.limit)

    for post in query:
        print(f'#{post.id}: "{post.title}" by {pretty_authors(post)} (last modified on {pretty_time(post.edited)})')

def get(args):
    post = db.session.query(BlogPost)\
            .filter_by(id=args.id)\
            .first()
    if not post:
        eprint(f'Post #{args.id} not found')
        return 1

    eprint(f'Title: {post.title}')
    eprint(f'Author(s): {pretty_authors(post)}')
    eprint(f'Created: on {pretty_time(post.time)}')
    if post.edited != post.time:
        eprint(f'Last edited: on {pretty_time(post.edited)}')

    if args.html:
        print(post.html)
    elif post.markdown:
        print(post.markdown)
    elif args.force_markdown:
        eprint('Converting HTML to Markdown...')
        print(html2text(post.html))
    else:
        eprint('Warning: Markdown unavailable, showing HTML')
        print(post.html)
