import sqlite3
from pathlib import Path

# Import generated proto classes
from proto.pData_pb2 import PowerMeasure
from proto.ups_test_pb2 import TestType
from proto.upsDefines_pb2 import spec, OverLoad
from proto.report_pb2 import TestReport, ReportSettings


class DataManager:
    def __init__(self, db_name="test_reports.db"):
        """Initialize the database and ensure all tables are created."""
        # Create the 'db' directory in the project root
        project_root = Path(__file__).parent.parent
        db_folder = project_root / "db"
        db_folder.mkdir(exist_ok=True)
        self.db_path = db_folder / db_name

        # Initialize database connection
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables in the SQLite database."""
        try:
            # Create PowerMeasure table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS PowerMeasure (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    voltage REAL,
                    current REAL,
                    power REAL,
                    pf REAL
                )
            """)

            # Create OverLoad table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS OverLoad (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    load_percentage INTEGER,
                    overload_time_min INTEGER
                )
            """)

            # Create spec table
            self.cursor.execute("""
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
            """)

            # Create ReportSettings table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ReportSettings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER,
                    standard TEXT,
                    ups_model INTEGER,
                    client_name TEXT,
                    brand_name TEXT,
                    test_engineer_name TEXT,
                    test_approval_name TEXT,
                    spec_id INTEGER,
                    FOREIGN KEY (spec_id) REFERENCES spec (id)
                )
            """)

            # Create TestReport table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS TestReport (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    settings_id INTEGER,
                    test_name TEXT,
                    test_description TEXT,
                    input_power_id INTEGER,
                    output_power_id INTEGER,
                    FOREIGN KEY (settings_id) REFERENCES ReportSettings (id),
                    FOREIGN KEY (input_power_id) REFERENCES PowerMeasure (id),
                    FOREIGN KEY (output_power_id) REFERENCES PowerMeasure (id)
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Error creating tables: {e}")

    def _validate_overload(self, overload: OverLoad):
        """Validate OverLoad object."""
        if (
            not isinstance(overload.load_percentage, int)
            or overload.load_percentage < 0
        ):
            raise ValueError("Invalid load_percentage: must be a non-negative integer.")
        if (
            not isinstance(overload.overload_time_min, int)
            or overload.overload_time_min < 0
        ):
            raise ValueError(
                "Invalid overload_time_min: must be a non-negative integer."
            )

    def insert_overload(self, overload: OverLoad):
        """Insert an OverLoad message into the database."""
        self._validate_overload(overload)
        try:
            self.cursor.execute(
                """
                INSERT INTO OverLoad (load_percentage, overload_time_min)
                VALUES (?, ?)
            """,
                (overload.load_percentage, overload.overload_time_min),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Error inserting OverLoad: {e}")

    def _validate_spec(self, ups_spec: spec):
        """Validate spec object."""
        required_fields = [
            ups_spec.Rating_va,
            ups_spec.RatedVoltage_volt,
            ups_spec.RatedCurrent_amp,
            ups_spec.MinInputVoltage_volt,
            ups_spec.MaxInputVoltage_volt,
            ups_spec.pf_rated_current,
            ups_spec.Max_Continous_Amp,
            ups_spec.overload_Amp,
            ups_spec.AvgSwitchTime_ms,
            ups_spec.AvgBackupTime_ms,
        ]
        if not all(isinstance(field, int) and field >= 0 for field in required_fields):
            raise ValueError(
                "Invalid spec field: all fields must be non-negative integers."
            )

        self._validate_overload(ups_spec.overload_long)
        self._validate_overload(ups_spec.overload_medium)
        self._validate_overload(ups_spec.overload_short)

    def insert_spec(self, ups_spec: spec):
        """Insert a spec message into the database."""
        self._validate_spec(ups_spec)

        try:
            # Insert overload entries and get their IDs
            overload_long_id = self.insert_overload(ups_spec.overload_long)
            overload_medium_id = self.insert_overload(ups_spec.overload_medium)
            overload_short_id = self.insert_overload(ups_spec.overload_short)

            # Insert spec data
            self.cursor.execute(
                """
                INSERT INTO spec (
                    phase, rating_va, rated_voltage, rated_current,
                    min_input_voltage, max_input_voltage, pf_rated_current,
                    max_continous_amp, overload_amp,
                    overload_long_id, overload_medium_id, overload_short_id,
                    avg_switch_time_ms, avg_backup_time_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    ups_spec.phase.name,  # Enum to string
                    ups_spec.Rating_va,
                    ups_spec.RatedVoltage_volt,
                    ups_spec.RatedCurrent_amp,
                    ups_spec.MinInputVoltage_volt,
                    ups_spec.MaxInputVoltage_volt,
                    ups_spec.pf_rated_current,
                    ups_spec.Max_Continous_Amp,
                    ups_spec.overload_Amp,
                    overload_long_id,
                    overload_medium_id,
                    overload_short_id,
                    ups_spec.AvgSwitchTime_ms,
                    ups_spec.AvgBackupTime_ms,
                ),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Error inserting spec: {e}")

    def insert_report_settings(self, settings: ReportSettings):
        """Insert ReportSettings into the database."""
        spec_id = self.insert_spec(settings.spec)

        self.cursor.execute(
            """
            INSERT INTO ReportSettings (
                report_id, standard, ups_model, client_name, brand_name,
                test_engineer_name, test_approval_name, spec_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                settings.report_id,
                settings.standard.name,  # Enum to string
                settings.ups_model,
                settings.client_name,
                settings.brand_name,
                settings.test_engineer_name,
                settings.test_approval_name,
                spec_id,
            ),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def _validate_power_measure(self, power: PowerMeasure):
        """Validate PowerMeasure object."""
        if not isinstance(power.voltage, (float, int)) or power.voltage < 0:
            raise ValueError("Invalid voltage: must be a non-negative number.")
        if not isinstance(power.current, (float, int)) or power.current < 0:
            raise ValueError("Invalid current: must be a non-negative number.")
        if not isinstance(power.power, (float, int)) or power.power < 0:
            raise ValueError("Invalid power: must be a non-negative number.")
        if not isinstance(power.pf, (float, int)) or not (0 <= power.pf <= 1):
            raise ValueError("Invalid pf: must be a number between 0 and 1.")

    def insert_power_measure(self, power: PowerMeasure):
        """Insert a PowerMeasure message into the database."""
        self._validate_power_measure(power)
        try:
            self.cursor.execute(
                """
                INSERT INTO PowerMeasure (type, voltage, current, power, pf)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    power.type.name,  # Enum to string
                    power.voltage,
                    power.current,
                    power.power,
                    power.pf,
                ),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Error inserting PowerMeasure: {e}")

    def _validate_test_report(self, report: TestReport):
        """Validate TestReport object."""
        # Validate TestReport settings
        if not isinstance(report.settings, ReportSettings):
            raise ValueError("Invalid settings: Must be a ReportSettings object.")

        # Validate input and output PowerMeasure
        if not isinstance(report.inputPower, PowerMeasure):
            raise ValueError("Invalid inputPower: Must be a PowerMeasure object.")
        self._validate_power_measure(report.inputPower)

        if not isinstance(report.outputpower, PowerMeasure):
            raise ValueError("Invalid outputpower: Must be a PowerMeasure object.")
        self._validate_power_measure(report.outputpower)

        # Validate testName
        if not isinstance(report.testName, TestType):
            raise ValueError("Invalid testName: Must be a TestType enum value.")

        # Validate testDescription
        if (
            not isinstance(report.testDescription, str)
            or not report.testDescription.strip()
        ):
            raise ValueError("Invalid testDescription: Must be a non-empty string.")

    def insert_test_report(self, report: TestReport):
        """Insert a TestReport message into the database."""
        # Validate TestReport object
        self._validate_test_report(report)

        try:
            # Insert PowerMeasure objects
            input_power_id = self.insert_power_measure(report.inputPower)
            output_power_id = self.insert_power_measure(report.outputpower)

            # Insert ReportSettings
            settings_id = self.insert_report_settings(report.settings)

            # Insert TestReport
            self.cursor.execute(
                """
                INSERT INTO TestReport (
                    settings_id, test_name, test_description, input_power_id, output_power_id
                )
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    settings_id,
                    report.testName.name,  # Enum to string
                    report.testDescription,
                    input_power_id,
                    output_power_id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Error inserting TestReport: {e}")

    def close(self):
        """Close the database connection."""
        self.conn.close()
    def get_test_report(self, report_id: int):
        """Retrieve a TestReport and related data from the database by report ID."""
        try:
            # Fetch the TestReport details
            self.cursor.execute(
                """
                SELECT
                    TestReport.id,
                    TestReport.test_name,
                    TestReport.test_description,
                    ReportSettings.report_id,
                    ReportSettings.standard,
                    ReportSettings.ups_model,
                    ReportSettings.client_name,
                    ReportSettings.brand_name,
                    ReportSettings.test_engineer_name,
                    ReportSettings.test_approval_name,
                    PowerMeasure1.type AS input_type,
                    PowerMeasure1.voltage AS input_voltage,
                    PowerMeasure1.current AS input_current,
                    PowerMeasure1.power AS input_power,
                    PowerMeasure1.pf AS input_pf,
                    PowerMeasure2.type AS output_type,
                    PowerMeasure2.voltage AS output_voltage,
                    PowerMeasure2.current AS output_current,
                    PowerMeasure2.power AS output_power,
                    PowerMeasure2.pf AS output_pf
                FROM
                    TestReport
                JOIN
                    ReportSettings ON TestReport.settings_id = ReportSettings.id
                JOIN
                    PowerMeasure AS PowerMeasure1 ON TestReport.input_power_id = PowerMeasure1.id
                JOIN
                    PowerMeasure AS PowerMeasure2 ON TestReport.output_power_id = PowerMeasure2.id
                WHERE
                    TestReport.id = ?
            """,
                (report_id,),
            )
            result = self.cursor.fetchone()
            if not result:
                return None

            # Map the fetched data to a dictionary or a structured object
            report = {
                "test_report_id": result[0],
                "test_name": result[1],
                "test_description": result[2],
                "settings": {
                    "report_id": result[3],
                    "standard": result[4],
                    "ups_model": result[5],
                    "client_name": result[6],
                    "brand_name": result[7],
                    "test_engineer_name": result[8],
                    "test_approval_name": result[9],
                },
                "input_power": {
                    "type": result[10],
                    "voltage": result[11],
                    "current": result[12],
                    "power": result[13],
                    "pf": result[14],
                },
                "output_power": {
                    "type": result[15],
                    "voltage": result[16],
                    "current": result[17],
                    "power": result[18],
                    "pf": result[19],
                },
            }
            return report
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving TestReport: {e}")

# Example Usage
if __name__ == "__main__":
    data_manager = DataManager()

    # Example PowerMeasure objects
    input_power = PowerMeasure(
        type=PowerMeasure.UPS_INPUT, voltage=230.0, current=10.0, power=2300.0, pf=0.98
    )
    output_power = PowerMeasure(
        type=PowerMeasure.UPS_OUTPUT, voltage=220.0, current=10.5, power=2310.0, pf=0.97
    )

    # Example spec object
    ups_spec = spec(
        phase=spec.SINGLE_PHASE,
        Rating_va=5000,
        RatedVoltage_volt=230,
        RatedCurrent_amp=21,
        MinInputVoltage_volt=200,
        MaxInputVoltage_volt=240,
        pf_rated_current=1,
        Max_Continous_Amp=25,
        overload_Amp=30,
        overload_long=OverLoad(load_percentage=110, overload_time_min=10),
        overload_medium=OverLoad(load_percentage=125, overload_time_min=5),
        overload_short=OverLoad(load_percentage=150, overload_time_min=2),
        AvgSwitchTime_ms=500,
        AvgBackupTime_ms=120000,
    )

    # Example ReportSettings object
    settings = ReportSettings(
        report_id=1,
        standard=ReportSettings.IEC_62040_3,
        ups_model=101,
        client_name="ABC Corp",
        brand_name="Brand Y",
        test_engineer_name="John Doe",
        test_approval_name="Jane Smith",
        spec=ups_spec,
    )

    # Example TestReport object
    report = TestReport(
        settings=settings,
        testName=TestType.FULL_LOAD_TEST,
        testDescription="Full load test for the UPS system",
        inputPower=input_power,
        outputpower=output_power,
    )

    # Insert TestReport into the database
    data_manager.insert_test_report(report)

    # Close database connection
    data_manager.close()
