from typing import Optional, Dict, Any


class Fetcher:
    """A class responsible for fetching data from the database."""

    def __init__(self, conn, cursor):
        """
        Initialize the Fetcher with a database connection and cursor.
        Args:
            connection (sqlite3.Connection): SQLite database connection.
            cursor (sqlite3.Cursor): SQLite cursor for executing queries.
        """
        self._conn = conn
        self._cursor = cursor

    def get_test_report_by_report_id(self, report_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a test report using the report ID from ReportSettings.
        Args:
            report_id (int): The report ID linking ReportSettings to TestReport.
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the test report details if found, None otherwise.
        """
        query = """
        SELECT 
            TestReport.id AS test_report_id,
            TestReport.test_name,
            TestReport.test_description,
            TestReport.test_result,
            ReportSettings.client_name,
            ReportSettings.standard,
            ReportSettings.ups_model,
            Measurement.m_unique_id AS measurement_unique_id,
            Measurement.name AS measurement_name
        FROM TestReport
        JOIN ReportSettings ON TestReport.settings_id = ReportSettings.id
        LEFT JOIN Measurement ON Measurement.test_report_id = TestReport.id
        WHERE ReportSettings.report_id = ?
        """
        self._cursor.execute(query, (report_id,))
        row = self._cursor.fetchone()

        if row:
            columns = [col[0] for col in self._cursor.description]
            return dict(zip(columns, row))

        return None

    def get_test_report(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a test report using the id of TestReport table.
        Args:
            id (int): id of TestReport table.
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the test report details if found, None otherwise.
        """
        query = """
        SELECT 
            TestReport.id AS test_report_id,
            TestReport.test_name,
            TestReport.test_description,
            TestReport.test_result,
            ReportSettings.client_name,
            ReportSettings.standard,
            ReportSettings.ups_model,
            Measurement.m_unique_id AS measurement_unique_id,
            Measurement.name AS measurement_name
        FROM TestReport
        JOIN ReportSettings ON TestReport.settings_id = ReportSettings.id
        LEFT JOIN Measurement ON Measurement.test_report_id = TestReport.id
        WHERE TestReport.id = ?
        """
        self._cursor.execute(query, (id,))
        row = self._cursor.fetchone()

        if row:
            columns = [col[0] for col in self._cursor.description]
            return dict(zip(columns, row))

        return None

    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """
        Fetch latest report from  TestReport table.
        Args:
            None.
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the test report details if found, None otherwise.
        """
        query = """
        SELECT 
            TestReport.id AS test_report_id,
            TestReport.test_name,
            TestReport.test_description,
            TestReport.test_result,
            ReportSettings.client_name,
            ReportSettings.standard,
            ReportSettings.ups_model,
            Measurement.m_unique_id AS measurement_unique_id,
            Measurement.name AS measurement_name
        FROM TestReport
        JOIN ReportSettings ON TestReport.settings_id = ReportSettings.id
        LEFT JOIN Measurement ON Measurement.test_report_id = TestReport.id
        ORDER BY
            TestReport.id DESC
        LIMIT 1
        """
        self._cursor.execute(query)
        row = self._cursor.fetchone()

        if row:
            columns = [col[0] for col in self._cursor.description]
            return dict(zip(columns, row))

        return None
