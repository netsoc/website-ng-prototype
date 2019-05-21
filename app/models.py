from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy_utc import UtcDateTime

from . import db

post_author_association = db.Table('blog_post_authors', db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('blog_posts.id'), nullable=False),
    db.Column('author_id', db.Integer, db.ForeignKey('users.id'), nullable=False)
)

class User(db.Model):
    __tablename__ = 'users'

    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(32), nullable=False)

    posts    = db.relationship('BlogPost', secondary=post_author_association, backref='authors')

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id       = db.Column(db.Integer, primary_key=True)
    title    = db.Column(db.Text, nullable=False)
    time     = db.Column(UtcDateTime, nullable=False)
    edited   = db.Column(UtcDateTime, nullable=False)
    markdown = db.Column(LONGTEXT, nullable=True)
    html     = db.Column(LONGTEXT, nullable=False)
