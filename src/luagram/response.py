import threading
from typing import TYPE_CHECKING

from .enums import Status
from .gadget.tools import arguments


if TYPE_CHECKING:
    from .luagram import Luagram


class Response:
    def __repr__(self) -> str:
        return 'Response<%s, %s>' % (self.status, self.query_id)

    def __init__(self, query: dict, client: 'Luagram', query_id: str) -> None:

        self.query = query
        self.client = client
        self.query_id = query_id
        
        self.update = None
        self.status = Status.PENDING
        self.error_info = None
        self._result_event = threading.Event()
    
    @property
    def done(self):
        return self._result_event.is_set()

    @arguments
    def wait(self, timeout: int=None):
        self._result_event.wait(timeout=timeout)

        if self.done:
            return self


    def set_update(self, update: dict):
        update_type = update.get('@type')
        self.client.logger.debug('query_id=%s type=%s received', self.query_id, update_type)

        if update_type == 'error':
            self.status = Status.ERROR
            self.error_info = update
        
        else:
            self.status = Status.OK
            self.update = update

        return self._result_event.set()

    