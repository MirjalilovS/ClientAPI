import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from api.main import app
from api.database import get_session
from api.models import SummaryData, UploadData

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


def test_summary_uid_only(client: TestClient, session: Session):
    # placeholder request, will be updated later

    test_data = [
        {
            "transaction_id": "95494198-1b28-4b68-9fe1-48da933d0104",
            "user_id": 622,
            "product_id": 465,
            "timestamp": "2024-11-03T19:17:50",
            "transaction_amount": 424.19,
        },
        {
            "transaction_id": "e47470dc-2aba-42cc-9daf-24b55c492efd",
            "user_id": 479,
            "product_id": 207,
            "timestamp": "2025-02-16T01:09:42",
            "transaction_amount": 496.82,
        },
        {
            "transaction_id": "905ac509-22cd-4aa6-8b30-1181c0139447",
            "user_id": 779,
            "product_id": 7,
            "timestamp": "2025-07-06T10:18:46",
            "transaction_amount": 85.45,
        },
        {
            "transaction_id": "d7d805b0-4277-4974-bbd9-0dcc75868700",
            "user_id": 525,
            "product_id": 384,
            "timestamp": "2025-10-02T17:41:45",
            "transaction_amount": 435.45,
        },
        {
            "transaction_id": "1583a7f0-9c15-4aee-9831-0a51cdf51cb5",
            "user_id": 946,
            "product_id": 22,
            "timestamp": "2025-09-25T22:53:08",
            "transaction_amount": 17.32,
        },
        {
            "transaction_id": "3503250b-eab6-41a0-bc4f-ca35933cb1c0",
            "user_id": 523,
            "product_id": 156,
            "timestamp": "2024-12-23T17:12:23",
            "transaction_amount": 324.76,
        },
        {
            "transaction_id": "bac663b9-f532-4ea4-a544-789967a35df9",
            "user_id": 373,
            "product_id": 408,
            "timestamp": "2025-08-23T16:33:17",
            "transaction_amount": 31.32,
        },
        {
            "transaction_id": "90d50e42-1494-4df3-9fc2-f66ac61356ed",
            "user_id": 917,
            "product_id": 229,
            "timestamp": "2025-04-25T11:52:26",
            "transaction_amount": 390.00,
        },
        {
            "transaction_id": "fc8e448c-d260-4055-a6d9-4fc5da033f3c",
            "user_id": 742,
            "product_id": 122,
            "timestamp": "2025-02-16T23:44:09",
            "transaction_amount": 241.50,
        },
        {
            "transaction_id": "0e4f3c0e-0db8-499d-9a9e-636621163a1a",
            "user_id": 652,
            "product_id": 466,
            "timestamp": "2025-02-20T05:11:30",
            "transaction_amount": 51.74,
        },
    ]

    for item in test_data:
        transaction = UploadData.model_validate(item)
        session.add(transaction)
    session.commit()

    statement = select(UploadData).where(UploadData.user_id == 479)
    results = session.exec(statement).all()
    print(f"SANITY CHECK: Found {len(results)} records for user 479 in the test DB.")
    assert len(results) > 0

    response = client.get("/summary/479")
    print(response.json())
    assert response.status_code == 200
    data = response.json()

    assert data["max_amount"] == 496.82
    assert data["min_amount"] == 496.82
    assert data["mean_amount"] == 496.82

    response = client.get("/summary/999")

    assert response.status_code == 404


def test_summary_with_dates(client: TestClient, session: Session):
    test_data = [
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
        {
            "transaction_id": "3503250b-eab6-41a0-bc4f-ca35933cb1c0",
            "user_id": 523,
            "product_id": 156,
            "timestamp": "2024-12-23T17:12:23",
            "transaction_amount": 324.76,
        },
        {
            "transaction_id": "bac663b9-f532-4ea4-a544-789967a35df9",
            "user_id": 373,
            "product_id": 408,
            "timestamp": "2025-08-23T16:33:17",
            "transaction_amount": 31.32,
        },
        {
            "transaction_id": "90d50e42-1494-4df3-9fc2-f66ac61356ed",
            "user_id": 917,
            "product_id": 229,
            "timestamp": "2025-04-25T11:52:26",
            "transaction_amount": 390.00,
        },
        {
            "transaction_id": "fc8e448c-d260-4055-a6d9-4fc5da033f3c",
            "user_id": 742,
            "product_id": 122,
            "timestamp": "2025-02-16T23:44:09",
            "transaction_amount": 241.50,
        },
        {
            "transaction_id": "0e4f3c0e-0db8-499d-9a9e-636621163a1a",
            "user_id": 652,
            "product_id": 466,
            "timestamp": "2025-02-20T05:11:30",
            "transaction_amount": 51.74,
        },
    ]
    # user 622 has multiple transactions and others have one each
    for item in test_data:
        transaction = UploadData.model_validate(item)
        session.add(transaction)
    session.commit()


# I can easily finish this before lunch, then we can go eat and then come back and lock in for a final stretch

# I need to test the following cases
# User ID: Valid and Invalid
# User ID + Dates: Valid User ID for all: Invalid dates
# Valid dates: Transactions exist, No Transactions exist, Start Data after End Date
