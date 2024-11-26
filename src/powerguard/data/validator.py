from pathlib import Path
from enum import Enum
from typing import Any, Optional
from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp

from google.protobuf.timestamp_pb2 import Timestamp
from proto.pData_pb2 import PowerMeasure, PowerMeasureType
from proto.report_pb2 import Measurement, ReportSettings, TestReport, TestStandard

from proto.ups_test_pb2 import TestResult, TestType
from proto.upsDefines_pb2 import LOAD, MODE, OverLoad, Phase, spec


class Validator:
    @staticmethod
    def _validate_non_negative(value: Any, field_name: str, types: tuple):
        """Generic validation for non-negative numbers."""
        if not isinstance(value, types) or value < 0:
            raise ValueError(
                f"{field_name} must be a non-negative {', '.join(t.__name__ for t in types)}."
            )

    @staticmethod
    def _validate_range(
        value: Any, field_name: str, min_val: float, max_val: float, types: tuple
    ):
        """Generic validation for values within a range."""
        if not isinstance(value, types) or not (min_val <= value <= max_val):
            raise ValueError(f"{field_name} must be between {min_val} and {max_val}.")

    @staticmethod
    def _validate_pf(pf: Any):
        Validator._validate_range(pf, "Power factor", 0, 1, (float, int))

    def _validate_overload(self, overload: OverLoad):
        """Validate OverLoad object."""
        self._validate_non_negative(overload.load_percentage, "load_percentage", (int,))
        self._validate_non_negative(
            overload.overload_time_min, "overload_time_min", (int,)
        )

    def _validate_power_measure(self, power_measure: PowerMeasure):
        """Validate PowerMeasure object."""
        for field, name in [
            (power_measure.voltage, "voltage"),
            (power_measure.current, "current"),
            (power_measure.power, "power"),
        ]:
            self._validate_non_negative(field, name, (float, int))
        self._validate_pf(power_measure.pf)

    def _validate_spec(self, ups_spec: spec):
        """Validate spec object."""
        non_negative_fields = [
            ("Rating_va", ups_spec.Rating_va),
            ("RatedVoltage_volt", ups_spec.RatedVoltage_volt),
            ("RatedCurrent_amp", ups_spec.RatedCurrent_amp),
            ("MinInputVoltage_volt", ups_spec.MinInputVoltage_volt),
            ("MaxInputVoltage_volt", ups_spec.MaxInputVoltage_volt),
            ("pf_rated_current", ups_spec.pf_rated_current),
            ("Max_Continous_Amp", ups_spec.Max_Continous_Amp),
            ("overload_Amp", ups_spec.overload_Amp),
            ("AvgSwitchTime_ms", ups_spec.AvgSwitchTime_ms),
            ("AvgBackupTime_ms", ups_spec.AvgBackupTime_ms),
        ]

        for name, value in non_negative_fields:
            self._validate_non_negative(value, name, (int,))

        for overload_type, overload in [
            ("overload_long", ups_spec.overload_long),
            ("overload_medium", ups_spec.overload_medium),
            ("overload_short", ups_spec.overload_short),
        ]:
            self._validate_overload(overload)

    def validate_measurement(self, measurement: Measurement):
        """Validate a Measurement object to ensure data integrity."""
        required_fields = [
            "m_unique_id",
            "time_stamp",
            "name",
            "mode",
            "phase_name",
            "load_type",
            "step_id",
            "load_percentage",
            "steady_state_voltage_tol",
            "voltage_dc_component",
            "load_pf_deviation",
            "switch_time_ms",
            "run_interval_sec",
            "backup_time_sec",
            "overload_time_sec",
            "temperature_1",
            "temperature_2",
        ]

        for field in required_fields:
            if getattr(measurement, field, None) is None:
                raise ValueError(f"Field '{field}' is required and cannot be None.")

        if not isinstance(measurement.time_stamp, Timestamp):
            raise TypeError(
                f"time_stamp must be a google.protobuf.Timestamp, got {type(measurement.time_stamp)}"
            )

        time_stamp_dt = measurement.time_stamp.ToDatetime()
        if not isinstance(time_stamp_dt, datetime):
            raise ValueError("time_stamp conversion to datetime failed")

        self._validate_range(
            measurement.load_percentage, "load_percentage", 0, 100, (int,)
        )

        for field, name in [
            (measurement.steady_state_voltage_tol, "steady_state_voltage_tol"),
            (measurement.voltage_dc_component, "voltage_dc_component"),
            (measurement.load_pf_deviation, "load_pf_deviation"),
            (measurement.switch_time_ms, "switch_time_ms"),
            (measurement.run_interval_sec, "run_interval_sec"),
            (measurement.backup_time_sec, "backup_time_sec"),
            (measurement.overload_time_sec, "overload_time_sec"),
        ]:
            self._validate_non_negative(field, name, (int,))

        if measurement.temperature_1 < -273 or measurement.temperature_2 < -273:
            raise ValueError("Temperature values cannot be below absolute zero.")

        if measurement.power_measures:
            for power_measure in measurement.power_measures:
                self._validate_power_measure(power_measure)

    def _validate_test_report(self, report: TestReport):
        """Validate TestReport object."""
        required_fields = [
            "settings",
            "testName",
            "testDescription",
            "test_result",
        ]

        for field in required_fields:
            if getattr(report, field, None) is None:
                raise ValueError(f"Field '{field}' is required and cannot be None.")

        if (
            not isinstance(report.settings.report_id, int)
            or report.settings.report_id < 0
        ):
            raise ValueError("report_id must be a non-negative integer.")

        #     # Validate testName as an enum
        # if not isinstance(report.testName, TestProto.TestType):  # Adjusted for enum type
        #     raise ValueError("testName must be a valid TestType enum value.")

        # Validate testDescription and test_result as strings
        for field, name in [
            (report.testDescription, "testDescription"),
        ]:
            if not isinstance(field, str) or not field.strip():
                raise ValueError(f"{name} must be a non-empty string.")

        if report.settings:
            self._validate_spec(report.settings.spec)
        if report.measurements:
            for measurement in report.measurements:
                self.validate_measurement(measurement)
