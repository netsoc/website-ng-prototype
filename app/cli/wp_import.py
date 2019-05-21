from getpass import getpass

import sqlalchemy as sql
import sqlalchemy.orm as orm
from sqlalchemy.dialects.mysql import INTEGER, BIGINT, LONGTEXT, MEDIUMTEXT, VARCHAR
from sqlalchemy_utc import UtcDateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
import flask

from .. import db
from ..models import User, BlogPost

WpBase = declarative_base()

# WordPress schemas so we can pull the posts for conversion (see https://codex.wordpress.org/Database_Description)
# User is needed so we can get the username
class WordPressUser(WpBase):
    __tablename__ = 'news_wp_users'

    id                    = sql.Column(BIGINT(20, unsigned=True), primary_key=True)
    user_login            = sql.Column(VARCHAR(60))
    user_pass             = sql.Column(VARCHAR(64))
    user_nicename         = sql.Column(VARCHAR(50))
    user_email            = sql.Column(VARCHAR(100))
    user_url              = sql.Column(VARCHAR(100))
    user_registered       = sql.Column(UtcDateTime)
    user_activation_key   = sql.Column(VARCHAR(60))
    user_status           = sql.Column(INTEGER(11))
    display_name          = sql.Column(VARCHAR(250))

class WordPressPost(WpBase):
    __tablename__ = 'news_wp_posts'

    id                    = sql.Column(BIGINT(unsigned=True), primary_key=True)
    post_author           = sql.Column(BIGINT(unsigned=True), sql.ForeignKey('news_wp_users.id'), nullable=False)
    post_date             = sql.Column(UtcDateTime, unique=False, nullable=False)
    post_date_gmt         = sql.Column(UtcDateTime, unique=False, nullable=False)
    post_content          = sql.Column(LONGTEXT, unique=False, nullable=False)
    post_title            = sql.Column(MEDIUMTEXT, nullable=False)
    post_category         = sql.Column(sql.Integer)
    post_excerpt          = sql.Column(MEDIUMTEXT)
    post_status           = sql.Column(VARCHAR(20))
    comment_status        = sql.Column(VARCHAR(20))
    ping_status           = sql.Column(VARCHAR(20))
    post_password         = sql.Column(VARCHAR(255))
    post_name             = sql.Column(VARCHAR(200), unique=False)
    to_ping               = sql.Column(MEDIUMTEXT)
    pinged                = sql.Column(MEDIUMTEXT)
    post_modified         = sql.Column(UtcDateTime)
    post_modified_gmt     = sql.Column(UtcDateTime)
    post_content_filtered = sql.Column(LONGTEXT)
    post_parent           = sql.Column(BIGINT(unsigned=True))
    guid                  = sql.Column(VARCHAR(255))
    menu_order            = sql.Column(sql.Integer)
    post_type             = sql.Column(VARCHAR(20))
    post_mime_type        = sql.Column(VARCHAR(100))
    comment_count         = sql.Column(BIGINT)

    # Not a column, but a relation to conveniently access the author
    post_user             = orm.relationship('WordPressUser')

def run(args):
    password = getpass(f'Password for {args.user}@{args.address}: ')
    wp_engine = sql.create_engine(URL(
        drivername='mysql+mysqlconnector',
        username=args.user,
        password=password,
        host=args.address,
        port=args.port,
        database=args.database,
        # Make sure we're using 4-byte UTF-8 for the MySQL connection
        query={'charset': 'utf8mb4'},
    ))

    WPSession = orm.sessionmaker(bind=wp_engine)
    wp_session = WPSession()
    for wp_post in wp_session.query(WordPressPost)\
            .filter_by(post_type='post', post_status='publish'):
            # ^^ Everything in WordPress is a goddamn post, we only want
            # published (https://wordpress.org/support/article/post-status/#publish)
            # blog posts (https://wordpress.org/support/article/post-types/#posts)
        # Import the unescaped title (some _very_ old posts have stuff like &amp;)
        wp_post.post_title = flask.Markup(wp_post.post_title).unescape()

        print(f'Importing "{wp_post.post_title}" by {wp_post.post_user.user_login} ({wp_post.post_date})...')
        author = User.query.filter_by(name=wp_post.post_user.user_login).first()
        if not author:
            print(f'Creating new user "{wp_post.post_user.user_login}"')
            author = User(name=wp_post.post_user.user_login)
            db.session.add(author)

        # Create a native (to this app) post from the WordPress one
        db.session.add(BlogPost(
            title=wp_post.post_title,
            authors=[author],
            time=wp_post.post_date,
            edited=wp_post.post_modified,
            html=wp_post.post_content
        ))
        db.session.commit()
