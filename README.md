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
```
3. Run `docker-compose up`
4. Server should be accessible from http://localhost:8080, hot reload should also work

## Blog Posts

### SQL Setup for Blog Posts

Stored in a mysql database in snark-www. The database is/was in netsocwww
in the table news_wp_posts.  
Every text segment on a page in the previous website was stored as a post and is stored in here.

Table is in the form:

| Field                 | Type                | Null | Key | Default | Extra          |
|-----------------------|:---------------------:|------:|-----:|---------------------:|----------------:|
| ID                    | bigint(20) unsigned | NO   | PRI | NULL | auto_increment |
| post_author           | bigint(20) unsigned | NO   | MUL | 0 |                |
| post_date             | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post_date_gmt         | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post_content          | longtext            | NO   |     | NULL |                |
| post_title            | mediumtext          | NO   |     | NULL |                |
| post_category         | int(4)              | NO   |     | 0 |                |
| post_excerpt          | mediumtext          | NO   |     | NULL |                |
| post_status           | varchar(20)         | NO   |     | publish |                |
| comment_status        | varchar(20)         | NO   |     | open |                |
| ping_status           | varchar(20)         | NO   |     | open |                |
| post_password         | varchar(255)        | NO   |     | |                |
| post_name             | varchar(200)        | NO   | MUL | |                |
| to_ping               | mediumtext          | NO   |     | NULL |                |
| pinged                | mediumtext          | NO   |     | NULL |                |
| post_modified         | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post_modified_gmt     | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post_content_filtered | longtext            | NO   |     | NULL |                |
| post_parent           | bigint(20) unsigned | NO   | MUL | 0 |                |
| guid                  | varchar(255)        | NO   |     | |                |
| menu_order            | int(11)             | NO   |     | 0 |                |
| post_type             | varchar(20)         | NO   | MUL | post |                |
| post_mime_type        | varchar(100)        | NO   |     | |                |
| comment_count         | bigint(20)          | NO   |     | 0 |                |

Posts should be easy to display using sql alchemy and will be displayed on the home page