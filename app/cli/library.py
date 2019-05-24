import sys
from . import CLIError
from os import environ
from goodreads import client

from .. import db, pretty_authors
from ..models import BookAuthor, Book

def eprint(msg):
    print(msg, file=sys.stderr)
def find_or_make_authors(authors):
    obj_authors = []
    for author in authors:
        a = BookAuthor.find_one(author.name)
        if not a:
            a = BookAuthor(name=author.name)
            db.session.add(a)
        obj_authors.append(a)
    db.session.commit()
    return obj_authors
def get_book(id):
    book = Book.query.filter_by(id=id).first()
    if not book:
        raise CLIError(f'Book #{id} not found')
    return book

def list(args):
    query = Book.query\
            .order_by(Book.id.asc() if args.reverse else Book.id.desc())
    if args.limit != 0:
        query = query.limit(args.limit)

    for book in query:
        print(f'#{book.id}: "{book.title}" by {pretty_authors(book)} isbn: {book.isbn13}')

def list_simple(args):
    args.limit = 10
    args.reverse = False
    list(args)

def delete(args):
    book = get_book(args.id)
    db.session.delete(book)
    db.session.commit()
    eprint(f'Book #{book.id} deleted')

def get_callnum(isbn):
    """TODO implement properly"""
    base = 'http://classify.oclc.org/classify2/Classify?'
    summaryBase = '&summary=true'
    parmType = "isbn"
    return "XXX-XXX"

def goodread_cl():
    api_key = environ['GR_KEY']
    api_secret = environ['GR_SECRET']
    return client.GoodreadsClient(api_key, api_secret)

def new(args):
    # TODO add error checking
    gc = goodread_cl()
    print(args)

    book = gc.book(isbn=args.isbn13)
    cn = get_callnum(args.isbn13)

    authors = find_or_make_authors(book.authors)

    db_book = Book(
        title=book.title,
        callnumber=cn,
        isbn13=args.isbn13,
        image_url=book.image_url,
        publisher=book.publisher,
        description=book.description,
        rating=book.average_rating,
        num_pages=book.num_pages,
        edition=book.edition_information,
        authors=authors,
    )

    db.session.add(db_book)
    db.session.commit()
    eprint(f'Created book #{db_book.id}')
    eprint(db_book)
