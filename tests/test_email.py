import pytest

from arkitema_config import email


@pytest.mark.asyncio
async def test_send_email(mocker):
    mail_mock = mocker.patch("arkitema_config.email.Mail", return_value="mail_obj")
    sendgrid_mock = mocker.patch("arkitema_config.email.SendGridAPIClient")
    sendgrid_mock.return_value.send.return_value = "RESPONSE"

    result = await email.send_email("test@email.com", subject="Mock Email")
    assert result == "RESPONSE"
    assert len(mail_mock.mock_calls) == 1
    assert mail_mock.mock_calls[0][2]["from_email"] == "no-reply@arkitema.com"
    assert mail_mock.mock_calls[0][2]["to_emails"] == "test@email.com"
    assert mail_mock.mock_calls[0][2]["subject"] == "Mock Email"
    assert (
        mail_mock.mock_calls[0][2]["html_content"]
        == ""
    )

    assert len(sendgrid_mock.mock_calls) == 2
    assert sendgrid_mock.mock_calls[0][1] == ("c2VjcmV0",)
    assert sendgrid_mock.mock_calls[1][1] == ("mail_obj",)



@pytest.mark.asyncio
async def test_send_email_custom_body(mocker):
    mail_mock = mocker.patch("arkitema_config.email.Mail", return_value="mail_obj")
    sendgrid_mock = mocker.patch("arkitema_config.email.SendGridAPIClient")
    sendgrid_mock.return_value.send.return_value = "RESPONSE"

    result = await email.send_email("test@email.com", subject="Custom HTML Body", html_body="Hello!<br>")

    assert result == "RESPONSE"
    assert len(mail_mock.mock_calls) == 1
    assert mail_mock.mock_calls[0][2]["from_email"] == "no-reply@arkitema.com"
    assert mail_mock.mock_calls[0][2]["to_emails"] == "test@email.com"
    assert mail_mock.mock_calls[0][2]["subject"] == "Custom HTML Body"
    assert mail_mock.mock_calls[0][2]["html_content"] == "Hello!<br>"

    assert len(sendgrid_mock.mock_calls) == 2
    assert sendgrid_mock.mock_calls[0][1] == ("c2VjcmV0",)
    assert sendgrid_mock.mock_calls[1][1] == ("mail_obj",)
