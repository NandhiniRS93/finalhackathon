"""Document parser for extracting test cases from Word documents."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from docx import Document

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parser for extracting test scenarios from Word documents."""
    
    def __init__(self, document_path: str):
        """Initialize parser with document path."""
        self.document_path = Path(document_path)
        self._validate_file()
    
    def _validate_file(self) -> None:
        """Validate that the document file exists and is readable."""
        if not self.document_path.exists():
            raise FileNotFoundError(f"Document not found: {self.document_path}")
        
        if not self.document_path.is_file():
            raise ValueError(f"Path is not a file: {self.document_path}")
        
        if self.document_path.suffix.lower() not in ['.docx']:
            raise ValueError(f"Unsupported file format: {self.document_path.suffix}")
    
    def parse_test_scenarios(self, required_headers: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Parse test scenarios from Word document tables.
        
        Args:
            required_headers: List of required column headers. 
                            Defaults to ['Scenario ID', 'Description', 'Preconditions', 'Expected Results']
        
        Returns:
            List of test case dictionaries
        """
        if required_headers is None:
            required_headers = ['Scenario ID', 'Description', 'Preconditions', 'Expected Results']
        
        logger.info(f"Parsing test scenarios from {self.document_path}")
        
        try:
            document = Document(str(self.document_path))
            test_cases = []
            table_found = False
            
            for table_idx, table in enumerate(document.tables):
                logger.debug(f"Processing table {table_idx + 1}")
                
                # Extract headers from first row
                if not table.rows:
                    logger.debug(f"Table {table_idx + 1} is empty, skipping")
                    continue
                
                headers = [cell.text.strip() for cell in table.rows[0].cells]
                logger.debug(f"Table {table_idx + 1} headers: {headers}")
                
                # Check if this table contains the required headers
                if not all(header in headers for header in required_headers):
                    logger.debug(f"Table {table_idx + 1} doesn't contain required headers, skipping")
                    continue
                
                table_found = True
                logger.info(f"Found test scenarios table {table_idx + 1} with {len(table.rows) - 1} rows")
                
                # Create header index mapping
                header_indices = {header: headers.index(header) for header in required_headers}
                
                # Process data rows (skip header row)
                for row_idx, row in enumerate(table.rows[1:], 1):
                    cells = row.cells
                    
                    if len(cells) < len(required_headers):
                        logger.warning(f"Row {row_idx} has insufficient columns, skipping")
                        continue
                    
                    # Extract test case data
                    test_case = {
                        "id": cells[header_indices['Scenario ID']].text.strip(),
                        "summary": cells[header_indices['Description']].text.strip(),
                        "preconditions": cells[header_indices['Preconditions']].text.strip(),
                        "expected_results": cells[header_indices['Expected Results']].text.strip()
                    }
                    
                    # Validate that required fields are not empty
                    if not test_case["id"] or not test_case["summary"]:
                        logger.warning(f"Row {row_idx} missing required data (ID or Summary), skipping")
                        continue
                    
                    test_cases.append(test_case)
                    logger.debug(f"Parsed test case: {test_case['id']} - {test_case['summary'][:50]}...")
                
                # Process only the first matching table
                break
            
            if not table_found:
                raise ValueError(
                    f"No table found with required headers: {required_headers}. "
                    f"Please ensure your Word document contains a table with these exact column headers."
                )
            
            if not test_cases:
                raise ValueError("No valid test cases found in the document")
            
            logger.info(f"Successfully parsed {len(test_cases)} test cases from document")
            return test_cases
            
        except Exception as e:
            logger.error(f"Failed to parse document {self.document_path}: {e}")
            raise
    
    def validate_test_cases(self, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Validate parsed test cases for completeness and consistency.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating parsed test cases...")
        
        validation_results = {
            "valid_count": 0,
            "invalid_count": 0,
            "warnings": [],
            "errors": []
        }
        
        seen_ids = set()
        
        for idx, test_case in enumerate(test_cases):
            is_valid = True
            
            # Check for duplicate IDs
            if test_case["id"] in seen_ids:
                validation_results["errors"].append(f"Duplicate test case ID: {test_case['id']}")
                is_valid = False
            seen_ids.add(test_case["id"])
            
            # Check for empty required fields
            for field in ["id", "summary"]:
                if not test_case[field].strip():
                    validation_results["errors"].append(f"Test case {idx + 1}: Empty {field}")
                    is_valid = False
            
            # Check for overly long summaries
            if len(test_case["summary"]) > 255:
                validation_results["warnings"].append(
                    f"Test case {test_case['id']}: Summary is very long ({len(test_case['summary'])} chars)"
                )
            
            # Check for empty optional fields
            if not test_case.get("preconditions", "").strip():
                validation_results["warnings"].append(f"Test case {test_case['id']}: No preconditions specified")
            
            if not test_case.get("expected_results", "").strip():
                validation_results["warnings"].append(f"Test case {test_case['id']}: No expected results specified")
            
            if is_valid:
                validation_results["valid_count"] += 1
            else:
                validation_results["invalid_count"] += 1
        
        logger.info(f"Validation completed: {validation_results['valid_count']} valid, "
                   f"{validation_results['invalid_count']} invalid, "
                   f"{len(validation_results['warnings'])} warnings")
        
        return validation_results