# New-Netsoc-Website
New Netsoc website to be built using [Flask](http://flask.pocoo.org/)

## Development with Docker Compose
1. Install [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/)
2. Create a `.env` file, for example:
```
FLASK_ENV=development
FLASK_SECRET=hunter2
PUBLIC_HOST=localhost
HTTP_PORT=8080
MYSQL_DATA=./data
MYSQL_ROOT_PASSWORD=test 
MYSQL_DATABASE=netsocwww 
MYSQL_USER=netsoc 
MYSQL_PASSWORD=website
TZ=Europe/Dublin
GR_KEY=<your goodreads key *only required for generating books>
GR_SECRET=<your goodreads secret>
```
3. Run `docker-compose up`
4. Server should be accessible from http://localhost:8080, hot reload should also work

## MariaDB Docker Compose setup
Image is MariaDB 10.x. Service is called 'db' which means when accessing it from Flask the host is 'db'. Data is stored in the specified `MYSQL_DATA` directory on the host.

## Flask SQL Setup
[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) is used to query the database.

## Blog Posts

### Old WordPress blog posts
Stored in a MySQL database on `snark-www`. The database is/was `netsocwww`.
in the table news_wp_posts.
Every text segment on a page in the previous website was stored as a post and is stored in here.
See [`here`](https://codex.wordpress.org/Database_Description) for the schema.

Posts should be easy to display using SQLAlchemy and will be displayed on the home page.

### New blog post schema
See [`app/models.py`](app/models.py).

## Library

### Book schema
See [`app/models.py`](app/models.py).

### Adding Books
The `new` command allows for 3 options: single, list and manual add.
The first 2 options take an ISBN and auto generate the data from the Goodreads api, and get the ddc from [http://classify.oclc.org/classify2/](http://classify.oclc.org/classify2/).

### Goodreads Api
For "details" and keys see [Goodreads api](https://www.goodreads.com/api).

The python wrapper is technically outdated ... see [gooreads pypi](https://pypi.org/project/Goodreads/)


## CLI
The website is effectively read-only. To make changes (e.g. CRUD blog posts), use the CLI:
```bash
docker exec <app container name> website <command>
```
for edit commands run `docker exec -ti <app container name> website -e <editor of choice> books edit 9780201619188`

### Importing current posts from WordPress for development
To get some test posts, you can import the current website's posts to your local database.
First, you'll need to dump the DB from `snark-www`:
1. SSH into snark from cube
2. Run `mysqldump netsocwww > wordpress.sql`
3. Start the app locally (i.e. `docker-compose up`)
4. Copy the dump into your local DB container by running `docker cp wordpress.sql New-Netsoc-Website_db_1:/wordpress.sql`
5. Get a shell in your DB container by doing `docker exec -ti New-Netsoc-Website_db_1 /bin/bash`
6. Create a database for the old data using the `mysql` prompt (and your password)
7. Import the data by running `mysql -p<password> <your database name> < /wordpress.sql`
8. Convert the data to the new format (readable by the app) using the CLI - exit from the DB shell and run `docker exec -ti New-Netsoc-Website_app_1 website import db <your database name> root`

### Managing the Library
Adding books (example list) 
```bash
docker exec -ti <app container name> website books new -l
isbn-1
isbn-2
...
<Ctrl-d>
```

