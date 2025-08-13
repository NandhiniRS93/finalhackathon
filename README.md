<<<<<<< HEAD
<<<<<<< HEAD
# Xray Test Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Automate test case import from Word documents to Xray Cloud with seamless Jira integration.

## 🚀 Features

- **📄 Document Parsing**: Extract test scenarios from structured Word documents
- **☁️ Xray Integration**: Bulk import test cases to Xray Cloud
- **🔗 Jira Linking**: Automatically link test cases to Jira issues
- **🔐 Security First**: Environment-based credential management
- **📊 Progress Tracking**: Real-time progress bars and detailed logging
- **✅ Validation**: Comprehensive test case validation before import
- **🖥️ CLI Interface**: Full command-line interface with flexible options

## 📋 Prerequisites

- Python 3.8 or higher
- Xray Cloud account with API access
- Jira Cloud account with API access
- Word documents (.docx) with test scenarios in table format

## 🛠️ Installation

### Option 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/xray-test-automation.git
cd xray-test-automation

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Option 2: Direct Installation

```bash
pip install xray-test-automation
```

## ⚙️ Configuration

### 1. Environment Variables

Copy the example environment file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Xray Cloud Configuration
XRAY_CLIENT_ID=your_xray_client_id_here
XRAY_CLIENT_SECRET=your_xray_client_secret_here

# Jira Configuration  
JIRA_EMAIL=your_jira_email@company.com
JIRA_API_TOKEN=your_jira_api_token_here
JIRA_BASE_URL=https://yourcompany.atlassian.net

# Project Configuration
PROJECT_KEY=YOUR_PROJECT_KEY
LINK_TO_ISSUE_KEY=ISSUE-123

# File Paths
TEST_DOCUMENT_PATH=./samples/sample_test_scenarios.docx
```

### 2. Getting API Credentials

#### Xray Cloud API Credentials
1. Log in to [Xray Cloud](https://xray.cloud.getxray.app/)
2. Go to Global Settings → API Keys
3. Generate new API Key
4. Copy the Client ID and Client Secret

#### Jira API Token
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create API token
3. Copy the generated token

## 📖 Document Format

Your Word document should contain a table with these exact column headers:

| Scenario ID | Description | Preconditions | Expected Results |
|-------------|-------------|---------------|------------------|
| TC-001 | Login with valid credentials | User account exists | User successfully logged in |
| TC-002 | Create new asset record | User has create permissions | Asset created with unique ID |

### Example Document Structure

```
Asset Management - Test Scenarios

Functional Test Scenarios

[TABLE WITH TEST CASES]

Notes:
• All scenarios should be executed in test environment
• Document any deviations from expected results
```

## 🚀 Usage

### Basic Usage

```bash
# Run with default configuration
python cli.py

# Or using the module
python -m src.main
```

### Command Line Options

```bash
# Specify document path
python cli.py -f /path/to/your/test_scenarios.docx

# Dry run (validate without creating)
python cli.py --dry-run

# Override configuration
python cli.py --project-key MYPROJ --link-to-issue STORY-123

# Verbose logging
python cli.py -v

# Custom log file
python cli.py --log-file ./logs/my_run.log
```

### Advanced Examples

```bash
# Full custom run
python cli.py \
    -f ./my_tests.docx \
    --project-key DEMO \
    --link-to-issue EPIC-456 \
    --verbose \
    --log-file ./logs/demo_import.log

# Validation only
python cli.py -f ./tests.docx --dry-run -v
```

## 📁 Project Structure

```
xray-test-automation/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── config.py            # Configuration management
│   ├── document_parser.py   # Word document parsing
│   ├── xray_client.py       # Xray Cloud API client
│   └── jira_client.py       # Jira API client
├── samples/
│   ├── sample_test_scenarios.py    # Sample document generator
│   ├── sample_test_scenarios.docx  # Sample Word document
│   └── README.md
├── tests/
│   └── test_*.py            # Unit tests
├── docs/
│   ├── API.md               # API documentation
│   └── TROUBLESHOOTING.md   # Common issues and solutions
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI
├── cli.py                   # Command-line interface
├── setup.py                 # Package setup
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .gitignore
├── LICENSE
└── README.md
```

## 🔧 API Reference

### Main Classes

#### `XrayTestAutomation`
Main orchestrator class that coordinates the entire process.

```python
from src.main import XrayTestAutomation

automation = XrayTestAutomation()
results = automation.run(
    document_path="./my_tests.docx",
    dry_run=False
)
```

#### `DocumentParser`
Parses test scenarios from Word documents.

```python
from src.document_parser import DocumentParser

parser = DocumentParser("./test_scenarios.docx")
test_cases = parser.parse_test_scenarios()
validation = parser.validate_test_cases(test_cases)
```

#### `XrayClient`
Handles Xray Cloud API interactions.

```python
from src.xray_client import XrayClient

client = XrayClient()
token = client.get_jwt_token()
payload = client.build_bulk_payload(test_cases)
job_response = client.submit_bulk_import(payload)
```

#### `JiraClient`
Manages Jira API operations for linking.

```python
from src.jira_client import JiraClient

jira = JiraClient()
response = jira.create_issue_link("TEST-123")
results = jira.bulk_create_links(["TEST-123", "TEST-124"])
```

## 🧪 Testing

### Generate Sample Document

```bash
# Create sample Word document for testing
cd samples
python sample_test_scenarios.py
```

### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test
python -m pytest tests/test_document_parser.py -v
```

### Manual Testing

```bash
# Test with sample document
python cli.py -f ./samples/sample_test_scenarios.docx --dry-run -v
```

## 📊 Logging and Monitoring

The tool provides comprehensive logging:

- **Console Output**: Real-time progress and status
- **Log Files**: Detailed execution logs (default: `./logs/xray_automation.log`)
- **Progress Bars**: Visual progress indication for long operations

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General information about progress
- `WARNING`: Warning messages for non-critical issues
- `ERROR`: Error messages for failures

### Example Output

```
2025-01-11 10:30:15,123 - root - INFO - Starting Xray Test Automation
2025-01-11 10:30:15,125 - src.main - INFO - Step 1: Parsing test scenarios from document...
2025-01-11 10:30:16,234 - src.document_parser - INFO - Successfully parsed 8 test cases from document
2025-01-11 10:30:16,235 - src.main - INFO - Step 2: Validating test cases...
2025-01-11 10:30:16,245 - src.main - INFO - Step 3: Authenticating with Xray Cloud...
2025-01-11 10:30:17,123 - src.xray_client - INFO - Successfully authenticated with Xray Cloud
Status: COMPLETED: 100%|██████████| 12/12 [00:45<00:00,  3.75s/check]
2025-01-11 10:31:02,567 - src.main - INFO - Summary:
2025-01-11 10:31:02,567 - src.main - INFO -   - Test cases parsed: 8
2025-01-11 10:31:02,567 - src.main - INFO -   - Test cases created: 8
2025-01-11 10:31:02,567 - src.main - INFO -   - Links created: 8
```

## ❗ Troubleshooting

### Common Issues

#### Authentication Errors
```
Failed to authenticate with Xray Cloud: 401 Unauthorized
```
**Solution**: Check your `XRAY_CLIENT_ID` and `XRAY_CLIENT_SECRET` in `.env`

#### Document Format Issues
```
No table found with required headers
```
**Solution**: Ensure your Word document has a table with exact headers: `Scenario ID`, `Description`, `Preconditions`, `Expected Results`

#### Jira Linking Failures
```
Failed to link test case TEST-123: 404 Not Found
```
**Solution**: Verify the `LINK_TO_ISSUE_KEY` exists and your Jira permissions

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python cli.py -v --log-file ./debug.log
```

### Getting Help

1. Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Review log files for detailed error messages
3. Validate your document format with `--dry-run`
4. Test API credentials separately

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python -m pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/xray-test-automation.git
cd xray-test-automation

# Install development dependencies
pip install -e .[dev]

# Run pre-commit hooks
pre-commit install

# Run tests
python -m pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Xray Cloud](https://xray.cloud.getxray.app/) for test management
- [Atlassian Jira](https://www.atlassian.com/software/jira) for issue tracking
- [python-docx](https://python-docx.readthedocs.io/) for document parsing
- The open source community for continuous inspiration

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/yourusername/xray-test-automation/issues)
- 💬 [Discussions](https://github.com/yourusername/xray-test-automation/discussions)

---

**Made with ❤️ for QA teams worldwide**
=======
# finalhackathon
>>>>>>> ec62fc1a749d163bef47677e39600dec43daaa74
=======

>>>>>>> 9116de506febf38efb16350acce51bd4189f14aa
