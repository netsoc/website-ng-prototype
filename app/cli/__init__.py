import sys
import os
import argparse

DEFAULT_EDITOR = os.environ.get('EDITOR', 'nano')

class CLIError(Exception):
    pass

from .. import app, init_tables
from . import wp_import, blog

def c_dev(_args):
    app.run(host='::', port=os.environ['HTTP_PORT'])

def run():
    init_tables()

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(required=True, dest='command')

    # Command to run the Flask development server
    p_app = subparsers.add_parser('app', help='Run the development server')
    p_app.set_defaults(func=c_dev)


    # Import command
    p_import = subparsers.add_parser('import', help='Import blog posts from WordPress')
    p_import.add_argument('address', help='Address of the MySQL instance hosting WordPress')
    p_import.add_argument('-p', '--port', help='MySQL port', type=int, default=3306)
    p_import.add_argument('database', help='WordPress database name')
    p_import.add_argument('user', help='WordPress database user')
    p_import.set_defaults(func=wp_import.run)


    # Blog posts command
    p_blog = subparsers.add_parser('posts', help='Manage blog posts')
    p_blog.set_defaults(func=blog.list_simple)
    blog_sub = p_blog.add_subparsers(dest='blog_command')

    # Blog posts list command
    blog_list = blog_sub.add_parser('list', help='List blog posts')
    blog_list.add_argument('-n', '--limit', help='Max number of posts to retrieve (0 for unlimited)', type=int, default=0)
    blog_list.add_argument('-r', '--reverse', help='Reverse the order of blog posts (defaults to newest first)', action='store_true', default=False)
    blog_list.set_defaults(func=blog.list)

    # Blog posts retrieval command
    blog_get = blog_sub.add_parser('get', help='Retrieve a blog post by its ID')
    blog_get.add_argument('id', help='Post ID', type=int)
    ex_group = blog_get.add_mutually_exclusive_group()
    ex_group.add_argument('--html', help='Force retrieval of post HTML (defaults to Markdown if available)', action='store_true', default=False)
    ex_group.add_argument('--force-markdown', help='If a post has no Markdown, convert it from HTML (via html2text)', action='store_true', default=False)
    blog_get.set_defaults(func=blog.get)

    # Blog posts deletion command
    blog_delete = blog_sub.add_parser('delete', help='Delete a blog post by its ID')
    blog_delete.add_argument('id', help='Post ID', type=int)
    blog_delete.set_defaults(func=blog.delete)

    # Blog posts creation command
    blog_new = blog_sub.add_parser('new', help='Create a new blog post')
    blog_new.add_argument('-a', '--authors', help='Post author(s) - pass for each author', action='append', required=True)
    blog_new.add_argument('-e', '--editor', help='Command to run as editor', default=DEFAULT_EDITOR)
    blog_new.add_argument('--html', help='Write HTML directly instead of Markdown', action='store_true', default=False)
    blog_new.add_argument('title', help='Post title')
    blog_new.set_defaults(func=blog.new)

    # Blog posts editing command
    blog_edit = blog_sub.add_parser('edit', help='Edit an existing blog post')
    blog_edit.add_argument('-t', '--title', help='Updated post title')
    blog_edit.add_argument('-a', '--authors', help='Updated post author(s) - replaces existing authors if passed', action='append')
    blog_edit.add_argument('-e', '--editor', help='Command to run as editor', default=DEFAULT_EDITOR)
    ex_group = blog_edit.add_mutually_exclusive_group()
    ex_group.add_argument('--no-content', help='Only edit attributes (e.g. title, authors)', action='store_true', default=False)
    ex_group.add_argument('--html', help='Force editing of post HTML (defaults to Markdown if available), '+
            'WARNING: Passing this option when a Markdown version exists will remove the Markdown version', action='store_true', default=False)
    ex_group.add_argument('--force-markdown', help='If a post has no Markdown, convert it from HTML (via html2text) before editing', action='store_true', default=False)
    blog_edit.add_argument('id', help='Post ID', type=int)
    blog_edit.set_defaults(func=blog.edit)

    args = parser.parse_args()
    sys.exit(args.func(args))
