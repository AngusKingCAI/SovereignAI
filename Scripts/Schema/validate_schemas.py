#!/usr/bin/env python3
"""
Schema Validation Script for SovereignAI Governance Files

Validates YAML frontmatter in markdown files against JSON schemas.
Ensures governance files follow proper structure and type constraints.
Also validates file categorization compliance with repository structure rules.
"""

import json
import yaml
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Schema mapping based on file location and naming
SCHEMA_MAPPING = {
    "workflow": "workflow-schema.json",
    "rules": "rules-schema.json", 
    "agents": "agents-schema.json",
    "skill": "skill-schema.json",
    "reference": "reference-schema.json",
    "template": "template-schema.json"
}

# Categorization rules
CATEGORIZATION_RULES = {
    "Scripts/": {
        "allowed_subdirs": ["Schema", "Infrastructure", "Harness Tests", "App Tests", "Build", "Deployment", "Maintenance", "Utilities", "Logging", "Analysis", "Misc"],
        "file_rules": {
            "Schema/": {
                "allowed_patterns": ["validate_*.py", "*-schema.json", "*_config.json"],
                "forbidden_patterns": ["*"],
                "description": "Schema validation scripts and JSON schemas"
            },
            "Infrastructure/": {
                "allowed_patterns": ["setup_*.py", "*_setup.py", "install_*.py"],
                "description": "Infrastructure automation scripts"
            },
            "Harness Tests/": {
                "allowed_patterns": ["test_*.py", "validate_*.py"],
                "description": "Harness testing and validation scripts"
            },
            "App Tests/": {
                "allowed_patterns": ["test_*.py", "*_test.py"],
                "description": "Application code testing scripts"
            },
            "Build/": {
                "allowed_patterns": ["build_*.py", "compile_*.py"],
                "description": "Build and compilation scripts"
            },
            "Deployment/": {
                "allowed_patterns": ["deploy_*.py", "release_*.py"],
                "description": "Deployment automation scripts"
            },
            "Maintenance/": {
                "allowed_patterns": ["cleanup_*.py", "maintain_*.py"],
                "description": "Maintenance and cleanup scripts"
            },
            "Utilities/": {
                "allowed_patterns": ["util_*.py", "helper_*.py"],
                "description": "General utility scripts"
            },
            "Logging/": {
                "allowed_subdirs": [".session_state", "__pycache__"],
                "allowed_patterns": ["*_logger.py", "*_tracker.py", "*_state.py"],
                "file_rules": {
                    ".session_state/": {
                        "allowed_patterns": ["*.json"],
                        "description": "Session state management"
                    },
                    "__pycache__/": {
                        "allowed_patterns": ["*.pyc"],
                        "description": "Python cache files"
                    }
                },
                "description": "Logging and tracking scripts"
            },
            "Misc/": {
                "allowed_subdirs": ["HookLogs"],
                "allowed_patterns": ["*_post_compact.py", "reload_*.py"],
                "file_rules": {
                    "HookLogs/": {
                        "allowed_patterns": ["*.txt"],
                        "description": "Hook debug logs"
                    }
                },
                "description": "Miscellaneous scripts"
            },
            "App Tests/": {
                "allowed_patterns": [".gitkeep", "test_*.py", "*_test.py"],
                "description": "Application test files"
            }
        }
    },
    "Workflow/": {
        "allowed_subdirs": ["Workflow_Reference", "Architect", "Planner", "Executor", "Researcher", "Reviewer", "Templates", "Creation Workflows", "Validation Workflows"],
        "file_rules": {
            "Workflow_Reference/": {
                "allowed_patterns": ["*_Patterns.md", "*_Framework.md", "*_Guidelines.md"],
                "description": "Universal framework references"
            },
            "Templates/": {
                "allowed_patterns": ["*_Template.md"],
                "description": "Workflow templates"
            },
            "Creation Workflows/": {
                "allowed_patterns": ["*_Workflow.md"],
                "description": "Creation workflows"
            },
            "Validation Workflows/": {
                "allowed_patterns": ["*_Workflow.md"],
                "description": "Validation workflows"
            },
            "Architect/": {
                "allowed_subdirs": ["Reference", "Templates"],
                "allowed_patterns": ["*.md"],
                "file_rules": {
                    "Reference/": {
                        "allowed_patterns": ["*_Patterns.md", "*_Framework.md", "*_Specifications.md"],
                        "description": "Architect reference documents"
                    },
                    "Templates/": {
                        "allowed_patterns": ["*_Template.md"],
                        "description": "Architect templates"
                    }
                }
            },
            "Planner/": {
                "allowed_subdirs": ["Reference", "Templates"],
                "allowed_patterns": ["*.md"],
                "file_rules": {
                    "Reference/": {
                        "allowed_patterns": ["*_Patterns.md", "*_Specifications.md", "*_Overview.md"],
                        "description": "Planner reference documents"
                    },
                    "Templates/": {
                        "allowed_patterns": ["*_Template.md"],
                        "description": "Planner templates"
                    }
                }
            },
            "Executor/": {
                "allowed_subdirs": ["Reference", "Templates"],
                "allowed_patterns": ["*.md"],
                "file_rules": {
                    "Reference/": {
                        "allowed_patterns": ["*_Patterns.md"],
                        "description": "Executor reference documents"
                    },
                    "Templates/": {
                        "allowed_patterns": ["*_Template.md"],
                        "description": "Executor templates"
                    }
                }
            },
            "Researcher/": {
                "allowed_subdirs": [],
                "allowed_patterns": ["*.md"],
                "file_rules": {}
            },
            "Reviewer/": {
                "allowed_subdirs": ["Reference"],
                "allowed_patterns": ["*.md"],
                "file_rules": {
                    "Reference/": {
                        "allowed_patterns": ["*_Patterns.md", "*_Reference.md", "*_Guide.md"],
                        "description": "Reviewer reference documents"
                    }
                }
            }
        }
    },
    "Docs/": {
        "allowed_subdirs": ["Architect", "Planner", "Executor", "Researcher", "Reviewer", "Code", "Research", "Architecture", "Governance", "Devin Local IDE Documents", "External AI Reviews", "Sovereign AI Design Docs"],
        "file_rules": {
            "Architect/": {
                "allowed_subdirs": ["Code", "Research", "Architecture", "Governance", "Repository"],
                "allowed_patterns": ["*.md"],
                "description": "Architect agent documentation"
            },
            "Planner/": {
                "allowed_subdirs": ["Code", "Research", "Architecture", "Governance", "Repository"],
                "allowed_patterns": ["*.md"],
                "description": "Planner agent documentation"
            },
            "Executor/": {
                "allowed_subdirs": ["Code", "Research", "Architecture", "Governance", "Repository"],
                "allowed_patterns": ["*.md"],
                "description": "Executor agent documentation"
            },
            "Researcher/": {
                "allowed_subdirs": ["Code", "Research", "Architecture", "Governance", "Repository"],
                "allowed_patterns": ["*.md"],
                "description": "Researcher agent documentation"
            },
            "Reviewer/": {
                "allowed_subdirs": ["Code", "Research", "Architecture", "Governance", "Repository"],
                "allowed_patterns": ["*.md"],
                "description": "Reviewer agent documentation"
            },
            "Code/": {
                "allowed_subdirs": ["Python", "JavaScript", "Markdown", "YAML"],
                "file_rules": {
                    "Python/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Python code documentation"
                    },
                    "JavaScript/": {
                        "allowed_patterns": ["*.md"],
                        "description": "JavaScript code documentation"
                    },
                    "Markdown/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Markdown code documentation"
                    },
                    "YAML/": {
                        "allowed_patterns": ["*.md"],
                        "description": "YAML code documentation"
                    }
                },
                "description": "Code documentation by language"
            },
            "Research/": {
                "allowed_subdirs": ["Architecture", "BestPractices", "CaseStudies"],
                "allowed_patterns": ["*.md"],
                "description": "Research documentation by domain"
            },
            "Architecture/": {
                "allowed_subdirs": ["DesignPatterns", "SystemArchitecture", "ComponentArchitecture"],
                "allowed_patterns": ["*.md"],
                "description": "Architecture documentation by domain"
            },
            "Governance/": {
                "allowed_subdirs": ["Workflows", "Processes"],
                "allowed_patterns": ["*.md"],
                "description": "Governance documentation by domain"
            },
            "Devin Local IDE Documents/": {
                "allowed_subdirs": ["05-Reference"],
                "file_rules": {
                    "05-Reference/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Devin IDE reference documentation"
                    }
                },
                "allowed_patterns": ["*.md"],
                "description": "Devin Local IDE documentation"
            },
            "External AI Reviews/": {
                "allowed_patterns": ["*.md"],
                "description": "External AI review documentation"
            },
            "Sovereign AI Design Docs/": {
                "allowed_patterns": ["*.md"],
                "description": "Sovereign AI design documentation"
            }
        }
    },
    "Logs/": {
        "allowed_subdirs": ["Architect", "Planner", "Executor", "Researcher", "Reviewer", ".Archived"],
        "file_rules": {
            "Architect/": {
                "allowed_subdirs": ["Consistency Review", "Session", "Validation"],
                "description": "Architect logs by type"
            },
            "Planner/": {
                "allowed_subdirs": ["Roundtable", "Session", "Validation"],
                "file_rules": {
                    "Roundtable/": {
                        "allowed_subdirs": ["Internal", "External"],
                        "description": "Round Table review logs"
                    }
                }
            },
            "Executor/": {
                "allowed_subdirs": ["Session", "Handoff", "Validation"],
                "description": "Executor logs by type"
            },
            "Researcher/": {
                "allowed_subdirs": ["Session"],
                "description": "Researcher logs by type"
            },
            "Reviewer/": {
                "allowed_subdirs": ["Session", "BP"],
                "file_rules": {
                    "BP/": {
                        "allowed_subdirs": ["App", "Harness"],
                        "description": "Best Practice scan logs"
                    }
                }
            },
            ".Archived/": {
                "allowed_subdirs": ["Misc", "20-29", "30-39"],
                "file_rules": {
                    "Misc/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Archived miscellaneous logs"
                    },
                    "20-29/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Archived logs from conversation IDs 20-29"
                    },
                    "30-39/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Archived logs from conversation IDs 30-39"
                    }
                },
                "description": "Archived logs"
            }
        }
    },
    "Plans/": {
        "allowed_subdirs": ["Completed", "Queued"],
        "file_rules": {
            "Completed/": {
                "allowed_subdirs": ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-99", "Misc"],
                "file_rules": {
                    "0-9/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Plans 0-9"
                    },
                    "10-19/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Plans 10-19"
                    },
                    "20-29/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Plans 20-29"
                    },
                    "30-39/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Plans 30-39"
                    },
                    "40-49/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Plans 40-49"
                    },
                    "50-59/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Plans 50-59"
                    },
                    "60-69/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Plans 60-69"
                    },
                    "70-79/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Plans 70-79"
                    },
                    "80-89/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Plans 80-89"
                    },
                    "90-99/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Plans 90-99"
                    },
                    "Misc/": {
                        "allowed_patterns": ["*.md"],
                        "description": "Miscellaneous plans"
                    }
                },
                "description": "Completed project plans"
            },
            "Queued/": {
                "allowed_patterns": ["*.md"],
                "description": "Queued project plans"
            }
        }
    },
    "Agents/": {
        "allowed_subdirs": ["Architect", "Executor", "Planner", "Researcher", "Reviewer"],
        "allowed_patterns": ["AGENTS.md"],
        "file_rules": {
            "Architect/": {
                "allowed_patterns": ["AGENTS.md"],
                "description": "Architect agent governance"
            },
            "Executor/": {
                "allowed_patterns": ["AGENTS.md"],
                "description": "Executor agent governance"
            },
            "Planner/": {
                "allowed_patterns": ["AGENTS.md"],
                "description": "Planner agent governance"
            },
            "Researcher/": {
                "allowed_patterns": ["AGENTS.md"],
                "description": "Researcher agent governance"
            },
            "Reviewer/": {
                "allowed_patterns": ["AGENTS.md"],
                "description": "Reviewer agent governance"
            }
        }
    },
    ".devin/": {
        "allowed_subdirs": ["skills", "rules"],
        "file_rules": {
            "skills/": {
                "allowed_subdirs": ["architect", "executor", "planner", "researcher", "reviewer"],
                "file_rules": {
                    "architect/": {
                        "allowed_patterns": ["SKILL.md"],
                        "description": "Architect skill definition"
                    },
                    "executor/": {
                        "allowed_patterns": ["SKILL.md"],
                        "description": "Executor skill definition"
                    },
                    "planner/": {
                        "allowed_patterns": ["SKILL.md"],
                        "description": "Planner skill definition"
                    },
                    "researcher/": {
                        "allowed_patterns": ["SKILL.md"],
                        "description": "Researcher skill definition"
                    },
                    "reviewer/": {
                        "allowed_patterns": ["SKILL.md"],
                        "description": "Reviewer skill definition"
                    }
                }
            },
            "rules/": {
                "allowed_patterns": ["*.md"],
                "description": "Agent rule definitions"
            }
        }
    }
}

def extract_frontmatter(file_path: Path) -> Optional[Dict]:
    """Extract YAML frontmatter from markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for YAML frontmatter (--- delimited)
        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            if frontmatter_end != -1:
                frontmatter_str = content[3:frontmatter_end].strip()
                return yaml.safe_load(frontmatter_str)
        
        return None
    except Exception as e:
        print(f"Error extracting frontmatter from {file_path}: {e}")
        return None

def determine_schema_type(file_path: Path) -> Optional[str]:
    """Determine which schema to use based on file path and name."""
    path_str = str(file_path).lower()
    
    # Workflow files
    if 'workflow' in path_str and file_path.suffix == '.md':
        return 'workflow'
    
    # Rules files
    if 'rules' in path_str and file_path.name.endswith('_rules.md'):
        return 'rules'
    
    # AGENTS.md
    if file_path.name == 'agents.md':
        return 'agents'
    
    # Skill files
    if 'skill' in path_str and file_path.name == 'SKILL.md':
        return 'skill'
    
    # Reference files
    if 'reference' in path_str and file_path.suffix == '.md':
        return 'reference'
    
    # Template files
    if 'template' in path_str and file_path.suffix == '.md':
        return 'template'
    
    return None

def load_schema(schema_type: str, schema_dir: Path) -> Dict:
    """Load JSON schema for given type."""
    schema_file = schema_dir / SCHEMA_MAPPING[schema_type]
    with open(schema_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_frontmatter(frontmatter: Dict, schema: Dict) -> Tuple[bool, List[str]]:
    """Validate frontmatter against schema using basic validation."""
    errors = []
    
    # Check required fields
    required_fields = schema.get('required', [])
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")
    
    # Check field types and patterns
    properties = schema.get('properties', {})
    for field, field_schema in properties.items():
        if field in frontmatter:
            value = frontmatter[field]
            
            # Type validation
            expected_type = field_schema.get('type')
            if expected_type == 'string' and not isinstance(value, str):
                errors.append(f"Field '{field}' should be string, got {type(value).__name__}")
            elif expected_type == 'array' and not isinstance(value, list):
                errors.append(f"Field '{field}' should be array, got {type(value).__name__}")
            elif expected_type == 'object' and not isinstance(value, dict):
                errors.append(f"Field '{field}' should be object, got {type(value).__name__}")
            
            # Pattern validation for strings
            if expected_type == 'string' and isinstance(value, str):
                pattern = field_schema.get('pattern')
                if pattern:
                    if not re.match(pattern, value):
                        errors.append(f"Field '{field}' does not match pattern: {pattern}")
            
            # Enum validation
            enum_values = field_schema.get('enum')
            if enum_values and value not in enum_values:
                errors.append(f"Field '{field}' must be one of: {enum_values}")
            
            # Min length validation for strings
            if expected_type == 'string' and isinstance(value, str):
                min_length = field_schema.get('minLength')
                if min_length and len(value) < min_length:
                    errors.append(f"Field '{field}' must be at least {min_length} characters")
    
    # Check for additional properties
    additional_props = schema.get('additionalProperties', True)
    if not additional_props:
        allowed_fields = set(properties.keys())
        for field in frontmatter:
            if field not in allowed_fields:
                errors.append(f"Unexpected field: {field}")
    
    is_valid = len(errors) == 0
    return is_valid, errors

def validate_categorization(file_path: Path, repo_root: Path) -> List[str]:
    """Validate file categorization against repository rules."""
    errors = []
    
    # Get relative path from repo root
    try:
        rel_path = file_path.relative_to(repo_root)
    except ValueError:
        errors.append(f"File is not within repository root: {file_path}")
        return errors
    
    path_parts = rel_path.parts
    path_str = str(rel_path)
    
    # Check root directory violations
    if len(path_parts) == 1:
        # File is at root level
        allowed_root_files = {"AGENTS.md", "PRINCIPLES.md", "STRUCTURE.md", ".gitignore"}
        if file_path.name not in allowed_root_files:
            errors.append(f"File at root level not approved: {file_path.name}. Approved root files: {allowed_root_files}")
        return errors
    
    # Get top-level directory
    top_dir = path_parts[0]
    top_dir_str = top_dir + "/"
    
    # Check if top-level directory is in categorization rules
    if top_dir_str not in CATEGORIZATION_RULES:
        errors.append(f"Unknown top-level directory: {top_dir_str}")
        return errors
    
    # Allow known working directory structures
    # Python cache and runtime files
    if ".session_state" in path_str or "__pycache__" in path_str:
        return errors
    
    # Known working subdirectories (more specific patterns)
    # Convert to use both forward and backward slashes for cross-platform compatibility
    known_patterns = [
        "Reference/", "Templates/", "Session/", "Consistency Review/", "Consistency_Review/", "BP/", "HookLogs/", ".Archived/", "05-Reference/",
        "skills/architect/", "skills/executor/", "skills/planner/", "skills/researcher/", "skills/reviewer/",
        "tui_tests/", "web_tests/", "Misc/", "20-29/", "30-39/",
        "01-Getting-Started/", "02-Essential-Commands/", "03-Models/", "04-Extensibility/", "06-Advanced-Features/", "08-Troubleshooting/",
        "External AI Reviews/", "Sovereign AI Design Docs/",
        "0-9/", "10-19/", "40-49/", "50-59/", "60-69/", "70-79/", "80-89/", "90-99/",
        "Templates/", "Creation Workflows/", "Validation Workflows/"  # Add Templates/, Creation Workflows/, Validation Workflows/ to known patterns
    ]
    
    if any(pattern in path_str.replace("\\", "/") for pattern in known_patterns):
        return errors
    
    # Get categorization rules for this directory
    current_rules = CATEGORIZATION_RULES[top_dir_str]
    
    # Special check for Docs/ root directory - no files allowed directly
    if top_dir_str == "Docs/" and len(path_parts) == 2:
        errors.append(f"File not allowed directly in Docs/ root directory. Must use agent-specific subdirectory (Docs/{{Agent}}/) or universal category (Docs/{{Category}}/)")
        return errors
    
    # Validate subdirectory structure for remaining files
    if len(path_parts) > 2:
        # File is in a subdirectory
        subdirs = list(path_parts[1:-1])  # All parts except top dir and filename
        
        for i, subdir in enumerate(subdirs):
            current_path_str = "/".join([top_dir] + subdirs[:i+1]) + "/"
            
            # Check if this subdirectory is allowed at current level
            if "allowed_subdirs" in current_rules:
                if subdir not in current_rules["allowed_subdirs"]:
                    # Check if it's allowed in file_rules instead
                    if "file_rules" in current_rules and subdir in current_rules["file_rules"]:
                        current_rules = current_rules["file_rules"][subdir]
                    else:
                        errors.append(f"Subdirectory '{subdir}' not allowed in {current_path_str}. Allowed: {current_rules['allowed_subdirs']}")
                        return errors
                else:
                    # Navigate into the subdirectory if it has file_rules
                    if "file_rules" in current_rules and subdir in current_rules["file_rules"]:
                        current_rules = current_rules["file_rules"][subdir]
            elif "file_rules" in current_rules and subdir in current_rules["file_rules"]:
                # Navigate into file_rules structure
                current_rules = current_rules["file_rules"][subdir]
            else:
                # No explicit rules for this level, allow it
                pass
        
        # Validate file naming patterns at the final level
        final_dir_str = "/".join([top_dir] + subdirs) + "/"
        
        # Build the complete set of allowed patterns
        allowed_patterns = []
        
        # Get patterns from current level
        if "allowed_patterns" in current_rules:
            allowed_patterns.extend(current_rules["allowed_patterns"])
        
        # Also check if parent directory has patterns that should apply
        parent_rules = CATEGORIZATION_RULES[top_dir_str]
        if "allowed_patterns" in parent_rules:
            allowed_patterns.extend(parent_rules["allowed_patterns"])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_patterns = []
        for pattern in allowed_patterns:
            if pattern not in seen:
                seen.add(pattern)
                unique_patterns.append(pattern)
        
        if unique_patterns:
            filename = file_path.name
            pattern_matched = False
            
            for pattern in unique_patterns:
                # Convert glob pattern to regex
                regex_pattern = pattern.replace("*", ".*").replace("?", ".")
                if re.match(regex_pattern, filename):
                    pattern_matched = True
                    break
            
            if not pattern_matched:
                errors.append(f"File '{filename}' does not match allowed patterns in {final_dir_str}. Allowed: {unique_patterns}")
        
        if "forbidden_patterns" in current_rules:
            filename = file_path.name
            for pattern in current_rules["forbidden_patterns"]:
                regex_pattern = pattern.replace("*", ".*").replace("?", ".")
                if re.match(regex_pattern, filename):
                    errors.append(f"File '{filename}' matches forbidden pattern in {final_dir_str}. Forbidden: {current_rules['forbidden_patterns']}")
    
    return errors

def validate_file(file_path: Path, schema_dir: Path, repo_root: Path) -> Dict:
    """Validate a single markdown file against appropriate schema and categorization."""
    result = {
        'file': str(file_path),
        'valid': True,
        'has_frontmatter': False,
        'schema_type': None,
        'categorization_valid': True,
        'errors': []
    }
    
    # Determine schema type
    schema_type = determine_schema_type(file_path)
    if not schema_type:
        result['schema_type'] = None
        # Files without schema types don't get schema validation
        return result
    
    result['schema_type'] = schema_type
    
    # Extract frontmatter
    frontmatter = extract_frontmatter(file_path)
    if not frontmatter:
        result['has_frontmatter'] = False
        result['valid'] = False
        result['errors'].append("No YAML frontmatter found")
        return result
    
    result['has_frontmatter'] = True
    
    # Load and validate schema
    try:
        schema = load_schema(schema_type, schema_dir)
        is_valid, errors = validate_frontmatter(frontmatter, schema)
        if not is_valid:
            result['valid'] = False
            result['errors'].extend(errors)
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Schema loading error: {e}")
    
    return result

def scan_directory(directory: Path, schema_dir: Path, repo_root: Path) -> List[Dict]:
    """Scan directory for markdown files and validate them."""
    results = []
    
    # Find all markdown files using proper path handling
    if directory.exists():
        md_files = list(directory.rglob("*.md"))
        
        for md_file in md_files:
            result = validate_file(md_file, schema_dir, repo_root)
            results.append(result)
    
    return results

def generate_report(results: List[Dict]) -> str:
    """Generate human-readable validation report."""
    total_files = len(results)
    valid_files = sum(1 for r in results if r['valid'])
    invalid_files = total_files - valid_files
    cat_valid_files = sum(1 for r in results if r['categorization_valid'])
    cat_invalid_files = total_files - cat_valid_files
    
    report = []
    report.append("=" * 60)
    report.append("Schema and Categorization Validation Report")
    report.append("=" * 60)
    report.append(f"Total files scanned: {total_files}")
    report.append(f"Schema valid files: {valid_files}")
    report.append(f"Schema invalid files: {invalid_files}")
    report.append(f"Categorization valid files: {cat_valid_files}")
    report.append(f"Categorization invalid files: {cat_invalid_files}")
    report.append("")
    
    # Group invalid files by error type
    schema_invalid = [r for r in results if not r['valid'] and r['schema_type']]
    cat_invalid = [r for r in results if not r['categorization_valid']]
    both_invalid = [r for r in results if not r['valid'] and not r['categorization_valid']]
    
    # Report schema validation failures
    if schema_invalid:
        report.append("Schema Validation Failures:")
        for result in schema_invalid:
            report.append(f"  - {result['file']}")
            report.append(f"    Schema type: {result['schema_type']}")
            for error in result['errors']:
                report.append(f"    {error}")
        report.append("")
    
    # Report categorization failures
    if cat_invalid:
        report.append("Categorization Validation Failures:")
        for result in cat_invalid:
            report.append(f"  - {result['file']}")
            for error in result['errors']:
                report.append(f"    {error}")
        report.append("")
    
    # Summary
    if invalid_files == 0 and cat_invalid_files == 0:
        report.append("PASS: All files validated successfully!")
    else:
        if invalid_files > 0:
            report.append(f"FAIL: {invalid_files} file(s) failed schema validation")
        if cat_invalid_files > 0:
            report.append(f"FAIL: {cat_invalid_files} file(s) failed categorization validation")
    
    return "\n".join(report)

def scan_all_files(directory: Path, schema_dir: Path, repo_root: Path) -> List[Dict]:
    """Scan directory for all files and validate categorization."""
    results = []
    
    # Find all files using proper path handling
    if directory.exists():
        all_files = list(directory.rglob("*"))
        
        for file_path in all_files:
            if file_path.is_file():
                # All files get categorization validation
                result = {
                    'file': str(file_path),
                    'valid': True,
                    'has_frontmatter': False,
                    'schema_type': None,
                    'categorization_valid': True,
                    'errors': []
                }
                
                # Validate categorization
                cat_errors = validate_categorization(file_path, repo_root)
                if cat_errors:
                    result['categorization_valid'] = False
                    result['valid'] = False
                    result['errors'].extend(cat_errors)
                
                # Markdown files also get schema validation
                if file_path.suffix == ".md":
                    schema_result = validate_file(file_path, schema_dir, repo_root)
                    # Merge schema validation results
                    if not schema_result['valid']:
                        result['valid'] = False
                        result['has_frontmatter'] = schema_result['has_frontmatter']
                        result['schema_type'] = schema_result['schema_type']
                        # Add schema errors that aren't already categorization errors
                        for error in schema_result['errors']:
                            if error not in result['errors']:
                                result['errors'].append(error)
                
                results.append(result)
    
    return results

def main():
    """Main validation function."""
    # Setup paths using string paths for Windows compatibility
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    schema_dir = script_dir
    
    print(f"Schema and Categorization Validation Script")
    print(f"Schema directory: {schema_dir}")
    print(f"Repository root: {repo_root}")
    print()
    
    # Scan all directories for categorization and schema validation
    all_dirs = [
        repo_root / "Scripts",
        repo_root / "Workflow",
        repo_root / "Agents",
        repo_root / "Docs",
        repo_root / "Logs",
        repo_root / ".devin",
        repo_root / "Plans"
    ]
    
    all_results = []
    for check_dir in all_dirs:
        if check_dir.exists():
            print(f"Scanning {check_dir} for categorization and schema validation...")
            results = scan_all_files(check_dir, schema_dir, repo_root)
            all_results.extend(results)
        else:
            print(f"Directory not found: {check_dir}")
    
    # Validate specific root files
    root_files = [
        repo_root / "AGENTS.md",
        repo_root / "PRINCIPLES.md",
        repo_root / "STRUCTURE.md"
    ]
    for root_file in root_files:
        if root_file.exists():
            print(f"Validating {root_file}...")
            result = validate_file(root_file, schema_dir, repo_root)
            all_results.append(result)
        else:
            print(f"File not found: {root_file}")
    
    # Generate report
    report = generate_report(all_results)
    print()
    print(report)
    
    # Exit with error code if any validation failed
    invalid_count = sum(1 for r in all_results if not r['valid'])
    cat_invalid_count = sum(1 for r in all_results if not r['categorization_valid'])
    if invalid_count > 0 or cat_invalid_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()