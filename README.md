# CAPLCLimat - Back End
## Introduction
Project holding the back-end implementation of CAPLC.

## Setup

### Setup code
Create organisation directory
```shell script
mkdir CAPLClimat
cd CAPLClimat
```

Set up virtualenv
(Using pyenv here)
```shell script
pyenv install 3.8.1
pyenv virtualenv 3.8.1 CAPLCLimat
pyenv local CAPLCLimat
```

Clone back-end Git repository
```shell script
git clone git@github.com:CAPLClimat/back-end.git
cd back-end
```

Install requirements
```shell script
pip install -r requirements.txt
```

Install pre-commit
```shell script
pre-commit install
```

## Setting up PostgreSQL
I recommend install PostgreSQL using Docker as this [article](https://medium.com/hackernoon/dont-install-postgres-docker-pull-postgres-bee20e200198) suggest.

Install [Docker](https://www.docker.com/get-started)

Start PostgreSQL container
```shell script
docker run --rm  --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data  postgres:9.6
```

After that, you should be able to access PostgreSQL shell
```shell script
$ psql -h localhost -U postgres -d postgres
Password for user postgres:
psql (10.12 (Ubuntu 10.12-0ubuntu0.18.04.1), server 9.6.16)
Type "help" for help.

postgres=#
```
A password will be asked, used the one defined in variable POSTGRES_PASSWORD when you ran the docker. (here it is `docker`)

Setting up DBs
```postgresql
CREATE DATABASE caplc_db; -- Development DB
CREATE DATABASE test_caplc_db; -- Testing DB

ALTER ROLE user_test WITH PASSWORD 'password' LOGIN;

GRANT ALL PRIVILEGES ON DATABASE caplc_db TO user_test;
GRANT ALL PRIVILEGES ON DATABASE test_caplc_db TO user_test;

-- If needed
ALTER USER user_test CREATEDB;
```

With this, the app should be able to access the DB using the following URIs
```python
SQLALCHEMY_DATABASE_URI = "postgresql://user_test:password@localhost:5432/caplc_db"
SQLALCHEMY_DATABASE_URI = "postgresql://user_test:password@localhost:5432/test_caplc_db"
```
They are currently hardcoded in the config file. Need to move that to env file.

## Running the server
In development
```shell script
$ python manage.py run
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 118-492-186


```

Testing if it's running
```shell script
$ curl 127.0.0.1:5000/api/ping
{
  "data": "pong"
}
```

Adding an admin
```shell script
$ python manage.py shell
>>> import json
>>> from app.services.user_services import create_admin_user
>>> data = {"email": "admin@test.com", "password":"password", "first_name": "First name", "last_name": "Last Name"}
>>> create_admin_user(json.dumps(data))
```
