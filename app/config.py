from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	DATABASE_URL: str
	ANTHROPIC_API_KEY: str
	OPENAI_API_KEY: str = ""  # For embeddings (text-embedding-3-small)
	APP_ENV: str = "development"
	JWT_SECRET_KEY: str = "your-secret-key-please-change-this-in-production-use-openssl-rand-hex-32"
	
	# Chunking settings
	CHUNK_SIZE: int = 800
	CHUNK_OVERLAP: int = 100

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
