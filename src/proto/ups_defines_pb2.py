# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: ups_defines.proto
# Protobuf Python Version: 5.28.2
"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 5, 28, 2, "", "ups_defines.proto"
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x11ups_defines.proto\x12\x03ups">\n\x08OverLoad\x12\x17\n\x0fload_percentage\x18\x01 \x01(\r\x12\x19\n\x11overload_time_min\x18\x02 \x01(\r"\x8f\x03\n\x04spec\x12\x19\n\x05phase\x18\x01 \x01(\x0e\x32\n.ups.Phase\x12\x10\n\x08rated_va\x18\x02 \x01(\r\x12\x15\n\rrated_voltage\x18\x03 \x01(\r\x12\x15\n\rrated_current\x18\x04 \x01(\r\x12\x19\n\x11min_input_voltage\x18\x05 \x01(\r\x12\x19\n\x11max_input_voltage\x18\x06 \x01(\r\x12\x18\n\x10pf_rated_current\x18\x07 \x01(\r\x12\x19\n\x11max_continous_amp\x18\x08 \x01(\r\x12\x14\n\x0coverload_amp\x18\t \x01(\r\x12$\n\roverload_long\x18\n \x01(\x0b\x32\r.ups.OverLoad\x12&\n\x0foverload_medium\x18\x0b \x01(\x0b\x32\r.ups.OverLoad\x12%\n\x0eoverload_short\x18\x0c \x01(\x0b\x32\r.ups.OverLoad\x12\x1a\n\x12\x61vg_switch_time_ms\x18\x14 \x01(\x04\x12\x1a\n\x12\x61vg_backup_time_ms\x18\x15 \x01(\x04**\n\x05Phase\x12\x10\n\x0cSINGLE_PHASE\x10\x00\x12\x0f\n\x0bTHREE_PHASE\x10\x01*"\n\x04LOAD\x12\n\n\x06LINEAR\x10\x00\x12\x0e\n\nNON_LINEAR\x10\x01*I\n\x04MODE\x12\x0f\n\x0bNORMAL_MODE\x10\x00\x12\x10\n\x0cSTORAGE_MODE\x10\x01\x12\x0e\n\nFAULT_MODE\x10\x02\x12\x0e\n\nALARM_MODE\x10\x04\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "ups_defines_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_PHASE"]._serialized_start = 492
    _globals["_PHASE"]._serialized_end = 534
    _globals["_LOAD"]._serialized_start = 536
    _globals["_LOAD"]._serialized_end = 570
    _globals["_MODE"]._serialized_start = 572
    _globals["_MODE"]._serialized_end = 645
    _globals["_OVERLOAD"]._serialized_start = 26
    _globals["_OVERLOAD"]._serialized_end = 88
    _globals["_SPEC"]._serialized_start = 91
    _globals["_SPEC"]._serialized_end = 490
# @@protoc_insertion_point(module_scope)