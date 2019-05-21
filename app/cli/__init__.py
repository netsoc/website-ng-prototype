import os
import argparse

from .. import app, db
from . import wp_import

def c_dev(_args):
    app.run(host='::', port=os.environ['HTTP_PORT'])

def run():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(required=True, dest='command')

    p_app = subparsers.add_parser('app', help='Run the development server')
    p_app.set_defaults(func=c_dev)

    p_app = subparsers.add_parser('import', help='Import blog posts from WordPress')
    p_app.add_argument('address', help='Address of the MySQL instance hosting WordPress')
    p_app.add_argument('-p', '--port', help='MySQL port', type=int, default=3306)
    p_app.add_argument('database', help='WordPress database name')
    p_app.add_argument('user', help='WordPress database user')
    p_app.set_defaults(func=wp_import.run)

    args = parser.parse_args()
    args.func(args)