import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base_class import BaseEntity
from app.api.deps import get_db
from app.core.config import settings
from app.modules.users.models import User
from app.core.security import get_password_hash

# Use the same DB for testing but we will rollback
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    # Setup - create tables (they should already exist from alembic but just in case)
    BaseEntity.metadata.create_all(bind=engine)
    yield engine
    # Teardown - don't drop all tables because it's shared with dev DB right now

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture(scope="function")
def test_user(db):
    user = User(
        email="testuser@example.com",
        password_hash=get_password_hash("StrongP@ss1"),
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    return user
