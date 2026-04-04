from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	DATABASE_URL: str
	ANTHROPIC_API_KEY: str
	OPENAI_API_KEY: str = ""  # For embeddings (text-embedding-3-small)
	APP_ENV: str = "development"
	JWT_SECRET_KEY: str = "your-secret-key-please-change-this-in-production-use-openssl-rand-hex-32"
	DOCUMENTS_STORAGE_DIR: str = "uploads/documents"
	CORS_ALLOW_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://aifindd.vercel.app,https://universalaifind.xyz"
	CORS_ALLOW_ORIGIN_REGEX: str = r"^https://.*\.vercel\.app$"
	
	# Chunking settings
	CHUNK_SIZE: int = 800
	CHUNK_OVERLAP: int = 100

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

	@property
	def cors_origins(self) -> list[str]:
		return [origin.strip() for origin in self.CORS_ALLOW_ORIGINS.split(",") if origin.strip()]


settings = Settings()
