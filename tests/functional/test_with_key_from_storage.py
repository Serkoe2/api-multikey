import datetime
import pytest
from api_multikey.multikey import with_key_from_storage, APIKeyError
from api_multikey.storage.memory_storage import MemoryStorage

# Создаем мок функцию, которая будет вызываться из декорированной функции
count_error = 0


def mock_function(api_key, error=None):
    global count_error
    if error:
        if count_error == 1:
            return api_key
        count_error += 1
        raise error
    return api_key


@pytest.fixture
def mock_sync_storage():
    return MemoryStorage({}, base_limit=2, soft_error=True)


def test_with_key_from_storage(mock_sync_storage):
    # Создаем функцию с декоратором
    decorated_function = with_key_from_storage(mock_sync_storage)(mock_function)

    # Вызываем функцию с доступным ключом
    mock_sync_storage.add_key('key1')
    result = decorated_function()
    assert result == 'key1'
    # Ключ не должен быть заблокирован
    assert mock_sync_storage.storage['key1']['is_locked'] is False


@pytest.mark.timeout(2)
def test_error(mock_sync_storage):
    global count_error
    # Создаем функцию с декоратором
    decorated_function = with_key_from_storage(mock_sync_storage)(mock_function)
    mock_sync_storage.add_key('key1')
    result = decorated_function(error=APIKeyError())
    count_error = 0
    result = decorated_function()
    assert result == 'key1'


if __name__ == "__main__":
    pytest.main()
