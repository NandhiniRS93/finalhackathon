# Troubleshooting Guide

This document covers common issues and their solutions when using the Xray Test Automation tool.

## 🔧 Common Issues

### Authentication Issues

#### ❌ Xray Authentication Failed
```
ERROR - Failed to authenticate with Xray Cloud: 401 Unauthorized
```

**Causes:**
- Invalid Client ID or Client Secret
- Expired credentials
- Network connectivity issues

**Solutions:**
1. Verify credentials in `.env` file:
   ```bash
   # Check your .env file
   cat .env | grep XRAY
   ```

2. Test credentials manually:
   ```bash
   curl -X POST "https://xray.cloud.getxray.app/api/v2/authenticate" \
        -H "Content-Type: application/json" \
        -d '{"client_id":"YOUR_ID","client_secret":"YOUR_SECRET"}'
   ```

3. Regenerate API keys in Xray Cloud:
   - Go to Global Settings → API Keys
   - Delete old key and create new one

#### ❌ Jira Authentication Failed
```
ERROR - Request failed when linking TEST-123: 401 Unauthorized
```

**Solutions:**
1. Verify Jira credentials:
   ```bash
   # Test Jira API access
   curl -u "your_email@company.com:your_api_token" \
        "https://yourcompany.atlassian.net/rest/api/3/myself"
   ```

2. Check API token permissions in Jira

3. Ensure email matches Jira account exactly

### Document Format Issues

#### ❌ No Table Found
```
ERROR - No table found with required headers: ['Scenario ID', 'Description', 'Preconditions', 'Expected Results']
```

**Solutions:**
1. Check table headers are exactly as required (case-sensitive):
   - ✅ `Scenario ID` (correct)
   - ❌ `scenario id` (incorrect)
   - ❌ `Test ID` (incorrect)

2. Ensure table is properly formatted in Word:
   - Use Insert → Table feature
   - Don't use text formatted to look like a table

3. Verify document structure:
   ```bash
   # Use dry-run to validate without importing
   python cli.py -f your_document.docx --dry-run -v
   ```

#### ❌ Empty or Invalid Test Cases
```
WARNING - Row 3 missing required data (ID or Summary), skipping
```

**Solutions:**
1. Check for empty cells in required columns
2. Ensure all test cases have unique IDs
3. Verify no merged cells in the table

### API and Network Issues

#### ❌ Request Timeout
```
ERROR - Failed to submit bulk import: ReadTimeout: HTTPSConnectionPool
```

**Solutions:**
1. Check internet connection
2. Increase timeout in configuration:
   ```env
   REQUEST_TIMEOUT=60
   ```

3. Try smaller batches if document is very large

#### ❌ Rate Limiting
```
ERROR - Too Many Requests: 429
```

**Solutions:**
1. Add delays between requests
2. Reduce concurrent operations
3. Contact Xray/Jira support to increase limits

### Project and Permission Issues

#### ❌ Project Not Found
```
ERROR - Project with key 'WRONG' does not exist
```

**Solutions:**
1. Verify project key in Jira:
   ```bash
   # List projects
   curl -u "email:token" \
        "https://yourcompany.atlassian.net/rest/api/3/project"
   ```

2. Ensure user has access to the project

3. Check project key is correctly set:
   ```env
   PROJECT_KEY=CORRECT_KEY
   ```

#### ❌ Issue Linking Failed
```
WARNING - Failed to link TEST-123: 404 Not Found
```

**Solutions:**
1. Verify target issue exists:
   ```bash
   curl -u "email:token" \
        "https://yourcompany.atlassian.net/rest/api/3/issue/ISSUE-123"
   ```

2. Check link type permissions
3. Verify issue is accessible to your user

### File and Path Issues

#### ❌ File Not Found
```
ERROR - Document not found: ./my_tests.docx
```

**Solutions:**
1. Check file path:
   ```bash
   ls -la ./my_tests.docx
   ```

2. Use absolute paths:
   ```bash
   python cli.py -f /full/path/to/document.docx
   ```

3. Verify file permissions (readable)

#### ❌ Log Directory Issues
```
ERROR - Permission denied: ./logs/xray_automation.log
```

**Solutions:**
1. Create log directory:
   ```bash
   mkdir -p logs
   ```

2. Check permissions:
   ```bash
   chmod 755 logs
   ```

3. Use different log path:
   ```bash
   python cli.py --log-file /tmp/xray.log
   ```

## 🐛 Debugging Steps

### 1. Enable Debug Logging
```bash
python cli.py -v --log-file ./debug.log
```

### 2. Test Individual Components

#### Test Document Parsing
```python
from src.document_parser import DocumentParser

parser = DocumentParser("./your_document.docx")
test_cases = parser.parse_test_scenarios()
print(f"Found {len(test_cases)} test cases")
```

#### Test Xray Authentication
```python
from src.xray_client import XrayClient

client = XrayClient()
token = client.get_jwt_token()
print("Authentication successful!")
```

#### Test Jira Connection
```python
from src.jira_client import JiraClient

jira = JiraClient()
exists = jira.validate_issue_exists("YOUR-ISSUE-123")
print(f"Issue exists: {exists}")
```

### 3. Validate Configuration
```bash
# Check all environment variables
python -c "from src.config import Config; print('Valid:', Config.validate())"
```

### 4. Use Dry Run Mode
```bash
# Test everything without making changes
python cli.py --dry-run -v
```

## 🔍 Error Codes Reference

| Error Code | Meaning | Common Causes |
|------------|---------|---------------|
| 400 | Bad Request | Invalid request format, missing required fields |
| 401 | Unauthorized | Invalid credentials, expired tokens |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist (project, issue, etc.) |
| 429 | Too Many Requests | Rate limiting, too many API calls |
| 500 | Internal Server Error | Service is down, temporary issue |

## 📝 Log Analysis

### Successful Run Pattern
```
INFO - Starting Xray Test Automation
INFO - Step 1: Parsing test scenarios from document...
INFO - Successfully parsed X test cases from document
INFO - Step 2: Validating test cases...
INFO - Step 3: Authenticating with Xray Cloud...
INFO - Successfully authenticated with Xray Cloud
INFO - Step 4: Creating test cases in Xray Cloud...
INFO - Bulk import job submitted successfully with jobId: abc123
INFO - Step 5: Waiting for test case creation to complete...
INFO - Bulk import job abc123 completed successfully
INFO - Step 6: Creating links to Jira issue...
INFO - Summary: X parsed, X created, X linked
```

### Failed Run Indicators
```
ERROR - Failed to authenticate with Xray Cloud
ERROR - No table found with required headers
ERROR - Bulk import job failed
ERROR - Request failed when linking
```

## 🆘 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide** for your specific error
2. **Run with verbose logging** (`-v`) to get detailed output
3. **Test with the sample document** to isolate issues
4. **Verify your credentials** work with curl/Postman

### Information to Include

When reporting issues, please include:

1. **Complete error message** from logs
2. **Command used** (with sensitive data removed)
3. **Environment details**:
   - Python version: `python --version`
   - Package version: `pip show xray-test-automation`
   - Operating system

4. **Configuration** (sanitized):
   ```bash
   # Remove sensitive values
   cat .env | sed 's/=.*/=***/' 
   ```

5. **Document format** (if parsing issues):
   - Table structure
   - Column headers
   - Sample row

### Where to Get Help

1. **GitHub Issues**: [Report bugs and request features](https://github.com/yourusername/xray-test-automation/issues)
2. **Discussions**: [Ask questions and share experiences](https://github.com/yourusername/xray-test-automation/discussions)
3. **Documentation**: [Check the full documentation](README.md)

## 🔧 Advanced Debugging

### Network Debugging
```bash
# Test Xray connectivity
curl -v https://xray.cloud.getxray.app/api/v2/authenticate

# Test Jira connectivity  
curl -v https://yourcompany.atlassian.net/rest/api/3/myself
```

### Python Environment Debugging
```bash
# Check Python environment
python -c "import sys; print(sys.path)"
pip list | grep -E "(requests|docx|dotenv)"
```

### Document Debugging
```python
# Inspect document structure
from docx import Document

doc = Document('./your_document.docx')
for i, table in enumerate(doc.tables):
    print(f"Table {i}: {len(table.rows)} rows, {len(table.columns)} columns")
    headers = [cell.text.strip() for cell in table.rows[0].cells]
    print(f"Headers: {headers}")
```

Remember: Most issues are related to configuration, credentials, or document format. Double-check these first!