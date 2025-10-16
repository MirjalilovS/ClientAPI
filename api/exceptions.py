class InvalidFileType(Exception):
    """Raised when an uploaded file is not a CSV."""

    pass


class CSVProcessingError(Exception):
    """Raised for errors during CSV data parsing and validation."""

    pass


class UserNotFoundError(Exception):
    """Raised when a summary query returns no results for a user."""

    pass


class InvalidDateRange(Exception):
    """Raised when the start date is after the end date."""

    pass


class NoTransactionsFoundError(Exception):
    """Raised when no transactions are found for the given user and date range."""

    pass
