from pathlib import Path
from enum import Enum
from typing import Any, Optional
from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp

from google.protobuf.timestamp_pb2 import Timestamp
from proto.pData_pb2 import PowerMeasure, PowerMeasureType
from proto.report_pb2 import Measurement, ReportSettings, TestReport, TestStandard

from proto.ups_test_pb2 import TestResult, TestType
from proto.ups_defines_pb2 import LOAD, MODE, OverLoad, Phase, spec


class Validator:
    @staticmethod
    def _validate_non_negative(value: Any, field_name: str, types: tuple):
        """Generic validation for non-negative numbers."""
        if not isinstance(value, types):
            try:
                value = types[0](value)  # Attempt to cast to the first type
            except (ValueError, TypeError):
                raise TypeError(
                    f"'{field_name}' must be of type {', '.join(t.__name__ for t in types)}, got {type(value)}"
                )
        if value < 0:
            raise ValueError(
                f"'{field_name}' must be a non-negative value, got {value}."
            )

    @staticmethod
    def _validate_range(value, field_name, min_val=None, max_val=None, types=(int,)):
        """
        Validate that a value is within a specified range and of a valid type.
        """
        # Attempt to cast the value if it's not already the correct type
        if not isinstance(value, types):
            try:
                value = types[0](value)  # Convert to the first expected type
            except (ValueError, TypeError):
                raise TypeError(
                    f"'{field_name}' must be of type {types}, got {type(value)}"
                )

        # Check the range if min_val and max_val are provided
        if min_val is not None and value < min_val:
            raise ValueError(f"'{field_name}' must be >= {min_val}, got {value}")
        if max_val is not None and value > max_val:
            raise ValueError(f"'{field_name}' must be <= {max_val}, got {value}")

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
            ("rated_va", ups_spec.rated_va),
            ("rated_voltage", ups_spec.rated_voltage),
            ("rated_current", ups_spec.rated_current),
            ("min_input_voltage", ups_spec.min_input_voltage),
            ("max_input_voltage", ups_spec.max_input_voltage),
            ("pf_rated_current", ups_spec.pf_rated_current),
            ("max_continous_amp", ups_spec.max_continous_amp),
            ("overload_Amp", ups_spec.overload_amp),
            ("avg_switch_time_ms", ups_spec.avg_switch_time_ms),
            ("avg_backup_time_ms", ups_spec.avg_backup_time_ms),
        ]

        for name, value in non_negative_fields:
            self._validate_non_negative(value, name, (int,))

        for overload_type, overload in [
            ("overload_long", ups_spec.overload_long),
            ("overload_medium", ups_spec.overload_medium),
            ("overload_short", ups_spec.overload_short),
        ]:
            self._validate_overload(overload)

    def _validate_report_settings(self, report_settings: ReportSettings):
        """Validate ReportSettings object."""
        # Validate required fields
        required_fields = [
            ("report_id", report_settings.report_id),
            ("standard", report_settings.standard),
            ("ups_model", report_settings.ups_model),
        ]
        for field_name, value in required_fields:
            if value is None:
                raise ValueError(f"'{field_name}' is required and cannot be None.")

        # Validate optional fields (if provided)
        optional_text_fields = [
            ("client_name", report_settings.client_name),
            ("brand_name", report_settings.brand_name),
            ("test_engineer_name", report_settings.test_engineer_name),
            ("test_approval_name", report_settings.test_approval_name),
        ]
        for field_name, value in optional_text_fields:
            if value is not None and not isinstance(value, str):
                raise TypeError(
                    f"'{field_name}' must be of type str, got {type(value)}."
                )

        # Validate spec_id (if provided)
        if report_settings.report_id is not None:
            self._validate_non_negative(report_settings.report_id, "report_id", (int,))

    def validate_measurement(self, measurement: Measurement):
        """Validate a Measurement object to ensure data integrity."""
        # Fields that are always mandatory
        required_fields = [
            "m_unique_id",
            "time_stamp",
            "name",
        ]

        for field in required_fields:
            if getattr(measurement, field, None) is None:
                raise ValueError(f"Field '{field}' is required and cannot be None.")

        # Validate time_stamp
        if not isinstance(measurement.time_stamp, Timestamp):
            raise TypeError(
                f"time_stamp must be a google.protobuf.Timestamp, got {type(measurement.time_stamp)}"
            )

        time_stamp_dt = measurement.time_stamp.ToDatetime()
        if not isinstance(time_stamp_dt, datetime):
            raise ValueError("time_stamp conversion to datetime failed")

        # Validate optional numeric fields if provided
        optional_numeric_fields = [
            ("load_percentage", 0, 100, (int,)),
            ("steady_state_voltage_tol", 0, None, (int,)),
            ("voltage_dc_component", 0, None, (int,)),
            ("load_pf_deviation", 0, None, (int,)),
            ("switch_time_ms", 0, None, (int,)),
            ("run_interval_sec", 0, None, (int,)),
            ("backup_time_sec", 0, None, (int,)),
            ("overload_time_sec", 0, None, (int,)),
        ]

        for field, min_value, max_value, types in optional_numeric_fields:
            value = getattr(measurement, field, None)
            if value is not None:
                self._validate_range(value, field, min_value, max_value, types)

        # Validate temperatures if provided
        if measurement.temperature_1 is not None and measurement.temperature_1 < -273:
            raise ValueError("temperature_1 cannot be below absolute zero.")
        if measurement.temperature_2 is not None and measurement.temperature_2 < -273:
            raise ValueError("temperature_2 cannot be below absolute zero.")

        # Validate power measures if provided
        if measurement.power_measures:
            for power_measure in measurement.power_measures:
                self._validate_power_measure(power_measure)

    def _validate_test_report(self, report: TestReport):
        """Validate TestReport object."""
        required_fields = [
            "settings",
            "test_name",
            "test_description",
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

        # Validate testDescription and test_result as strings
        for field, name in [
            (report.test_description, "test_description"),
        ]:
            if not isinstance(field, str) or not field.strip():
                raise ValueError(f"{name} must be a non-empty string.")

        if report.settings:
            self._validate_report_settings(report.settings)
            if report.settings.spec:
                self._validate_spec(report.settings.spec)
        if report.measurements:
            for measurement in report.measurements:
                self.validate_measurement(measurement)
