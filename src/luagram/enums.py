import enum


class Status(enum.Enum):
    OK = enum.auto()
    ERROR = enum.auto()
    PENDING = enum.auto()


class AuthState(enum.Enum):
    NONE = None
    READY = 'authorizationStateReady'
    CLOSED = 'authorizationStateClosed'
    CLOSING = 'authorizationStateClosing'
    WAIT_CODE = 'authorizationStateWaitCode'
    WAIT_PASSWORD = 'authorizationStateWaitPassword'
    WAIT_PHONE_NUMBER = 'authorizationStateWaitPhoneNumber'
    WAIT_REGISTRATION = 'authorizationStateWaitRegistration'
    WAIT_ENCRYPTION_KEY = 'authorizationStateWaitEncryptionKey'
    WAIT_TDLIB_PARAMETERS = 'authorizationStateWaitTdlibParameters'

