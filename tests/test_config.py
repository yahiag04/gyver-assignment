def test_settings_read_runtime_values_from_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test-model")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("UPLOAD_DIR", "test-uploads")
    monkeypatch.setenv("MAX_UPLOAD_MB", "12")

    from app.core.config import Settings

    settings = Settings(_env_file=None)

    assert settings.openai_api_key == "test-key"
    assert settings.openai_model == "gpt-test-model"
    assert settings.database_url == "sqlite:///./test.db"
    assert str(settings.upload_dir) == "test-uploads"
    assert settings.max_upload_mb == 12


def test_settings_work_without_an_llm_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    from app.core.config import Settings

    settings = Settings(_env_file=None)

    assert settings.openai_api_key is None
