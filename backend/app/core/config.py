from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SecureIssueHub API"
    database_url: str

    # Cookies / sessions
    session_cookie_name: str = "sid"
    csrf_cookie_name: str = "csrf"
    session_expire_minutes: int = 60 * 24 * 7  # 7 dní

    # Cookie policy (localhost vs prod)
    cookie_samesite: str = "lax"  # "lax" je ok pre väčšinu web appiek
    cookie_secure: bool = False  # na localhost False, v produkcii True (HTTPS)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
