from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer


def test_azure_add_schema(settings_env):
    from arkitema_config.security import azure_scheme

    assert isinstance(azure_scheme, SingleTenantAzureAuthorizationCodeBearer)
