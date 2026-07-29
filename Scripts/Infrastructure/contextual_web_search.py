#!/usr/bin/env python3
"""
Contextual Web Search for Best Practice Analysis

Performs intelligent web searches based on document type, content, and governance context.
This function reasons about what type of best practice search should be done for each document.

BP Research: 2026 contextual best practice search for governance compliance
- Analyze document type and content
- Determine relevant best practice categories
- Generate specific search queries
- Cache results for efficiency
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class ContextualWebSearch:
    """Intelligent web search for best practice analysis based on document context."""

    def __init__(self, cache_dir: str = None):
        """
        Initialize contextual web search with caching.

        Args:
            cache_dir: Directory for caching search results
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".web_search_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Best practice search patterns by document type
        self.search_patterns = {
            "configuration": {
                "json": [
                    "JSON configuration file best practices",
                    "JSON schema validation patterns",
                    "JSON security best practices",
                    "Configuration management best practices"
                ],
                "yaml": [
                    "YAML configuration file best practices",
                    "YAML schema validation patterns",
                    "YAML security best practices",
                    "Configuration management YAML patterns"
                ],
                "toml": [
                    "TOML configuration file best practices",
                    "TOML configuration patterns",
                    "Configuration file formats comparison"
                ]
            },
            "governance": {
                "rules": [
                    "Governance rules best practices",
                    "Rule enforcement patterns",
                    "Compliance rule design patterns",
                    "Governance rule documentation standards"
                ],
                "workflow": [
                    "Workflow design best practices",
                    "Workflow documentation standards",
                    "Process governance patterns",
                    "Workflow validation patterns"
                ],
                "agent": [
                    "AI agent governance best practices",
                    "Multi-agent coordination patterns",
                    "Agent role definition standards",
                    "Agent governance frameworks"
                ]
            },
            "documentation": {
                "markdown": [
                    "Markdown documentation best practices",
                    "Technical documentation standards",
                    "Documentation governance patterns",
                    "Markdown formatting guidelines"
                ],
                "readme": [
                    "README best practices",
                    "Project documentation standards",
                    "Documentation structure patterns",
                    "Getting started documentation guidelines"
                ],
                "reference": [
                    "Reference documentation best practices",
                    "Technical reference standards",
                    "API documentation patterns",
                    "Reference documentation organization"
                ]
            },
            "code": {
                "python": [
                    "Python best practices",
                    "Python code style standards",
                    "Python security best practices",
                    "Python testing patterns"
                ],
                "scripts": [
                    "Script design best practices",
                    "Automation script patterns",
                    "Script error handling patterns",
                    "Script documentation standards"
                ]
            },
            "infrastructure": {
                "hooks": [
                    "Git hooks best practices",
                    "Event-driven hooks patterns",
                    "Hook configuration standards",
                    "Automated hook patterns"
                ],
                "skills": [
                    "AI skill definition best practices",
                    "Skill documentation standards",
                    "Skill implementation patterns",
                    "Skill governance frameworks"
                ],
                "schema": [
                    "JSON schema best practices",
                    "Schema validation patterns",
                    "Schema documentation standards",
                    "Schema governance patterns"
                ]
            }
        }

    def _analyze_document_context(self, file_path: str, file_content: str = None) -> Dict:
        """
        Analyze document to determine context for best practice search.

        Args:
            file_path: Path to the document
            file_content: Optional file content for deeper analysis

        Returns:
            Dictionary with document context information
        """
        path = Path(file_path)
        context = {
            "file_type": "unknown",
            "file_extension": path.suffix.lower(),
            "directory": str(path.parent),
            "filename": path.name,
            "search_categories": [],
            "specific_patterns": []
        }

        # Determine file type based on extension and path
        if path.suffix.lower() in ['.json', '.yaml', '.yml', '.toml']:
            context["file_type"] = "configuration"
            context["search_categories"].append("configuration")
        
        elif path.suffix.lower() == '.md':
            # Determine documentation type from filename and path
            if 'workflow' in str(path).lower():
                context["file_type"] = "governance"
                context["search_categories"].append("governance")
                context["search_categories"].append("workflow")
            elif 'rule' in str(path).lower():
                context["file_type"] = "governance"
                context["search_categories"].append("governance")
                context["search_categories"].append("rules")
            elif 'agent' in str(path).lower():
                context["file_type"] = "governance"
                context["search_categories"].append("governance")
                context["search_categories"].append("agent")
            elif 'reference' in str(path).lower():
                context["file_type"] = "documentation"
                context["search_categories"].append("documentation")
                context["search_categories"].append("reference")
            elif 'readme' in path.name.lower():
                context["file_type"] = "documentation"
                context["search_categories"].append("documentation")
                context["search_categories"].append("readme")
            else:
                context["file_type"] = "documentation"
                context["search_categories"].append("documentation")
                context["search_categories"].append("markdown")
        
        elif path.suffix.lower() == '.py':
            # Determine if it's infrastructure code or application code
            if 'scripts' in str(path).lower():
                context["file_type"] = "infrastructure"
                context["search_categories"].append("infrastructure")
                context["search_categories"].append("scripts")
            else:
                context["file_type"] = "code"
                context["search_categories"].append("code")
                context["search_categories"].append("python")
        
        elif path.suffix.lower() in ['.sh', '.bash']:
            context["file_type"] = "infrastructure"
            context["search_categories"].append("infrastructure")
            context["search_categories"].append("scripts")
        
        # Analyze specific patterns from filename
        if 'hook' in path.name.lower():
            context["search_categories"].append("infrastructure")
            context["search_categories"].append("hooks")
        
        elif 'skill' in path.name.lower():
            context["search_categories"].append("infrastructure")
            context["search_categories"].append("skills")
        
        elif 'schema' in path.name.lower():
            context["search_categories"].append("infrastructure")
            context["search_categories"].append("schema")
        
        elif 'config' in path.name.lower():
            context["search_categories"].append("configuration")

        # Generate specific search patterns based on context
        for category in context["search_categories"]:
            if category in self.search_patterns:
                ext = context["file_extension"] if context["file_extension"] else "default"
                if ext in self.search_patterns[category]:
                    context["specific_patterns"].extend(self.search_patterns[category][ext])
                elif "default" in self.search_patterns[category]:
                    context["specific_patterns"].extend(self.search_patterns[category]["default"])
                else:
                    # Use first available pattern
                    if self.search_patterns[category]:
                        first_key = list(self.search_patterns[category].keys())[0]
                        context["specific_patterns"].extend(self.search_patterns[category][first_key])

        return context

    def _generate_search_queries(self, context: Dict) -> List[str]:
        """
        Generate specific search queries based on document context.

        Args:
            context: Document context from analyze_document_context

        Returns:
            List of specific search queries
        """
        queries = []
        
        # Add context-specific patterns
        if context["specific_patterns"]:
            queries.extend(context["specific_patterns"])
        
        # Add generic patterns for file type
        file_type = context["file_type"]
        if file_type in self.search_patterns:
            for pattern_list in self.search_patterns[file_type].values():
                queries.extend(pattern_list)
        
        # Add filename-specific searches
        filename = context["filename"]
        if filename.lower().endswith('.md'):
            queries.append(f"{filename.replace('.md', '')} documentation best practices")
            queries.append(f"{filename.replace('.md', '')} governance patterns")
        
        elif filename.lower().endswith('.json'):
            queries.append(f"{filename.replace('.json', '')} JSON configuration best practices")
            queries.append(f"{filename.replace('.json', '')} configuration validation patterns")
        
        # Remove duplicates and limit to reasonable number
        unique_queries = list(dict.fromkeys(queries))  # Preserve order while removing duplicates
        return unique_queries[:10]  # Limit to 10 most relevant queries

    def _cache_key(self, query: str) -> str:
        """Generate cache key for a search query."""
        return hashlib.md5(query.encode()).hexdigest()

    def _get_cached_result(self, query: str) -> Optional[Dict]:
        """Get cached search result if available."""
        cache_file = self.cache_dir / f"{self._cache_key(query)}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # Check if cache is still valid (7 days)
                    cache_date = datetime.fromisoformat(data["timestamp"])
                    if (datetime.now() - cache_date).days < 7:
                        return data
            except Exception:
                pass
        return None

    def _cache_result(self, query: str, results: List[Dict]):
        """Cache search results."""
        cache_file = self.cache_dir / f"{self._cache_key(query)}.json"
        cache_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

    def generate_search_plan(self, file_path: str, file_content: str = None) -> Dict:
        """
        Generate contextual search plan for a specific document.

        Args:
            file_path: Path to the document
            file_content: Optional file content for deeper analysis

        Returns:
            Dictionary with search plan including context and queries
        """
        # Analyze document context
        context = self._analyze_document_context(file_path, file_content)
        
        # Generate specific search queries
        queries = self._generate_search_queries(context)
        
        # Create search plan
        search_plan = {
            "file_path": file_path,
            "context": context,
            "search_queries": queries,
            "recommended_searches": queries[:5],  # Top 5 recommended
            "cache_dir": str(self.cache_dir),
            "timestamp": datetime.now().isoformat()
        }
        
        return search_plan

    def save_search_plan(self, search_plan: Dict, output_file: str):
        """
        Save search plan to file for reference.

        Args:
            search_plan: Search plan dictionary
            output_file: Path to save search plan
        """
        with open(output_file, 'w') as f:
            json.dump(search_plan, f, indent=2)


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate contextual web search plan for best practice analysis"
    )
    parser.add_argument(
        "file_path",
        help="Path to the document to analyze"
    )
    parser.add_argument(
        "--content",
        help="Optional file content for deeper analysis",
        default=None
    )
    parser.add_argument(
        "--output",
        help="Path to save search plan JSON",
        default=None
    )
    parser.add_argument(
        "--cache-dir",
        help="Directory for caching search results",
        default=None
    )

    args = parser.parse_args()

    # Initialize contextual search
    search = ContextualWebSearch(args.cache_dir)

    # Generate search plan
    file_content = args.content
    if args.content and args.content.endswith('.md'):
        # Read file content if it's a file path
        try:
            with open(args.content, 'r') as f:
                file_content = f.read()
        except Exception:
            pass

    search_plan = search.generate_search_plan(args.file_path, file_content)

    # Print search plan
    print("=" * 60)
    print("CONTEXTUAL WEB SEARCH PLAN")
    print("=" * 60)
    print(f"File: {search_plan['file_path']}")
    print(f"File Type: {search_plan['context']['file_type']}")
    print(f"Categories: {', '.join(search_plan['context']['search_categories'])}")
    print("")
    print("Recommended Search Queries:")
    for i, query in enumerate(search_plan['recommended_searches'], 1):
        print(f"  {i}. {query}")
    print("")
    print("All Search Queries:")
    for i, query in enumerate(search_plan['search_queries'], 1):
        print(f"  {i}. {query}")
    print("=" * 60)

    # Save search plan if requested
    if args.output:
        search.save_search_plan(search_plan, args.output)
        print(f"\nSearch plan saved to: {args.output}")

    sys.exit(0)


if __name__ == "__main__":
    main()