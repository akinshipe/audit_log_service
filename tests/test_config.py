import os
import pytest

from log_service.config import LogServiceConfig


@pytest.fixture
def reset_log_service_config_singleton():
    LogServiceConfig._instance = None
    yield
    LogServiceConfig._instance = None


def test_log_service_config_singleton(reset_log_service_config_singleton):
    """Test that LogServiceConfig is a singleton."""
    instance1 = LogServiceConfig.get_instance()
    instance2 = LogServiceConfig.get_instance()
    assert instance1 is instance2


def test_log_service_config_no_direct_instantiation(reset_log_service_config_singleton):
    """Ensure LogServiceConfig cannot be directly instantiated."""

    # create and instance
    LogServiceConfig.get_instance()

    # assert an new istance raises an exception
    with pytest.raises(Exception) as exc_info:
        LogServiceConfig()
    assert "This class is a singleton, use the get_instance method!" in str(
        exc_info.value
    )


def test_get_db_url_is_correct(mocker, reset_log_service_config_singleton):
    """Test get_db_url returns the correct path"""
    mocker.patch.dict(os.environ, {"TEST_MODE": "False"})
    expected_path = os.path.join(os.getcwd(), "databases", "SQLite-main.db")
    assert LogServiceConfig.get_instance().get_db_url() == expected_path
