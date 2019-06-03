import json
import requests
import subprocess
import sys
import tempfile

from bs4 import BeautifulSoup
from difflib import get_close_matches
from goodreads import client
from goodreads.request import GoodreadsRequestException
from os import environ
from requests.adapters import HTTPAdapter
from sqlalchemy import or_
from tqdm import tqdm
from urllib3.util.retry import Retry
from xml.etree import ElementTree as ET

from . import CLIError
from .. import db, pretty_authors
from ..models import BookAuthor, Book, BookTypes

# Goodreads Client setup
api_key = environ['GR_KEY']
api_secret = environ['GR_SECRET']
gc = client.GoodreadsClient(api_key, api_secret)

reqs = requests.Session()
reqs.mount = HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5))

def table_keys(table):
    return [key for key in table.__dict__.keys() if key[0]!='_' and key!='id']

def eprint(msg):
    tqdm.write(msg, file=sys.stderr)

# author is of type: list of dict
def find_or_make_authors(authors):
    obj_authors = []
    for author in authors:
        name = author.get('name', None)
        print(name)
        a = BookAuthor.find_one(name)
        if not a:
            # try to get data from GoodreadsClient
            # gr_a = gc.find_author(name)
            # author = gr_a._author_dict if gr_a else author
            print(author.get('name',None))
            a = BookAuthor(
                name=author.get('name',None),
                gr_link=author.get('link',None) or author.get('gr_link',None),
            )
            db.session.add(a)
        obj_authors.append(a)
    db.session.commit()
    return obj_authors

def get_book(id):
    book = Book.query.filter(or_(
        Book.id == id,
        Book.isbn == id,
        Book.isbn13 == id)
    ).first()

    if not book:
        raise CLIError(f'Book #{id} not found')
    return book

def list(args):
    query = Book.query\
            .order_by(Book.id.asc() if args.reverse else Book.id.desc())
    if args.limit != 0:
        query = query.limit(args.limit)
    for book in query:
        print(f'#{book.id}: "{book.title}"')# by {pretty_authors(book)} isbn: {book.isbn}')

def list_simple(args):
    args.limit = 10
    args.reverse = False
    list(args)

def delete(args):
    book = get_book(id=args.id)
    db.session.delete(book)
    db.session.commit()
    eprint(f'Book #{book.id} deleted')

def get(args):
    try:
        book = get_book(args.id)
        print(
            f"   #{book.id:<3} \"{book.title}\"\n\tby {pretty_authors(book)}"\
            f"\n\t{book.callnumber} :: {book.isbn13}//{book.isbn}"\
            f"\n\t{book.image_url}"\
            f"\n\t{book.publisher}"\
            f"\n\ttype: {book.type}"\
            f"\n\tHas description: {book.description!=None}"
        )
        print(book.publisher)
    except Exception as e:
        print(f'> ERROR: {e} ')

def edit(args):
    try:
        book = get_book(args.id)
        book_dict = {key:book.__dict__[key] for key in table_keys(book)}
        updated_book = edit_loop(book_dict, args.editor)
        books = Book.query.filter(Book.id==book.id).update(updated_book)
        db.session.commit()
        eprint(' > Updated {books}')

    except Exception as e:
        print(f'> ERROR: {e} ')

def edit_loop(book_dict, editor):
    with tempfile.NamedTemporaryFile(mode='r+', prefix='book-', suffix='.json') as tmp_book:
        # Write book fields to file
        json.dump(book_dict, tmp_book, indent=4)
        tmp_book.flush()
        conf = 'e'

        while(conf in 'Ee'):
            try:
                # Open the editor to edit the book
                subprocess.call([editor, tmp_book.name])
                # Rewind to the start of the file to read the modified contents
                tmp_book.seek(0,0)
                # Read data into JSON
                book_dict = json.load(tmp_book)

                # Confirm edit
                print(json.dumps(book_dict, indent=4))
                conf = input("Confirm book data (y) edit (e) or cancel: ")

            except Exception as e:
                print(f'> ERROR: {e} ')
                conf = input("Confirm book data (y) edit (e) or cancel: ")

        if not conf in 'yY':
            raise CLIError('editing canceled')
        return book_dict

def new(args):
    if args.manual: return manual_add(args)

    msgs, isbns = [], []
    if args.list: isbns = sys.stdin.read().splitlines()
    elif args.single: isbns = [args.single]

    for isbn in tqdm(isbns): #TODO tqdm?
        if Book.query.filter((Book.isbn==isbn) | (Book.isbn13==isbn)).first():
            eprint(f'{isbn}\t> ISBN already in db')
        else:
            msgs.append(generate_book(isbn, args.type, verbose=args.verbose))
    msgs = sorted(msgs, key=lambda m: m['status'])
    eprint("\n".join(map(lambda m: f"{m['isbn']}\t{m['status']}", msgs)))

def remove_empty_vals(d):
    return {key:d[key] for key in d if not d[key] in ('',None)}

from sqlalchemy import inspect

def manual_add(args):
    try:
        book_dict = {}
        for col in inspect(db.engine).get_columns('library'):
            if col['name']!='id':
                book_dict[col['name']] = '' if col['nullable'] else 'Required'
        book_dict['authors'] = [{'name': 'add more objects for more authors'}]

        book = edit_loop(book_dict, args.editor)

        authors = find_or_make_authors(book['authors'])
        book['authors'] = ''

        db_book = Book(**remove_empty_vals(book))
        db_book.authors = authors

        db.session.add(db_book)
        db.session.commit()
        print(f'> ADDED as #{db_book.id} ')
    except Exception as e:
        print(f'> ERROR: {e}')

def _get_xml(paramValue, paramType='isbn', verbose=False):
    """Classify docs: http://classify.oclc.org/classify2/api_docs/index.html """
    base = 'http://classify.oclc.org/classify2/Classify?'

    params = {paramType:paramValue.encode('utf-8'),'summary':True}
    r = reqs.get(base, params=params)
    if verbose: print(r.url)
    xdoc = ET.fromstring(r.text)
    return xdoc

def _get_closest_index(match, choices):
    return choices.index(get_close_matches(match, choices, n=1)[0])

def get_ddc(isbn, book, verbose=False):
    ddc = None
    try:
        # Get xml + namesapce + code
        xdoc = _get_xml(isbn, verbose=verbose)
        ns = xdoc.tag.split('}')[0]+'}'
        respCode = xdoc.find(f'.//{ns}response').get('code')

        # Multiwork response - automatically select work based on title
        if respCode =='4':
            works = xdoc.findall(f'.//{ns}work')
            # Automatically select right book
            num = _get_closest_index(book.title, [x.get('title') for x in works])

            if verbose:
                eprint('Multiple Works: ')
                eprint('\n'.join([f'{i}) {w.get("title")}' for i,w in enumerate(works)]))
                eprint(f'Goodreads Title: {book.title}')
                eprint(f'Automatically selected {num}')

            # Get single work response
            xdoc = _get_xml(works[num].get('owi'), 'owi')
            respCode = xdoc.find(f'.//{ns}response').get('code')

        # single work response
        if respCode == '0' or respCode == '2':
            ddc = xdoc.find(f'.//{ns}recommendations/{ns}ddc/{ns}mostPopular').get('sfa')
        return ddc
    except Exception as e:
        return ddc

def generate_book(isbn, b_type, verbose=False):
    status = ''
    try:
        book = gc.book(isbn=isbn)
        if verbose:
            print(json.dumps(book._book_dict['authors'], indent=4))
        authors = find_or_make_authors([a._author_dict for a in book.authors])

        ddc = get_ddc(isbn, book, verbose=verbose)
        if not ddc:
            status += ' (2 No DDC)'
            ddc = 'XXX.XX'
        base_cn = ddc[:7] +' '+ book.authors[0].name.split()[-1][:3].upper()
        cn = base_cn
        i = 1
        while Book.query.filter_by(callnumber=cn).first():
            cn = base_cn + f' ({i})'
            i += 1

        # Select image
        image_url = book.image_url
        if 'nophoto' in book.image_url:
            r = reqs.get(book.link)
            soup = BeautifulSoup(r.text, 'html.parser')
            img = soup.find(id='coverImage')
            if img:
                image_url = img.get('src')
            else:
                status += ' (1 No IMG)'

        db_book = Book(
            title=book.title,
            callnumber=cn,
            isbn=book.isbn,
            isbn13=book.isbn13,
            # TODO update image search
            image_url=image_url,
            publisher=book.publisher,
            description=book.description,
            rating=book.average_rating,
            num_pages=book.num_pages,
            authors=authors,
            type=b_type,
        )

        db.session.add(db_book)

        try:
            db.session.commit()
            status = f'> ADDED as #{db_book.id} ' + status
        except Exception as e:
            db.session.rollback()
            status = f'> COMMIT FAILURE: {e} '

    # GoodreadsRequestException
    except Exception as e:
        if isinstance(e, GoodreadsRequestException):
            e = ' '.join(e.__str__())
        status = f'> FAILURE: {e}'
    finally:
        return {'isbn':isbn, 'status': status}

def drop(args):
    db.metadata.drop_all(db.engine)
