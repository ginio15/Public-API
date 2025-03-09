import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from services.db.db_config import Base, get_db

# 1. Create a test database URL using in-memory SQLite for better isolation
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_db.sqlite"

# 2. Create test engine and session
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 3. Create the tables fresh for each test session
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    # Optionally drop tables after tests
    Base.metadata.drop_all(bind=test_engine)

# 4. Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Apply the override to our FastAPI app
app.dependency_overrides[get_db] = override_get_db

# 6. Create a TestClient that uses the overridden app
client = TestClient(app)

# Basic test to ensure the API is working
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Lets Rock"}

