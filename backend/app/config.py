from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./smartplant.db"
    jwt_secret: str = "change-this-secret"
    device_api_key: str = "change-device-key"
    admin_username: str = "admin"
    admin_password: str = "change-me"
    cors_origins: str = "http://localhost:5173"
    token_expire_minutes: int = 120

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


settings = Settings()

print("=== BACKEND CONFIG ===")
print("DEVICE_API_KEY loaded:", settings.device_api_key)
print("DEVICE_API_KEY length:", len(settings.device_api_key))
print("======================")
