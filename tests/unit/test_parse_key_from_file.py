import os
import pytest
from api_multikey.utils import parse_key_from_file


# Create Temporary files
@pytest.fixture
def create_temporary_files(tmpdir):
    file_paths = []
    for i in range(3):
        file_path = tmpdir.join(f'keys_{i}.txt')
        if i != 1:
            keys = [f'key_{i}_{j}' for j in range(1, 4)]
        else:
            keys = []
        with open(file_path, 'w') as file:
            file.write('\n'.join(keys))
        file_paths.append(file_path)
    yield file_paths
    for file_path in file_paths:
        os.remove(str(file_path))


def test_parse_key_from_file_existing_file(create_temporary_files):
    file_path = create_temporary_files[0]
    keys = parse_key_from_file(str(file_path))
    assert keys == ['key_0_1', 'key_0_2', 'key_0_3']


def test_parse_key_from_file_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        parse_key_from_file('nonexistent_file.txt')


def test_parse_key_from_file_empty_file(create_temporary_files):
    file_path = create_temporary_files[1]
    keys = parse_key_from_file(str(file_path))
    assert keys == []


def test_parse_key_from_file_blank_lines(create_temporary_files):
    file_path = create_temporary_files[2]
    keys = parse_key_from_file(str(file_path))
    assert keys == ['key_2_1', 'key_2_2', 'key_2_3']
