from typing import Any

from pydantic import AnyHttpUrl, ConfigDict, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings


def convert_env_to_list(cls, v: str | list[str]) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list):
        return v
    raise ValueError(v)


class ServerSettings(BaseSettings):
    API_STR: str = "/api"
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = [
        "http://localhost:4200",
        "http://0.0.0.0:4200",
    ]

    # validators
    _convert_to_list = field_validator("BACKEND_CORS_ORIGINS")(convert_env_to_list)

    # configuration
    model_config = ConfigDict(case_sensitive=True)


class AzureSettings(BaseSettings):
    AAD_APP_CLIENT_ID: str
    AAD_TENANT_ID: str
    AAD_OPENAPI_CLIENT_ID: str | None
    AAD_TEST_CLIENT_SECRET: str | None = None

    # configuration
    model_config = ConfigDict(case_sensitive=True)


class PostgresSettings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    POSTGRES_SSL: bool = False
    POSTGRES_MAX_OVERFLOW: int = 30
    POSTGRES_POOL_SIZE: int = 20
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @model_validator(mode="before")
    @classmethod
    def assemble_db_connection(cls, data: Any) -> Any:
        if isinstance(data.get("SQLALCHEMY_DATABASE_URI"), str):
            return data["SQLALCHEMY_DATABASE_URI"]
        else:
            data["SQLALCHEMY_DATABASE_URI"] = PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=data.get("POSTGRES_USER"),
                password=data.get("POSTGRES_PASSWORD"),
                host=data.get("POSTGRES_HOST"),
                path=data.get("POSTGRES_DB"),
                port=int(data.get("POSTGRES_PORT")) if data.get("POSTGRES_PORT") else None,
            )
        return data

    # configuration
    model_config = ConfigDict(case_sensitive=True)


class EmailSettings(BaseSettings):
    SENDGRID_SECRET: str
    EMAIL_NOTIFICATION_FROM: str
    INTERNAL_EMAIL_DOMAINS_LIST: str | None = None
    DEFAULT_AD_FQDN: str

    # validators
    _convert_to_list = field_validator("INTERNAL_EMAIL_DOMAINS_LIST")(convert_env_to_list)

    # configuration
    model_config = ConfigDict(case_sensitive=True)


class MetricsSettings(BaseSettings):
    OTLP_GRPC_ENDPOINT: AnyHttpUrl = "http://tempo-distributor.monitoring:4317"
    ENABLE_METRICS: bool = True
    ENABLE_TELEMETRY: bool = True

    # configuration
    model_config = ConfigDict(case_sensitive=True)


class Settings(ServerSettings, AzureSettings, PostgresSettings, EmailSettings, MetricsSettings):
    ROUTER_URL: AnyHttpUrl
    AAD_GRAPH_SECRET: str

    # configuration
    model_config = ConfigDict(case_sensitive=True)
