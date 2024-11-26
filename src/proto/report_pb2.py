# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: report.proto
# Protobuf Python Version: 5.28.2
"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 5, 28, 2, "", "report.proto"
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
import pData_pb2 as pData__pb2
import ups_test_pb2 as ups__test__pb2
import upsDefines_pb2 as upsDefines__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0creport.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x0bpData.proto\x1a\x0eups_test.proto\x1a\x10upsDefines.proto"\xd1\x01\n\x0eReportSettings\x12\x11\n\treport_id\x18\x01 \x01(\r\x12\x1f\n\x08standard\x18\x02 \x01(\x0e\x32\r.TestStandard\x12\x11\n\tups_model\x18\x03 \x01(\r\x12\x17\n\x04spec\x18\x04 \x01(\x0b\x32\t.ups.spec\x12\x13\n\x0b\x63lient_name\x18\x05 \x01(\t\x12\x12\n\nbrand_name\x18\x06 \x01(\t\x12\x1a\n\x12test_engineer_name\x18\x07 \x01(\t\x12\x1a\n\x12test_approval_name\x18\x08 \x01(\t"\xf3\x03\n\x0bMeasurement\x12\x13\n\x0bm_unique_id\x18\x01 \x01(\r\x12.\n\ntime_stamp\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x17\n\x04mode\x18\x04 \x01(\x0e\x32\t.ups.MODE\x12\x12\n\nphase_name\x18\x05 \x01(\t\x12\x1c\n\tload_type\x18\x06 \x01(\x0e\x32\t.ups.LOAD\x12\x0f\n\x07step_id\x18\x07 \x01(\r\x12\x17\n\x0fload_percentage\x18\x08 \x01(\r\x12-\n\x0epower_measures\x18\t \x03(\x0b\x32\x15.measure.PowerMeasure\x12 \n\x18steady_state_voltage_tol\x18\n \x01(\r\x12\x1c\n\x14voltage_dc_component\x18\x0b \x01(\r\x12\x19\n\x11load_pf_deviation\x18\x0c \x01(\r\x12\x16\n\x0eswitch_time_ms\x18\r \x01(\r\x12\x18\n\x10run_interval_sec\x18\x0e \x01(\r\x12\x17\n\x0f\x62\x61\x63kup_time_sec\x18\x0f \x01(\r\x12\x19\n\x11overload_time_sec\x18\x10 \x01(\r\x12\x15\n\rtemperature_1\x18\x11 \x01(\r\x12\x15\n\rtemperature_2\x18\x12 \x01(\r"\xb5\x01\n\nTestReport\x12!\n\x08settings\x18\x01 \x01(\x0b\x32\x0f.ReportSettings\x12 \n\x08testName\x18\x02 \x01(\x0e\x32\x0e.Test.TestType\x12\x17\n\x0ftestDescription\x18\x03 \x01(\t\x12"\n\x0cmeasurements\x18\x04 \x03(\x0b\x32\x0c.Measurement\x12%\n\x0btest_result\x18\x05 \x01(\x0e\x32\x10.Test.TestResult*c\n\x0cTestStandard\x12\x0f\n\x0bIEC_62040_1\x10\x00\x12\x0f\n\x0bIEC_62040_2\x10\x01\x12\x0f\n\x0bIEC_62040_3\x10\x02\x12\x0f\n\x0bIEC_62040_4\x10\x03\x12\x0f\n\x0bIEC_62040_5\x10\x04\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "report_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_TESTSTANDARD"]._serialized_start = 994
    _globals["_TESTSTANDARD"]._serialized_end = 1093
    _globals["_REPORTSETTINGS"]._serialized_start = 97
    _globals["_REPORTSETTINGS"]._serialized_end = 306
    _globals["_MEASUREMENT"]._serialized_start = 309
    _globals["_MEASUREMENT"]._serialized_end = 808
    _globals["_TESTREPORT"]._serialized_start = 811
    _globals["_TESTREPORT"]._serialized_end = 992
# @@protoc_insertion_point(module_scope)
