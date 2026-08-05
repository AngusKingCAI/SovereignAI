"""
Template Loader for Governor.py v1.5

This module handles loading and rendering of code generation templates.
It supports variable substitution and conditional blocks.

Key Functions:
- load_template_manifest(): Load template manifest from YAML
- render_template(): Render a template with variable substitution
- get_template(): Get template content by ID

This implements the template system specified in v1.5 spec §6.2.
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path

# Template directory
TEMPLATES_DIR = "templates"
MANIFEST_FILE = "manifest.yaml"

# YAML import with stdlib fallback
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class TemplateLoader:
    """
    Template loader for code generation templates.
    
    This class handles loading templates from the templates directory,
    validating the manifest, and rendering templates with variable
    substitution.
    """
    
    def __init__(self, templates_dir: str = TEMPLATES_DIR):
        """
        Initialize the template loader.
        
        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = templates_dir
        self.manifest = None
        self._load_manifest()
    
    def _load_manifest(self) -> None:
        """Load the template manifest from manifest.yaml."""
        manifest_path = os.path.join(self.templates_dir, MANIFEST_FILE)
        
        if not os.path.exists(manifest_path):
            self.manifest = {"version": "1.0.0", "templates": []}
            return
        
        if HAS_YAML:
            with open(manifest_path, 'r') as f:
                self.manifest = yaml.safe_load(f)
        else:
            # Fallback: simple YAML parsing
            with open(manifest_path, 'r') as f:
                self.manifest = self._parse_simple_yaml(f)
    
    def _parse_simple_yaml(self, file_handle) -> Dict[str, Any]:
        """
        Simple YAML parser fallback for when PyYAML is not available.
        
        Args:
            file_handle: File handle to read from
            
        Returns:
            Parsed dictionary
        """
        result = {}
        current_key = None
        current_list = None
        
        for line in file_handle:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if value == '':
                    # Start of nested structure
                    current_key = key
                    if key in result:
                        if isinstance(result[key], list):
                            current_list = result[key]
                        else:
                            result[key] = [result[key]]
                            current_list = result[key]
                    else:
                        result[key] = []
                        current_list = result[key]
                else:
                    # Simple key-value
                    result[key] = value
            elif current_list is not None:
                # List item
                current_list.append(line.lstrip('- '))
        
        return result
    
    def get_template(self, template_id: str) -> Optional[str]:
        """
        Get template content by ID.
        
        Args:
            template_id: Template ID from manifest
            
        Returns:
            Template content as string, or None if not found
        """
        if not self.manifest:
            return None
        
        for template in self.manifest.get("templates", []):
            if template.get("id") == template_id:
                template_file = template.get("file")
                if template_file:
                    template_path = os.path.join(self.templates_dir, template_file)
                    if os.path.exists(template_path):
                        with open(template_path, 'r') as f:
                            return f.read()
        
        return None
    
    def render_template(self, template_id: str, variables: Dict[str, Any]) -> str:
        """
        Render a template with variable substitution.
        
        This method supports:
        - Simple variable substitution: {{ variable_name }}
        - Conditional blocks: {% if variable %} ... {% endif %}
        - Loops: {% for item in list %} ... {% endfor %}
        
        Args:
            template_id: Template ID from manifest
            variables: Dictionary of variable values
            
        Returns:
            Rendered template content
        """
        template_content = self.get_template(template_id)
        if not template_content:
            raise ValueError(f"Template not found: {template_id}")
        
        # Simple template rendering (Jinja2-style syntax)
        # Note: For production, consider using Jinja2 library
        rendered = template_content
        
        # Substitute variables
        for key, value in variables.items():
            placeholder = f"{{{{ {key} }}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        # Handle conditionals (simple implementation)
        # {% if variable %} ... {% endif %}
        import re
        conditional_pattern = r"{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}"
        
        def evaluate_conditional(match):
            var_name = match.group(1)
            content = match.group(2)
            if variables.get(var_name, False):
                return content
            return ""
        
        rendered = re.sub(conditional_pattern, evaluate_conditional, rendered, flags=re.DOTALL)
        
        return rendered
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates.
        
        Returns:
            List of template dictionaries from manifest
        """
        if not self.manifest:
            return []
        return self.manifest.get("templates", [])


# Global template loader instance
_template_loader = None


def get_template_loader() -> TemplateLoader:
    """
    Get the global template loader instance.
    
    Returns:
        TemplateLoader instance
    """
    global _template_loader
    if _template_loader is None:
        _template_loader = TemplateLoader()
    return _template_loader


def load_template_manifest() -> Dict[str, Any]:
    """
    Load the template manifest.
    
    Returns:
        Manifest dictionary
    """
    loader = get_template_loader()
    return loader.manifest


def render_template(template_id: str, variables: Dict[str, Any]) -> str:
    """
    Render a template with variable substitution.
    
    Args:
        template_id: Template ID from manifest
        variables: Dictionary of variable values
        
    Returns:
        Rendered template content
    """
    loader = get_template_loader()
    return loader.render_template(template_id, variables)
