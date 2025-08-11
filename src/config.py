"""Configuration management for Xray Test Automation."""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for managing environment variables and settings."""
    
    # Xray Cloud Configuration
    XRAY_CLIENT_ID: str = os.getenv('XRAY_CLIENT_ID', '')
    XRAY_CLIENT_SECRET: str = os.getenv('XRAY_CLIENT_SECRET', '')
    XRAY_AUTH_URL: str = "https://xray.cloud.getxray.app/api/v2/authenticate"
    XRAY_BULK_IMPORT_URL: str = "https://xray.cloud.getxray.app/api/v2/import/test/bulk"
    XRAY_BULK_STATUS_URL_TEMPLATE: str = "https://xray.cloud.getxray.app/api/v2/import/test/bulk/{jobId}/status"
    
    # Jira Configuration
    JIRA_EMAIL: str = os.getenv('JIRA_EMAIL', '')
    JIRA_API_TOKEN: str = os.getenv('JIRA_API_TOKEN', '')
    JIRA_BASE_URL: str = os.getenv('JIRA_BASE_URL', 'https://yourcompany.atlassian.net')
    
    @property
    def JIRA_ISSUE_LINK_URL(self) -> str:
        """Generate Jira issue link URL based on base URL."""
        return f"{self.JIRA_BASE_URL}/rest/api/3/issueLink"
    
    # Project Configuration
    PROJECT_KEY: str = os.getenv('PROJECT_KEY', '')
    LINK_TO_ISSUE_KEY: str = os.getenv('LINK_TO_ISSUE_KEY', '')
    
    # File Configuration
    TEST_DOCUMENT_PATH: str = os.getenv('TEST_DOCUMENT_PATH', './samples/sample_test_scenarios.docx')
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', './logs/xray_automation.log')
    
    # API Configuration
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '20'))
    RETRY_INTERVAL: int = int(os.getenv('RETRY_INTERVAL', '5'))
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration values are present."""
        required_fields = [
            'XRAY_CLIENT_ID',
            'XRAY_CLIENT_SECRET',
            'JIRA_EMAIL',
            'JIRA_API_TOKEN',
            'PROJECT_KEY',
            'LINK_TO_ISSUE_KEY'
        ]
        
        missing_fields = []
        for field in required_fields:
            value = getattr(cls, field)
            if not value or value.strip() == '':
                missing_fields.append(field)
        
        if missing_fields:
            logging.error(f"Missing required configuration fields: {', '.join(missing_fields)}")
            logging.error("Please check your .env file or environment variables.")
            return False
        
        return True
    
    @classmethod
    def create_log_directory(cls) -> None:
        """Create log directory if it doesn't exist."""
        log_path = Path(cls.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def setup_logging(cls) -> None:
        """Setup logging configuration."""
        cls.create_log_directory()
        
        # Configure logging
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper()),
            format=log_format,
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )