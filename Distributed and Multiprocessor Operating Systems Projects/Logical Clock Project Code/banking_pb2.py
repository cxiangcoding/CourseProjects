# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: banking.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rbanking.proto\"L\n\rClientRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x11\n\tinterface\x18\x02 \x01(\t\x12\r\n\x05money\x18\x03 \x01(\x05\x12\r\n\x05\x63lock\x18\x04 \x01(\x05\"]\n\x0e\x42ranchResponse\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x11\n\tinterface\x18\x02 \x01(\t\x12\x0e\n\x06result\x18\x03 \x01(\t\x12\r\n\x05money\x18\x04 \x01(\x05\x12\r\n\x05\x63lock\x18\x05 \x01(\x05\x32o\n\x06\x42ranch\x12\x30\n\x0bMsgDelivery\x12\x0e.ClientRequest\x1a\x0f.BranchResponse\"\x00\x12\x33\n\x0eMsgPropagation\x12\x0e.ClientRequest\x1a\x0f.BranchResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'banking_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CLIENTREQUEST._serialized_start=17
  _CLIENTREQUEST._serialized_end=93
  _BRANCHRESPONSE._serialized_start=95
  _BRANCHRESPONSE._serialized_end=188
  _BRANCH._serialized_start=190
  _BRANCH._serialized_end=301
# @@protoc_insertion_point(module_scope)
