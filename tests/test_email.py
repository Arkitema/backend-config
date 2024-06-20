import pytest

from lcaplatform_config import email


@pytest.mark.asyncio
async def test_send_email_no_kwargs(mocker):
    mail_mock = mocker.patch("lcaplatform_config.email.Mail", return_value="mail_obj")
    sendgrid_mock = mocker.patch("lcaplatform_config.email.SendGridAPIClient")
    sendgrid_mock.return_value.send.return_value = "RESPONSE"

    result = await email.send_email("test@email.com", email_type=email.EmailType.TASK_ASSIGN)
    assert result == "RESPONSE"
    assert len(mail_mock.mock_calls) == 1
    assert mail_mock.mock_calls[0][2]["from_email"] == "no-reply@arkitema.com"
    assert mail_mock.mock_calls[0][2]["to_emails"] == "test@email.com"
    assert mail_mock.mock_calls[0][2]["subject"] == "LCA project"
    assert (
        mail_mock.mock_calls[0][2]["html_content"]
        == "Hello, <br>You have been assingned to new task <strong></strong>. <br><br>With best regards, LCA team. <br><i>This email was generated automatically</i>"
    )

    assert len(sendgrid_mock.mock_calls) == 2
    assert sendgrid_mock.mock_calls[0][1] == ("c2VjcmV0",)
    assert sendgrid_mock.mock_calls[1][1] == ("mail_obj",)


@pytest.mark.asyncio
async def test_send_email_with_kwargs(mocker):
    mail_mock = mocker.patch("lcaplatform_config.email.Mail", return_value="mail_obj")
    sendgrid_mock = mocker.patch("lcaplatform_config.email.SendGridAPIClient")
    sendgrid_mock.return_value.send.return_value = "RESPONSE"
    result = await email.send_email(
        "test@email.com", email_type=email.EmailType.TASK_COMMENT, **{"task": "test_task", "comment": "test_comment"}
    )
    assert result == "RESPONSE"
    assert len(mail_mock.mock_calls) == 1
    assert mail_mock.mock_calls[0][2]["from_email"] == "no-reply@arkitema.com"
    assert mail_mock.mock_calls[0][2]["to_emails"] == "test@email.com"
    assert mail_mock.mock_calls[0][2]["subject"] == "LCA project"
    assert (
        mail_mock.mock_calls[0][2]["html_content"]
        == "Hello, <br>The task <strong>test_task</strong> has new comment<br><strong>test_comment</strong><br><br>With best regards, LCA team. <br><i>This email was generated automatically</i>"
    )

    assert len(sendgrid_mock.mock_calls) == 2
    assert sendgrid_mock.mock_calls[0][1] == ("c2VjcmV0",)
    assert sendgrid_mock.mock_calls[1][1] == ("mail_obj",)


@pytest.mark.asyncio
async def test_send_email_custom_body(mocker):
    mail_mock = mocker.patch("lcaplatform_config.email.Mail", return_value="mail_obj")
    sendgrid_mock = mocker.patch("lcaplatform_config.email.SendGridAPIClient")
    sendgrid_mock.return_value.send.return_value = "RESPONSE"

    result = await email.send_email("test@email.com", html_body="Hello!<br>")

    assert result == "RESPONSE"
    assert len(mail_mock.mock_calls) == 1
    assert mail_mock.mock_calls[0][2]["from_email"] == "no-reply@arkitema.com"
    assert mail_mock.mock_calls[0][2]["to_emails"] == "test@email.com"
    assert mail_mock.mock_calls[0][2]["subject"] == "LCA project"
    assert mail_mock.mock_calls[0][2]["html_content"] == "Hello!<br>"

    assert len(sendgrid_mock.mock_calls) == 2
    assert sendgrid_mock.mock_calls[0][1] == ("c2VjcmV0",)
    assert sendgrid_mock.mock_calls[1][1] == ("mail_obj",)


# working example for sending email
# @pytest.mark.asyncio
# async def test_send_email():
#     email.settings.EMAIL_NOTIFICATION_FROM = "no-reply@arkitema.com"
#     email.settings.SENDGRID_SECRET = ""
#     response = await email.send_email(
#         "chrk@arkitema.com", email.EmailType.INVITE_TO_LCA, **{"project_name": "test_project", "url": "lca.com"}
#     )
#     assert response.status_code == 202
