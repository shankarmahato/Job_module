# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from . import configurator_pb2 as configurator__pb2


class ProgramStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.getProgramInfo = channel.unary_unary(
                '/Configurator.Program/getProgramInfo',
                request_serializer=configurator__pb2.ProgramInfoRequest.SerializeToString,
                response_deserializer=configurator__pb2.ProgramInfoResponse.FromString,
                )


class ProgramServicer(object):
    """Missing associated documentation comment in .proto file"""

    def getProgramInfo(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ProgramServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'getProgramInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.getProgramInfo,
                    request_deserializer=configurator__pb2.ProgramInfoRequest.FromString,
                    response_serializer=configurator__pb2.ProgramInfoResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Configurator.Program', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Program(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def getProgramInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Configurator.Program/getProgramInfo',
            configurator__pb2.ProgramInfoRequest.SerializeToString,
            configurator__pb2.ProgramInfoResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)