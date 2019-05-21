import sys
import os
import argparse

from .. import app, init_tables
from . import wp_import, blog

def c_dev(_args):
    app.run(host='::', port=os.environ['HTTP_PORT'])

def run():
    init_tables()

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(required=True, dest='command')

    p_app = subparsers.add_parser('app', help='Run the development server')
    p_app.set_defaults(func=c_dev)

    p_import = subparsers.add_parser('import', help='Import blog posts from WordPress')
    p_import.add_argument('address', help='Address of the MySQL instance hosting WordPress')
    p_import.add_argument('-p', '--port', help='MySQL port', type=int, default=3306)
    p_import.add_argument('database', help='WordPress database name')
    p_import.add_argument('user', help='WordPress database user')
    p_import.set_defaults(func=wp_import.run)

    p_blog = subparsers.add_parser('blog', help='Manage blog posts')
    blog_sub = p_blog.add_subparsers(dest='blog_command')

    blog_list = blog_sub.add_parser('list', help='List blog posts')
    blog_list.add_argument('-n', '--limit', help='Max number of posts to retrieve (0 for unlimited)', type=int, default=0)
    blog_list.add_argument('-r', '--reverse', help='Reverse the order of blog posts (defaults to newest first)', action='store_true', default=False)
    blog_list.set_defaults(func=blog.list)

    blog_get = blog_sub.add_parser('get', help='Retrieve a blog post by its ID')
    blog_get.add_argument('id', help='Post ID', type=int)
    ex_group = blog_get.add_mutually_exclusive_group()
    ex_group.add_argument('--html', help='Force retrieval of post HTML (defaults to Markdown if available)', action='store_true', default=False)
    ex_group.add_argument('--force-markdown', help='If a post has no Markdown, convert it from HTML (via html2text)', action='store_true', default=False)
    blog_get.set_defaults(func=blog.get)

    args = parser.parse_args()
    sys.exit(args.func(args))
