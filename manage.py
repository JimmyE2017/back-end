import os

from flask_script import Manager

from app import create_app

app = create_app(os.getenv("ENVIRONMENT", "dev"))
app.app_context().push()

manager = Manager(app)


@manager.command
def run():
    app.run()


if __name__ == "__main__":
    manager.run()
