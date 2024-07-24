import os
import re
import lupa
import uuid
import queue
import getpass
import logging
import platform
import threading
from typing import Optional, Callable, Union, List
from logging.handlers import RotatingFileHandler

from .enums import Status, AuthState
from .gadget import TDJson, tools
from .response import Response


__version__ = '1.0.3'



class Params:
    @tools.arguments
    def __init__(self,
                 api_id: int,
                 api_hash: str,
                 database_encryption_key: str,
                 app_version: str = __version__,
                 device_model: Optional[str] = None,
                 system_version: Optional[str] = None,
                 system_language_code: str = 'en',
                 test_mode: bool = False,
                 use_secret_chats: bool = True,
                 use_file_database: bool = True,
                 use_message_database: bool = True,
                 use_chat_info_database: bool = True):

        if not isinstance(api_id, int):
            raise TypeError(f'Expected a int for \'api_id\', but got {type(api_id).__name__} instead.')
        
        if not isinstance(api_hash, str):
            raise TypeError(f'Expected a string for \'api_hash\', but got {type(api_hash).__name__} instead.')

        if not isinstance(database_encryption_key, str):
            raise TypeError(f'Expected a string for \'database_encryption_key\', but got {type(database_encryption_key).__name__} instead.')

        if not isinstance(app_version, str):
            raise TypeError(f'Expected a string for \'app_version\', but got {type(app_version).__name__} instead.')
            
        if not (isinstance(device_model, str) or device_model is None):
            raise TypeError(f'Expected a string or None for \'device_model\', but got {type(device_model).__name__} instead.')
        
        if not (isinstance(system_version, str) or system_version is None):
            raise TypeError(f'Expected a string or None for \'system_version\', but got {type(system_version).__name__} instead.')
        
        if not isinstance(system_language_code, str):
            raise TypeError(f'Expected a string for \'system_language_code\', but got {type(system_language_code).__name__} instead.')
        

        if not device_model or not system_version:
            system = platform.uname()

            if system.machine in ('x86_64', 'AMD64'):
                default_device_model = 'PC 64bit'

            elif system.machine in ('i386', 'i686', 'x86'):
                default_device_model = 'PC 32bit'

            else:
                default_device_model = system.machine

            default_system_version = re.sub(r'-.+', '', system.release)
            device_model = device_model or default_device_model
            system_version = system_version or default_system_version
            
        self.api_id = api_id
        self.api_hash = api_hash
        self.database_encryption_key = database_encryption_key

        self.app_version = app_version
        self.device_model = device_model
        self.system_version = system_version
        self.system_language_code = system_language_code
        
        self.test_mode = bool(test_mode)
        self.use_secret_chats = bool(use_secret_chats)
        self.use_file_database = bool(use_file_database)
        self.use_message_database = bool(use_message_database)
        self.use_chat_info_database = bool(use_chat_info_database)


class Settings:
    @tools.arguments
    def __init__(self,
                 verbosity: int = 0,
                 base_logger: Optional['BaseLogger'] = None,
                 queue_put_timeout: int = 10,
                 updates_queue_size: int = 1000) -> None:

        if not isinstance(verbosity, int):
            raise TypeError(f'Expected a int for \'verbosity\', but got {type(verbosity).__name__} instead.')


        if not (isinstance(base_logger, BaseLogger) or base_logger is None):
            raise TypeError(f'Expected a BaseLogger or None for \'base_logger\', but got {type(base_logger).__name__} instead.')

        if base_logger is None:
            base_logger = BaseLogger()

        if not isinstance(queue_put_timeout, int):
            raise TypeError(f'Expected a int for \'queue_put_timeout\', but got {type(queue_put_timeout).__name__} instead.')

        if not isinstance(updates_queue_size, int):
            raise TypeError(f'Expected a int for \'updates_queue_size\', but got {type(updates_queue_size).__name__} instead.')
        

        self.verbosity = verbosity
        self.base_logger = base_logger
        self.queue_put_timeout = queue_put_timeout
        self.updates_queue_size = updates_queue_size


class BaseLogger:
    @tools.arguments
    def __init__(self,
                 path: Optional[str] = None,
                 level: int = 1,
                 max_file_size: int = 0):


        if not (isinstance(path, str) or path is None):
            raise TypeError(f'Expected a string or None for \'file\', but got {type(path).__name__} instead.')

        if not isinstance(level, int):
            raise TypeError(f'Expected a int for \'level\', but got {type(level).__name__} instead.')
        

        if not isinstance(max_file_size, int):
            raise TypeError(f'Expected a int for \'max_file_size\', but got {type(max_file_size).__name__} instead.')
        

        self.path = path
        self.level = level
        self.max_file_size = max_file_size


class LuagramClient:
    @tools.arguments
    def __init__(self,
                 name: str,
                 params: Params,
                 settings: Optional[Settings] = None,
                 library_path: Optional[str] = None):
        

        if not isinstance(name, str):
            raise TypeError(f'Expected a string for \'name\', but got {type(name).__name__} instead.')
        
        if not isinstance(params, Params):
            raise TypeError(f'Expected a Params for \'api_hash\', but got {type(params).__name__} instead.')
        
        if not (isinstance(settings, Settings) or settings is None):
            raise TypeError(f'Expected a Settings or None for \'settings\', but got {type(params).__name__} instead.')

        if not isinstance(library_path, str):
            raise TypeError(f'Expected a string for \'library_path\', but got {type(library_path).__name__} instead.')

        if settings is None:
            settings = Settings()


        self.name = name
        self.params = params
        self.settings = settings
    
    
        self.logger = logging.getLogger('luagram.client.%s' % name)
        if settings.base_logger.path:
            path = settings.base_logger.path.replace('%name', name)

            dir_name = os.path.dirname(path)
            if not os.path.isdir(dir_name):
                os.makedirs(dir_name)

            hdlr = RotatingFileHandler(path,
                                       maxBytes=settings.base_logger.max_file_size)

            self.logger.addHandler(hdlr)
        self.logger.setLevel(settings.base_logger.level)


        self._tdjson = TDJson(self.logger,
                              verbosity=settings.verbosity,
                              library_path=library_path)
        
        self._pending_results = {}
        
        self._updates_queue = queue.Queue(maxsize=settings.updates_queue_size)
        self._stopped_event = threading.Event()


        self._listener_thread = threading.Thread(target=self._listener, daemon=True)
        self._listener_thread.start()

    @tools.arguments
    def __call__(self,
                 query: dict,
                 block: bool=True):
        return self._send_query(query, block=block)


    @tools.arguments
    def start(self,
              token: Optional[str] = None,
              phone: Union[str, Callable] = lambda: input('Please enter your phone (or bot token): '),
              last_name: Union[str, Callable] = lambda: input('Enter last name: '),
              first_name: Union[str, Callable] = lambda: input('Enter first name: '),
              code_callback: Callable = lambda _: input('Please enter the code you received: '),
              password_callback: Optional[Union[str, Callable]] = lambda _: getpass.getpass('Please enter your password: ')) -> None:

        result = None
        next_step = AuthState.NONE
        self.logger.info('started')
        
        while next_step != AuthState.READY:
            self.logger.info('[login] auth state: %s', next_step)

            if next_step is AuthState.NONE:
                self.logger.info('getting authorization state')

                result = self._send_query(
                    {
                        '@type': 'getAuthorizationState'
                    },
                    query_id='getAuthorizationState')
            
            
            elif next_step is AuthState.WAIT_TDLIB_PARAMETERS:
                self.logger.info('setting tdlib parameters')
    
                parameters = {
                    'api_id': self.params.api_id,
                    'api_hash': self.params.api_hash,
                    'use_test_dc': self.params.test_mode,
                    'device_model': self.params.device_model,
                    'system_version': self.params.system_version,
                    'application_version': self.params.app_version,
                    'system_language_code': self.params.system_language_code,
                    
                    'use_secret_chats': self.params.use_secret_chats,
                    'use_file_database': self.params.use_file_database,
                    'use_message_database': self.params.use_message_database,
                    'use_chat_info_database': self.params.use_chat_info_database,
                    
                    
                    'files_directory': os.path.join('.app-data', self.name),
                    'database_directory': os.path.join('.app-data', self.name, 'database')

                }
        
                result = self._send_query(
                    {
                        '@type': 'setTdlibParameters',
                        'parameters': parameters,

                        # 1.8.6 <= tdlib
                        **parameters,
                        'database_encryption_key': self.params.database_encryption_key
                    },
                    query_id='updateAuthorizationState'
                )
            
            elif next_step is AuthState.WAIT_ENCRYPTION_KEY:
                self.logger.info('sending tdlib encryption key')
                result = self._send_query(
                    {
                        '@type': 'checkDatabaseEncryptionKey',
                        'encryption_key': self.params.database_encryption_key
                    },
                    query_id='updateAuthorizationState'
                )
            
            elif next_step is AuthState.WAIT_PHONE_NUMBER:
                if not token and callable(phone):
                    data = phone()

                    if ':' in data:
                        token = data 
                    
                    else:
                        phone = data
                
                if token:
                    self.logger.info('sending bot token')
                    query = {
                        '@type': 'checkAuthenticationBotToken',
                        'token': token
                    }
                
                else:
                    self.logger.info('sending phone number')
                    query = {
                        '@type': 'setAuthenticationPhoneNumber',
                        'phone_number': phone
                    }
                
                result = self._send_query(query, query_id='updateAuthorizationState')
            
            elif next_step is AuthState.WAIT_CODE:

                self.logger.debug('sending code')
                result = self._send_query(
                    {
                        '@type': 'checkAuthenticationCode',
                        'code': code_callback(result)
                    },
                    query_id='updateAuthorizationState'
                )

            elif next_step is AuthState.WAIT_PASSWORD:
                self.logger.debug('sending password')
                result = self._send_query(
                    {
                        '@type': 'checkAuthenticationPassword',
                        'password': password_callback(result)
                    },
                    query_id='updateAuthorizationState'
                )
            
            elif next_step is AuthState.WAIT_REGISTRATION:
                
                if callable(first_name):
                    first_name = first_name()
                
                if callable(last_name):
                    last_name = last_name()
                
                result = self._send_query(
                    {
                        '@type': 'registerUser',
                        'first_name': first_name, 'last_name': last_name
                    },
                    query_id='updateAuthorizationState'
                )
            
            if result.status is Status.OK:
                try:
                    auth_state = result.update.get('authorization_state')
                    if auth_state is None:
                        next_step = AuthState(result.update.get('@type'))
                    
                    else:
                        
                        next_step = AuthState(auth_state.get('@type'))
                
                except ValueError:
                    next_step = AuthState.NONE
            
            else:
                self.logger.error('auth state error: %s', result.error_info)

    @tools.arguments
    def get_updates(self, handlers: List[Callable]):
        self.logger.info('getting updates: %s handlers', len(handlers))
        while not self._stopped_event.is_set():
            try:
                update = self._updates_queue.get(timeout=0.5)

            except queue.Empty:
                continue

            else:
                if update:
                    update_type = update.get('@type')
        
                    for value in handlers.values():
                        if lupa.lua_type(value) == 'table':
                            if lupa.lua_type(value[2]) == 'table':
                                if update_type not in value[2].values():
                                    continue
        
                            handler = value[1]
 
                        elif lupa.lua_type(value) == 'function':
                            handler = value

                        try:
                            handler(update)

                        except BaseException as e:
                            self.logger.error('handler %s: %s', handler, e)


    def stop(self):
        self._tdjson.stop()
        self._stopped_event.set()
        self._listener_thread.join()

    def _send_query(self,
                    query: dict,
                    *,
                    block: bool=True,
                    query_id: Optional[Union[str, int]] = None):
        block = bool(block)
        query = dict(query)

        if not query_id:
            query_id = uuid.uuid4().hex
    
        if '@extra' not in query:
            query['@extra'] = {}

        query['@extra']['query_id'] = query_id

        self._pending_results[query_id] = result = Response(query=query,
                                                            client=self,
                                                            query_id=query_id)
        
        try:
            self._tdjson.send(query)
        
        except Exception as err:
            self._pending_results.pop(query_id)
            self.logger.error('send query: %s', query, exc_info=err)
        
        else:
            if block:
                result = result.wait()

            return result

    def _listener(self):
        self.logger.info('listener started')
        while not self._stopped_event.is_set():
            update = self._tdjson.receive()
            if update:
                extra = update.get('@extra')
                query_id = None

                if update.get('@type') == 'updateAuthorizationState':
                    query_id = update['@type']
                
                elif isinstance(extra, dict):
                    query_id = extra.get('query_id')

                else:
                    self.logger.debug('extra has not been found in the update')
        
                if not query_id:
                    self.logger.debug('query_id has not been found in the update')
                
                result = self._pending_results.get(query_id)

                if result is None:
                    self.logger.debug('result has not been found in by query_id=%s', query_id)

                else:
                    result.set_update(update)
                    self._pending_results.pop(query_id, None)

            self._updates_queue.put(update, timeout=self.settings.queue_put_timeout)
