from abc import ABC, abstractmethod


class SyncStorage(ABC):
    @abstractmethod
    def get_first_key(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_first_busy_key(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def add_key(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def return_key(self, *args, **kwargs):
        raise NotImplementedError
