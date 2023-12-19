import abc


class HandlerInterface(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def read(file_path):
        pass
