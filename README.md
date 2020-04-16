# CAPLCLimat - Back End
## Introduction
Project holding the back-end implementation of CAPLC.

## Local Setup

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
### Setting up environment variables
Project is configured using environment variables in the following files.
- `venv/local.env`
- `venv/development.env`
- `venv/production.env`

They are ignored by git so you'll have to create the file according to the setup you want.
You can use `venv/env.example` as a template
Adapt the setting accordingly.
For the local setup, you don't have to do anything except of copying the env.example to the correct file.
```shell script
$ mv venv/env.example venv/local.env
```

Then to export those variables, run :
```shell script
export $(grep -v '^#' venv/local.env | xargs)
```
WARNING : The variables are exported for the current session only. They need to be re-exported
once you open another terminal

Add it your `.bashrc` if you want the variable to be exported everytime you open a terminal.

### Setting up Mongo locally if needed
Install [Docker](https://www.docker.com/get-started)

Install [Docker Compose](https://docs.docker.com/compose/install/)

Start Mongo container
```shell script
$ docker-compose -f mongo/docker-compose.mongo_only.yml up --build -d
Creating mongo_caplc ... done
```

After that, you should be able to access Mongo shell through docker by
```shell script
$ docker exec -it mongo_caplc mongo mongodb://caplc_user:password123@127.0.0.1:27017/caplcDB
MongoDB shell version v4.2.5
connecting to: mongodb://127.0.0.1:27017/caplcDB?compressors=disabled&gssapiServiceName=mongodb
Implicit session: session { "id" : UUID("16e3d350-9cfc-430b-bf73-c957f0de67c6") }
MongoDB server version: 4.2.5
>
```

FYI, those credentials are currently hardcoded in the setup file `docker/mongo-init.js` which is run at the creation of the container.

You may need to change it according to your `local.env` file

### Running the server

```shell script
$ flask run
 * Serving Flask app "app:create_app('local')" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 210-427-520

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
$ flask create_admin
User first name [admin]:
User last name [user]:
Email [admin@test.com]:
Password:
Repeat for confirmation:
Admin User admin@test.com created.
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
