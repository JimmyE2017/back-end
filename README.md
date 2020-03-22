# CAPLCLimat - Back End
## Introduction
Project holding the back-end implementation of CAPLC.

## Setup
Create organisation directory
```shell script
mkdir CAPLClimat
cd CAPLClimat
```

Set up virtualenv
(Using pyenv)
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

## Running the server
In development
```shell script
python manage.py
```

Testing if it's running
```shell script
curl 127.0.0.1:5000/api/ping
```
