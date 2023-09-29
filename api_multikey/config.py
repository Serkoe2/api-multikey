from api_multikey.storage.memory_storage import MemoryStorage

storages = {
    'memory': MemoryStorage({}, base_limit=60, soft_error=True)
}