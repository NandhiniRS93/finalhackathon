# API Documentation

This document provides detailed information about the API components of the Xray Test Automation tool.

## 📋 Table of Contents

- [Configuration Management](#configuration-management)
- [Document Parser](#document-parser)
- [Xray Client](#xray-client)
- [Jira Client](#jira-client)
- [Main Automation](#main-automation)
- [Data Structures](#data-structures)
- [Error Handling](#error-handling)

## 🔧 Configuration Management

### `Config` Class

The `Config` class manages all configuration settings and environment variables.

#### Properties

```python
from src.config import Config

# Xray Configuration
Config.XRAY_CLIENT_ID          # Xray client ID
Config.XRAY_CLIENT_SECRET      # Xray client secret
Config.XRAY_AUTH_URL           # Authentication endpoint
Config.XRAY_BULK_IMPORT_URL    # Bulk import endpoint
Config.XRAY_BULK_STATUS_URL_TEMPLATE  # Status check template

# Jira Configuration
Config.JIRA_EMAIL              # Jira user email
Config.JIRA_API_TOKEN          # Jira API token
Config.JIRA_BASE_URL           # Jira base URL
Config.JIRA_ISSUE_LINK_URL     # Issue link endpoint (computed)

# Project Configuration
Config.PROJECT_KEY             # Target project key
Config.LINK_TO_ISSUE_KEY       # Issue to link test cases to

# File Configuration
Config.TEST_DOCUMENT_PATH      # Default document path
Config.LOG_LEVEL               # Logging level
Config.LOG_FILE                # Log file path

# API Configuration
Config.MAX_RETRIES             # Maximum retry attempts
Config.RETRY_INTERVAL          # Retry interval in seconds
Config.REQUEST_TIMEOUT         # Request timeout in seconds
```

#### Methods

##### `Config.validate() -> bool`
Validates that all required configuration values are present.

```python
if Config.validate():
    print("Configuration is valid")
else:
    print("Missing required configuration")
```

##### `Config.setup_logging() -> None`
Sets up logging configuration with file and console handlers.

```python
Config.setup_logging()
```

## 📄 Document Parser

### `DocumentParser` Class

Parses test scenarios from Word documents.

#### Constructor

```python
from src.document_parser import DocumentParser

parser = DocumentParser(document_path: str)
```

**Parameters:**
- `document_path` (str): Path to the Word document

**Raises:**
- `FileNotFoundError`: If document doesn't exist
- `ValueError`: If file format is unsupported

#### Methods

##### `parse_test_scenarios(required_headers: Optional[List[str]] = None) -> List[Dict[str, str]]`

Parses test scenarios from the document.

```python
# Use default headers
test_cases = parser.parse_test_scenarios()

# Use custom headers
custom_headers = ['ID', 'Title', 'Steps', 'Expected']
test_cases = parser.parse_test_scenarios(custom_headers)
```

**Parameters:**
- `required_headers` (Optional[List[str]]): Column headers to look for

**Returns:**
- `List[Dict[str, str]]`: List of test case dictionaries

**Default Headers:**
- `Scenario ID`
- `Description` 
- `Preconditions`
- `Expected Results`

**Test Case Dictionary Structure:**
```python
{
    "id": "TC-001",
    "summary": "Login with valid credentials",
    "preconditions": "User account exists in system",
    "expected_results": "User is logged in successfully"
}
```

##### `validate_test_cases(test_cases: List[Dict[str, str]]) -> Dict[str, Any]`

Validates parsed test cases for completeness and consistency.

```python
validation_results = parser.validate_test_cases(test_cases)
```

**Returns:**
```python
{
    "valid_count": 5,
    "invalid_count": 1,
    "warnings": ["Test case TC-003: No preconditions specified"],
    "errors": ["Test case 2: Empty id"]
}
```

## ☁️ Xray Client

### `XrayClient` Class

Handles interactions with Xray Cloud API.

#### Constructor

```python
from src.xray_client import XrayClient

client = XrayClient(config: Optional[Config] = None)
```

#### Methods

##### `get_jwt_token() -> str`

Authenticates with Xray Cloud and returns JWT token.

```python
token = client.get_jwt_token()
```

**Returns:**
- `str`: JWT authentication token

**Raises:**
- `requests.exceptions.RequestException`: On authentication failure

##### `build_bulk_payload(test_cases: List[Dict[str, str]]) -> Dict[str, Any]`

Builds the bulk import payload from test cases.

```python
payload = client.build_bulk_payload(test_cases)
```

**Parameters:**
- `test_cases` (List[Dict[str, str]]): Test cases from document parser

**Returns:**
```python
{
    "tests": [
        {
            "fields": {
                "project": {"key": "PROJ"},
                "summary": "Test Summary",
                "description": "Test Scenario ID: TC-001",
                "labels": ["Functional", "Automated"],
                "issuetype": {"name": "Test"}
            },
            "steps": [
                {
                    "action": "Execute test scenario: Test Summary",
                    "data": "Preconditions: ...",
                    "result": "Expected results: ..."
                }
            ]
        }
    ]
}
```

##### `submit_bulk_import(bulk_payload: Dict[str, Any]) -> Dict[str, Any]`

Submits bulk import job to Xray Cloud.

```python
job_response = client.submit_bulk_import(payload)
```

**Returns:**
```python
{
    "jobId": "abc123-def456-ghi789",
    "status": "SUBMITTED"
}
```

##### `poll_bulk_status(job_id: str) -> Dict[str, Any]`

Polls bulk import job status until completion.

```python
result = client.poll_bulk_status("abc123-def456-ghi789")
```

**Returns:**
```python
{
    "status": "COMPLETED",
    "createdTests": [
        {
            "testKey": "TEST-123",
            "testId": "12345"
        }
    ]
}
```

## 🔗 Jira Client

### `JiraClient` Class

Handles Jira API operations for issue linking.

#### Constructor

```python
from src.jira_client import JiraClient

jira = JiraClient(config: Optional[Config] = None)
```

#### Methods

##### `create_issue_link(test_key: str, link_type: str = "Tests") -> requests.Response`

Creates a link between a test case and a Jira issue.

```python
response = jira.create_issue_link("TEST-123", "Tests")
```

**Parameters:**
- `test_key` (str): Test case key from Xray
- `link_type` (str): Link relationship type

**Returns:**
- `requests.Response`: HTTP response object

##### `bulk_create_links(test_keys: List[str], link_type: str = "Tests") -> Dict[str, Any]`

Creates links for multiple test cases.

```python
results = jira.bulk_create_links(["TEST-123", "TEST-124"])
```

**Returns:**
```python
{
    "successful": [
        {"test_key": "TEST-123", "status": "linked"}
    ],
    "failed": [
        {"test_key": "TEST-124", "error": "404 Not Found"}
    ],
    "total": 2
}
```

##### `validate_issue_exists(issue_key: str) -> bool`

Validates that a Jira issue exists.

```python
exists = jira.validate_issue_exists("STORY-123")
```

## 🎯 Main Automation

### `XrayTestAutomation` Class

Main orchestrator class for the automation process.

#### Constructor

```python
from src.main import XrayTestAutomation

automation = XrayTestAutomation(config: Optional[Config] = None)
```

#### Methods

##### `run(document_path: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]`

Executes the complete automation workflow.

```python
# Full execution
results = automation.run("./my_tests.docx")

# Dry run (validation only)
results = automation.run("./my_tests.docx", dry_run=True)
```

**Parameters:**
- `document_path` (Optional[str]): Path to test document
- `dry_run` (bool): If True, validates without creating test cases

**Returns:**
```python
{
    "success": True,
    "test_cases_parsed": 8,
    "test_cases_created": 8,
    "links_created": 8,
    "errors": []
}
```

**Process Steps:**
1. Parse test scenarios from document
2. Validate test cases
3. Authenticate with Xray Cloud
4. Submit bulk import job
5. Poll for completion
6. Create Jira issue links

## 📊 Data Structures

### Test Case Dictionary
```python
test_case = {
    "id": "TC-001",                    # Unique test identifier
    "summary": "Test description",     # Brief test description
    "preconditions": "Prerequisites",  # Test preconditions
    "expected_results": "Expected outcome"  # Expected results
}
```

### Validation Results
```python
validation = {
    "valid_count": 5,                  # Number of valid test cases
    "invalid_count": 1,                # Number of invalid test cases
    "warnings": [                      # List of warning messages
        "Test case TC-003: No preconditions specified"
    ],
    "errors": [                        # List of error messages
        "Test case 2: Empty id"
    ]
}
```

### Execution Results
```python
results = {
    "success": True,                   # Overall success status
    "test_cases_parsed": 8,           # Number of test cases parsed
    "test_cases_created": 8,          # Number of test cases created
    "links_created": 8,               # Number of links created
    "errors": []                      # List of error messages
}
```

### Link Creation Results
```python
link_results = {
    "successful": [                    # Successfully created links
        {"test_key": "TEST-123", "status": "linked"}
    ],
    "failed": [                        # Failed link attempts
        {
            "test_key": "TEST-124",
            "status_code": 404,
            "error": "Issue not found"
        }
    ],
    "total": 2                         # Total links attempted
}
```

## ❌ Error Handling

### Common Exceptions

#### `FileNotFoundError`
Raised when the specified document doesn't exist.

```python
try:
    parser = DocumentParser("./nonexistent.docx")
except FileNotFoundError as e:
    print(f"Document not found: {e}")
```

#### `ValueError`
Raised for invalid document format or configuration.

```python
try:
    test_cases = parser.parse_test_scenarios()
except ValueError as e:
    print(f"Invalid document format: {e}")
```

#### `requests.exceptions.RequestException`
Raised for HTTP/API related errors.

```python
try:
    token = client.get_jwt_token()
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
```

#### `TimeoutError`
Raised when operations exceed timeout limits.

```python
try:
    result = client.poll_bulk_status(job_id)
except TimeoutError as e:
    print(f"Operation timed out: {e}")
```

### Error Response Handling

API clients return error information in response objects:

```python
response = jira.create_issue_link("TEST-123")
if response.status_code != 201:
    print(f"Link creation failed: {response.status_code}")
    print(f"Error details: {response.text}")
```

### Logging Integration

All API classes use Python's logging module:

```python
import logging

# Enable debug logging for detailed API information
logging.getLogger('src.xray_client').setLevel(logging.DEBUG)
logging.getLogger('src.jira_client').setLevel(logging.DEBUG)
```

## 🔍 Usage Examples

### Basic Document Processing
```python
from src.document_parser import DocumentParser

# Parse document
parser = DocumentParser("./test_scenarios.docx")
test_cases = parser.parse_test_scenarios()

# Validate test cases
validation = parser.validate_test_cases(test_cases)
if validation["errors"]:
    print("Validation failed:", validation["errors"])
```

### Xray Integration
```python
from src.xray_client import XrayClient
from src.config import Config

# Configure and authenticate
Config.setup_logging()
client = XrayClient()

# Process test cases
token = client.get_jwt_token()
payload = client.build_bulk_payload(test_cases)
job = client.submit_bulk_import(payload)
result = client.poll_bulk_status(job["jobId"])
```

### Complete Workflow
```python
from src.main import XrayTestAutomation

# Run full automation
automation = XrayTestAutomation()
results = automation.run("./my_tests.docx")

if results["success"]:
    print(f"Created {results['test_cases_created']} test cases")
    print(f"Created {results['links_created']} links")
else:
    print("Automation failed:", results["errors"])
```