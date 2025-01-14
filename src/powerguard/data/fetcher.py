from collections import defaultdict
from typing import Any, Dict, List, Optional


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
    # def get_test_report(self, report_id: int) -> Optional[List[Dict[str, Any]]]:
    #     """
    #     Fetch test reports using the report ID from ReportSettings.

    #     Args:
    #         report_id (int): The report ID linking ReportSettings to TestReport.

    #     Returns:
    #         Optional[List[Dict[str, Any]]]: A list of dictionaries containing test report details if found, None otherwise.
    #     """
    #     query = """
    #     SELECT 
    #         TestReport.id AS test_report_id,
    #         TestReport.sub_report_id,
    #         TestReport.test_name,
    #         TestReport.test_description,
    #         TestReport.test_result,
    #         ReportSettings.client_name,
    #         ReportSettings.standard,
    #         ReportSettings.ups_model,
    #         Measurement.m_unique_id AS measurement_unique_id,
    #         Measurement.name AS measurement_name,
    #         Measurement.timestamp AS measurement_timestamp, 
    #         Measurement.load_type AS measurement_loadtype,
    #         PowerMeasure.id AS power_measure_id,
    #         PowerMeasure.type AS power_measure_type,           
    #         PowerMeasure.voltage AS power_measure_voltage,
    #         PowerMeasure.current AS power_measure_current,
    #         PowerMeasure.power AS power_measure_power,
    #         PowerMeasure.energy AS power_measure_energy,
    #         PowerMeasure.pf AS power_measure_pf,
    #         PowerMeasure.frequency AS power_measure_frequency
    #     FROM TestReport
    #     JOIN ReportSettings ON TestReport.settings_id = ReportSettings.id
    #     LEFT JOIN Measurement ON Measurement.test_report_id = TestReport.id
    #     LEFT JOIN PowerMeasure ON PowerMeasure.measurement_id = Measurement.id
    #     WHERE ReportSettings.report_id = ?
    #     ORDER BY TestReport.sub_report_id
    #     """
    #     self._cursor.execute(query, (report_id,))
    #     rows = self._cursor.fetchall()

    #     if not rows:
    #         return None

    #     columns = [col[0] for col in self._cursor.description]
    #     return [dict(zip(columns, row)) for row in rows]

    def get_test_report(self, test_report_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a test report using the test_report_id from TestReport Table incremental ID.
        Args:
            sub_report_id (int): The test_report_id linking  TestReport and Report Setting.
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the test report details if found, None otherwise.
        """
        query = """
        SELECT 
            TestReport.id AS test_report_id,
            TestReport.sub_report_id,
            TestReport.test_name,
            TestReport.test_description,
            TestReport.test_result,
            ReportSettings.client_name,
            ReportSettings.standard,
            ReportSettings.ups_model,
            Measurement.m_unique_id AS measurement_unique_id,
            Measurement.name AS measurement_name,
            Measurement.timestamp AS measurement_timestamp, 
            Measurement.load_type AS measurement_loadtype,
            PowerMeasure.id AS power_measure_id,
            PowerMeasure.type AS power_measure_type,           
            PowerMeasure.voltage AS power_measure_voltage,
            PowerMeasure.current AS power_measure_current,
            PowerMeasure.power AS power_measure_power,
            PowerMeasure.energy AS power_measure_energy,
            PowerMeasure.pf AS power_measure_pf,
            PowerMeasure.frequency AS power_measure_frequency
        FROM TestReport
        JOIN ReportSettings ON TestReport.settings_id = ReportSettings.id
        LEFT JOIN Measurement ON Measurement.test_report_id = TestReport.id
        LEFT JOIN PowerMeasure ON PowerMeasure.measurement_id = Measurement.id
        WHERE TestReport.id= ?
        """
        self._cursor.execute(query, (test_report_id,))
        rows = self._cursor.fetchall()

        if not rows:
            return None

        columns = [col[0] for col in self._cursor.description]
        return [dict(zip(columns, row)) for row in rows]



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
