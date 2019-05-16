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
