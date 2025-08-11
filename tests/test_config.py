"""Tests for configuration management."""

import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from src.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Clean up after tests."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_config_validation_success(self):
        """Test successful configuration validation."""
        # Set required environment variables
        required_vars = {
            'XRAY_CLIENT_ID': 'test_client_id',
            'XRAY_CLIENT_SECRET': 'test_client_secret',
            'JIRA_EMAIL': 'test@example.com',
            'JIRA_API_TOKEN': 'test_token',
            'PROJECT_KEY': 'TEST',
            'LINK_TO_ISSUE_KEY': 'TEST-123'
        }
        
        for key, value in required_vars.items():
            os.environ[key] = value
        
        # Reload config with new environment variables
        from importlib import reload
        from src import config
        reload(config)
        
        self.assertTrue(config.Config.validate())
    
    def test_config_validation_failure_missing_fields(self):
        """Test configuration validation with missing fields."""
        # Clear environment variables
        for var in ['XRAY_CLIENT_ID', 'XRAY_CLIENT_SECRET', 'JIRA_EMAIL', 
                   'JIRA_API_TOKEN', 'PROJECT_KEY', 'LINK_TO_ISSUE_KEY']:
            os.environ.pop(var, None)
        
        # Reload config
        from importlib import reload
        from src import config
        reload(config)
        
        self.assertFalse(config.Config.validate())
    
    def test_jira_issue_link_url_property(self):
        """Test JIRA issue link URL property generation."""
        os.environ['JIRA_BASE_URL'] = 'https://test.atlassian.net'
        
        # Reload config
        from importlib import reload
        from src import config
        reload(config)
        
        expected_url = 'https://test.atlassian.net/rest/api/3/issueLink'
        self.assertEqual(config.Config.JIRA_ISSUE_LINK_URL, expected_url)
    
    def test_create_log_directory(self):
        """Test log directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'nested', 'test.log')
            
            # Set log file path
            os.environ['LOG_FILE'] = log_file
            
            # Reload config and create directory
            from importlib import reload
            from src import config
            reload(config)
            config.Config.create_log_directory()
            
            # Verify directory was created
            log_dir = Path(log_file).parent
            self.assertTrue(log_dir.exists())
    
    def test_default_values(self):
        """Test default configuration values."""
        # Clear environment variables
        for var in os.environ.copy():
            if var.startswith(('XRAY_', 'JIRA_', 'PROJECT_', 'LINK_TO_', 'TEST_', 'LOG_')):
                os.environ.pop(var, None)
        
        # Reload config
        from importlib import reload
        from src import config
        reload(config)
        
        # Test default values
        self.assertEqual(config.Config.XRAY_AUTH_URL, 'https://xray.cloud.getxray.app/api/v2/authenticate')
        self.assertEqual(config.Config.LOG_LEVEL, 'INFO')
        self.assertEqual(config.Config.MAX_RETRIES, 20)
        self.assertEqual(config.Config.RETRY_INTERVAL, 5)
        self.assertEqual(config.Config.REQUEST_TIMEOUT, 30)


if __name__ == '__main__':
    unittest.main()