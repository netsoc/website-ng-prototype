from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy_utc import UtcDateTime

from . import db

# No such thing as arrays in MySQL - we need a separate table that SQLAlchemy will
# automagically populate / read so we can access a user's posts and a post's author(s)
post_author_association = db.Table('blog_post_authors', db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('blog_posts.id'), nullable=False),
    db.Column('author_id', db.Integer, db.ForeignKey('users.id'), nullable=False)
)
book_author_association = db.Table('book_authors', db.Model.metadata,
    db.Column('book_id', db.Integer, db.ForeignKey('library.id'), nullable=False),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id'), nullable=False)
)

class User(db.Model):
    __tablename__ = 'users'

    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(32), nullable=False)

    posts    = db.relationship('BlogPost', secondary=post_author_association, backref='authors')

    @classmethod
    def find_one(cls, name):
        return cls.query.filter_by(name=name).first()

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id       = db.Column(db.Integer, primary_key=True)
    title    = db.Column(db.Text, nullable=False)
    time     = db.Column(UtcDateTime, nullable=False)
    edited   = db.Column(UtcDateTime, nullable=False)
    markdown = db.Column(LONGTEXT, nullable=True)
    html     = db.Column(LONGTEXT, nullable=False)

    @classmethod
    def find_one(cls, id):
        return cls.query.filter_by(id=id).first()

class BookAuthor(db.Model):
    __tablename__ = 'authors'

    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(64), nullable=False)
    about     = db.Column(LONGTEXT, nullable=True)
    gr_link   = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)

    books     = db.relationship('Book', secondary=book_author_association, backref='authors')

    @classmethod
    def find_one(cls, name):
        return cls.query.filter_by(name=name).first()


class Book(db.Model):
    __tablename__ = 'library'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.Text, nullable=False)
    callnumber  = db.Column(db.String(15), unique=True, nullable=True)
    isbn        = db.Column(db.String(10), unique=True, nullable=True)
    isbn13      = db.Column(db.String(13), unique=True, nullable=False)
    image_url   = db.Column(db.Text, nullable=True)
    publisher   = db.Column(db.String(120), nullable=True)
    description = db.Column(LONGTEXT, nullable=True)
    rating      = db.Column(db.Float, nullable=True)
    num_pages   = db.Column(db.Integer, nullable=True)
    edition     = db.Column(db.String(40), nullable=True)
