from sqlalchemy.dialects.mysql import LONGTEXT

from . import db

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    authors = db.Column(db.ARRAY(db.String(32)), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    edited = db.Column(db.DateTime, nullable=False)
    markdown = db.Column(LONGTEXT, nullable=True)
    html = db.Column(LONGTEXT, nullable=False)
