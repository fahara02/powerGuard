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
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    2,
    '',
    'report.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import pData_pb2 as pData__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0creport.proto\x1a\x0bpData.proto\"&\n\x06report\x12\x1c\n\x05power\x18\x01 \x01(\x0b\x32\r.PowerMeasure\"\n\n\x08UPS_SPEC*f\n\x08TestType\x12\x0e\n\nSwitchTest\x10\x00\x12\x0e\n\nBackupTest\x10\x01\x12\x12\n\x0e\x45\x66\x66iciencyTest\x10\x02\x12\x14\n\x10InputVoltageTest\x10\x03\x12\x10\n\x0cWaveformTest\x10\x04\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'report_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_TESTTYPE']._serialized_start=81
  _globals['_TESTTYPE']._serialized_end=183
  _globals['_REPORT']._serialized_start=29
  _globals['_REPORT']._serialized_end=67
  _globals['_UPS_SPEC']._serialized_start=69
  _globals['_UPS_SPEC']._serialized_end=79
# @@protoc_insertion_point(module_scope)
