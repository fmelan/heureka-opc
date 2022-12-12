from pydantic import BaseSettings


class Settings(BaseSettings):
    topic: str
    bootstrap_servers: str
    security_protocol: str
    sasl_plain_username: str
    sasl_plain_password: str
    sasl_mechanism: str
    auto_offset_reset: str
    enable_auto_commit: bool
    mongodb_connstring: str
    database_name: str

    class Config:
        env_file = ".env"


settings = Settings()
