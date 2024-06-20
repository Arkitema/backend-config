import logging
from enum import Enum

from requests import Response
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from lcaplatform_config import config

    settings = config.Settings()

logger = logging.getLogger(__name__)


class EmailType(Enum):
    INVITE_TO_LCA = (
        "Hello, <br>"
        "You have been invited to <strong>project {project_name}</strong> on LCA Platform. <br>"
        "You can now access it via <strong>{url}</strong> <br><br>"
        "With best regards, LCA team. <br>"
        "<i>This email was generated automatically</i>"
    )
    TASK_ASSIGN = (
        "Hello, <br>"
        "You have been assingned to new task <strong>{task}</strong>. <br><br>"
        "With best regards, LCA team. <br>"
        "<i>This email was generated automatically</i>"
    )
    TASK_STATUS_CHANGE = (
        "Hello, <br>"
        "The task's <strong>{task}</strong> status has been changed <strong>{status}</strong><br><br>"
        "With best regards, LCA team. <br>"
        "<i>This email was generated automatically</i>"
    )
    TASK_COMMENT = (
        "Hello, <br>"
        "The task <strong>{task}</strong> has new comment<br><strong>{comment}</strong><br><br>"
        "With best regards, LCA team. <br>"
        "<i>This email was generated automatically</i>"
    )


async def send_email(
    recepient: str,
    email_type: EmailType = EmailType.INVITE_TO_LCA,
    html_body: str = None,
    **kwargs,
) -> Response:
    """
    Send an email invitation to the LCA Platform using Sendgrid

    Parameters
    ----------
    recepient: str
        email address of recipient
    email_type: EmailType
        enum values with default template
    html_body: str = None,
        not required custom html email body
    **kwargs: any
        kwargs for inserting in html body template,
        Enum template vars are:
        INVITE_TO_LCA: {"project_name":"<>", "url": "<>"}
        TASK_ASSIGN: {"task":", "<>"}
        TASK_STATUS_CHANGE: {"task":"<>", "status": "<>"}
        TASK_COMMENT: {"task":"<>", "comment": "<>"}

    """
    message_body = ""
    if html_body:
        message_body = html_body
    else:
        is_error = True
        while is_error:
            try:
                message_body = email_type.value.format(**kwargs)
                is_error = False
            except KeyError as e:
                for arg in e.args:
                    kwargs[arg] = ""

    message = Mail(
        from_email=settings.EMAIL_NOTIFICATION_FROM,
        to_emails=recepient,
        subject="LCA project",
        html_content=message_body,
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_SECRET)

        response = sg.send(message)
    except Exception as e:
        logger.error(e)
        response = e.body

    return response
