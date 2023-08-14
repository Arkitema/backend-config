from typing import Any

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


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
    _convert_to_list = validator("BACKEND_CORS_ORIGINS", allow_reuse=True)(convert_env_to_list)

    class Config:
        case_sensitive = True


class AzureSettings(BaseSettings):
    AAD_APP_CLIENT_ID: str
    AAD_TENANT_ID: str
    AAD_TEST_CLIENT_SECRET: str | None

    class Config:
        case_sensitive = True


class PostgresSettings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    POSTGRES_SSL: bool = False
    POSTGRES_MAX_OVERFLOW = 30
    POSTGRES_POOL_SIZE: int = 20
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
            port=values.get("POSTGRES_PORT"),
        )

    class Config:
        case_sensitive = True


class EmailSettings(BaseSettings):
    SENDGRID_SECRET: str
    EMAIL_NOTIFICATION_FROM: str
    INTERNAL_EMAIL_DOMAINS_LIST: str | None = None
    DEFAULT_AD_FQDN: str

    # validators
    _convert_to_list = validator("INTERNAL_EMAIL_DOMAINS_LIST", allow_reuse=True)(convert_env_to_list)

    class Config:
        case_sensitive = True


class MetricsSettings(BaseSettings):
    OTLP_GRPC_ENDPOINT: AnyHttpUrl = "http://tempo-distributor.monitoring:4317"
    ENABLE_METRICS: bool = True
    ENABLE_TELEMETRY: bool = True

    class Config:
        case_sensitive = True


class Settings(ServerSettings, AzureSettings, PostgresSettings, EmailSettings, MetricsSettings):
    ROUTER_URL: AnyHttpUrl
    AAD_GRAPH_SECRET: str

    class Config:
        case_sensitive = True
