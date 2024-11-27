# import logging
# import sqlite3
# from pathlib import Path
# from typing import Any, Optional

# from pydantic import BaseModel, PrivateAttr, field_validator

# # Import generated proto classes
# from powerguard.bootstrap import paths
# from proto.pData_pb2 import PowerMeasure, PowerMeasureType
# from proto.report_pb2 import ReportSettings, TestReport, TestStandard
# from proto.ups_test_pb2 import TestResult, TestType
# from proto.upsDefines_pb2 import OverLoad, Phase, spec


# class DataManager(BaseModel):
#     db_name: str = "test_reports.db"
#     db_path: Optional[Path] = None  # Will be set after validation
#     _conn: sqlite3.Connection = PrivateAttr()  # Private attribute for connection
#     _cursor: sqlite3.Cursor = PrivateAttr()  # Private attribute for cursor

#     @field_validator("db_name")
#     def validate_db_name(cls, v: str):
#         """Validate db_name field to ensure it's a string and properly formatted."""
#         if not v.endswith(".db"):
#             raise ValueError("Database name must end with '.db'")
#         return v

#     def __init__(self, **kwargs):
#         """Initialize the database and ensure all tables are created."""
#         super().__init__(**kwargs)

#         db_folder = paths.get("db_dir")
#         db_folder.mkdir(parents=True, exist_ok=True)

#         # Set the db_path if it's not provided
#         if not self.db_path:
#             self.db_path = db_folder / self.db_name

#         # Initialize database connection and cursor
#         self._conn = sqlite3.connect(self.db_path)
#         self._cursor = self._conn.cursor()
#         self._create_tables()

#     def __enter__(self):
#         """Enable context manager for database connection."""
#         if self._conn is None:
#             self._conn = sqlite3.connect(self.db_path)
#             self._cursor = self._conn.cursor()
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         """Exit the runtime context, ensuring the connection is closed."""
#         self.close()

#     def close(self):
#         """Close the database connection."""
#         self._conn.close()

#     def _create_tables(self):
#         """Create necessary tables in the SQLite database."""
#         """Create all tables in the database with foreign key constraints."""
#         schema_queries = [
#             """
#             CREATE TABLE IF NOT EXISTS PowerMeasure (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 type TEXT NOT NULL,
#                 voltage REAL NOT NULL,
#                 current REAL NOT NULL,
#                 power REAL NOT NULL,
#                 pf REAL NOT NULL
#             )
#             """,
#             """
#             CREATE TABLE IF NOT EXISTS OverLoad (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 load_percentage INTEGER NOT NULL,
#                 overload_time_min INTEGER NOT NULL
#             )
#             """,
#             """
#             CREATE TABLE IF NOT EXISTS spec (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 phase TEXT NOT NULL,
#                 rating_va INTEGER NOT NULL,
#                 rated_voltage INTEGER NOT NULL,
#                 rated_current INTEGER NOT NULL,
#                 min_input_voltage INTEGER NOT NULL,
#                 max_input_voltage INTEGER NOT NULL,
#                 pf_rated_current INTEGER NOT NULL,
#                 max_continous_amp INTEGER NOT NULL,
#                 overload_amp INTEGER NOT NULL,
#                 overload_long_id INTEGER NOT NULL,
#                 overload_medium_id INTEGER NOT NULL,
#                 overload_short_id INTEGER NOT NULL,
#                 avg_switch_time_ms INTEGER NOT NULL,
#                 avg_backup_time_ms INTEGER NOT NULL,
#                 FOREIGN KEY (overload_long_id) REFERENCES OverLoad (id) ,
#                 FOREIGN KEY (overload_medium_id) REFERENCES OverLoad (id) ,
#                 FOREIGN KEY (overload_short_id) REFERENCES OverLoad (id)
#             )
#             """,
#             """
#             CREATE TABLE IF NOT EXISTS ReportSettings (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 report_id INTEGER NOT NULL UNIQUE,
#                 standard TEXT NOT NULL,
#                 ups_model INTEGER NOT NULL,
#                 client_name TEXT NOT NULL,
#                 brand_name TEXT NOT NULL,
#                 test_engineer_name TEXT NOT NULL,
#                 test_approval_name TEXT NOT NULL,
#                 spec_id INTEGER NOT NULL,
#                 FOREIGN KEY (spec_id) REFERENCES spec (id)
#             )
#             """,
#             """
#             CREATE TABLE IF NOT EXISTS TestReport (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 settings_id INTEGER NOT NULL,
#                 test_name TEXT NOT NULL,
#                 test_description TEXT NOT NULL,
#                 input_power_id INTEGER NOT NULL,
#                 output_power_id INTEGER NOT NULL,
#                 FOREIGN KEY (settings_id) REFERENCES ReportSettings (id) ON DELETE CASCADE,
#                 FOREIGN KEY (input_power_id) REFERENCES PowerMeasure (id) ON DELETE CASCADE,
#                 FOREIGN KEY (output_power_id) REFERENCES PowerMeasure (id) ON DELETE CASCADE
#             )
#             """,
#         ]
#         try:
#             for query in schema_queries:
#                 self._cursor.execute(query)

#             self._conn.commit()
#         except sqlite3.Error as e:
#             raise Exception(f"Error creating tables: {e}")

#     @staticmethod
#     def _validate_non_negative_integer(value: Any, field_name: str):
#         if not isinstance(value, int) or value < 0:
#             raise ValueError(f"{field_name} must be a non-negative integer.")

#     @staticmethod
#     def _validate_non_negative_float(value: Any, field_name: str):
#         if not isinstance(value, (float, int)) or value < 0:
#             raise ValueError(f"{field_name} must be a non-negative float.")

#     @staticmethod
#     def _validate_pf(pf: Any):
#         if not isinstance(pf, (float, int)) or not (0 <= pf <= 1):
#             raise ValueError("Power factor must be between 0 and 1.")

#     def _validate_overload(self, overload: OverLoad):
#         """Validate OverLoad object."""
#         self._validate_non_negative_integer(overload.load_percentage, "load_percentage")
#         self._validate_non_negative_integer(
#             overload.overload_time_min, "overload_time_min"
#         )

#     def _validate_power_measure(self, power_measure: PowerMeasure):
#         """Validate PowerMeasure object."""
#         self._validate_non_negative_float(power_measure.voltage, "voltage")
#         self._validate_non_negative_float(power_measure.current, "current")
#         self._validate_non_negative_float(power_measure.power, "power")
#         self._validate_pf(power_measure.pf)

#     def _validate_spec(self, ups_spec: spec):
#         """Validate spec object."""
#         required_fields = [
#             ups_spec.Rating_va,
#             ups_spec.RatedVoltage_volt,
#             ups_spec.RatedCurrent_amp,
#             ups_spec.MinInputVoltage_volt,
#             ups_spec.MaxInputVoltage_volt,
#             ups_spec.pf_rated_current,
#             ups_spec.Max_Continous_Amp,
#             ups_spec.overload_Amp,
#             ups_spec.AvgSwitchTime_ms,
#             ups_spec.AvgBackupTime_ms,
#         ]
#         if not all(isinstance(field, int) and field >= 0 for field in required_fields):
#             raise ValueError(
#                 "Invalid spec field: all fields must be non-negative integers."
#             )

#         self._validate_overload(ups_spec.overload_long)
#         self._validate_overload(ups_spec.overload_medium)
#         self._validate_overload(ups_spec.overload_short)

#     def _validate_test_report(self, report: TestReport):
#         """Validate TestReport object."""
#         # Validate TestReport settings
#         if not isinstance(report.settings, ReportSettings):
#             raise ValueError("Invalid settings: Must be a ReportSettings object.")

#         # Validate input and output PowerMeasure
#         if not isinstance(report.inputPower, PowerMeasure):
#             raise ValueError("Invalid inputPower: Must be a PowerMeasure object.")
#         self._validate_power_measure(report.inputPower)

#         if not isinstance(report.outputpower, PowerMeasure):
#             raise ValueError("Invalid outputpower: Must be a PowerMeasure object.")
#         self._validate_power_measure(report.outputpower)

#         # Validate testName
#         if (
#             not isinstance(report.testName, int)
#             or report.testName not in TestType.values()
#         ):
#             raise ValueError("Invalid testName: Must be a TestType enum value.")

#         # Validate testDescription
#         if (
#             not isinstance(report.testDescription, str)
#             or not report.testDescription.strip()
#         ):
#             raise ValueError("Invalid testDescription: Must be a non-empty string.")

#     def _check_id_exists(self, table_name: str, entry_id: int):
#         """Check if an entry with the given ID exists in the specified table."""
#         try:
#             self._cursor.execute(
#                 f"SELECT 1 FROM {table_name} WHERE id = ?", (entry_id,)
#             )
#             return self._cursor.fetchone() is not None
#         except sqlite3.Error as e:
#             raise Exception(f"Error checking ID existence in {table_name}: {e}")

#     def _check_value_exists(self, table_name: str, column_name: str, value: any):
#         """
#         Check if a specific value exists in a given column of a table.

#         Args:
#             table_name (str): Name of the table to query.
#             column_name (str): Name of the column to check.
#             value (any): Value to search for in the specified column.

#         Returns:
#             bool: True if the value exists, False otherwise.
#         """
#         try:
#             query = f"SELECT 1 FROM {table_name} WHERE {column_name} = ?"
#             self._cursor.execute(query, (value,))
#             return self._cursor.fetchone() is not None
#         except sqlite3.Error as e:
#             raise Exception(f"Error checking value in {table_name}.{column_name}: {e}")

#     def insert_overload(self, overload: OverLoad):
#         """Insert an OverLoad message into the database or return the existing entry if it already exists."""
#         self._validate_overload(overload)
#         try:
#             # Check if the same OverLoad already exists
#             self._cursor.execute(
#                 """
#                 SELECT id
#                 FROM OverLoad
#                 WHERE load_percentage = ? AND overload_time_min = ?
#                 """,
#                 (overload.load_percentage, overload.overload_time_min),
#             )
#             existing_id = self._cursor.fetchone()

#             if existing_id:
#                 # Return the existing ID if a match is found
#                 return existing_id[0]

#             # Insert a new OverLoad entry if no match exists
#             self._cursor.execute(
#                 """
#                 INSERT INTO OverLoad (load_percentage, overload_time_min)
#                 VALUES (?, ?)
#                 """,
#                 (overload.load_percentage, overload.overload_time_min),
#             )
#             self._conn.commit()

#             # Return the newly inserted row ID
#             return self._cursor.lastrowid

#         except sqlite3.Error as e:
#             raise Exception(f"Error inserting OverLoad: {e}")

#     def insert_power_measure(self, power: PowerMeasure):
#         """Insert a PowerMeasure message into the database."""
#         self._validate_power_measure(power)
#         try:
#             power_type_name = PowerMeasureType.Name(power.type)
#             self._cursor.execute(
#                 """
#                 INSERT INTO PowerMeasure (type, voltage, current, power, pf)
#                 VALUES (?, ?, ?, ?, ?)
#             """,
#                 (
#                     power_type_name,  # Enum to string
#                     power.voltage,
#                     power.current,
#                     power.power,
#                     power.pf,
#                 ),
#             )
#             self._conn.commit()
#             return self._cursor.lastrowid
#         except sqlite3.Error as e:
#             raise Exception(f"Error inserting PowerMeasure: {e}")

#     def insert_spec(self, ups_spec: spec):
#         """Insert a spec message into the database or return the existing entry if it already exists."""
#         self._validate_spec(ups_spec)

#         try:
#             # Insert overload entries and get their IDs
#             phase_name = Phase.Name(ups_spec.phase)
#             overload_long_id = self.insert_overload(ups_spec.overload_long)
#             overload_medium_id = self.insert_overload(ups_spec.overload_medium)
#             overload_short_id = self.insert_overload(ups_spec.overload_short)

#             # Check if the same spec already exists
#             self._cursor.execute(
#                 """
#                 SELECT id
#                 FROM spec
#                 WHERE phase = ? AND rating_va = ? AND rated_voltage = ? AND rated_current = ?
#                 AND min_input_voltage = ? AND max_input_voltage = ? AND pf_rated_current = ?
#                 AND max_continous_amp = ? AND overload_amp = ?
#                 AND overload_long_id = ? AND overload_medium_id = ? AND overload_short_id = ?
#                 AND avg_switch_time_ms = ? AND avg_backup_time_ms = ?
#                 """,
#                 (
#                     phase_name,  # Enum converted to string
#                     ups_spec.Rating_va,
#                     ups_spec.RatedVoltage_volt,
#                     ups_spec.RatedCurrent_amp,
#                     ups_spec.MinInputVoltage_volt,
#                     ups_spec.MaxInputVoltage_volt,
#                     ups_spec.pf_rated_current,
#                     ups_spec.Max_Continous_Amp,
#                     ups_spec.overload_Amp,
#                     overload_long_id,
#                     overload_medium_id,
#                     overload_short_id,
#                     ups_spec.AvgSwitchTime_ms,
#                     ups_spec.AvgBackupTime_ms,
#                 ),
#             )
#             existing_id = self._cursor.fetchone()

#             if existing_id:
#                 # Return the existing ID if a match is found
#                 return existing_id[0]

#             # Insert a new spec entry if no match exists
#             self._cursor.execute(
#                 """
#                 INSERT INTO spec (
#                     phase, rating_va, rated_voltage, rated_current,
#                     min_input_voltage, max_input_voltage, pf_rated_current,
#                     max_continous_amp, overload_amp,
#                     overload_long_id, overload_medium_id, overload_short_id,
#                     avg_switch_time_ms, avg_backup_time_ms
#                 )
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """,
#                 (
#                     phase_name,
#                     ups_spec.Rating_va,
#                     ups_spec.RatedVoltage_volt,
#                     ups_spec.RatedCurrent_amp,
#                     ups_spec.MinInputVoltage_volt,
#                     ups_spec.MaxInputVoltage_volt,
#                     ups_spec.pf_rated_current,
#                     ups_spec.Max_Continous_Amp,
#                     ups_spec.overload_Amp,
#                     overload_long_id,
#                     overload_medium_id,
#                     overload_short_id,
#                     ups_spec.AvgSwitchTime_ms,
#                     ups_spec.AvgBackupTime_ms,
#                 ),
#             )
#             self._conn.commit()

#             # Return the newly inserted row ID
#             return self._cursor.lastrowid

#         except sqlite3.Error as e:
#             raise Exception(f"Error inserting spec: {e}")

#     def insert_report_settings(self, settings: ReportSettings):
#         """Insert ReportSettings into the database."""
#         try:
#             # Check if report_id already exists
#             if self._check_value_exists(
#                 "ReportSettings", "report_id", settings.report_id
#             ):
#                 logging.debug(
#                     "ReportSettings with report_id %s already exists.",
#                     settings.report_id,
#                 )
#                 # Optionally, return the existing ID
#                 self._cursor.execute(
#                     "SELECT id FROM ReportSettings WHERE report_id = ?",
#                     (settings.report_id,),
#                 )
#                 return self._cursor.fetchone()[0]

#             # Insert spec first, since it's a foreign key reference
#             spec_id = self.insert_spec(settings.spec)

#             # Insert ReportSettings data
#             self._cursor.execute(
#                 """
#                 INSERT INTO ReportSettings (
#                     report_id, standard, ups_model, client_name, brand_name,
#                     test_engineer_name, test_approval_name, spec_id
#                 )
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#                 """,
#                 (
#                     settings.report_id,
#                     TestStandard.Name(settings.standard),  # Convert Enum to string
#                     settings.ups_model,
#                     settings.client_name,
#                     settings.brand_name,
#                     settings.test_engineer_name,
#                     settings.test_approval_name,
#                     spec_id,
#                 ),
#             )
#             self._conn.commit()

#             # Return the last inserted row ID
#             return self._cursor.lastrowid

#         except sqlite3.Error as e:
#             raise Exception(f"Error inserting ReportSettings: {e}")

#         except Exception as e:
#             # Catch any other unexpected exceptions
#             raise Exception(f"Unexpected error inserting ReportSettings: {e}")

#     def insert_test_report(self, report: TestReport):
#         """Insert a TestReport message into the database."""
#         logging.debug(
#             "Inserting TestReport: %s with report_id %d",
#             report,
#             report.settings.report_id,
#         )
#         self._validate_test_report(report)

#         try:
#             # Convert the TestType enum to its string name
#             test_name = TestType.Name(report.testName)

#             # Check if report_id exists and handle accordingly
#             if self._check_value_exists(
#                 "ReportSettings", "report_id", report.settings.report_id
#             ):
#                 # If the report_id already exists, fetch its settings_id
#                 logging.debug(
#                     "ReportSettings with report_id %d already exists.",
#                     report.settings.report_id,
#                 )
#                 self._cursor.execute(
#                     "SELECT id FROM ReportSettings WHERE report_id = ?",
#                     (report.settings.report_id,),
#                 )
#                 settings_id = self._cursor.fetchone()[0]
#             else:
#                 # Insert new ReportSettings and get its ID
#                 logging.debug(
#                     "Creating new ReportSettings for report_id %d.",
#                     report.settings.report_id,
#                 )
#                 settings_id = self.insert_report_settings(report.settings)

#             # Check if a TestReport with this settings_id already exists
#             self._cursor.execute(
#                 "SELECT id, input_power_id, output_power_id FROM TestReport WHERE settings_id = ?",
#                 (settings_id,),
#             )
#             test_report_row = self._cursor.fetchone()

#             if test_report_row:
#                 # If TestReport exists, reuse the existing PowerMeasure IDs
#                 test_report_id = test_report_row[0]
#                 input_power_id = test_report_row[1]
#                 output_power_id = test_report_row[2]
#                 logging.debug(
#                     "Updating existing TestReport with id %d for settings_id %d.",
#                     test_report_id,
#                     settings_id,
#                 )
#                 # Update the existing TestReport
#                 self._cursor.execute(
#                     """
#                     UPDATE TestReport
#                     SET test_name = ?, test_description = ?
#                     WHERE id = ?
#                     """,
#                     (
#                         test_name,
#                         report.testDescription,
#                         test_report_id,
#                     ),
#                 )
#             else:
#                 # Insert new PowerMeasure objects
#                 logging.debug("Creating new PowerMeasure entries for the TestReport.")
#                 input_power_id = self.insert_power_measure(report.inputPower)
#                 output_power_id = self.insert_power_measure(report.outputpower)

#                 # Insert a new TestReport
#                 logging.debug(
#                     "Inserting new TestReport for settings_id %d.", settings_id
#                 )
#                 self._cursor.execute(
#                     """
#                     INSERT INTO TestReport (
#                         settings_id, test_name, test_description, input_power_id, output_power_id
#                     )
#                     VALUES (?, ?, ?, ?, ?)
#                     """,
#                     (
#                         settings_id,
#                         test_name,
#                         report.testDescription,
#                         input_power_id,
#                         output_power_id,
#                     ),
#                 )
#                 test_report_id = self._cursor.lastrowid

#             # Commit the transaction to save changes
#             self._conn.commit()

#             # Return the ID of the TestReport
#             return test_report_id

#         except sqlite3.Error as e:
#             # Catch and handle SQLite-specific errors
#             raise Exception(f"Error inserting/updating TestReport into database: {e}")

#         except Exception as e:
#             # Catch and handle any other exceptions
#             raise Exception(f"Unexpected error inserting/updating TestReport: {e}")

#     def get_test_report(self, report_id: int):
#         """Retrieve a TestReport and related data from the database by report ID."""
#         try:
#             # Fetch the TestReport details
#             self._cursor.execute(
#                 """
#                 SELECT
#                     TestReport.id,
#                     TestReport.test_name,
#                     TestReport.test_description,
#                     ReportSettings.report_id,
#                     ReportSettings.standard,
#                     ReportSettings.ups_model,
#                     ReportSettings.client_name,
#                     ReportSettings.brand_name,
#                     ReportSettings.test_engineer_name,
#                     ReportSettings.test_approval_name,
#                     PowerMeasure1.type AS input_type,
#                     PowerMeasure1.voltage AS input_voltage,
#                     PowerMeasure1.current AS input_current,
#                     PowerMeasure1.power AS input_power,
#                     PowerMeasure1.pf AS input_pf,
#                     PowerMeasure2.type AS output_type,
#                     PowerMeasure2.voltage AS output_voltage,
#                     PowerMeasure2.current AS output_current,
#                     PowerMeasure2.power AS output_power,
#                     PowerMeasure2.pf AS output_pf
#                 FROM
#                     TestReport
#                 JOIN
#                     ReportSettings ON TestReport.settings_id = ReportSettings.id
#                 JOIN
#                     PowerMeasure AS PowerMeasure1 ON TestReport.input_power_id = PowerMeasure1.id
#                 JOIN
#                     PowerMeasure AS PowerMeasure2 ON TestReport.output_power_id = PowerMeasure2.id
#                 WHERE
#                     ReportSettings.report_id = ?
#             """,
#                 (report_id,),
#             )
#             result = self._cursor.fetchone()
#             if not result:
#                 return None

#             # Map the fetched data to a dictionary or a structured object
#             report = {
#                 "test_report_id": result[0],
#                 "test_name": result[1],
#                 "test_description": result[2],
#                 "settings": {
#                     "report_id": result[3],
#                     "standard": result[4],
#                     "ups_model": result[5],
#                     "client_name": result[6],
#                     "brand_name": result[7],
#                     "test_engineer_name": result[8],
#                     "test_approval_name": result[9],
#                 },
#                 "input_power": {
#                     "type": result[10],
#                     "voltage": result[11],
#                     "current": result[12],
#                     "power": result[13],
#                     "pf": result[14],
#                 },
#                 "output_power": {
#                     "type": result[15],
#                     "voltage": result[16],
#                     "current": result[17],
#                     "power": result[18],
#                     "pf": result[19],
#                 },
#             }
#             return report
#         except sqlite3.Error as e:
#             raise Exception(f"Error retrieving TestReport: {e}")

#     def get_latest_test_report(self):
#         """Retrieve the latest TestReport and its associated data."""
#         try:
#             # Fetch the latest TestReport
#             self._cursor.execute(
#                 """
#                 SELECT
#                     TestReport.id,
#                     TestReport.test_name,
#                     TestReport.test_description,
#                     ReportSettings.report_id,
#                     ReportSettings.standard,
#                     ReportSettings.ups_model,
#                     ReportSettings.client_name,
#                     ReportSettings.brand_name,
#                     ReportSettings.test_engineer_name,
#                     ReportSettings.test_approval_name,
#                     PowerMeasure1.type AS input_type,
#                     PowerMeasure1.voltage AS input_voltage,
#                     PowerMeasure1.current AS input_current,
#                     PowerMeasure1.power AS input_power,
#                     PowerMeasure1.pf AS input_pf,
#                     PowerMeasure2.type AS output_type,
#                     PowerMeasure2.voltage AS output_voltage,
#                     PowerMeasure2.current AS output_current,
#                     PowerMeasure2.power AS output_power,
#                     PowerMeasure2.pf AS output_pf
#                 FROM
#                     TestReport
#                 JOIN
#                     ReportSettings ON TestReport.settings_id = ReportSettings.id
#                 JOIN
#                     PowerMeasure AS PowerMeasure1 ON TestReport.input_power_id = PowerMeasure1.id
#                 JOIN
#                     PowerMeasure AS PowerMeasure2 ON TestReport.output_power_id = PowerMeasure2.id
#                 ORDER BY
#                     TestReport.id DESC
#                 LIMIT 1
#             """
#             )
#             result = self._cursor.fetchone()
#             if not result:
#                 return None

#             # Map the fetched data to a dictionary or structured object
#             report = {
#                 "test_report_id": result[0],
#                 "test_name": result[1],
#                 "test_description": result[2],
#                 "settings": {
#                     "report_id": result[3],
#                     "standard": result[4],
#                     "ups_model": result[5],
#                     "client_name": result[6],
#                     "brand_name": result[7],
#                     "test_engineer_name": result[8],
#                     "test_approval_name": result[9],
#                 },
#                 "input_power": {
#                     "type": result[10],
#                     "voltage": result[11],
#                     "current": result[12],
#                     "power": result[13],
#                     "pf": result[14],
#                 },
#                 "output_power": {
#                     "type": result[15],
#                     "voltage": result[16],
#                     "current": result[17],
#                     "power": result[18],
#                     "pf": result[19],
#                 },
#             }
#             return report
#         except sqlite3.Error as e:
#             raise Exception(f"Error retrieving the latest TestReport: {e}")

#     def get_all_report_id_testName(self):
#         """Retrieve all TestReport IDs and their corresponding test names."""
#         try:
#             self._cursor.execute(
#                 """
#                 SELECT id, test_name
#                 FROM TestReport
#                 """
#             )
#             results = self.cursor.fetchall()
#             return [{"report_id": row[0], "test_name": row[1]} for row in results]
#         except sqlite3.Error as e:
#             raise Exception(f"Error retrieving TestReport IDs and test names: {e}")

#     def _delete_entry(self, table_name: str, entry_id: int):
#         """Delete an entry from the specified table if it exists."""
#         if not self._check_id_exists(table_name, entry_id):
#             raise ValueError(
#                 f"Entry with ID {entry_id} does not exist in {table_name}."
#             )

#         try:
#             self._cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (entry_id,))
#             self._conn.commit()
#             return f"Entry with ID {entry_id} successfully deleted from {table_name}."
#         except sqlite3.Error as e:
#             raise Exception(f"Error deleting entry from {table_name}: {e}")

#     def delete_overload(self, overload_id: int):
#         """Delete an OverLoad entry by ID."""
#         try:
#             return self._delete_entry("OverLoad", overload_id)
#         except ValueError as ve:
#             return str(ve)
#         except Exception as e:
#             raise Exception(f"Unexpected error while deleting OverLoad: {e}")

#     def delete_power_measure(self, power_measure_id: int):
#         """Delete a PowerMeasure entry by ID."""
#         try:
#             return self._delete_entry("PowerMeasure", power_measure_id)
#         except ValueError as ve:
#             return str(ve)
#         except Exception as e:
#             raise Exception(f"Unexpected error while deleting PowerMeasure: {e}")

#     def delete_spec(self, spec_id: int, cascading: bool = True):
#         """
#         Deletes a spec entry by ID. If cascading is True, it also deletes related OverLoad entries.
#         """
#         try:
#             # Check if the spec entry exists
#             if not self._check_id_exists("spec", spec_id):
#                 raise ValueError(f"spec with ID {spec_id} does not exist.")

#             if cascading:
#                 # Get OverLoad IDs associated with the spec
#                 self._cursor.execute(
#                     """
#                     SELECT overload_long_id, overload_medium_id, overload_short_id
#                     FROM spec WHERE id = ?
#                     """,
#                     (spec_id,),
#                 )
#                 overload_ids = self._cursor.fetchone()

#                 # Delete related OverLoad entries
#                 if overload_ids:
#                     for overload_id in overload_ids:
#                         if overload_id:
#                             self._delete_entry("OverLoad", overload_id)

#             # Delete the spec entry
#             self._delete_entry("spec", spec_id)
#             self._conn.commit()

#             if cascading:
#                 return f"spec with ID {spec_id} and related OverLoad entries deleted."
#             else:
#                 return f"spec with ID {spec_id} deleted without affecting related OverLoad entries."

#         except sqlite3.Error as e:
#             raise Exception(f"Error deleting spec with ID {spec_id}: {e}")
#         except ValueError as ve:
#             return str(ve)

#     def delete_report_settings(self, settings_id: int, cascading: bool = True):
#         """
#         Deletes a ReportSettings entry by ID along with its related spec entry.
#         """
#         try:
#             if cascading:
#                 # Check if the ReportSettings entry exists
#                 if not self._check_id_exists("ReportSettings", settings_id):
#                     raise ValueError(
#                         f"ReportSettings with ID {settings_id} does not exist."
#                     )

#                 # Get the related spec_id
#                 self._cursor.execute(
#                     "SELECT spec_id FROM ReportSettings WHERE id = ?", (settings_id,)
#                 )
#                 spec_row = self._cursor.fetchone()
#                 if spec_row:
#                     spec_id = spec_row[0]
#                     if spec_id:
#                         self.delete_spec(spec_id)  # Cascade to delete the spec

#             # Delete the ReportSettings entry
#             self._delete_entry("ReportSettings", settings_id)
#             self._conn.commit()
#             if cascading:
#                 return f"ReportSettings with ID {settings_id} and related spec deleted."
#             else:
#                 return f"ReportSettings with ID {settings_id} deleted without affecting related spec entries."
#         except sqlite3.Error as e:
#             raise Exception(f"Error deleting ReportSettings with ID {settings_id}: {e}")
#         except ValueError as ve:
#             return str(ve)

#     def delete_test_report(self, test_report_id: int, cascading: bool = True):
#         """
#         Deletes a TestReport entry by ID along with all its related entries.
#         This includes cascading deletions for associated entries in:
#         - ReportSettings
#         - PowerMeasure (input and output)
#         """
#         try:
#             if cascading:
#                 # Check if the TestReport exists
#                 if not self._check_id_exists("TestReport", test_report_id):
#                     raise ValueError(
#                         f"TestReport with ID {test_report_id} does not exist."
#                     )

#                 # Get related ReportSettings ID and PowerMeasure IDs
#                 self._cursor.execute(
#                     "SELECT settings_id, input_power_id, output_power_id FROM TestReport WHERE id = ?",
#                     (test_report_id,),
#                 )
#                 row = self._cursor.fetchone()
#                 if row is None:
#                     raise ValueError(
#                         f"No data found for TestReport with ID {test_report_id}."
#                     )

#                 settings_id, input_power_id, output_power_id = row

#                 # Delete related PowerMeasure entries
#                 if input_power_id:
#                     self._delete_entry("PowerMeasure", input_power_id)
#                 if output_power_id:
#                     self._delete_entry("PowerMeasure", output_power_id)

#                 # Delete related ReportSettings and cascade to spec
#                 if settings_id:
#                     try:
#                         self.delete_report_settings(settings_id)
#                     except Exception as e:
#                         raise Exception(
#                             f"Failed to delete ReportSettings with ID {settings_id}: {e}"
#                         )

#             # Finally, delete the TestReport itself
#             self._delete_entry("TestReport", test_report_id)
#             self._conn.commit()
#             if cascading:
#                 return f"TestReport with ID {test_report_id} and all related entries have been deleted."
#             else:
#                 return f"TestReport with ID {test_report_id} deleted without affecting related reportsettings,powermeasure entries."
#         except sqlite3.Error as e:
#             raise Exception(f"Error deleting TestReport with ID {test_report_id}: {e}")
#         except ValueError as ve:
#             return str(ve)

#     def clean_database(self):
#         """Clean up the database by removing duplicate and orphaned entries."""
#         try:
#             # Step 1: Remove duplicate PowerMeasure entries
#             logging.debug("Removing duplicate PowerMeasure entries.")
#             self._cursor.execute(
#                 """
#                 DELETE FROM PowerMeasure
#                 WHERE id NOT IN (
#                     SELECT MIN(id)
#                     FROM PowerMeasure
#                     GROUP BY type, voltage, current, power, pf
#                 )
#                 """
#             )

#             # Step 2: Remove unused PowerMeasure entries
#             logging.debug("Removing unused PowerMeasure entries.")
#             self._cursor.execute(
#                 """
#                 DELETE FROM PowerMeasure
#                 WHERE id NOT IN (
#                     SELECT input_power_id FROM TestReport
#                     UNION
#                     SELECT output_power_id FROM TestReport
#                 )
#                 """
#             )

#             # Step 3: Remove unused OverLoad entries
#             logging.debug("Removing unused OverLoad entries.")
#             self._cursor.execute(
#                 """
#                 DELETE FROM OverLoad
#                 WHERE id NOT IN (
#                     SELECT overload_long_id FROM spec
#                     UNION
#                     SELECT overload_medium_id FROM spec
#                     UNION
#                     SELECT overload_short_id FROM spec
#                 )
#                 """
#             )

#             # Step 4: Remove orphaned ReportSettings
#             logging.debug("Removing orphaned ReportSettings entries.")
#             self._cursor.execute(
#                 """
#                 DELETE FROM ReportSettings
#                 WHERE id NOT IN (
#                     SELECT settings_id FROM TestReport
#                 )
#             """
#             )

#             # Step 5: Remove orphaned spec entries
#             logging.debug("Removing orphaned spec entries.")
#             self._cursor.execute(
#                 """
#                 DELETE FROM spec
#                 WHERE id NOT IN (
#                     SELECT spec_id FROM ReportSettings
#                 )
#                 """
#             )

#             # Commit the changes
#             self._conn.commit()
#             logging.info("Database cleanup completed successfully.")

#         except sqlite3.Error as e:
#             # Handle SQLite errors
#             logging.error(f"Error during database cleanup: {e}")
#             raise Exception(f"Error during database cleanup: {e}")

#         except Exception as e:
#             # Handle unexpected errors
#             logging.error(f"Unexpected error during database cleanup: {e}")
#             raise Exception(f"Unexpected error during database cleanup: {e}")

#     def generate_mock_data(self, reportId, clientname, brandname, engineername):
#         # Example PowerMeasure objects
#         input_power = PowerMeasure(
#             type=PowerMeasureType.UPS_INPUT,
#             voltage=230.0,
#             current=10.0,
#             power=2300.0,
#             pf=0.98,
#         )
#         output_power = PowerMeasure(
#             type=PowerMeasureType.UPS_OUTPUT,
#             voltage=220.0,
#             current=10.5,
#             power=2310.0,
#             pf=0.97,
#         )
#         overload_long = OverLoad(load_percentage=110, overload_time_min=10)
#         overload_medium = OverLoad(load_percentage=125, overload_time_min=5)
#         overload_short = OverLoad(load_percentage=150, overload_time_min=2)

#         # Example spec object
#         ups_spec = spec(
#             phase=Phase.SINGLE_PHASE,
#             Rating_va=5000,
#             RatedVoltage_volt=230,
#             RatedCurrent_amp=21,
#             MinInputVoltage_volt=200,
#             MaxInputVoltage_volt=240,
#             pf_rated_current=1,
#             Max_Continous_Amp=25,
#             overload_Amp=30,
#             overload_long=overload_long,
#             overload_medium=overload_medium,
#             overload_short=overload_short,
#             AvgSwitchTime_ms=500,
#             AvgBackupTime_ms=120000,
#         )

#         # Example ReportSettings object
#         settings = ReportSettings(
#             report_id=reportId,
#             standard=TestStandard.IEC_62040_3,
#             ups_model=101,
#             client_name=clientname,
#             brand_name=brandname,
#             test_engineer_name=engineername,
#             test_approval_name="Jane Smith",
#             spec=ups_spec,
#         )

#         # Example TestReport object
#         report = TestReport(
#             settings=settings,
#             testName=TestType.FULL_LOAD_TEST,
#             testDescription="Full load test for the UPS system",
#             inputPower=input_power,
#             outputpower=output_power,
#         )

#         print("generated mock report for client :", clientname)
#         # Close database connection

#         return report


# # Example Usage
# if __name__ == "__main__":
#     data_manager = DataManager()
#     report = data_manager.generate_mock_data(2, "walton", "maxgreen", "fhr")

#     report_id = data_manager.insert_test_report(report)
#     unique_id = report.settings.report_id
#     print(
#         f"check newly inserted test report with id {report_id} for unique id {unique_id} "
#     )
#     report = data_manager.generate_mock_data(3, "walton", "maxgreen", "fhr")

#     report_id = data_manager.insert_test_report(report)
#     unique_id = report.settings.report_id
#     print(
#         f"check newly inserted test report with id {report_id} for unique id {unique_id} "
#     )
#     # print(f"Deleting TestReport with ID {report_id}")
#     # print(data_manager.delete_test_report(report_id))

#     # Close database connection
#     data_manager.close()


# def aggregate_report_data(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
#     """
#     Aggregates data from a list of rows into a hierarchical structure.
#     Args:
#         rows (list): List of dictionaries containing report data.
#     Returns:
#         dict: Aggregated report data.
#     """
#     if not rows:
#         raise ValueError("No rows provided to aggregate")

#     if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
#         raise TypeError("Rows must be a list of dictionaries")

#     # Start with the first row
#     aggregated = {
#         "test_report_id": rows[0]["test_report_id"],
#         "test_name": rows[0]["test_name"],
#         "test_description": rows[0]["test_description"],
#         "test_result": rows[0]["test_result"],
#         "client_name": rows[0]["client_name"],
#         "standard": rows[0]["standard"],
#         "ups_model": rows[0]["ups_model"],
#         "measurements": [],  # This will hold the list of measurements
#     }

#     # Group data for measurements and power measures
#     measurements = defaultdict(lambda: {"power_measures": []})

#     for row in rows:
#         measurement_id = row["measurement_unique_id"]
#         measurement = measurements[measurement_id]

#         # Only update measurement details once
#         if not measurement.get("measurement_name"):
#             measurement.update(
#                 {
#                     "measurement_unique_id": row.get("measurement_unique_id"),
#                     "measurement_name": row.get("measurement_name"),
#                     "measurement_timestamp": row.get("measurement_timestamp"),
#                     "measurement_loadtype": row.get("measurement_loadtype"),
#                     "load_percentage": row.get("load_percentage", 0),  # Default to 0 if missing
#                     "phase_name": row.get("phase_name", "Unknown"),  # Default to "Unknown" if missing
#                     "step_id": row.get("step_id", 0),  # Default to 0 if missing
#                     "steady_state_voltage_tol": row.get("steady_state_voltage_tol", 0),  # Default to 0 if missing
#                     "voltage_dc_component": row.get("voltage_dc_component", 0),  # Default to 0 if missing
#                     "load_pf_deviation": row.get("load_pf_deviation", 0),  # Default to 0 if missing
#                     "switch_time_ms": row.get("switch_time_ms", 0),  # Default to 0 if missing
#                     "run_interval_sec": row.get("run_interval_sec", 0),  # Default to 0 if missing
#                     "backup_time_sec": row.get("backup_time_sec", 0),  # Default to 0 if missing
#                     "overload_time_sec": row.get("overload_time_sec", 0),  # Default to 0 if missing
#                     "temperature_1": row.get("temperature_1", 0),  # Default to 0 if missing
#                     "temperature_2": row.get("temperature_2", 0),  # Default to 0 if missing
#                 }
#             )

#         # Add power measures to this measurement
#         if row.get("power_measure_id"):
#             measurement["power_measures"].append(
#                 {
#                     "power_measure_id": row["power_measure_id"],
#                     "power_measure_type": row["power_measure_type"],
#                     "power_measure_name": row["power_measure_name"],
#                     "power_measure_voltage": row["power_measure_voltage"],
#                     "power_measure_current": row["power_measure_current"],
#                     "power_measure_power": row["power_measure_power"],
#                     "power_measure_pf": row["power_measure_pf"],
#                 }
#             )

#     # Convert measurements to a list and add to the report
#     for index, measurement in enumerate(measurements.values()):  # Add index here
#         # Create a flattened list for each measurement
#         measurement_data = {
#             f"measurements_{index}_measurement_unique_id": measurement["measurement_unique_id"],
#             f"measurements_{index}_measurement_name": measurement["measurement_name"],
#             f"measurements_{index}_measurement_timestamp": measurement["measurement_timestamp"],
#             f"measurements_{index}_measurement_loadtype": measurement["measurement_loadtype"],
#             f"measurements_{index}_load_percentage": measurement["load_percentage"],
#             f"measurements_{index}_phase_name": measurement["phase_name"],
#             f"measurements_{index}_step_id": measurement["step_id"],
#             f"measurements_{index}_steady_state_voltage_tol": measurement["steady_state_voltage_tol"],
#             f"measurements_{index}_voltage_dc_component": measurement["voltage_dc_component"],
#             f"measurements_{index}_load_pf_deviation": measurement["load_pf_deviation"],
#             f"measurements_{index}_switch_time_ms": measurement["switch_time_ms"],
#             f"measurements_{index}_run_interval_sec": measurement["run_interval_sec"],
#             f"measurements_{index}_backup_time_sec": measurement["backup_time_sec"],
#             f"measurements_{index}_overload_time_sec": measurement["overload_time_sec"],
#             f"measurements_{index}_temperature_1": measurement["temperature_1"],
#             f"measurements_{index}_temperature_2": measurement["temperature_2"],
#         }

#         # Add power measures after the measurement data
#         for i, power_measure in enumerate(measurement["power_measures"]):
#             measurement_data.update({
#                 f"measurements_{index}_power_measures_{i}_power_measure_id": power_measure["power_measure_id"],
#                 f"measurements_{index}_power_measures_{i}_power_measure_type": power_measure["power_measure_type"],
#                 f"measurements_{index}_power_measures_{i}_power_measure_name": power_measure["power_measure_name"],
#                 f"measurements_{index}_power_measures_{i}_power_measure_voltage": power_measure["power_measure_voltage"],
#                 f"measurements_{index}_power_measures_{i}_power_measure_current": power_measure["power_measure_current"],
#                 f"measurements_{index}_power_measures_{i}_power_measure_power": power_measure["power_measure_power"],
#                 f"measurements_{index}_power_measures_{i}_power_measure_pf": power_measure["power_measure_pf"],
#             })

#         # Add the measurement data with power measures to the final report
#         aggregated["measurements"].append(measurement_data)

#     return aggregated


# def aggregate_report_data(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
#     """
#     Aggregates data from a list of rows into a hierarchical structure.
#     Args:
#         rows (list): List of dictionaries containing report data.
#     Returns:
#         dict: Aggregated report data.
#     """
#     if not rows:
#         raise ValueError("No rows provided to aggregate")
#     if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
#         raise TypeError("Rows must be a list of dictionaries")

#     # Initialize the aggregated report with basic details from the first row
#     aggregated = {key: rows[0][key] for key in [
#         "test_report_id", "test_name", "test_description",
#         "test_result", "client_name", "standard", "ups_model"
#     ]}
#     aggregated["measurements"] = []

#     # Group and aggregate measurements
#     measurements = defaultdict(lambda: {
#         **{key: None for key in [
#             "measurement_unique_id", "measurement_name", "measurement_timestamp",
#             "measurement_loadtype", "load_percentage", "phase_name", "step_id",
#             "steady_state_voltage_tol", "voltage_dc_component", "load_pf_deviation",
#             "switch_time_ms", "run_interval_sec", "backup_time_sec",
#             "overload_time_sec", "temperature_1", "temperature_2"
#         ]},
#         "power_measures": []
#     })

#     for row in rows:
#         measurement = measurements[row["measurement_unique_id"]]
#         if not measurement["measurement_name"]:  # Fill measurement details only once
#             measurement.update({
#                 key: row.get(key, 0 if "time" in key or "tol" in key else "Unknown")
#                 for key in measurement if key != "power_measures"
#             })
#         if row.get("power_measure_id"):
#             measurement["power_measures"].append({
#                 key: row[key] for key in [
#                     "power_measure_id", "power_measure_type", "power_measure_name",
#                     "power_measure_voltage", "power_measure_current", "power_measure_power", "power_measure_pf"
#                 ]
#             })

#     # Add ordered measurements with power measures to the final report
#     for index, (measurement_id, measurement) in enumerate(measurements.items()):
#         measurement_data = {
#             f"measurements_{index}_{key}": value for key, value in measurement.items()
#             if key != "power_measures"
#         }
#         for i, power_measure in enumerate(measurement["power_measures"]):
#             measurement_data.update({
#                 f"measurements_{index}_power_measures_{i}_{key}": value
#                 for key, value in power_measure.items()
#             })
#         aggregated["measurements"].append(measurement_data)

#     return aggregated


# def aggregate_report_data(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
#     """
#     Aggregates data from a list of rows into a hierarchical structure.
#     Args:
#         rows (list): List of dictionaries containing report data.
#     Returns:
#         dict: Aggregated report data.
#     """
#     if not rows:
#         raise ValueError("No rows provided to aggregate")
#     if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
#         raise TypeError("Rows must be a list of dictionaries")

#     # Mandatory keys
#     mandatory_keys = {
#         "measurement_unique_id",
#         "measurement_name",
#         "measurement_timestamp",
#     }

#     # Validate rows for mandatory keys
#     for row in rows:
#         missing_keys = mandatory_keys - row.keys()
#         if missing_keys:
#             raise ValueError(f"Missing mandatory keys {missing_keys} in row: {row}")

#     # Initialize the aggregated report with basic details from the first row
#     aggregated = {
#         key: rows[0][key]
#         for key in [
#             "test_report_id",
#             "test_name",
#             "test_description",
#             "test_result",
#             "client_name",
#             "standard",
#             "ups_model",
#         ]
#     }
#     aggregated["measurements"] = []

#     # Group and aggregate measurements
#     measurements = defaultdict(
#         lambda: {
#             **{
#                 key: None
#                 for key in [
#                     "measurement_unique_id",
#                     "measurement_name",
#                     "measurement_timestamp",
#                     "measurement_loadtype",
#                     "load_percentage",
#                     "phase_name",
#                     "step_id",
#                     "steady_state_voltage_tol",
#                     "voltage_dc_component",
#                     "load_pf_deviation",
#                     "switch_time_ms",
#                     "run_interval_sec",
#                     "backup_time_sec",
#                     "overload_time_sec",
#                     "temperature_1",
#                     "temperature_2",
#                 ]
#             },
#             "power_measures": [],
#         }
#     )

#     for row in rows:
#         measurement = measurements[row["measurement_unique_id"]]
#         if not measurement[
#             "measurement_name"
#         ]:  # Fill measurement details only once
#             measurement.update(
#                 {
#                     key: row.get(
#                         key, 0 if "time" in key or "tol" in key else "Unknown"
#                     )
#                     for key in measurement
#                     if key != "power_measures"
#                 }
#             )
#         if row.get("power_measure_id"):
#             measurement["power_measures"].append(
#                 {
#                     key: row[key]
#                     for key in [
#                         "power_measure_id",
#                         "power_measure_type",
#                         "power_measure_name",
#                         "power_measure_voltage",
#                         "power_measure_current",
#                         "power_measure_power",
#                         "power_measure_pf",
#                     ]
#                 }
#             )

#     # Add ordered measurements with power measures to the final report
#     for index, (measurement_id, measurement) in enumerate(measurements.items()):
#         measurement_data = {
#             f"measurements_{index}_{key}": value
#             for key, value in measurement.items()
#             if key != "power_measures"
#         }
#         for i, power_measure in enumerate(measurement["power_measures"]):
#             measurement_data.update(
#                 {
#                     f"measurements_{index}_power_measures_{i}_{key}": value
#                     for key, value in power_measure.items()
#                 }
#             )
#         aggregated["measurements"].append(measurement_data)

#     return aggregated

# def aggregate_report_data(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
#     """
#     Aggregates data from a list of rows into a hierarchical structure.
#     Args:
#         rows (list): List of dictionaries containing report data.
#     Returns:
#         dict: Aggregated report data.
#     """
#     if not rows:
#         raise ValueError("No rows provided to aggregate")

#     if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
#         raise TypeError("Rows must be a list of dictionaries")

#     # Start with the first row
#     aggregated = {
#         "test_report_id": rows[0]["test_report_id"],
#         "test_name": rows[0]["test_name"],
#         "test_description": rows[0]["test_description"],
#         "test_result": rows[0]["test_result"],
#         "client_name": rows[0]["client_name"],
#         "standard": rows[0]["standard"],
#         "ups_model": rows[0]["ups_model"],
#         "measurements": [],  # This will hold the list of measurements
#     }

#     # Group data for measurements and power measures
#     measurements = defaultdict(lambda: {"power_measures": []})

#     for row in rows:
#         measurement_id = row["measurement_unique_id"]
#         measurement = measurements[measurement_id]

#         # Only update measurement details once
#         if not measurement.get("measurement_name"):
#             measurement.update(
#                 {
#                     "measurement_unique_id": row.get("measurement_unique_id"),
#                     "measurement_name": row.get("measurement_name"),
#                     "measurement_timestamp": row.get("measurement_timestamp"),
#                     "measurement_loadtype": row.get("measurement_loadtype"),
#                     "load_percentage": row.get("load_percentage", 0),  # Default to 0 if missing
#                     "phase_name": row.get("phase_name", "Unknown"),  # Default to "Unknown" if missing
#                     "step_id": row.get("step_id", 0),  # Default to 0 if missing
#                     "steady_state_voltage_tol": row.get("steady_state_voltage_tol", 0),  # Default to 0 if missing
#                     "voltage_dc_component": row.get("voltage_dc_component", 0),  # Default to 0 if missing
#                     "load_pf_deviation": row.get("load_pf_deviation", 0),  # Default to 0 if missing
#                     "switch_time_ms": row.get("switch_time_ms", 0),  # Default to 0 if missing
#                     "run_interval_sec": row.get("run_interval_sec", 0),  # Default to 0 if missing
#                     "backup_time_sec": row.get("backup_time_sec", 0),  # Default to 0 if missing
#                     "overload_time_sec": row.get("overload_time_sec", 0),  # Default to 0 if missing
#                     "temperature_1": row.get("temperature_1", 0),  # Default to 0 if missing
#                     "temperature_2": row.get("temperature_2", 0),  # Default to 0 if missing
#                 }
#             )

#         # Add power measures to this measurement
#         if row.get("power_measure_id"):
#             measurement["power_measures"].append(
#                 {
#                     "power_measure_id": row["power_measure_id"],
#                     "power_measure_type": row["power_measure_type"],
#                     "power_measure_name": row["power_measure_name"],
#                     "power_measure_voltage": row["power_measure_voltage"],
#                     "power_measure_current": row["power_measure_current"],
#                     "power_measure_power": row["power_measure_power"],
#                     "power_measure_pf": row["power_measure_pf"],
#                 }
#             )

#     # Convert measurements to a list and add to the report
#     aggregated["measurements"] = list(measurements.values())

#     return aggregated
