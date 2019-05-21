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
See `[here](https://codex.wordpress.org/Database_Description)` for the schema.

Posts should be easy to display using SQLAlchemy and will be displayed on the home page.

### New blog post schema
See `[app/models.py](app/models.py)`.

## CLI
The website is effectively read-only. To make changes (e.g. CRUD blog posts), use the CLI:
```bash
docker exec <app container name> website <command>
```
