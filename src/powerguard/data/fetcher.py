from typing import Optional, Dict, Any
from collections import defaultdict


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

    def get_test_report(self, report_id: int) -> Optional[Dict[str, Any]]:
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
            Measurement.name AS measurement_name,
            Measurement.timestamp AS measurement_timestamp, 
            Measurement.load_type AS measurement_loadtype,
            PowerMeasure.id AS power_measure_id,
            PowerMeasure.type AS power_measure_type,
            PowerMeasure.name AS power_measure_name,
            PowerMeasure.voltage AS power_measure_voltage,
            PowerMeasure.current AS power_measure_current,
            PowerMeasure.power AS power_measure_power,
            PowerMeasure.pf AS power_measure_pf
        FROM TestReport
        JOIN ReportSettings ON TestReport.settings_id = ReportSettings.id
        LEFT JOIN Measurement ON Measurement.test_report_id = TestReport.id
        LEFT JOIN PowerMeasure ON PowerMeasure.measurement_id = Measurement.id
        WHERE TestReport.id= ?
        """
        self._cursor.execute(query, (report_id,))
        rows = self._cursor.fetchall()

        if not rows:
            return None

        columns = [col[0] for col in self._cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    # def get_test_report(self, report_id: int) -> Optional[Dict[str, Any]]:
    #     """
    #     Fetch a test report using the report ID from ReportSettings.
    #     Args:
    #         report_id (int): The report ID linking ReportSettings to TestReport.
    #     Returns:
    #         Optional[Dict[str, Any]]: A dictionary containing the test report details if found, None otherwise.
    #     """
    #     query = """
    #     SELECT
    #         TestReport.id AS test_report_id,
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
    #         PowerMeasure.name AS power_measure_name,
    #         PowerMeasure.voltage AS power_measure_voltage,
    #         PowerMeasure.current AS power_measure_current,
    #         PowerMeasure.power AS power_measure_power,
    #         PowerMeasure.pf AS power_measure_pf
    #     FROM TestReport
    #     JOIN ReportSettings ON TestReport.settings_id = ReportSettings.id
    #     LEFT JOIN Measurement ON Measurement.test_report_id = TestReport.id
    #     LEFT JOIN PowerMeasure ON PowerMeasure.measurement_id = Measurement.id
    #     WHERE TestReport.id = ?
    #     """
    #     self._cursor.execute(query, (report_id,))
    #     rows = self._cursor.fetchall()

    #     if not rows:
    #         return None

    #     # Group data based on the hierarchy
    #     report = None
    #     measurements = defaultdict(lambda: {"power_measures": []})

    #     for row in rows:
    #         # Extract common columns for the report
    #         if not report:
    #             report = {
    #                 "test_report_id": row[0],
    #                 "test_name": row[1],
    #                 "test_description": row[2],
    #                 "test_result": row[3],
    #                 "client_name": row[4],
    #                 "standard": row[5],
    #                 "ups_model": row[6],
    #                 "measurements": []
    #             }

    #         # Handle measurement and power measures
    #         measurement_id = row[7]
    #         if measurement_id:
    #             measurement = measurements[measurement_id]
    #             if not measurement["power_measures"]:  # Populate measurement only once
    #                 measurement.update({
    #                     "measurement_unique_id": measurement_id,
    #                     "measurement_name": row[8],
    #                     "measurement_timestamp": row[9],
    #                     "measurement_loadtype": row[10],
    #                 })
    #             if row[11]:  # If a power measure exists
    #                 measurement["power_measures"].append({
    #                     "power_measure_id": row[11],
    #                     "power_measure_type": row[12],
    #                     "power_measure_name": row[13],
    #                     "power_measure_voltage": row[14],
    #                     "power_measure_current": row[15],
    #                     "power_measure_power": row[16],
    #                     "power_measure_pf": row[17],
    #                 })

    #     # Add measurements to the report
    #     report["measurements"] = list(measurements.values())
    #     return report

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
