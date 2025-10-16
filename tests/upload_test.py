import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from api.main import app
from api.database import get_session

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True,  # echo=True is great for debugging
)


@pytest.fixture(name="session")
def session_fixture():

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)
    engine.dispose()

    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture(name="client")
def client_fixture(session: Session):

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_upload(client: TestClient):
    file_path = os.path.join(os.path.dirname(__file__), "dummy_transactions_mid.csv")

    with open(file_path, "rb") as f:
        response = client.post(
            "/upload", files={"file": ("dummy_transactions.csv", f, "text/csv")}
        )

    assert response.status_code == 201
    assert response.json() == {
        "message": "Successfully uploaded and processed 10 transactions."
    }


def test_upload_invalid_file_type(client: TestClient):
    file_path = os.path.join(os.path.dirname(__file__), "invalid_file.txt")

    with open(file_path, "rb") as f:
        response = client.post(
            "/upload", files={"file": ("invalid_file.txt", f, "text/plain")}
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file type. Please upload a CSV file."}
