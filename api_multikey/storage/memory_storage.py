import datetime

from api_multikey.storage.exception import KeyExistError, KeyNotFoundError
from api_multikey.storage.interface import SyncStorage


class MemoryStorage(SyncStorage):
    def __init__(self, storage: dict,
                 base_limit: int,
                 soft_error: bool = True):
        """Memory local storage

        :param storage:dict Object, for storage keys
        :param base_limit:int Base limit in seconds, that key will be unavailable
        :param soft_error:bool Raise Error if True
        """
        self.storage = storage
        self.base_limit = base_limit
        self.soft_error = soft_error

    def get_first_key(self, timestamp: datetime.datetime = None, **kwargs) -> str | None:
        """Get the first key from the storage and set a lock on it if found.
        
        This method retrieves the first key from the storage where the timestamp
        is less than the specified timestamp. If a key is found, it is locked, and
        the key is returned
        
        :param timestamp: datetime.datetime, optional
            A timestamp to find a key with a timestamp less than this value.
            If not provided, the current UTC timestamp is used.
        
        :param kwargs: dict, optional
            Additional keyword arguments that can be passed to customize the behavior
            of the function. ( See __init__ )

        :raises: KeyExistError
                If the key already exists in the storage.
            
        :return: str or None  The first key found that meets the criteria, or None if no such key is found.
        """
        keys_sorted_by_timestamp = sorted(self.storage.keys(), key=lambda k: self.storage[k]['timestamp'])
        if timestamp is None:
            timestamp = datetime.datetime.utcnow()

        for key in keys_sorted_by_timestamp:
            if self.storage[key]['timestamp'] < timestamp and not self.storage[key]['is_locked']:
                # Lock key for use
                self.storage[key]['is_locked'] = True
                return key

        self.__raise_exception(KeyNotFoundError("Available keys not found"), kwargs)
        return None

    def get_first_busy_key(self, timestamp: datetime.datetime = None, **kwargs) -> str | None:
        """Get the first unlocked key from the storage with a timestamp greater than or equal to the specified timestamp.

        This method retrieves the first key from the storage where the timestamp is greater than or equal to the
        specified timestamp and the key is not locked. If such a key is found, it is marked as locked and returned.

        Optionally, you can specify a timestamp for filtering the keys. If not provided, the current UTC timestamp
        will be used.

        :param timestamp: datetime.datetime, optional
            A timestamp to filter the keys. Keys with timestamps greater than or equal to this value
            will be considered. This timestamp may be provided as a datetime object or a string representation
            of a date and time. If not provided, the current UTC timestamp will be used.

        :param kwargs: dict, optional
            Additional keyword arguments that can be passed to customize the behavior of the function ( See __init__ )

        :raises: KeyNotFoundError
            If no available key is found matching the criteria.

        :return: str or None
            The first unlocked key found that meets the criteria, or None if no such key is found.
        """

        keys_sorted_by_timestamp = sorted(self.storage.keys(), key=lambda k: self.storage[k]['timestamp'])
        if timestamp is None:
            timestamp = datetime.datetime.utcnow()

        for key in keys_sorted_by_timestamp:
            if self.storage[key]['timestamp'] >= timestamp and not self.storage[key]['is_locked']:
                self.storage[key]['is_locked'] = True
                return key

        self.__raise_exception(KeyNotFoundError("Available keys not found"), kwargs)
        return None

    def add_key(self, key: str, timestamp: datetime.datetime = None, **kwargs):
        """Add a new key to the storage.

            This method adds a new key to the storage with the specified key name. If the key already
            exists in the storage, it raises a 'Key Exist' exception or None ( if soft_error is True )

            Optionally, you can specify a timestamp for the key. If not provided, the current UTC timestamp
            will be used.

            :param key: str
                The name of the key to be added to the storage.

            :param timestamp: datetime.datetime, optional
                A timestamp associated with the key. This timestamp is used to determine the key's
                availability and may be provided as a datetime object or a string representation of a date
                and time. If not provided, the current UTC timestamp will be used.

            :param kwargs: dict, optional
                Additional keyword arguments that can be passed to customize the behavior
                of the function  ( See __init__ )

            :raises: KeyExistError
                If the key already exists in the storage.

            :return: None
            """
        if key in self.storage:
            self.__raise_exception(KeyExistError("Key already exist"), kwargs)
        self.storage[key] = self.__make_key_body(timestamp)

    def return_key(self, key: str, timestamp: datetime.datetime = None, need_cold: bool = False, **kwargs):
        """ Return a key to the storage with an updated timestamp.

        This method returns a key to the storage and updates its timestamp ( if need_cold is True). If the key is not found in the
        storage, it raises a 'Key not Found' exception. Unlock returned key

        Optionally, you can specify a new timestamp for the key. If not provided, the current UTC timestamp
        will be used, and it will be increased by the 'base_limit' if provided.

        :param key: str
            The name of the key to be returned to the storage.

        :param timestamp: datetime.datetime, optional
            A timestamp to update the key with. If not provided, the current UTC timestamp will be used,
            and it will be increased by the 'base_limit' if provided.

        :param need_cold: bool, optional
            If params true, next usage that key will be set after base_limit

        :param kwargs: dict, optional
            Additional keyword arguments that can be passed to customize the behavior of the function ( See __init__ )

        :raises: KeyNotFoundError
            If the key is not found in the storage.

        :return: None
        """
        if key not in self.storage:
            self.__raise_exception(KeyNotFoundError("Key not Found"), kwargs)

        if timestamp is None:
            timestamp = datetime.datetime.utcnow()

        if need_cold:
            base_limit = kwargs['base_limit'] if 'base_limit' in kwargs else self.base_limit
            timestamp = timestamp + datetime.timedelta(seconds=base_limit)

        self.storage[key] = self.__make_key_body(timestamp)

    def __make_key_body(self, timestamp: datetime.datetime, is_locked: bool = False, **kwargs):
        return {'is_locked': is_locked, 'timestamp': timestamp}

    def __raise_exception(self, exception: Exception, kwargs: dict):
        """Wrapper for raise Exceptions"""

        soft_error = kwargs['soft_error'] if 'soft_error' in kwargs else self.soft_error
        if not soft_error:
            raise exception
