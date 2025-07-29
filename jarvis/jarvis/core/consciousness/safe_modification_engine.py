"""
Safe Modification Engine

Provides safe framework for suggesting and validating code changes,
ensuring system integrity while enabling intelligent self-modification.
"""

import time
import logging
import hashlib
import tempfile
import subprocess
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
import json
import shutil

logger = logging.getLogger(__name__)

class ModificationType(Enum):
    """Types of code modifications."""
    FUNCTION_ADD = "function_add"
    FUNCTION_MODIFY = "function_modify"
    FUNCTION_DELETE = "function_delete"
    CLASS_ADD = "class_add"
    CLASS_MODIFY = "class_modify"
    CLASS_DELETE = "class_delete"
    IMPORT_ADD = "import_add"
    IMPORT_REMOVE = "import_remove"
    VARIABLE_MODIFY = "variable_modify"
    COMMENT_ADD = "comment_add"

class SafetyLevel(Enum):
    """Safety levels for modifications."""
    SAFE = "safe"           # Low risk, can be applied automatically
    MODERATE = "moderate"   # Medium risk, requires validation
    RISKY = "risky"        # High risk, requires approval
    DANGEROUS = "dangerous" # Very high risk, blocked

@dataclass
class ModificationSuggestion:
    """Represents a suggested code modification."""
    suggestion_id: str
    modification_type: ModificationType
    file_path: str
    
    # Change details
    original_code: str
    modified_code: str
    line_start: int
    line_end: int
    
    # Safety assessment
    safety_level: SafetyLevel
    risk_factors: List[str] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    reasoning: str = ""
    confidence: float = 0.5
    
    # Status
    approved: bool = False
    applied: bool = False
    tested: bool = False
    
    # Timestamps
    created_at: float = field(default_factory=time.time)
    applied_at: Optional[float] = None

@dataclass
class ValidationResult:
    """Result of modification validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)

class SafeModificationEngine:
    """
    Safe framework for code modification suggestions and validation.
    
    This component provides a secure way to suggest, validate, and apply
    code changes while maintaining system integrity and safety.
    """
    
    def __init__(self, codebase_path: Path, backup_path: Optional[Path] = None):
        """
        Initialize the safe modification engine.
        
        Args:
            codebase_path: Path to the codebase
            backup_path: Optional path for backups
        """
        self.codebase_path = codebase_path
        self.backup_path = backup_path or (codebase_path.parent / "backups")
        
        # Modification tracking
        self._suggestions: Dict[str, ModificationSuggestion] = {}
        self._applied_modifications: List[str] = []
        self._rollback_stack: List[Dict[str, Any]] = []
        
        # Safety configuration
        self.auto_apply_safe = False  # Don't auto-apply even safe changes
        self.require_tests = True
        self.max_modifications_per_session = 10
        
        # Protected patterns (never modify these)
        self.protected_patterns = {
            "__init__.py",
            "main.py",
            "config.py",
            "requirements.txt",
            ".git/",
            "__pycache__/"
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Ensure backup directory exists
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SafeModificationEngine initialized for {codebase_path}")
    
    def suggest_modification(self, file_path: str, original_code: str, 
                           modified_code: str, line_start: int, line_end: int,
                           modification_type: ModificationType,
                           description: str = "", reasoning: str = "") -> str:
        """
        Suggest a code modification.
        
        Args:
            file_path: Path to the file to modify
            original_code: Original code content
            modified_code: Modified code content
            line_start: Starting line number
            line_end: Ending line number
            modification_type: Type of modification
            description: Description of the change
            reasoning: Reasoning for the change
            
        Returns:
            str: Suggestion ID
        """
        with self._lock:
            # Check if file is protected
            if self._is_protected_file(file_path):
                raise ValueError(f"File {file_path} is protected from modification")
            
            # Check modification limits
            if len(self._suggestions) >= self.max_modifications_per_session:
                raise ValueError("Maximum modifications per session exceeded")
            
            # Generate suggestion ID
            suggestion_id = self._generate_suggestion_id(file_path, original_code, modified_code)
            
            # Assess safety level
            safety_level, risk_factors = self._assess_safety(
                file_path, original_code, modified_code, modification_type
            )
            
            # Create suggestion
            suggestion = ModificationSuggestion(
                suggestion_id=suggestion_id,
                modification_type=modification_type,
                file_path=file_path,
                original_code=original_code,
                modified_code=modified_code,
                line_start=line_start,
                line_end=line_end,
                safety_level=safety_level,
                risk_factors=risk_factors,
                description=description,
                reasoning=reasoning
            )
            
            self._suggestions[suggestion_id] = suggestion
            
            logger.info(f"Created modification suggestion {suggestion_id} "
                       f"({modification_type.value}, {safety_level.value})")
            
            return suggestion_id
    
    def validate_modification(self, suggestion_id: str) -> ValidationResult:
        """
        Validate a modification suggestion.
        
        Args:
            suggestion_id: ID of the suggestion to validate
            
        Returns:
            ValidationResult: Validation results
        """
        with self._lock:
            if suggestion_id not in self._suggestions:
                return ValidationResult(
                    valid=False,
                    errors=[f"Suggestion {suggestion_id} not found"]
                )
            
            suggestion = self._suggestions[suggestion_id]
            
            # Create temporary file for validation
            temp_file = self._create_temp_file(suggestion)
            
            try:
                # Syntax validation
                syntax_valid, syntax_errors = self._validate_syntax(temp_file)
                
                # Import validation
                import_valid, import_errors = self._validate_imports(temp_file)
                
                # Test validation (if required)
                test_results = {}
                if self.require_tests:
                    test_results = self._run_tests(temp_file)
                
                # Combine results
                all_errors = syntax_errors + import_errors
                valid = syntax_valid and import_valid
                
                if self.require_tests and test_results:
                    valid = valid and test_results.get("success", False)
                    if not test_results.get("success", False):
                        all_errors.extend(test_results.get("errors", []))
                
                return ValidationResult(
                    valid=valid,
                    errors=all_errors,
                    test_results=test_results
                )
                
            finally:
                # Clean up temporary file
                if temp_file.exists():
                    temp_file.unlink()
    
    def apply_modification(self, suggestion_id: str, force: bool = False) -> bool:
        """
        Apply a modification suggestion.
        
        Args:
            suggestion_id: ID of the suggestion to apply
            force: Force application even if validation fails
            
        Returns:
            bool: True if modification was applied successfully
        """
        with self._lock:
            if suggestion_id not in self._suggestions:
                logger.error(f"Suggestion {suggestion_id} not found")
                return False
            
            suggestion = self._suggestions[suggestion_id]
            
            # Check if already applied
            if suggestion.applied:
                logger.warning(f"Suggestion {suggestion_id} already applied")
                return True
            
            # Validate modification unless forced
            if not force:
                validation = self.validate_modification(suggestion_id)
                if not validation.valid:
                    logger.error(f"Validation failed for {suggestion_id}: {validation.errors}")
                    return False
            
            # Check safety level
            if suggestion.safety_level == SafetyLevel.DANGEROUS:
                logger.error(f"Dangerous modification {suggestion_id} blocked")
                return False
            
            if suggestion.safety_level == SafetyLevel.RISKY and not suggestion.approved:
                logger.error(f"Risky modification {suggestion_id} requires approval")
                return False
            
            try:
                # Create backup
                backup_path = self._create_backup(suggestion.file_path)
                
                # Apply the modification
                success = self._apply_file_modification(suggestion)
                
                if success:
                    # Update suggestion status
                    suggestion.applied = True
                    suggestion.applied_at = time.time()
                    
                    # Add to applied modifications
                    self._applied_modifications.append(suggestion_id)
                    
                    # Add to rollback stack
                    self._rollback_stack.append({
                        "suggestion_id": suggestion_id,
                        "backup_path": str(backup_path),
                        "applied_at": time.time()
                    })
                    
                    logger.info(f"Applied modification {suggestion_id}")
                    return True
                else:
                    logger.error(f"Failed to apply modification {suggestion_id}")
                    return False
                    
            except Exception as e:
                logger.error(f"Error applying modification {suggestion_id}: {e}")
                return False
    
    def rollback_modification(self, suggestion_id: str) -> bool:
        """
        Rollback a previously applied modification.
        
        Args:
            suggestion_id: ID of the suggestion to rollback
            
        Returns:
            bool: True if rollback was successful
        """
        with self._lock:
            # Find the modification in rollback stack
            rollback_entry = None
            for entry in reversed(self._rollback_stack):
                if entry["suggestion_id"] == suggestion_id:
                    rollback_entry = entry
                    break
            
            if not rollback_entry:
                logger.error(f"No rollback entry found for {suggestion_id}")
                return False
            
            try:
                # Restore from backup
                backup_path = Path(rollback_entry["backup_path"])
                if not backup_path.exists():
                    logger.error(f"Backup file not found: {backup_path}")
                    return False
                
                suggestion = self._suggestions[suggestion_id]
                target_file = Path(suggestion.file_path)
                
                # Restore the file
                shutil.copy2(backup_path, target_file)
                
                # Update suggestion status
                suggestion.applied = False
                suggestion.applied_at = None
                
                # Remove from applied modifications
                if suggestion_id in self._applied_modifications:
                    self._applied_modifications.remove(suggestion_id)
                
                # Remove from rollback stack
                self._rollback_stack.remove(rollback_entry)
                
                logger.info(f"Rolled back modification {suggestion_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error rolling back modification {suggestion_id}: {e}")
                return False
    
    def get_suggestions(self, status_filter: str = None) -> List[ModificationSuggestion]:
        """
        Get modification suggestions.
        
        Args:
            status_filter: Optional status filter ('pending', 'applied', 'all')
            
        Returns:
            List[ModificationSuggestion]: Filtered suggestions
        """
        with self._lock:
            suggestions = list(self._suggestions.values())
            
            if status_filter == "pending":
                suggestions = [s for s in suggestions if not s.applied]
            elif status_filter == "applied":
                suggestions = [s for s in suggestions if s.applied]
            
            return suggestions
    
    def get_modification_statistics(self) -> Dict[str, Any]:
        """Get modification statistics."""
        with self._lock:
            total_suggestions = len(self._suggestions)
            applied_suggestions = len(self._applied_modifications)
            
            # Safety level distribution
            safety_counts = {}
            for suggestion in self._suggestions.values():
                level = suggestion.safety_level.value
                safety_counts[level] = safety_counts.get(level, 0) + 1
            
            # Modification type distribution
            type_counts = {}
            for suggestion in self._suggestions.values():
                mod_type = suggestion.modification_type.value
                type_counts[mod_type] = type_counts.get(mod_type, 0) + 1
            
            return {
                "total_suggestions": total_suggestions,
                "applied_suggestions": applied_suggestions,
                "pending_suggestions": total_suggestions - applied_suggestions,
                "rollback_stack_size": len(self._rollback_stack),
                "safety_level_distribution": safety_counts,
                "modification_type_distribution": type_counts,
                "auto_apply_safe": self.auto_apply_safe,
                "require_tests": self.require_tests
            }
    
    def _is_protected_file(self, file_path: str) -> bool:
        """Check if a file is protected from modification."""
        for pattern in self.protected_patterns:
            if pattern in file_path:
                return True
        return False
    
    def _generate_suggestion_id(self, file_path: str, original: str, modified: str) -> str:
        """Generate a unique suggestion ID."""
        content = f"{file_path}:{original}:{modified}:{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _assess_safety(self, file_path: str, original: str, modified: str, 
                      mod_type: ModificationType) -> Tuple[SafetyLevel, List[str]]:
        """Assess the safety level of a modification."""
        risk_factors = []
        
        # Check for dangerous patterns
        dangerous_patterns = ["import os", "subprocess", "eval(", "exec(", "__import__"]
        for pattern in dangerous_patterns:
            if pattern in modified and pattern not in original:
                risk_factors.append(f"Introduces dangerous pattern: {pattern}")
        
        # Check for core file modifications
        core_files = ["main.py", "config.py", "__init__.py"]
        if any(core_file in file_path for core_file in core_files):
            risk_factors.append("Modifying core system file")
        
        # Check modification size
        lines_changed = abs(len(modified.split('\n')) - len(original.split('\n')))
        if lines_changed > 50:
            risk_factors.append(f"Large modification: {lines_changed} lines changed")
        
        # Determine safety level
        if len(risk_factors) == 0:
            return SafetyLevel.SAFE, risk_factors
        elif len(risk_factors) <= 2:
            return SafetyLevel.MODERATE, risk_factors
        elif len(risk_factors) <= 4:
            return SafetyLevel.RISKY, risk_factors
        else:
            return SafetyLevel.DANGEROUS, risk_factors
    
    def _create_temp_file(self, suggestion: ModificationSuggestion) -> Path:
        """Create a temporary file with the modification applied."""
        temp_file = Path(tempfile.mktemp(suffix=".py"))
        
        # Read original file
        original_file = Path(suggestion.file_path)
        if original_file.exists():
            with open(original_file, 'r') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Apply modification
        start_idx = max(0, suggestion.line_start - 1)
        end_idx = min(len(lines), suggestion.line_end)
        
        new_lines = (
            lines[:start_idx] + 
            [suggestion.modified_code + '\n'] + 
            lines[end_idx:]
        )
        
        # Write to temp file
        with open(temp_file, 'w') as f:
            f.writelines(new_lines)
        
        return temp_file
    
    def _validate_syntax(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate Python syntax."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            compile(content, str(file_path), 'exec')
            return True, []
            
        except SyntaxError as e:
            return False, [f"Syntax error: {e}"]
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    def _validate_imports(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate imports in the file."""
        # Simple import validation - could be enhanced
        return True, []
    
    def _run_tests(self, file_path: Path) -> Dict[str, Any]:
        """Run tests for the modified file."""
        # Placeholder for test execution
        return {"success": True, "errors": []}
    
    def _create_backup(self, file_path: str) -> Path:
        """Create a backup of the file."""
        source_file = Path(file_path)
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        # Generate backup filename
        timestamp = int(time.time())
        backup_name = f"{source_file.name}.backup.{timestamp}"
        backup_file = self.backup_path / backup_name
        
        # Copy file to backup location
        shutil.copy2(source_file, backup_file)
        
        return backup_file
    
    def _apply_file_modification(self, suggestion: ModificationSuggestion) -> bool:
        """Apply the modification to the actual file."""
        try:
            file_path = Path(suggestion.file_path)
            
            # Read current file content
            if file_path.exists():
                with open(file_path, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Apply modification
            start_idx = max(0, suggestion.line_start - 1)
            end_idx = min(len(lines), suggestion.line_end)
            
            new_lines = (
                lines[:start_idx] + 
                [suggestion.modified_code + '\n'] + 
                lines[end_idx:]
            )
            
            # Write modified content
            with open(file_path, 'w') as f:
                f.writelines(new_lines)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply file modification: {e}")
            return False
