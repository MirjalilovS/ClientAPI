# E-Commerce Transaction API

This project is a RESTful API service developed in Python using the FastAPI framework. It has two endpoints /upload and /summary. The /upload endpoint accepts a CSV file upload and validates the file format before storing the data for processing in an SQLModel database. The /summary endpoint accepts a user ID and returns the summary statistics for the user including the maximum, minimum and mean transaction amount for that user. Optionally, the client can specify a start and end date in which transactions that will be included must lie in.

## Tech Stack

This project is built using the following stacky.

* **Framework:**
    * **FastAPI:** A web framework for building APIs.
    * **Uvicorn:** The ASGI server used to run the application.

* **Data & Validation:**
    * **SQLModel:** A library for interacting with SQL databases from Python code, with Python objects. It combines Pydantic and SQLAlchemy and is made by the creator of FastAPI.
    * **Pydantic:** Used for data validation and ensuring type hints are respected.
    * **python-multipart:** Required for handling the CSV uploads.

* **Testing:**
    * **Pytest:** The framework used for writing and running the test suite.
    * **HTTPX:** A fully featured HTTP client used within `TestClient` to make requests to the API during tests.

* **Development & Code Quality:**
    * **Black:** An uncompromising code formatter to ensure consistent style.
    * **pre-commit:** Used to manage and run pre-commit hooks that run the Black formatter prior to commits.
    * **Faker:** A library for generating fake data, used to create the sample `dummy_transactions.csv` file but not used in the main logic.

## Installation, Setup and Testing

The setup assumes that you are using a Linux system or WSL. To get the latest development version clone the repo using:

```bash
git clone git@github.com:MirjalilovS/ClientAPI.git
```

To setup the project please finput the following commands in the terminal:

```bash
python3 -m venv venv
source venv/bin/activate
pip install .
```

Although somewhat optional, install the black formatter to run through pre-commits by inputting the following:

```bash
pip install pre-commit
pre-commit install
```

You can run all the unit tests through inputting the following command:

```bash
pytest
```

You can run tests in a specific module by running the following command:
```bash
pytest tests/chosen_test.py"
```

Finally, you can run the app through the following command:

```bash
uvicorn api.main:app --reload
```

Then open https://127.0.0.1:8000/docs for the Swagger UI interactive documentation.

## API Endpoints
Explanation of the endpoints
## Architecture and Design Decisions
Will insert the .puml diagrams here after fixing them up, and explain the package structure etc.
## Features
Features include: Upload and Validate CSV files, Calculate and retrieve summary statistics (min, max, mean) for a specific user within a date range. Handle up to 1 million transactions efficiently and comprehensive error handling and input validation
