import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request


@pytest.fixture
def client(tmp_path):
    from app.core.config import Settings
    from app.db.session import get_session
    from app.main import create_app

    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        upload_dir=tmp_path / "uploads",
        _env_file=None,
    )
    test_app = create_app(settings)

    def override_get_session(request: Request):
        with request.app.state.session_factory() as session:
            yield session

    test_app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(test_app) as test_client:
            yield test_client
    finally:
        test_app.dependency_overrides.clear()
        test_app.state.engine.dispose()
