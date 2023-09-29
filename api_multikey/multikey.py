import datetime
import time
from functools import wraps

from api_multikey.exception import ArgumentsError, APIKeyError
from api_multikey.storage.interface import SyncStorage
from api_multikey.utils import get_sync_storage, parse_key_from_file


def init_key_to_storage(keys: list[str] = None, filepath: str = None, storage: SyncStorage | str = None):
    """Initialize keys and add them to the specified storage.

        This function initializes a list of keys or retrieves them from a file and adds them to a SyncStorage
        instance specified by the 'storage' parameter using the 'add_key' method.

        You can provide either a list of keys directly, specify a file containing the keys, or specify a string
        identifier for the desired SyncStorage object. If both 'keys' and 'filepath' are provided will be union.

        :param keys: list of str, optional
            A list of keys to be added to the storage.

        :param filepath: str, optional
            The path to a file containing keys. Each key should be on a separate line in the file.

        :param storage: SyncStorage or str, optional
            A SyncStorage object where the keys should be added or a string identifier for the desired SyncStorage.
            If a string identifier is provided, the corresponding SyncStorage object will be retrieved using
            the 'get_sync_storage' function.

        :raises: ArgumentsError
            If neither 'keys' nor 'filepath' are specified.

        :return: None
    """
    if not keys and not filepath:
        ArgumentsError("must be specified keys or filepath with keys")
    if not isinstance(storage, SyncStorage):
        storage = get_sync_storage(storage)

    keys = keys if keys else []
    if filepath:
        keys = list(set(keys).union(parse_key_from_file(filepath)))

    for _ in keys:
        storage.add_key(_)


def with_key_from_storage(storage: SyncStorage | str = None):
    """Decorator for handling API keys from a storage.

    This decorator is designed to be used with functions that require an API key for their operation. It manages the
    retrieval, usage, and return of API keys from the specified `storage`. If the `storage` argument is a string,
    it is treated as an identifier for a SyncStorage object, which is retrieved using the 'get_sync_storage' function.

    The decorator continuously tries to obtain an API key from the storage and passes it to the decorated function.
    If no API key is available, it checks for the next available key and waits until it becomes available.
    If an APIKeyError is raised during the function's execution, the key is returned to the storage with an optional
    flag for "cold" return.

    Your function need to raise APIKeyError, if you have some error with Api Keys. In another cases error will not be handled
    at decorator

    :param storage: SyncStorage or str, optional
        A SyncStorage object or a string identifier for the desired SyncStorage object.

    :return: decorator
        The decorator function that can be applied to other functions.

    Example Usage:
    ```python
    @with_key_from_storage('my_storage')
    def api_function(api_key):
        # Your API function code here
        pass
    ```

    Example Usage with SyncStorage object:
    ```python
    my_storage = get_sync_storage('my_storage')

    @with_key_from_storage(my_storage)
    def api_function(api_key):
        # Your API function code here
        pass
    ```
    """
    if not isinstance(storage, SyncStorage):
        storage = get_sync_storage(storage)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                api_key = storage.get_first_key(soft_error=True)
                if api_key is None:
                    r = storage.get_first_busy_key(soft_error=False)
                    api_key, next_free_key_dt = r
                    current_time = datetime.datetime.utcnow()
                    print(next_free_key_dt)
                    # Get waiting time and increase by 1s ( fot fix bug with ms)
                    time.sleep((next_free_key_dt - current_time).total_seconds() + 1)
                try:
                    result = func(api_key, *args, **kwargs)
                    storage.return_key(api_key)
                    return result
                except APIKeyError as e:
                    storage.return_key(api_key, need_cold=True)

        return wrapper

    return decorator
