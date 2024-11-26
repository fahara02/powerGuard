import logging
import sqlite3
from proto.pData_pb2 import PowerMeasure, PowerMeasureType
from proto.report_pb2 import Measurement, ReportSettings, TestReport, TestStandard
from proto.ups_test_pb2 import TestResult, TestType
from proto.upsDefines_pb2 import LOAD, MODE, OverLoad, Phase, spec


class Inserter:
    def __init__(self, conn, cursor):
        self._conn = conn
        self._cursor = cursor

    def measurement_to_db_row(self, measurement, test_report_id):
        # Convert Protobuf Timestamp to ISO 8601 string
        time_stamp_str = measurement.time_stamp.ToDatetime().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return (
            int(measurement.m_unique_id),  # Ensure it's an integer
            time_stamp_str,  # ISO 8601 format
            str(measurement.name),  # Convert to string
            MODE.Name(
                measurement.mode
            ),  # Convert enum to string (if SQLite expects text)
            str(measurement.phase_name),  # Convert to string
            LOAD.Name(
                measurement.load_type
            ),  # Convert enum to string (if SQLite expects text)
            int(measurement.step_id),  # Ensure it's an integer
            int(measurement.load_percentage),  # Ensure it's an integer
            int(measurement.steady_state_voltage_tol),  # Ensure it's an integer
            int(measurement.voltage_dc_component),  # Ensure it's an integer
            int(measurement.load_pf_deviation),  # Ensure it's an integer
            int(measurement.switch_time_ms),  # Ensure it's an integer
            int(measurement.run_interval_sec),  # Ensure it's an integer
            int(measurement.backup_time_sec),  # Ensure it's an integer
            int(measurement.overload_time_sec),  # Ensure it's an integer
            int(measurement.temperature_1),  # Ensure it's an integer
            int(measurement.temperature_2),  # Ensure it's an integer
            int(test_report_id),  # Ensure it's an integer (foreign key)
        )

    def insert_overload(
        self,
        overload: OverLoad,
        no_commit: bool = False,
    ):
        """Insert an OverLoad message into the database or return the existing entry if it already exists."""
        try:
            # Check if the same OverLoad already exists
            query = """
                SELECT id
                FROM OverLoad
                WHERE load_percentage = ? AND overload_time_min = ?
            """
            self._cursor.execute(
                query, (overload.load_percentage, overload.overload_time_min)
            )
            existing_row = self._cursor.fetchone()

            if existing_row:
                logging.debug(
                    f"Overload with load_percentage={overload.load_percentage} and overload_time_min={overload.overload_time_min} already exists."
                )
                return existing_row[0]

            # Insert a new OverLoad entry if no match exists
            self._cursor.execute(
                """
                INSERT INTO OverLoad (load_percentage, overload_time_min)
                VALUES (?, ?)
                """,
                (overload.load_percentage, overload.overload_time_min),
            )
            if no_commit:
                logging.debug(f"Exiting without commit ")
            else:
                self._conn.commit()
                # Return the newly inserted row ID
                return self._cursor.lastrowid

        except sqlite3.Error as e:
            logging.error(f"Database error while inserting OverLoad: {e}")
            raise Exception(f"Error inserting OverLoad: {e}")

    def insert_power_measure(
        self,
        power: PowerMeasure,
        measurement_id: int,
        savepoint_name: str,
        no_commit: bool = False,
    ):
        """Insert a PowerMeasure message into the database."""
        try:
            # Start the savepoint for this operation to ensure rollback on error
            self._conn.execute(f"SAVEPOINT {savepoint_name}")

            # Insert into PowerMeasure table with measurement_id as FK
            self._cursor.execute(
                """
                INSERT INTO PowerMeasure (measurement_id, type, name, voltage, current, power, pf)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    measurement_id,  # Foreign key linking to Measurement
                    PowerMeasureType.Name(power.type),  # Enum to string
                    str(power.name),  # Convert name to string
                    power.voltage,  # Voltage value
                    power.current,  # Current value
                    power.power,  # Power value
                    power.pf,  # Power factor value
                ),
            )

        except sqlite3.Error as e:
            # Rollback to the savepoint in case of an error
            self._conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
            raise Exception(f"Error inserting PowerMeasure: {e}")

        except Exception as e:
            # Rollback to the savepoint for any other unexpected error
            self._conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
            raise Exception(f"Unexpected error inserting PowerMeasure: {e}")

        finally:
            if no_commit:
                logging.debug(f"Exiting without commit ")
            else:
                self._conn.commit()

    def insert_spec(
        self,
        ups_spec: spec,
        no_commit: bool = False,
    ):
        """Insert a spec message into the database or return the existing entry if it already exists."""

        try:
            # Insert overload entries and get their IDs
            overload_ids = {
                "long": self.insert_overload(ups_spec.overload_long),
                "medium": self.insert_overload(ups_spec.overload_medium),
                "short": self.insert_overload(ups_spec.overload_short),
            }

            # Check if the same spec already exists
            query = """
                SELECT id
                FROM spec
                WHERE phase = ? AND rating_va = ? AND rated_voltage = ? AND rated_current = ?
                AND min_input_voltage = ? AND max_input_voltage = ? AND pf_rated_current = ?
                AND max_continous_amp = ? AND overload_amp = ?
                AND overload_long_id = ? AND overload_medium_id = ? AND overload_short_id = ?
                AND avg_switch_time_ms = ? AND avg_backup_time_ms = ?
            """
            params = (
                Phase.Name(ups_spec.phase),  # Enum converted to string
                ups_spec.Rating_va,
                ups_spec.RatedVoltage_volt,
                ups_spec.RatedCurrent_amp,
                ups_spec.MinInputVoltage_volt,
                ups_spec.MaxInputVoltage_volt,
                ups_spec.pf_rated_current,
                ups_spec.Max_Continous_Amp,
                ups_spec.overload_Amp,
                overload_ids["long"],
                overload_ids["medium"],
                overload_ids["short"],
                ups_spec.AvgSwitchTime_ms,
                ups_spec.AvgBackupTime_ms,
            )

            self._cursor.execute(query, params)
            existing_id = self._cursor.fetchone()

            if existing_id:
                # Return the existing ID if a match is found
                return existing_id[0]

            # Insert a new spec entry if no match exists
            insert_query = """
                INSERT INTO spec (
                    phase, rating_va, rated_voltage, rated_current,
                    min_input_voltage, max_input_voltage, pf_rated_current,
                    max_continous_amp, overload_amp,
                    overload_long_id, overload_medium_id, overload_short_id,
                    avg_switch_time_ms, avg_backup_time_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            self._cursor.execute(insert_query, params)
            if no_commit:
                logging.debug(f"Exiting without commit ")
            else:
                self._conn.commit()

                # Return the newly inserted row ID
                return self._cursor.lastrowid

        except sqlite3.Error as e:
            raise Exception(f"Error inserting spec: {e}")

    def insert_report_settings(self, settings: ReportSettings):
        """Insert ReportSettings into the database."""
        try:
            # Check if report_id already exists in the ReportSettings table
            query = "SELECT id FROM ReportSettings WHERE report_id = ?"
            self._cursor.execute(query, (settings.report_id,))
            existing_row = self._cursor.fetchone()
            if existing_row:
                logging.debug(
                    "ReportSettings with report_id %s already exists.",
                    settings.report_id,
                )
                return existing_row[0]

            # Insert spec first, since it's a foreign key reference
            spec_id = self.insert_spec(settings.spec)

            # Insert ReportSettings data
            self._cursor.execute(
                """
                INSERT INTO ReportSettings (
                    report_id, standard, ups_model, client_name, brand_name,
                    test_engineer_name, test_approval_name, spec_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    settings.report_id,
                    TestStandard.Name(settings.standard),  # Convert Enum to string
                    settings.ups_model,
                    settings.client_name,
                    settings.brand_name,
                    settings.test_engineer_name,
                    settings.test_approval_name,
                    spec_id,
                ),
            )
            self._conn.commit()

            # Return the last inserted row ID
            return self._cursor.lastrowid

        except sqlite3.Error as e:
            raise Exception(f"Error inserting ReportSettings: {e}")

        except Exception as e:
            # Catch any other unexpected exceptions
            raise Exception(f"Unexpected error inserting ReportSettings: {e}")

    def insert_measurement(
        self,
        measurement,
        test_report_id,
        savepoint_name: str,
        no_commit: bool = False,
    ):
        """Insert a Measurement record and its associated PowerMeasures."""
        try:
            # Start a savepoint for this operation
            self._conn.execute(f"SAVEPOINT {savepoint_name}")

            # Validate the measurement
            self._validator.validate_measurement(measurement)

            # Convert measurement to row
            db_row = self.measurement_to_db_row(measurement, test_report_id)

            # Insert Measurement into the database
            self._cursor.execute(
                """
                INSERT INTO Measurement (
                    m_unique_id, timestamp, name, mode, phase_name, load_type,
                    step_id, load_percentage, steady_state_voltage_tol, voltage_dc_component,
                    load_pf_deviation, switch_time_ms, run_interval_sec, backup_time_sec,
                    overload_time_sec, temperature_1, temperature_2, test_report_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                db_row,
            )
            measurement_id = self._cursor.lastrowid  # Get the new ID

            # Insert associated PowerMeasures
            if measurement.power_measures:
                for power_measure in measurement.power_measures:
                    power_measure_savepoint_name = (
                        f"{savepoint_name}_power_measure_{power_measure.name}"
                    )
                    self.insert_power_measure(
                        power_measure,
                        measurement_id,
                        power_measure_savepoint_name,
                        False,
                    )

            # Only release savepoint here (no commit)
            self._conn.execute(f"RELEASE SAVEPOINT {savepoint_name}")
            if no_commit:
                logging.debug(f"Exiting without commit ")
            else:
                self._conn.commit()

        except sqlite3.Error as e:
            # Rollback to the savepoint on error
            self._conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
            raise Exception(f"Error inserting Measurement: {e}")

    def insert_test_report(self, report: TestReport):
        """Insert a TestReport message into the database."""
        logging.debug(
            "Inserting TestReport: %s with report_id %d",
            report,
            report.settings.report_id,
        )

        try:
            # Convert the TestType enum to its string name
            test_name = TestType.Name(report.testName)

            # Generate a unique savepoint name using report ID
            savepoint_name = f"test_report_{report.settings.report_id}"

            # Start the transaction and set savepoint
            self._conn.execute("BEGIN")
            self._conn.execute(f"SAVEPOINT {savepoint_name}")

            # Check if report_id already exists in the ReportSettings table
            query_same_report_id = (
                "SELECT report_id FROM ReportSettings WHERE report_id = ?"
            )
            self._cursor.execute(query_same_report_id, (report.settings.report_id,))
            existing_row = self._cursor.fetchone()

            if existing_row:
                # Return the existing ID if report_id exists
                logging.debug(
                    "ReportSettings with report_id %d already exists.",
                    report.settings.report_id,
                )
                return existing_row[0]
            else:
                # Insert new ReportSettings and get its ID
                logging.debug(
                    "Creating new ReportSettings for report_id %d.",
                    report.settings.report_id,
                )
                settings_id = self.insert_report_settings(report.settings)

            # Check if a TestReport with this settings_id already exists
            query_same_settings_id = "SELECT id FROM TestReport WHERE settings_id = ?"
            self._cursor.execute(query_same_settings_id, (settings_id,))
            test_report_row = self._cursor.fetchone()

            if test_report_row:
                # If TestReport exists, reuse the existing ID
                test_report_id = test_report_row[0]
                logging.debug(
                    "Updating existing TestReport with id %d for settings_id %d.",
                    test_report_id,
                    settings_id,
                )
                # Update the existing TestReport
                self._cursor.execute(
                    """
                    UPDATE TestReport
                    SET test_name = ?, test_description = ?, test_result = ?
                    WHERE id = ?
                    """,
                    (
                        test_name,
                        report.testDescription,
                        TestResult.Name(report.test_result),
                        test_report_id,
                    ),
                )
            else:
                # Insert a new TestReport
                logging.debug(
                    "Inserting new TestReport for settings_id %d.", settings_id
                )
                self._cursor.execute(
                    """
                    INSERT INTO TestReport (
                        settings_id, test_name, test_description, test_result
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        settings_id,
                        test_name,
                        report.testDescription,
                        TestResult.Name(report.test_result),
                    ),
                )
                test_report_id = self._cursor.lastrowid

            # Insert associated measurements
            if report.measurements:
                logging.debug(
                    "Inserting measurements for TestReport ID %d.", test_report_id
                )
                for measurement in report.measurements:
                    # Insert measurement and handle savepoint correctly
                    try:
                        measurement_savepoint_name = (
                            f"measurement_{measurement.m_unique_id}"
                        )
                        self._conn.execute(f"SAVEPOINT {measurement_savepoint_name}")
                        self.insert_measurement(
                            measurement, test_report_id, measurement_savepoint_name
                        )
                        self._conn.execute(
                            f"RELEASE SAVEPOINT {measurement_savepoint_name}"
                        )
                    except Exception as e:
                        # If there's an error with the measurement insertion, rollback to savepoint
                        logging.error(f"Error inserting measurement: {e}")
                        self._conn.execute(
                            f"ROLLBACK TO SAVEPOINT {measurement_savepoint_name}"
                        )
                        raise

            # Commit the transaction to save changes
            self._conn.commit()

            # Return the ID of the TestReport
            return test_report_id

        except sqlite3.Error as e:
            # Rollback the transaction in case of any SQLite error
            self._conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
            raise Exception(f"Error inserting/updating TestReport into database: {e}")

        except Exception as e:
            # Handle any unexpected errors and rollback
            logging.error(f"Unexpected error inserting/updating TestReport: {e}")
            self._conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
            raise
