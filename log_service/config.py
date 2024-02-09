import os
from threading import Lock

DB_DIRECTORY_PATH = "databases"  # todo should be an env var
DB_NAME = "SQLite-main.db"  # todo should be an env var


class LogServiceConfig:
    """
    A singleton class designed to manage the logging service configuration, specifically
    for providing needed configuration information such as the database URL.

    This class uses the Singleton design pattern to ensure that only one configuration instance
    is created and used across the application. It guarantees that the instance is thread-safe
    by utilizing a lock during the instance creation process.

    Attributes:
        _instance (LogServiceConfig, optional): A class-level attribute that holds the single instance
            of LogServiceConfig. Direct access to this attribute is not recommended.
        _lock (Lock): A threading lock used to synchronize the thread-safe creation of the singleton instance.

    Methods:
        __init__(): The constructor is private to prevent external instantiation. Use `LogServiceConfig.get_instance()`.
        get_instance(): A class method to retrieve or create the singleton instance of LogServiceConfig.
        get_db_url(): A static method that computes and returns the database URL using the current working directory
            and predefined database directory and name.

    Usage:
        Obtain the configuration instance and the database URL as follows:

            config = LogServiceConfig.get_instance()
            db_url = config.get_db_url()

    Raises:
        Exception: If there's an attempt to instantiate the class directly, instead of using the `get_instance` method.
    """

    _instance = None
    _lock: Lock = Lock()

    def __init__(self) -> None:
        """Private constructor to enforce the singleton pattern."""
        if LogServiceConfig._instance:
            raise Exception("This class is a singleton, use the get_instance method!")
        LogServiceConfig._instance = self

    @classmethod
    def get_instance(cls) -> "LogServiceConfig":
        """
        Retrieves the singleton instance of the LogServiceConfig class. If the instance does not exist,
        it creates one in a thread-safe manner using a lock.

        Returns:
            LogServiceConfig: The singleton instance of the class.
        """
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = LogServiceConfig()
        return cls._instance

    @staticmethod
    def get_db_url() -> str:
        """
        Computes and returns the full path to the database file based on the current
        working directory, database directory path, and database name.

        Returns:
            str: The path to the database file.
        """
        return os.path.join(os.getcwd(), DB_DIRECTORY_PATH, DB_NAME)
