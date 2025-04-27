import os
import sys
import pytest
import logging
import asyncio
from unittest import mock
from main import check_env, check_dashboard_files, logo_tmpl

# Test configuration
TEST_DATA_DIR = "test_data"

class _version_info():
    def __init__(self, major, minor):
        self.major = major
        self.minor = minor
        
@pytest.fixture
def setup_test_env():
    """Fixture to set up test environment directories"""
    os.makedirs(f"{TEST_DATA_DIR}/config", exist_ok=True)
    os.makedirs(f"{TEST_DATA_DIR}/plugins", exist_ok=True)
    os.makedirs(f"{TEST_DATA_DIR}/temp", exist_ok=True)
    yield
    # Cleanup after tests
    for dir_path in [f"{TEST_DATA_DIR}/config", f"{TEST_DATA_DIR}/plugins", f"{TEST_DATA_DIR}/temp"]:
        if os.path.exists(dir_path):
            for file in os.listdir(dir_path):
                os.remove(os.path.join(dir_path, file))
            os.rmdir(dir_path)
    if os.path.exists(TEST_DATA_DIR):
        os.rmdir(TEST_DATA_DIR)

def test_logo_exists():
    """Test that the ASCII logo is properly defined"""
    assert logo_tmpl is not None
    assert isinstance(logo_tmpl, str)
    assert len(logo_tmpl) > 0
    assert "APTIX" in logo_tmpl or "__" in logo_tmpl

@pytest.mark.parametrize("version_info,should_exit", [
    (_version_info(3, 10), False),    # Minimum acceptable version
    (_version_info(3, 11), False),    # Above minimum version
    (_version_info(3, 9), True),      # Too old minor version
    (_version_info(2, 7), True),      # Too old major version
])
def test_check_env_python_version(monkeypatch, version_info, should_exit):
    """
    Test check_env function's Python version validation
    
    Parameters:
        monkeypatch: pytest fixture for modifying objects
        version_info: Python version info object
        should_exit: Whether the function should exit
    """
    monkeypatch.setattr(sys, 'version_info', version_info)
    
    if should_exit:
        with pytest.raises(SystemExit):
            check_env()
    else:
        with mock.patch('os.makedirs') as mock_makedirs:
            check_env()
            mock_makedirs.assert_any_call("data/config", exist_ok=True)
            mock_makedirs.assert_any_call("data/plugins", exist_ok=True)
            mock_makedirs.assert_any_call("data/temp", exist_ok=True)

def test_check_env_creates_directories(monkeypatch, setup_test_env):
    """Test that check_env creates the required directories"""
    version_info_correct = _version_info(3, 10)
    monkeypatch.setattr(sys, 'version_info', version_info_correct)
    
    with mock.patch('os.makedirs') as mock_makedirs:
        check_env()
        assert mock_makedirs.call_count == 3
        mock_makedirs.assert_any_call("data/config", exist_ok=True)
        mock_makedirs.assert_any_call("data/plugins", exist_ok=True)
        mock_makedirs.assert_any_call("data/temp", exist_ok=True)

def test_check_env_mime_types(monkeypatch):
    """Test that check_env registers the correct MIME types"""
    version_info_correct = _version_info(3, 10)
    monkeypatch.setattr(sys, 'version_info', version_info_correct)
    
    with mock.patch('os.makedirs'):
        with mock.patch('mimetypes.add_type') as mock_add_type:
            check_env()
            mock_add_type.assert_any_call("text/javascript", ".js")
            mock_add_type.assert_any_call("text/javascript", ".mjs")
            mock_add_type.assert_any_call("application/json", ".json")

@pytest.mark.asyncio
async def test_check_dashboard_files_up_to_date(monkeypatch, caplog):
    """Test check_dashboard_files when dashboard is already up to date"""
    caplog.set_level(logging.INFO)
    
    async def mock_get_version():
        return f"v1.0.0"  # Same as VERSION in main.py for this test
        
    monkeypatch.setattr('Aptixbot.core.config.default.VERSION', "1.0.0")
    monkeypatch.setattr('Aptixbot.core.utils.io.get_dashboard_version', mock_get_version)
    
    await check_dashboard_files()
    assert "Dashboard files are up to date" in caplog.text

@pytest.mark.asyncio
async def test_check_dashboard_files_needs_update(monkeypatch, caplog):
    """Test check_dashboard_files when dashboard needs an update"""
    caplog.set_level(logging.INFO)
    
    async def mock_get_version():
        return f"v0.9.0"  # Older than VERSION in main.py
        
    monkeypatch.setattr('Aptixbot.core.config.default.VERSION', "1.0.0")
    monkeypatch.setattr('Aptixbot.core.utils.io.get_dashboard_version', mock_get_version)
    
    await check_dashboard_files()
    assert "Dashboard update detected" in caplog.text

@pytest.mark.asyncio
async def test_check_dashboard_files_download_success(monkeypatch, caplog):
    """Test successful dashboard download"""
    caplog.set_level(logging.INFO)
    
    async def mock_get_version():
        return None  # No version found, needs download
        
    async def mock_download():
        return True  # Download successful
    
    monkeypatch.setattr('Aptixbot.core.utils.io.get_dashboard_version', mock_get_version)
    monkeypatch.setattr('Aptixbot.core.utils.io.download_dashboard', mock_download)
    
    await check_dashboard_files()
    assert "Starting to download dashboard files" in caplog.text
    assert "Dashboard download completed successfully" in caplog.text

@pytest.mark.asyncio
async def test_check_dashboard_files_download_failure(monkeypatch, caplog):
    """Test dashboard download failure"""
    caplog.set_level(logging.CRITICAL)
    
    async def mock_get_version():
        return None  # No version found, needs download
        
    async def mock_download():
        raise Exception("Download failed")
    
    monkeypatch.setattr('Aptixbot.core.utils.io.get_dashboard_version', mock_get_version)
    monkeypatch.setattr('Aptixbot.core.utils.io.download_dashboard', mock_download)
    
    await check_dashboard_files()
    assert "Failed to download dashboard files" in caplog.text