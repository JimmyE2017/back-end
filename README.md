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

## Setting up Mongo
Install [Docker](https://www.docker.com/get-started)
Install [Docker Compose](https://docs.docker.com/compose/install/)

Start Mongo container
```shell script
docker-compose -f docker/docker-compose.yml up --build -d
```

After that, you should be able to access Mongo shell through docker by
```shell script
$ docker exec -it mongo_caplc mongo mongodb://caplc_user:password123@127.0.0.1:27017/caplc
```

FYI, DBs should be already set up by file `docker/mongo-init.js`

With this, the app should be able to access the DB using the following configs
```python
MONGODB_SETTINGS = {"db": "caplc", "host": "mongodb://caplc_user:password123@127.0.0.1:27017"}
MONGODB_SETTINGS = {"db": "caplc_test", "host": "mongodb://caplc_user:password123@127.0.0.1:27017"}
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

Adding an admin (Can only be done through shell currently)
```shell script
$ python manage.py shell
>>> import json
>>> from app.services.user_services import create_admin_user
>>> data = {"email": "admin@test.com", "password":"password", "firstName": "First name", "lastName": "Last Name"}
>>> create_admin_user(json.dumps(data))
```

## Contributing
### Project architecture
```text
.
├── app/
│   ├── api/
│   │   └── v1/
│   ├── common/
│   │   ├── access_level.py
│   │   ├── errors.py
│   ├── config.py
│   ├── extensions.py
│   ├── __init__.py
│   ├── models/
│   ├── services/
│   └── urls.py
├── manage.py
├── migrations/
├── scripts/
└── tests
```

Folders :
- `app/api/` holds all the `Ressource` object from flask-restful. (Basically the endpoints we define)
- `app/common/` holds methods and variables that are shared among all services
- `app/models/` holds the MongoEngine models linked to the tables in DB
- `app/services/` holds the logics of the code.
- `app/schemas/` holds the marshmallow's schema that validates the data received by the API
- `tests/` holds all the tests files

Files :
- `app/urls.py` defines the pattern of the urls linked to our endpoints
- `app/config.py` defines the config of the app
- `app/__init__.py` holds the `create_app` method for the application factory
- `manage.py` defines the CLI commands

### Running test
We are using pytest, so simply executes one of the following
```shell script
pytest
python -m pytest (all tests)
python -m pytest tests/ (all tests)
python -m pytest tests/test_sample.py (single test file)
python -m pytest tests/utils/test_sample.py::test_answer_correct (single test method)
```
