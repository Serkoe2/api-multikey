import pytest
from api_multikey import utils
from api_multikey.exception import StorageNotFound


class MockSyncStorage:
    def __init__(self, name):
        self.name = name


@pytest.fixture
def patch_storage(monkeypatch):
    def mock_get_storages():
        return {
            'storage1': MockSyncStorage('Storage 1'),
            'storage2': MockSyncStorage('Storage 2')
        }

    monkeypatch.setattr('api_multikey.utils.get_storages', mock_get_storages)


def test_get_sync_storage_with_existing_key(patch_storage):
    storage = utils.get_sync_storage('storage1')
    assert isinstance(storage, MockSyncStorage)
    assert storage.name == 'Storage 1'


def test_get_sync_storage_with_none_argument(patch_storage):
    storage = utils.get_sync_storage(None)
    assert isinstance(storage, MockSyncStorage)
    assert storage.name == 'Storage 1'


def test_get_sync_storage_with_nonexistent_key(patch_storage):
    with pytest.raises(StorageNotFound):
        utils.get_sync_storage('nonexistent_storage')


def test_get_sync_storage_with_invalid_type_argument(patch_storage):
    with pytest.raises(StorageNotFound):
        utils.get_sync_storage(123)


def test_get_sync_storage_with_valid_type_argument(patch_storage):
    storage = utils.get_sync_storage('storage2')
    assert isinstance(storage, MockSyncStorage)
    assert storage.name == 'Storage 2'
