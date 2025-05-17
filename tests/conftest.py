import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope="session")
def app():
    # tạo app với config testing
    app = create_app()
    app.config.update({
        "TESTING": True,
        # Dùng SQLite in-memory cho nhanh, tránh tác động Oracle thật
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    with app.app_context():
        db.create_all()    # tạo schema
        yield app
        db.drop_all()      # dọn dẹp

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
