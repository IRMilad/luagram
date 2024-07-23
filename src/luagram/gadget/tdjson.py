import sys
import json
import ctypes.util
from logging import Logger
from typing import Optional
from ctypes import CDLL, CFUNCTYPE, c_int, c_char_p, c_double, c_void_p, c_longlong



class TDJson:
    def __init__(self, logger: Logger, verbosity: int, library_path: Optional[str] = None):
        self.logger = logger

        if library_path is None:
            library_path = ctypes.util.find_library('tdjson')

        if library_path is None:
            sys.exit('tdjson library not found')

        else:
            self._tdjson = CDLL(library_path)
            self.logger.info('Using shared library "%s"', library_path)



        # load tdjson functions 
        self._td_json_client_create = self._tdjson.td_json_client_create
        self._td_json_client_create.restype = c_void_p
        self._td_json_client_create.argtypes = []
        self.td_json_client = self._td_json_client_create()


        self._td_json_client_receive = self._tdjson.td_json_client_receive
        self._td_json_client_receive.restype = c_char_p
        self._td_json_client_receive.argtypes = [c_void_p, c_double]


        self._td_json_client_send = self._tdjson.td_json_client_send
        self._td_json_client_send.restype = None
        self._td_json_client_send.argtypes = [c_void_p, c_char_p]


        self._td_json_client_execute = self._tdjson.td_json_client_execute
        self._td_json_client_execute.restype = c_char_p
        self._td_json_client_execute.argtypes = [c_void_p, c_char_p]


        self._td_json_client_destroy = self._tdjson.td_json_client_destroy
        self._td_json_client_destroy.restype = None
        self._td_json_client_destroy.argtypes = [c_void_p]


        self._td_set_log_verbosity_level = self._tdjson.td_set_log_verbosity_level
        self._td_set_log_verbosity_level.restype = None
        self._td_set_log_verbosity_level.argtypes = [c_int]
        self._td_set_log_verbosity_level(verbosity)


        fatal_error_callback_type = CFUNCTYPE(None, c_char_p)
        self._td_set_log_fatal_error_callback = self._tdjson.td_set_log_fatal_error_callback
        self._td_set_log_fatal_error_callback.restype = None
        self._td_set_log_fatal_error_callback.argtypes = [fatal_error_callback_type]

        def on_fatal_error_callback(error_message: str) -> None:
            self.logger.error('TDLib fatal error: %s', error_message)

        c_on_fatal_error_callback = fatal_error_callback_type(on_fatal_error_callback)
        self._td_set_log_fatal_error_callback(c_on_fatal_error_callback)

    def stop(self):
        return self._td_json_client_destroy(self.td_json_client)

    def send(self, query: dict) -> None:
        dump = json.dumps(query)
        self.logger.debug('sent query: %s', dump)
        self._td_json_client_send(self.td_json_client, dump.encode(encoding='utf-8'))

    def receive(self) -> Optional[dict]:
        result = self._td_json_client_receive(self.td_json_client, 1.0)

        if result:
            self.logger.debug('received: %s', result)
            return json.loads(result)

    def execute(self, query):
        dump = json.dumps(query)
        self.logger.debug('sent query: %s', dump)
        result = self._td_json_client_execute(self.td_json_client,
                                              dump.encode(encoding='utf-8'))

        if result:
            self.logger.debug('received: %s', result)
            return json.loads(result)



        