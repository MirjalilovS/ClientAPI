import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from decimal import Decimal

from api.main import app
from api.database import get_session
from api.models import UploadData, SummaryData

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True,
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


@pytest.fixture(name="populated_db")
def populated_db_fixture(session: Session):
    """
    Provides a pre-populated database for tests that need to query data.
    """
    test_data = [
        # 5 transactions for user 622 beginning 2024-11-03 and ending 2025-10-02
        {
            "transaction_id": "95494198-1b28-4b68-9fe1-48da933d0104",
            "user_id": 622,
            "product_id": 465,
            "timestamp": "2024-11-03T19:17:50",
            "transaction_amount": 424.19,
        },
        {
            "transaction_id": "e47470dc-2aba-42cc-9daf-24b55c492efd",
            "user_id": 622,
            "product_id": 207,
            "timestamp": "2025-02-16T01:09:42",
            "transaction_amount": 496.82,
        },
        {
            "transaction_id": "905ac509-22cd-4aa6-8b30-1181c0139447",
            "user_id": 622,
            "product_id": 7,
            "timestamp": "2025-07-06T10:18:46",
            "transaction_amount": 85.45,
        },
        {
            "transaction_id": "d7d805b0-4277-4974-bbd9-0dcc75868700",
            "user_id": 622,
            "product_id": 384,
            "timestamp": "2025-10-02T17:41:45",
            "transaction_amount": 435.45,
        },
        {
            "transaction_id": "1583a7f0-9c15-4aee-9831-0a51cdf51cb5",
            "user_id": 622,
            "product_id": 22,
            "timestamp": "2025-09-25T22:53:08",
            "transaction_amount": 17.32,
        },
        # 1 transaction for user 523
        {
            "transaction_id": "3503250b-eab6-41a0-bc4f-ca35933cb1c0",
            "user_id": 523,
            "product_id": 156,
            "timestamp": "2024-12-23T17:12:23",
            "transaction_amount": 324.76,
        },
    ]
    for item in test_data:
        transaction = UploadData.model_validate(item)
        session.add(transaction)
    session.commit()


class TestUploadEndpoint:
    """Tests for the /upload endpoint."""

    def test_upload_success(self, client: TestClient, session: Session):
        csv_content = (
            "transaction_id,user_id,product_id,timestamp,transaction_amount\n"
            "a1a1a1a1-1a1a-1a1a-1a1a-1a1a1a1a1a1a,1,1,2025-01-01T12:00:00,10.00"
        )

        response = client.post(
            "/upload", files={"file": ("test.csv", csv_content, "text/csv")}
        )

        assert response.status_code == 201
        assert response.json() == {
            "message": "Successfully uploaded and processed 1 transactions."
        }

        transaction = session.exec(
            select(UploadData).where(UploadData.user_id == 1)
        ).one()
        assert transaction.transaction_amount == Decimal("10.00")

    def test_upload_invalid_file_type(self, client: TestClient):
        response = client.post(
            "/upload", files={"file": ("test.txt", "some content", "text/plain")}
        )
        assert response.status_code == 400
        assert (
            "Invalid file type. Please upload a CSV file." in response.json()["detail"]
        )


class TestSummaryEndpoint:
    """Tests for the /summary endpoint."""

    def test_summary_for_valid_user(self, client: TestClient, populated_db):
        response = client.get("/summary/622")

        assert response.status_code == 200
        data = response.json()

        assert Decimal(data["max_amount"]) == Decimal("496.82")
        assert Decimal(data["min_amount"]) == Decimal("17.32")
        assert data["transaction_count"] == 5

    def test_summary_for_invalid_user(self, client: TestClient, populated_db):
        response = client.get("/summary/999")
        assert response.status_code == 404
        assert "No transactions found" in response.json()["detail"]

    def test_summary_with_date_range(self, client: TestClient, populated_db):
        response = client.get(
            "/summary/622?start_date=2025-01-01T00:00:00&end_date=2025-12-31T23:59:59"
        )

        assert response.status_code == 200
        data = response.json()

        assert Decimal(data["max_amount"]) == Decimal("496.82")
        assert Decimal(data["min_amount"]) == Decimal("17.32")
        assert data["transaction_count"] == 4

    def test_summary_no_transactions_in_range(self, client: TestClient, populated_db):
        response = client.get(
            "/summary/622?start_date=2023-01-01T00:00:00&end_date=2023-12-31T23:59:59"
        )
        assert response.status_code == 404

    def test_summary_invalid_date_range(self, client: TestClient, populated_db):
        response = client.get(
            "/summary/622?start_date=2025-01-01T00:00:00&end_date=2024-01-01T00:00:00"
        )
        assert response.status_code == 400
        assert "start_date cannot be after end_date" in response.json()["detail"]
