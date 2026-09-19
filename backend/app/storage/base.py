from abc import ABC, abstractmethod
from typing import IO

class StorageService(ABC):
    @abstractmethod
    def save(self, file_obj: IO, object_key: str, content_type: str) -> str:
        """Saves a file to storage and returns the storage_key."""
        pass

    @abstractmethod
    def delete(self, object_key: str) -> bool:
        """Deletes a file from storage."""
        pass

    @abstractmethod
    def exists(self, object_key: str) -> bool:
        """Checks if a file exists in storage."""
        pass

    @abstractmethod
    def get(self, object_key: str) -> IO:
        """Retrieves a file from storage."""
        pass
