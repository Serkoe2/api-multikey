import datetime
import pytest

from api_multikey.storage.exception import KeyExistError, KeyNotFoundError
from api_multikey.storage.memory_storage import MemoryStorage


# Создаем фикстуру, которая будет использоваться в тестах для инициализации объекта MemoryStorage
@pytest.fixture
def memory_storage():
    return MemoryStorage({}, base_limit=60, soft_error=False)


def test_add_key(memory_storage):
    key = 'test_key'
    timestamp = datetime.datetime(2023, 9, 30, 12, 0, 0)

    # Добавляем ключ
    memory_storage.add_key(key, timestamp=timestamp)

    # Убеждаемся, что ключ добавлен в хранилище
    assert key in memory_storage.storage

    # Попытка добавить тот же ключ снова должна вызвать исключение KeyExistError
    with pytest.raises(KeyExistError):
        memory_storage.add_key(key, timestamp=timestamp)

    # Проверка, что timestamp добавляется автоматически
    memory_storage.add_key('test_key_2')
    assert isinstance(memory_storage.storage['test_key']['timestamp'], datetime.datetime)


def test_get_first_key(memory_storage):
    key1 = 'key1'
    key2 = 'key2'
    key3 = 'key3'

    # Добавляем ключи с разными временными метками
    timestamp1 = datetime.datetime(2023, 9, 30, 12, 0, 0)
    timestamp2 = datetime.datetime(2023, 9, 30, 12, 15, 0)
    timestamp3 = datetime.datetime(2023, 9, 30, 12, 30, 0)

    memory_storage.add_key(key1, timestamp=timestamp1)
    memory_storage.add_key(key2, timestamp=timestamp2)
    memory_storage.add_key(key3, timestamp=timestamp3)

    # Попытка получить первый доступный ключ с текущим временем должна вернуть key1
    current_time = datetime.datetime(2023, 9, 30, 12, 10, 0)
    result_key = memory_storage.get_first_key(timestamp=current_time)
    assert result_key == key1

    # Блокируем key1
    memory_storage.storage[key1]['is_locked'] = True

    # Попытка получить первый доступный ключ с текущим временем должна вернуть key2
    current_time = datetime.datetime(2023, 9, 30, 12, 20, 0)
    result_key = memory_storage.get_first_key(timestamp=current_time)
    assert result_key == key2

    # Блокируем key2
    memory_storage.storage[key2]['is_locked'] = True

    # Попытка получить первый доступный ключ с текущим временем должна вернуть key3
    current_time = datetime.datetime(2023, 9, 30, 12, 40, 0)
    result_key = memory_storage.get_first_key(timestamp=current_time)
    assert result_key == key3

    # Попытка получить первый доступный ключ с текущим временем, когда нет доступных ключей, должна вызвать исключение KeyNotFoundError
    with pytest.raises(KeyNotFoundError):
        current_time = datetime.datetime(2023, 9, 30, 12, 50, 0)
        result_key = memory_storage.get_first_key(timestamp=current_time)



def test_get_first_busy_key(memory_storage):
    key1 = 'key1'
    key2 = 'key2'
    key3 = 'key3'

    # Добавляем ключи с разными временными метками и блокируем их
    timestamp1 = datetime.datetime(2023, 9, 30, 12, 0, 0)
    timestamp2 = datetime.datetime(2023, 9, 30, 12, 15, 0)
    timestamp3 = datetime.datetime(2023, 9, 30, 12, 30, 0)

    memory_storage.add_key(key1, timestamp=timestamp1)
    memory_storage.add_key(key2, timestamp=timestamp2)
    memory_storage.add_key(key3, timestamp=timestamp3)

    memory_storage.storage[key1]['is_locked'] = True
    memory_storage.storage[key2]['is_locked'] = True
    memory_storage.storage[key3]['is_locked'] = True

    # Попытка получить первый доступный (незаблокированный) ключ с текущим временем должна вернуть None
    current_time = datetime.datetime(2023, 9, 30, 12, 10, 0)
    result_key = memory_storage.get_first_busy_key(timestamp=current_time, soft_error=True)
    assert result_key is None

    # Разблокируем key1
    memory_storage.storage[key1]['is_locked'] = False

    # Попытка получить первый доступный ключ с текущим временем должна вернуть key1
    current_time = datetime.datetime(2023, 9, 30, 12, 0, 0)
    result_key = memory_storage.get_first_busy_key(timestamp=current_time)
    assert result_key[0] == key1
    assert result_key[1] == timestamp1

    # Блокируем key1
    memory_storage.storage[key1]['is_locked'] = True

    # Разблокируем key2
    memory_storage.storage[key2]['is_locked'] = False

    # Попытка получить первый доступный ключ с текущим временем должна вернуть key2
    current_time = datetime.datetime(2023, 9, 30, 12, 0, 0)
    result_key = memory_storage.get_first_busy_key(timestamp=current_time)
    assert result_key[0] == key2
    assert result_key[1] == timestamp2

    # Блокируем key2
    memory_storage.storage[key2]['is_locked'] = True

    # Разблокируем key3
    memory_storage.storage[key3]['is_locked'] = False

    # Попытка получить первый доступный ключ с текущим временем должна вернуть key3
    current_time = datetime.datetime(2023, 9, 30, 12, 0, 0)
    result_key = memory_storage.get_first_busy_key(timestamp=current_time)
    assert result_key[0] == key3
    assert result_key[1] == timestamp3

    # Блокируем key3
    memory_storage.storage[key3]['is_locked'] = True

    # Попытка получить первый доступный ключ с текущим временем, когда нет доступных ключей, должна вызвать исключение KeyNotFoundError
    current_time = datetime.datetime(2023, 9, 30, 12, 50, 0)
    result_key = memory_storage.get_first_busy_key(timestamp=current_time, soft_error=True)
    assert result_key is None



def test_return_key(memory_storage):
    key = 'test_key'
    timestamp = datetime.datetime(2023, 9, 30, 12, 0, 0)

    # Добавляем ключ
    memory_storage.add_key(key, timestamp=timestamp)

    # Возвращаем ключ с обновленным временем
    new_timestamp = datetime.datetime(2023, 9, 30, 12, 30, 0)

    memory_storage.return_key(key, timestamp=new_timestamp)
    assert memory_storage.storage[key]['timestamp'] == new_timestamp

    memory_storage.return_key(key, timestamp=new_timestamp, need_cold=True)

    # Убеждаемся, что ключ обновлен
    assert memory_storage.storage[key]['timestamp'] == new_timestamp + datetime.timedelta(minutes=1)

    # # Попытка вернуть несуществующий ключ должна вызвать исключение KeyNotFoundError
    with pytest.raises(KeyNotFoundError):
        memory_storage.return_key('nonexistent_key', timestamp=new_timestamp)
