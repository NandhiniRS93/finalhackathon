"""Main script for Xray test case automation."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .config import Config
from .document_parser import DocumentParser
from .xray_client import XrayClient
from .jira_client import JiraClient

logger = logging.getLogger(__name__)


class XrayTestAutomation:
    """Main class for orchestrating the test case automation process."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the automation with configuration."""
        self.config = config or Config()
        self.xray_client = XrayClient(self.config)
        self.jira_client = JiraClient(self.config)
    
    def run(self, document_path: Optional[str] = None, dry_run: bool = False) -> dict:
        """
        Run the complete automation process.
        
        Args:
            document_path: Path to the test document (optional, uses config if not provided)
            dry_run: If True, parse and validate only without creating test cases
        
        Returns:
            Dictionary with execution results
        """
        results = {
            "success": False,
            "test_cases_parsed": 0,
            "test_cases_created": 0,
            "links_created": 0,
            "errors": []
        }
        
        try:
            # Use provided path or fall back to config
            doc_path = document_path or self.config.TEST_DOCUMENT_PATH
            logger.info(f"Starting automation process with document: {doc_path}")
            
            # Step 1: Parse test scenarios from document
            logger.info("Step 1: Parsing test scenarios from document...")
            parser = DocumentParser(doc_path)
            test_cases = parser.parse_test_scenarios()
            results["test_cases_parsed"] = len(test_cases)
            
            # Step 2: Validate test cases
            logger.info("Step 2: Validating test cases...")
            validation_results = parser.validate_test_cases(test_cases)
            
            if validation_results["errors"]:
                logger.error("Validation errors found:")
                for error in validation_results["errors"]:
                    logger.error(f"  - {error}")
                results["errors"].extend(validation_results["errors"])
                return results
            
            if validation_results["warnings"]:
                logger.warning("Validation warnings:")
                for warning in validation_results["warnings"]:
                    logger.warning(f"  - {warning}")
            
            if dry_run:
                logger.info(f"Dry run completed. Would create {len(test_cases)} test cases.")
                results["success"] = True
                return results
            
            # Step 3: Authenticate with Xray
            logger.info("Step 3: Authenticating with Xray Cloud...")
            jwt_token = self.xray_client.get_jwt_token()
            
            # Step 4: Submit bulk import
            logger.info("Step 4: Creating test cases in Xray Cloud...")
            bulk_payload = self.xray_client.build_bulk_payload(test_cases)
            job_response = self.xray_client.submit_bulk_import(bulk_payload)
            job_id = job_response.get("jobId")
            
            # Step 5: Poll for completion
            logger.info("Step 5: Waiting for test case creation to complete...")
            status_data = self.xray_client.poll_bulk_status(job_id)
            created_tests = status_data.get("createdTests", [])
            results["test_cases_created"] = len(created_tests)
            
            if not created_tests:
                error_msg = "No test cases were created successfully"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                return results
            
            # Step 6: Create Jira links
            if self.config.LINK_TO_ISSUE_KEY:
                logger.info("Step 6: Creating links to Jira issue...")
                
                # Validate target issue exists
                if not self.jira_client.validate_issue_exists(self.config.LINK_TO_ISSUE_KEY):
                    warning_msg = f"Target issue {self.config.LINK_TO_ISSUE_KEY} may not exist"
                    logger.warning(warning_msg)
                
                # Extract test keys
                test_keys = [test.get("testKey") for test in created_tests if test.get("testKey")]
                
                if test_keys:
                    link_results = self.jira_client.bulk_create_links(test_keys)
                    results["links_created"] = len(link_results["successful"])
                    
                    if link_results["failed"]:
                        logger.warning(f"{len(link_results['failed'])} links failed to create")
                        for failed in link_results["failed"]:
                            logger.warning(f"  - {failed['test_key']}: {failed.get('error', 'Unknown error')}")
                else:
                    logger.warning("No test keys found for linking")
            else:
                logger.info("Step 6: Skipping Jira linking (no LINK_TO_ISSUE_KEY configured)")
            
            results["success"] = True
            logger.info("Automation completed successfully!")
            
            # Summary
            logger.info(f"Summary:")
            logger.info(f"  - Test cases parsed: {results['test_cases_parsed']}")
            logger.info(f"  - Test cases created: {results['test_cases_created']}")
            logger.info(f"  - Links created: {results['links_created']}")
            
            return results
            
        except Exception as e:
            error_msg = f"Automation failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            return results


def setup_argument_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Automate test case import from Word documents to Xray Cloud",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                          # Use default configuration
  %(prog)s -f ./my_test_cases.docx                  # Specify document path
  %(prog)s --dry-run                                # Validate only, don't create
  %(prog)s -f ./tests.docx --project-key MYPROJ    # Override project key
        """
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Path to the Word document containing test cases'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse and validate test cases without creating them'
    )
    
    parser.add_argument(
        '--project-key',
        type=str,
        help='Override the project key from configuration'
    )
    
    parser.add_argument(
        '--link-to-issue',
        type=str,
        help='Override the issue key to link test cases to'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Override the log file path'
    )
    
    return parser


def main():
    """Main entry point for the CLI."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Override config with command line arguments
    if args.verbose:
        Config.LOG_LEVEL = 'DEBUG'
    
    if args.log_file:
        Config.LOG_FILE = args.log_file
    
    if args.project_key:
        Config.PROJECT_KEY = args.project_key
    
    if args.link_to_issue:
        Config.LINK_TO_ISSUE_KEY = args.link_to_issue
    
    # Setup logging
    Config.setup_logging()
    
    logger.info("Starting Xray Test Automation")
    logger.info(f"Configuration loaded from environment and command line arguments")
    
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Please check your .env file.")
        sys.exit(1)
    
    # Initialize and run automation
    try:
        automation = XrayTestAutomation()
        results = automation.run(
            document_path=args.file,
            dry_run=args.dry_run
        )
        
        if results["success"]:
            logger.info("Automation completed successfully!")
            sys.exit(0)
        else:
            logger.error("Automation failed!")
            for error in results["errors"]:
                logger.error(f"Error: {error}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()