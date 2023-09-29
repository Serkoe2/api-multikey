from api_multikey.exception import ArgumentsError
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
