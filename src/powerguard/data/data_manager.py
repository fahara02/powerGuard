import logging
import sqlite3
from typing import Optional, Dict, Any
from pathlib import Path
from typing import Any, Optional
import time
from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp

from pydantic import BaseModel, PrivateAttr, field_validator

# Import generated proto classes
from powerguard.bootstrap import paths
from google.protobuf.timestamp_pb2 import Timestamp
from proto.pData_pb2 import PowerMeasure, PowerMeasureType
from proto.report_pb2 import Measurement, ReportSettings, TestReport, TestStandard
from proto.ups_test_pb2 import TestResult, TestType
from proto.ups_defines_pb2 import LOAD, MODE, OverLoad, Phase, spec

from powerguard.data.validator import Validator
from powerguard.data.inserter import Inserter
from powerguard.data.fetcher import Fetcher


class DataManager(BaseModel):
    db_name: str = "test_reports.db"
    db_path: Optional[Path] = None  # Will be set after validation
    _conn: sqlite3.Connection = PrivateAttr()  # Private attribute for connection
    _cursor: sqlite3.Cursor = PrivateAttr()  # Private attribute for cursor
    _validator: Validator = PrivateAttr()
    _inserter: Inserter = PrivateAttr()
    _fetcher: Fetcher = PrivateAttr()

    @field_validator("db_name")
    def validate_db_name(cls, v: str):
        """Validate db_name field to ensure it's a string and properly formatted."""
        if not v.endswith(".db"):
            raise ValueError("Database name must end with '.db'")
        return v

    def __init__(self, **kwargs):
        """Initialize the database and ensure all tables are created."""
        super().__init__(**kwargs)

        db_folder = paths.get("db_dir")
        db_folder.mkdir(parents=True, exist_ok=True)

        # Set the db_path if it's not provided
        if not self.db_path:
            self.db_path = db_folder / self.db_name

        # Initialize database connection and cursor
        self._conn = sqlite3.connect(self.db_path)
        self._cursor = self._conn.cursor()
        self._create_tables()
        self._validator = Validator()
        self._inserter = Inserter(self._conn, self._cursor)
        self._fetcher = Fetcher(self._conn, self._cursor)

    def __enter__(self):
        """Enable context manager for database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._cursor = self._conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context, ensuring the connection is closed."""
        self.close()

    def close(self):
        """Close the database connection."""
        self._conn.close()

    def _create_tables(self):
        """Create necessary tables in the SQLite database."""

        schema_queries = [
            # PowerMeasure table
            """
            CREATE TABLE IF NOT EXISTS PowerMeasure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id INTEGER NOT NULL, -- FK linking to Measurement table
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                voltage REAL,
                current REAL,
                power REAL,
                pf REAL,
                FOREIGN KEY (measurement_id) REFERENCES Measurement (id) ON DELETE CASCADE
            )
            """,
            # OverLoad table
            """
            CREATE TABLE IF NOT EXISTS OverLoad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                load_percentage INTEGER,
                overload_time_min INTEGER
            )
            """,
            # spec table
            """
            CREATE TABLE IF NOT EXISTS spec (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase TEXT,
                rating_va INTEGER,
                rated_voltage INTEGER,
                rated_current INTEGER,
                min_input_voltage INTEGER,
                max_input_voltage INTEGER,
                pf_rated_current INTEGER,
                max_continous_amp INTEGER,
                overload_amp INTEGER,
                overload_long_id INTEGER,
                overload_medium_id INTEGER,
                overload_short_id INTEGER,
                avg_switch_time_ms INTEGER,
                avg_backup_time_ms INTEGER,
                FOREIGN KEY (overload_long_id) REFERENCES OverLoad (id),
                FOREIGN KEY (overload_medium_id) REFERENCES OverLoad (id),
                FOREIGN KEY (overload_short_id) REFERENCES OverLoad (id)
            )
            """,
            # ReportSettings table
            """
            CREATE TABLE IF NOT EXISTS ReportSettings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL UNIQUE,
                standard TEXT NOT NULL,
                ups_model INTEGER NOT NULL,
                client_name TEXT,
                brand_name TEXT,
                test_engineer_name TEXT,
                test_approval_name TEXT,
                spec_id INTEGER,
                FOREIGN KEY (spec_id) REFERENCES spec (id)
            )
            """,
            # Measurement table
            """
            CREATE TABLE IF NOT EXISTS Measurement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                m_unique_id INTEGER NOT NULL, -- Unique proto ID
                timestamp DATETIME NOT NULL,
                name TEXT NOT NULL,
                mode TEXT,
                phase_name TEXT,
                load_type TEXT,
                step_id INTEGER,
                load_percentage INTEGER,
                steady_state_voltage_tol INTEGER,
                voltage_dc_component INTEGER,
                load_pf_deviation INTEGER,
                switch_time_ms INTEGER,
                run_interval_sec INTEGER,
                backup_time_sec INTEGER,
                overload_time_sec INTEGER,
                temperature_1 INTEGER,
                temperature_2 INTEGER,
                test_report_id INTEGER NOT NULL, -- Links to TestReport
                FOREIGN KEY (test_report_id) REFERENCES TestReport (id) ON DELETE CASCADE
            )
            """,
            # TestReport table
            """
            CREATE TABLE IF NOT EXISTS TestReport (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                settings_id INTEGER NOT NULL,
                test_name TEXT NOT NULL,
                test_description TEXT,
                test_result TEXT,
                FOREIGN KEY (settings_id) REFERENCES ReportSettings (id) ON DELETE CASCADE
            )
            """,
        ]
        try:
            for query in schema_queries:
                self._cursor.execute(query)

            self._conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Error creating tables: {e}")

    def _check_id_exists(self, table_name: str, entry_id: int):
        """Check if an entry with the given ID exists in the specified table."""
        try:
            self._cursor.execute(
                f"SELECT 1 FROM {table_name} WHERE id = ?", (entry_id,)
            )
            return self._cursor.fetchone() is not None
        except sqlite3.Error as e:
            raise Exception(f"Error checking ID existence in {table_name}: {e}")

    def _check_value_exists(self, table_name: str, column_name: str, value: any):
        """
        Check if a specific value exists in a given column of a table.

        Args:
            table_name (str): Name of the table to query.
            column_name (str): Name of the column to check.
            value (any): Value to search for in the specified column.

        Returns:
            bool: True if the value exists, False otherwise.
        """
        try:
            query = f"SELECT 1 FROM {table_name} WHERE {column_name} = ?"
            self._cursor.execute(query, (value,))
            return self._cursor.fetchone() is not None
        except sqlite3.Error as e:
            raise Exception(f"Error checking value in {table_name}.{column_name}: {e}")

    def insert_overload(self, overload: OverLoad):
        """Validate and insert OverLoad data."""
        self._validator._validate_overload(overload)  # Delegate validation
        return self._inserter.insert_overload(overload)  # Delegate insertion

    def insert_power_measure(
        self, power: PowerMeasure, measurement_id: int, savepoint_name: str
    ):
        """Validate and insert PowerMeasure data."""
        self._validator._validate_power_measure(power)  # Delegate validation
        self._inserter.insert_power_measure(power, measurement_id, savepoint_name, True)

    def insert_spec(self, ups_spec: spec):
        """Insert a spec message into the database or return the existing entry if it already exists."""
        self._validator._validate_spec(ups_spec)
        return self._inserter.insert_power_measure(ups_spec, False)

    def insert_report_settings(self, settings: ReportSettings):
        return self._inserter.insert_report_settings(settings)

    def insert_measurement(self, measurement, test_report_id, savepoint_name: str):
        self._validator.validate_measurement(measurement)
        return self._inserter.insert_measurement(measurement)

    def insert_test_report(self, report: TestReport):
        self._validator._validate_test_report(report)
        return self._inserter.insert_test_report(report)

    def get_test_report(self, report_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a test report using the id from TestReport Table.
        Args:
            id (int): The id from TestReport Table
        Returns:
            Optional[Dict[str, Any]]: The test report details if found, None otherwise.
        """
        return self._fetcher.get_test_report(report_id)

    def get_latest_test_report(self):
        """Retrieve the latest TestReport and its associated data."""
        return self._fetcher.get_latest_report()

    def get_all_report_id_testName(self):
        """Retrieve all TestReport IDs and their corresponding test names."""
        try:
            self._cursor.execute(
                """
                SELECT id, test_name
                FROM TestReport
                """
            )
            results = self.cursor.fetchall()
            return [{"report_id": row[0], "test_name": row[1]} for row in results]
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving TestReport IDs and test names: {e}")

    def _delete_entry(self, table_name: str, entry_id: int):
        """Delete an entry from the specified table if it exists."""
        if not self._check_id_exists(table_name, entry_id):
            raise ValueError(
                f"Entry with ID {entry_id} does not exist in {table_name}."
            )

        try:
            self._cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (entry_id,))
            self._conn.commit()
            return f"Entry with ID {entry_id} successfully deleted from {table_name}."
        except sqlite3.Error as e:
            raise Exception(f"Error deleting entry from {table_name}: {e}")

    def delete_overload(self, overload_id: int):
        """Delete an OverLoad entry by ID."""
        try:
            return self._delete_entry("OverLoad", overload_id)
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            raise Exception(f"Unexpected error while deleting OverLoad: {e}")

    def delete_power_measure(self, power_measure_id: int):
        """Delete a PowerMeasure entry by ID."""
        try:
            return self._delete_entry("PowerMeasure", power_measure_id)
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            raise Exception(f"Unexpected error while deleting PowerMeasure: {e}")

    def delete_spec(self, spec_id: int, cascading: bool = True):
        """
        Deletes a spec entry by ID. If cascading is True, it also deletes related OverLoad entries.
        """
        try:
            # Check if the spec entry exists
            if not self._check_id_exists("spec", spec_id):
                raise ValueError(f"spec with ID {spec_id} does not exist.")

            if cascading:
                # Get OverLoad IDs associated with the spec
                self._cursor.execute(
                    """
                    SELECT overload_long_id, overload_medium_id, overload_short_id
                    FROM spec WHERE id = ?
                    """,
                    (spec_id,),
                )
                overload_ids = self._cursor.fetchone()

                # Delete related OverLoad entries
                if overload_ids:
                    for overload_id in overload_ids:
                        if overload_id:
                            self._delete_entry("OverLoad", overload_id)

            # Delete the spec entry
            self._delete_entry("spec", spec_id)
            self._conn.commit()

            if cascading:
                return f"spec with ID {spec_id} and related OverLoad entries deleted."
            else:
                return f"spec with ID {spec_id} deleted without affecting related OverLoad entries."

        except sqlite3.Error as e:
            raise Exception(f"Error deleting spec with ID {spec_id}: {e}")
        except ValueError as ve:
            return str(ve)

    def delete_report_settings(self, settings_id: int, cascading: bool = True):
        """
        Deletes a ReportSettings entry by ID along with its related spec entry.
        """
        try:
            if cascading:
                # Check if the ReportSettings entry exists
                if not self._check_id_exists("ReportSettings", settings_id):
                    raise ValueError(
                        f"ReportSettings with ID {settings_id} does not exist."
                    )

                # Get the related spec_id
                self._cursor.execute(
                    "SELECT spec_id FROM ReportSettings WHERE id = ?", (settings_id,)
                )
                spec_row = self._cursor.fetchone()
                if spec_row:
                    spec_id = spec_row[0]
                    if spec_id:
                        self.delete_spec(spec_id)  # Cascade to delete the spec

            # Delete the ReportSettings entry
            self._delete_entry("ReportSettings", settings_id)
            self._conn.commit()
            if cascading:
                return f"ReportSettings with ID {settings_id} and related spec deleted."
            else:
                return f"ReportSettings with ID {settings_id} deleted without affecting related spec entries."
        except sqlite3.Error as e:
            raise Exception(f"Error deleting ReportSettings with ID {settings_id}: {e}")
        except ValueError as ve:
            return str(ve)

    def delete_test_report(self, test_report_id: int, cascading: bool = True):
        """
        Deletes a TestReport entry by ID along with all its related entries.
        This includes cascading deletions for associated entries in:
        - ReportSettings
        - PowerMeasure (input and output)
        """
        try:
            if cascading:
                # Check if the TestReport exists
                if not self._check_id_exists("TestReport", test_report_id):
                    raise ValueError(
                        f"TestReport with ID {test_report_id} does not exist."
                    )

                # Get related ReportSettings ID and PowerMeasure IDs
                self._cursor.execute(
                    "SELECT settings_id, input_power_id, output_power_id FROM TestReport WHERE id = ?",
                    (test_report_id,),
                )
                row = self._cursor.fetchone()
                if row is None:
                    raise ValueError(
                        f"No data found for TestReport with ID {test_report_id}."
                    )

                settings_id, input_power_id, output_power_id = row

                # Delete related PowerMeasure entries
                if input_power_id:
                    self._delete_entry("PowerMeasure", input_power_id)
                if output_power_id:
                    self._delete_entry("PowerMeasure", output_power_id)

                # Delete related ReportSettings and cascade to spec
                if settings_id:
                    try:
                        self.delete_report_settings(settings_id)
                    except Exception as e:
                        raise Exception(
                            f"Failed to delete ReportSettings with ID {settings_id}: {e}"
                        )

            # Finally, delete the TestReport itself
            self._delete_entry("TestReport", test_report_id)
            self._conn.commit()
            if cascading:
                return f"TestReport with ID {test_report_id} and all related entries have been deleted."
            else:
                return f"TestReport with ID {test_report_id} deleted without affecting related reportsettings,powermeasure entries."
        except sqlite3.Error as e:
            raise Exception(f"Error deleting TestReport with ID {test_report_id}: {e}")
        except ValueError as ve:
            return str(ve)

    def clean_database(self):
        """Clean up the database by removing duplicate and orphaned entries."""
        try:
            # Step 1: Remove duplicate PowerMeasure entries
            logging.debug("Removing duplicate PowerMeasure entries.")
            self._cursor.execute(
                """
                DELETE FROM PowerMeasure
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM PowerMeasure
                    GROUP BY type, voltage, current, power, pf
                )
                """
            )

            # Step 2: Remove unused PowerMeasure entries
            logging.debug("Removing unused PowerMeasure entries.")
            self._cursor.execute(
                """
                DELETE FROM PowerMeasure
                WHERE id NOT IN (
                    SELECT input_power_id FROM TestReport
                    UNION
                    SELECT output_power_id FROM TestReport
                )
                """
            )

            # Step 3: Remove unused OverLoad entries
            logging.debug("Removing unused OverLoad entries.")
            self._cursor.execute(
                """
                DELETE FROM OverLoad
                WHERE id NOT IN (
                    SELECT overload_long_id FROM spec
                    UNION
                    SELECT overload_medium_id FROM spec
                    UNION
                    SELECT overload_short_id FROM spec
                )
                """
            )

            # Step 4: Remove orphaned ReportSettings
            logging.debug("Removing orphaned ReportSettings entries.")
            self._cursor.execute(
                """
                DELETE FROM ReportSettings
                WHERE id NOT IN (
                    SELECT settings_id FROM TestReport
                )
            """
            )

            # Step 5: Remove orphaned spec entries
            logging.debug("Removing orphaned spec entries.")
            self._cursor.execute(
                """
                DELETE FROM spec
                WHERE id NOT IN (
                    SELECT spec_id FROM ReportSettings
                )
                """
            )

            # Commit the changes
            self._conn.commit()
            logging.info("Database cleanup completed successfully.")

        except sqlite3.Error as e:
            # Handle SQLite errors
            logging.error(f"Error during database cleanup: {e}")
            raise Exception(f"Error during database cleanup: {e}")

        except Exception as e:
            # Handle unexpected errors
            logging.error(f"Unexpected error during database cleanup: {e}")
            raise Exception(f"Unexpected error during database cleanup: {e}")

    def generate_mock_data(self, report_id, client_name, brand_name, engineer_name):
        now = datetime.now(tz=timezone.utc)
        timestamp_proto = Timestamp()
        timestamp_proto.FromDatetime(now)
        # Create OverLoad objects
        overload_long = OverLoad(load_percentage=110, overload_time_min=10)
        overload_medium = OverLoad(load_percentage=125, overload_time_min=5)
        overload_short = OverLoad(load_percentage=150, overload_time_min=2)

        # Create the spec object
        ups_spec = spec(
            phase=Phase.SINGLE_PHASE,  # SINGLE_PHASE from enum Phase
            rated_va=5000,
            rated_voltage=230,
            rated_current=21,
            min_input_voltage=200,
            max_input_voltage=240,
            pf_rated_current=100,  # 1.0 PF represented as 100 for simplicity
            max_continous_amp=25,
            overload_amp=30,
            overload_long=overload_long,
            overload_medium=overload_medium,
            overload_short=overload_short,
            avg_switch_time_ms=500,
            avg_backup_time_ms=120000,
        )

        # Create PowerMeasure objects
        input_power1 = PowerMeasure(
            type=PowerMeasureType.UPS_INPUT,
            name="input_power",
            voltage=230.0,
            current=10.0,
            power=2300.0,
            pf=0.98,
        )
        output_power1 = PowerMeasure(
            type=PowerMeasureType.UPS_OUTPUT,
            name="output_power",
            voltage=220.0,
            current=10.5,
            power=2310.0,
            pf=0.97,
        )
        input_power2 = PowerMeasure(
            type=PowerMeasureType.UPS_INPUT,
            name="input_power",
            voltage=231.0,
            current=11.0,
            power=2350.0,
            pf=0.98,
        )
        output_power2 = PowerMeasure(
            type=PowerMeasureType.UPS_OUTPUT,
            name="output_power",
            voltage=220.0,
            current=11.5,
            power=2360.0,
            pf=0.97,
        )
        input_power3 = PowerMeasure(
            type=PowerMeasureType.UPS_INPUT,
            name="input_power",
            voltage=230.0,
            current=10.0,
            power=2300.0,
            pf=0.98,
        )
        output_power3 = PowerMeasure(
            type=PowerMeasureType.UPS_OUTPUT,
            name="output_power",
            voltage=220.0,
            current=10.5,
            power=2310.0,
            pf=0.97,
        )
        input_power4 = PowerMeasure(
            type=PowerMeasureType.UPS_INPUT,
            name="input_power",
            voltage=231.0,
            current=11.0,
            power=2350.0,
            pf=0.98,
        )
        output_power4 = PowerMeasure(
            type=PowerMeasureType.UPS_OUTPUT,
            name="output_power",
            voltage=220.0,
            current=11.5,
            power=2350.0,
            pf=0.97,
        )
        input_power5 = PowerMeasure(
            type=PowerMeasureType.UPS_INPUT,
            name="input_power",
            voltage=251.0,
            current=7,
            power=2350.0,
            pf=0.98,
        )
        output_power5 = PowerMeasure(
            type=PowerMeasureType.UPS_OUTPUT,
            name="output_power",
            voltage=240.0,
            current=0,
            power=2350.0,
            pf=0.97,
        )
        input_power6 = PowerMeasure(
            type=PowerMeasureType.UPS_INPUT,
            name="input_power",
            voltage=264.0,
            current=8,
            power=2350.0,
            pf=0.98,
        )
        output_power6 = PowerMeasure(
            type=PowerMeasureType.UPS_OUTPUT,
            name="output_power",
            voltage=275.0,
            current=2350.0,
            power=2370,
            pf=0.97,
        )
        pMeasures1 = [input_power1, output_power1]
        pMeasures2 = [input_power2, output_power2]
        pMeasures3 = [input_power3, output_power3]
        pMeasures4 = [input_power4, output_power4]
        pMeasures5 = [input_power5, output_power5]
        pMeasures6 = [input_power6, output_power6]
        # Create a ReportSettings object
        report_settings = ReportSettings(
            report_id=report_id,
            standard=TestStandard.IEC_62040_3,
            ups_model=101,
            spec=ups_spec,
            client_name=client_name,
            brand_name=brand_name,
            test_engineer_name=engineer_name,
            test_approval_name="Jane Smith",
        )

        # Create a Measurement object
        measurement1 = Measurement(
            m_unique_id=1136,  # Example unique ID
            time_stamp=timestamp_proto,  # Example UNIX timestamp
            name="LIGHT_LOAD_AND_FUNCTION_TEST",
            mode=MODE.NORMAL_MODE,  # NORMAL_MODE from enum MODE
            phase_name="Phase 1",
            load_type=LOAD.LINEAR,  # LINEAR from enum LOAD
            step_id=1,
            load_percentage=100,
            power_measures=pMeasures1,
            steady_state_voltage_tol=5,
            voltage_dc_component=0,
            load_pf_deviation=2,
            switch_time_ms=500,
            run_interval_sec=3600,
            backup_time_sec=1800,
            overload_time_sec=300,
            temperature_1=25,
            temperature_2=30,
        )
        measurement2 = Measurement(
            m_unique_id=1137,  # Example unique ID
            time_stamp=timestamp_proto,  # Example UNIX timestamp
            name="LIGHT_LOAD_AND_FUNCTION_TEST",
            mode=MODE.NORMAL_MODE,  # NORMAL_MODE from enum MODE
            phase_name="Phase 1",
            load_type=LOAD.LINEAR,  # LINEAR from enum LOAD
            step_id=1,
            load_percentage=100,
            power_measures=pMeasures2,
            steady_state_voltage_tol=5,
            voltage_dc_component=0,
            load_pf_deviation=2,
            switch_time_ms=500,
            run_interval_sec=3600,
            backup_time_sec=1800,
            overload_time_sec=300,
            temperature_1=25,
            temperature_2=30,
        )
        measurement3 = Measurement(
            m_unique_id=1138,  # Example unique ID
            time_stamp=timestamp_proto,  # Example UNIX timestamp
            name="LIGHT_LOAD_AND_FUNCTION_TEST",
            mode=MODE.NORMAL_MODE,  # NORMAL_MODE from enum MODE
            phase_name="Phase 1",
            load_type=LOAD.LINEAR,  # LINEAR from enum LOAD
            step_id=1,
            load_percentage=100,
            power_measures=pMeasures3,
            steady_state_voltage_tol=5,
            voltage_dc_component=0,
            load_pf_deviation=2,
            switch_time_ms=500,
            run_interval_sec=3600,
            backup_time_sec=1800,
            overload_time_sec=300,
            temperature_1=25,
            temperature_2=30,
        )
        measurement4 = Measurement(
            m_unique_id=1139,  # Example unique ID
            time_stamp=timestamp_proto,  # Example UNIX timestamp
            name="LIGHT_LOAD_AND_FUNCTION_TEST",
            mode=MODE.NORMAL_MODE,  # NORMAL_MODE from enum MODE
            phase_name="Phase 1",
            load_type=LOAD.LINEAR,  # LINEAR from enum LOAD
            step_id=1,
            load_percentage=100,
            power_measures=pMeasures4,
            steady_state_voltage_tol=5,
            voltage_dc_component=0,
            load_pf_deviation=2,
            switch_time_ms=500,
            run_interval_sec=3600,
            backup_time_sec=1800,
            overload_time_sec=300,
            temperature_1=25,
            temperature_2=30,
        )
        measurement5 = Measurement(
            m_unique_id=1140,  # Example unique ID
            time_stamp=timestamp_proto,  # Example UNIX timestamp
            name="LIGHT_LOAD_AND_FUNCTION_TEST",
            mode=MODE.NORMAL_MODE,  # NORMAL_MODE from enum MODE
            phase_name="Phase 1",
            load_type=LOAD.LINEAR,  # LINEAR from enum LOAD
            step_id=1,
            load_percentage=100,
            power_measures=pMeasures5,
            steady_state_voltage_tol=5,
            voltage_dc_component=0,
            load_pf_deviation=2,
            switch_time_ms=500,
            run_interval_sec=3600,
            backup_time_sec=1800,
            overload_time_sec=300,
            temperature_1=25,
            temperature_2=30,
        )
        measurement6 = Measurement(
            m_unique_id=1141,  # Example unique ID
            time_stamp=timestamp_proto,  # Example UNIX timestamp
            name="LIGHT_LOAD_AND_FUNCTION_TEST",
            mode=MODE.NORMAL_MODE,  # NORMAL_MODE from enum MODE
            phase_name="Phase 1",
            load_type=LOAD.LINEAR,  # LINEAR from enum LOAD
            step_id=1,
            load_percentage=100,
            power_measures=pMeasures6,
            steady_state_voltage_tol=5,
            voltage_dc_component=0,
            load_pf_deviation=2,
            switch_time_ms=500,
            run_interval_sec=3600,
            backup_time_sec=1800,
            overload_time_sec=300,
            temperature_1=25,
            temperature_2=30,
        )
        measurements = [
            measurement1,
            measurement2,
            measurement3,
            measurement3,
            measurement4,
            measurement5,
            measurement6,
        ]
        # Create the TestReport object
        test_report = TestReport(
            settings=report_settings,
            test_name=TestType.LIGHT_LOAD_AND_FUNCTION_TEST,
            test_description="Normal opration in rated load with varying input voltage",
            measurements=measurements,
            test_result=TestResult.TEST_SUCCESSFUL,  # TEST_SUCCESSFUL from enum TestResult
        )

        print(f"Generated mock report for client: {client_name}")
        return test_report


# Example Usage
if __name__ == "__main__":
    data_manager = DataManager()
    report = data_manager.generate_mock_data(3119, "walton", "maxgreen", "fhr")

    report_id = data_manager.insert_test_report(report)
    unique_id = report.settings.report_id
    print(
        f"check newly inserted test report with id {report_id} for unique id {unique_id} "
    )
    data_manager.close()
