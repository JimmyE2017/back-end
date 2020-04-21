from setuptools import setup

requirements = [
    "Flask>=1.1.2",
    "Flask-JWT-Extended>=3.24.1",
    "Flask-Mail>=0.9.1",
    "flask-mongoengine>=0.9.5",
    "marshmallow>=3.5.1",
]

dev_requirements = ["pytest", "pre-commit", "black", "mongomock", "coverage"]


setup(
    name="CAPLC-backend",
    version="0.1.0",
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
)
