from api_multikey.exception import StorageNotFound
from api_multikey.config import storages as dict_of_storage
from api_multikey.storage.interface import SyncStorage


def get_sync_storage(storage: str | None) -> SyncStorage:
    """Get a SyncStorage object based on the provided storage identifier.

       This function retrieves a SyncStorage object based on the storage identifier provided as an argument.
       If the 'storage' argument is None, it returns the first available storage from the 'storages' dictionary.
       If the 'storage' argument is a string that matches a key in the 'storages' dictionary, it returns
       the corresponding SyncStorage object.

       :param storage: str or None
           A string identifier for the desired SyncStorage object. If None, the first available storage
           from the 'storages' dictionary will be returned.

       :return: SyncStorage
           The SyncStorage object associated with the provided 'storage' identifier.

       :raises: StorageNotFound
           If the 'storage' argument is a string that does not match any key in the 'storages' dictionary
           or if it is None and no storages are available.
    """
    storages = get_storages()

    if storage is None:
        for _ in storages.keys():
            return storages[_]
    if isinstance(storage, str) and storage in storages:
        return storages[storage]
    raise StorageNotFound("storage not found")


def parse_key_from_file(filepath: str) -> list[str]:
    """Read keys from a file and return them as a list of strings.

    This function reads keys from a file where each key is on a separate line and returns them as a list
    of strings.

    :param filepath: str
        The path to the file containing the keys.

    :return: list of str
        A list of keys read from the file.
    """
    keys = []
    with open(filepath, 'r') as file:
        for line in file:
            key = line.strip()
            if key:
                keys.append(key)
    return keys


def get_storages() -> dict:
    return dict_of_storage
