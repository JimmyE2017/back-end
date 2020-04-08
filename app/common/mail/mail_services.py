from flask import render_template
from flask_mail import Message

from app.common.mail import mail
from app.common.mail.schemas import password_reset_schema


def send_reset_password_mail(recipient: str, reset_url: str) -> None:
    msg = Message(
        subject=password_reset_schema["subject"],
        recipients=[recipient],
        body=render_template(
            password_reset_schema["body_template"], reset_url=reset_url
        ),
        html=render_template(
            password_reset_schema["html_template"], reset_url=reset_url
        ),
    )
    # TODO : Move that to a thread as it takes quite some times (Maybe use Redis ?)
    mail.send(msg)

    return
