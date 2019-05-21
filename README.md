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

## Blog Posts

### SQL Setup for Blog Posts

Stored in a mysql database in snark-www. The database is/was in netsocwww
in the table news_wp_posts.  
Every text segment on a page in the previous website was stored as a post and is stored in here.

Table is in the form:

| Field                 | Type                | Null | Key | Default | Extra          |
|-----------------------|:---------------------:|------:|-----:|---------------------:|----------------:|
| ID                    | bigint(20) unsigned | NO   | PRI | NULL | auto_increment |
| post\_author           | bigint(20) unsigned | NO   | MUL | 0 |                |
| post\_date             | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post\_date\_gmt         | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post\_content          | longtext            | NO   |     | NULL |                |
| post\_title            | mediumtext          | NO   |     | NULL |                |
| post\_category         | int(4)              | NO   |     | 0 |                |
| post\_excerpt          | mediumtext          | NO   |     | NULL |                |
| post\_status           | varchar(20)         | NO   |     | publish |                |
| comment\_status        | varchar(20)         | NO   |     | open |                |
| ping\_status           | varchar(20)         | NO   |     | open |                |
| post\_password         | varchar(255)        | NO   |     | |                |
| post\_name             | varchar(200)        | NO   | MUL | |                |
| to\_ping               | mediumtext          | NO   |     | NULL |                |
| pinged                | mediumtext          | NO   |     | NULL |                |
| post\_modified         | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post\_modified\_gmt     | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post\_content\_filtered | longtext            | NO   |     | NULL |                |
| post\_parent           | bigint(20) unsigned | NO   | MUL | 0 |                |
| guid                  | varchar(255)        | NO   |     | |                |
| menu\_order            | int(11)             | NO   |     | 0 |                |
| post\_type             | varchar(20)         | NO   | MUL | post |                |
| post\_mime\_type        | varchar(100)        | NO   |     | |                |
| comment\_count         | bigint(20)          | NO   |     | 0 |                |

Posts should be easy to display using sql alchemy and will be displayed on the home page

### Mariadb docker compose setup

Image is mariadb 10.2 as that is/was the setup for snark-www. Service is called 'db' which means when accessing it from flask app the host is 'db'. Data is stored in the volume db\_data which is persistent and will maintain the data in there until volume is destroyed.  
For the app service to access the app must link to db: 
```
links:
  - db
```
Also environment variables for the mysql must be set which are
```
MYSQL_ROOT_PASSWORD
MYSQL_DATABASE
MYSQL_USER
MYSQL_PASSWORD
```
If you want to delete all mysql data in the volume use the command ```docker-compose down --volumes ```

### Flask SQL Setup

[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) is used to query the mariadb database. A class was created for the blog posts tables. The class is BlogPost and has the columns defined above.  
It requires a URI for the database, which is the format ${MYSQL\_USER}@${HOST}:${PORT}/${MYSQL\_DATABASE} 
in this case the HOST is 'db' and PORT is 3306. WHen the application is loaded the URI is generated and connects to database. The flask app will create the blog table if it doesn't exists this table can be queried and inserted into.
