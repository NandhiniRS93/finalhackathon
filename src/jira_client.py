"""Jira API client for issue linking."""

import logging
from typing import Dict, Any, Optional
import requests

from .config import Config

logger = logging.getLogger(__name__)


class JiraClient:
    """Client for interacting with Jira API."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize Jira client with configuration."""
        self.config = config or Config()
        self.auth = (self.config.JIRA_EMAIL, self.config.JIRA_API_TOKEN)
    
    def create_issue_link(self, test_key: str, link_type: str = "Tests") -> requests.Response:
        """Create a link between a test case and a Jira issue."""
        logger.debug(f"Creating {link_type} link between {test_key} and {self.config.LINK_TO_ISSUE_KEY}")
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "type": {"name": link_type},
            "inwardIssue": {"key": self.config.LINK_TO_ISSUE_KEY},
            "outwardIssue": {"key": test_key}
        }
        
        try:
            response = requests.post(
                self.config.JIRA_ISSUE_LINK_URL,
                auth=self.auth,
                headers=headers,
                json=payload,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 201:
                logger.info(f"Successfully linked {test_key} to {self.config.LINK_TO_ISSUE_KEY}")
            else:
                logger.warning(f"Failed to link {test_key}: {response.status_code} - {response.text}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed when linking {test_key}: {e}")
            raise
    
    def bulk_create_links(self, test_keys: list[str], link_type: str = "Tests") -> Dict[str, Any]:
        """Create links for multiple test cases."""
        logger.info(f"Creating {link_type} links for {len(test_keys)} test cases...")
        
        results = {
            "successful": [],
            "failed": [],
            "total": len(test_keys)
        }
        
        for idx, test_key in enumerate(test_keys, 1):
            try:
                response = self.create_issue_link(test_key, link_type)
                
                if response.status_code == 201:
                    results["successful"].append({
                        "test_key": test_key,
                        "status": "linked"
                    })
                    logger.info(f"[{idx}/{len(test_keys)}] Successfully linked {test_key}")
                else:
                    results["failed"].append({
                        "test_key": test_key,
                        "status_code": response.status_code,
                        "error": response.text
                    })
                    logger.warning(f"[{idx}/{len(test_keys)}] Failed to link {test_key}")
                    
            except Exception as e:
                results["failed"].append({
                    "test_key": test_key,
                    "error": str(e)
                })
                logger.error(f"[{idx}/{len(test_keys)}] Error linking {test_key}: {e}")
        
        logger.info(f"Link creation completed: {len(results['successful'])} successful, {len(results['failed'])} failed")
        return results
    
    def validate_issue_exists(self, issue_key: str) -> bool:
        """Validate that a Jira issue exists."""
        logger.debug(f"Validating existence of issue {issue_key}")
        
        url = f"{self.config.JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
        
        try:
            response = requests.get(
                url,
                auth=self.auth,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            exists = response.status_code == 200
            logger.debug(f"Issue {issue_key} exists: {exists}")
            return exists
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to validate issue {issue_key}: {e}")
            return False