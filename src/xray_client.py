"""Xray Cloud API client for test case management."""

import json
import logging
import time
from typing import Dict, List, Any, Optional
import requests
from tqdm import tqdm

from .config import Config

logger = logging.getLogger(__name__)


class XrayClient:
    """Client for interacting with Xray Cloud API."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize Xray client with configuration."""
        self.config = config or Config()
        self._jwt_token: Optional[str] = None
    
    def get_jwt_token(self) -> str:
        """Authenticate with Xray Cloud and get JWT token."""
        logger.info("Authenticating with Xray Cloud...")
        
        payload = {
            "client_id": self.config.XRAY_CLIENT_ID,
            "client_secret": self.config.XRAY_CLIENT_SECRET
        }
        
        try:
            response = requests.post(
                self.config.XRAY_AUTH_URL,
                json=payload,
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._jwt_token = token_data
            logger.info("Successfully authenticated with Xray Cloud")
            return self._jwt_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to authenticate with Xray Cloud: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Xray authentication: {e}")
            raise
    
    def build_bulk_payload(self, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """Build bulk import payload from test cases."""
        logger.info(f"Building bulk payload for {len(test_cases)} test cases...")
        
        tests = []
        for tc in test_cases:
            test = {
                "fields": {
                    "project": {"key": self.config.PROJECT_KEY},
                    "summary": tc["summary"],
                    "description": f"Test Scenario ID: {tc['id']}",
                    "labels": ["Functional", "Automated"],
                    "issuetype": {"name": "Test"}
                },
                "steps": [
                    {
                        "action": f"Execute test scenario: {tc['summary']}",
                        "data": f"Preconditions: {tc['preconditions']}",
                        "result": tc['expected_results']
                    }
                ]
            }
            tests.append(test)
        
        logger.info(f"Successfully built bulk payload with {len(tests)} test cases")
        return {"tests": tests}
    
    def submit_bulk_import(self, bulk_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit bulk import job to Xray Cloud."""
        if not self._jwt_token:
            self.get_jwt_token()
        
        logger.info("Submitting bulk import job...")
        
        headers = {
            "Authorization": f"Bearer {self._jwt_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.config.XRAY_BULK_IMPORT_URL,
                headers=headers,
                json=bulk_payload,
                timeout=self.config.REQUEST_TIMEOUT * 2  # Bulk imports may take longer
            )
            response.raise_for_status()
            
            job_data = response.json()
            job_id = job_data.get("jobId")
            logger.info(f"Bulk import job submitted successfully with jobId: {job_id}")
            return job_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to submit bulk import: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from bulk import: {e}")
            raise
    
    def poll_bulk_status(self, job_id: str) -> Dict[str, Any]:
        """Poll bulk import job status until completion."""
        if not self._jwt_token:
            self.get_jwt_token()
        
        logger.info(f"Polling status for bulk import job {job_id}...")
        
        headers = {
            "Authorization": f"Bearer {self._jwt_token}"
        }
        
        url = self.config.XRAY_BULK_STATUS_URL_TEMPLATE.format(jobId=job_id)
        
        # Create progress bar
        pbar = tqdm(desc="Waiting for import completion", unit="check")
        
        try:
            for attempt in range(self.config.MAX_RETRIES):
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                status_data = response.json()
                status = status_data.get("status", "UNKNOWN")
                
                pbar.set_description(f"Status: {status}")
                pbar.update(1)
                
                if status == "COMPLETED":
                    pbar.close()
                    logger.info(f"Bulk import job {job_id} completed successfully")
                    return status_data
                elif status == "FAILED":
                    pbar.close()
                    error_msg = f"Bulk import job {job_id} failed: {status_data}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                else:
                    logger.debug(f"Job {job_id} status: {status}, waiting...")
                    time.sleep(self.config.RETRY_INTERVAL)
            
            pbar.close()
            raise TimeoutError(f"Bulk import job {job_id} did not complete within {self.config.MAX_RETRIES} attempts")
            
        except requests.exceptions.RequestException as e:
            pbar.close()
            logger.error(f"Failed to poll bulk import status: {e}")
            raise
        except json.JSONDecodeError as e:
            pbar.close()
            logger.error(f"Invalid JSON response from status check: {e}")
            raise