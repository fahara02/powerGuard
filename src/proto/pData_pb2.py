# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: pData.proto
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
    'pData.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bpData.proto\x12\x07measure\"\x97\x01\n\x0cPowerMeasure\x12\'\n\x04type\x18\x01 \x01(\x0e\x32\x19.measure.PowerMeasureType\x12\x0f\n\x07voltage\x18\x02 \x01(\x02\x12\x0f\n\x07\x63urrent\x18\x03 \x01(\x02\x12\r\n\x05power\x18\x04 \x01(\x02\x12\x0e\n\x06\x65nergy\x18\x05 \x01(\x02\x12\n\n\x02pf\x18\x06 \x01(\x02\x12\x11\n\tfrequency\x18\x07 \x01(\x02*<\n\x10PowerMeasureType\x12\r\n\tUPS_INPUT\x10\x00\x12\x0e\n\nUPS_OUTPUT\x10\x01\x12\t\n\x05MAINS\x10\x02\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'pData_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_POWERMEASURETYPE']._serialized_start=178
  _globals['_POWERMEASURETYPE']._serialized_end=238
  _globals['_POWERMEASURE']._serialized_start=25
  _globals['_POWERMEASURE']._serialized_end=176
# @@protoc_insertion_point(module_scope)
