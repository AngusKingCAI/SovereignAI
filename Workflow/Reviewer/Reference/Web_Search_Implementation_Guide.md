---
id: wf-rev-ref-web-search-guide
status: active
owner: reviewer-agent
updated: 2026-07-28
purpose: Practical implementation instructions for using robust web search infrastructure to prevent BP search failures
---

# Web Search Implementation Guide for Reviewer Agent

## Purpose
This guide provides practical implementation instructions for using the robust web search infrastructure to prevent BP (Best Practice) search failures during the Reviewer BP App Scanner Workflow.

## Infrastructure Components

### 1. Efficient Report Writer
**Location**: `Scripts/Infrastructure/efficient_report_writer.py`

**Usage**: Replace slow `edit` tool operations with efficient append operations.

**Benefits**:
- 10x faster file writing for large reports
- No need to read entire file for each update
- Eliminates edit tool validation overhead

**Implementation**:
```python
# Instead of using edit tool for each file:
from Scripts.Infrastructure.efficient_report_writer import create_writer

# Initialize writer at workflow start
writer = create_writer("Logs/Reviewer/BP/App", "SCAN-REPORT")

# For each file analysis:
analysis = {
    'type': 'Python file',
    'complexity': 'Medium',
    'compliance_status': 'PASS',
    'scan_results': '...',
    'best_practices_research': '...',
    'modularity_violations': '...',
    'best_practices_issues': '...',
    'specific_changes_needed': '...',
    'severity': 'LOW',
    'actionable_recommendations': '...'
}
writer.append_file_analysis(file_number, file_path, analysis)
```

### 2. Robust Web Search
**Location**: `Scripts/Infrastructure/robust_web_search.py`

**Usage**: Implement caching and rate limiting for web search operations.

**Benefits**:
- Automatic caching reduces redundant searches
- Rate limiting prevents search engine blocking
- Fallback mechanisms for reliability
- Statistics tracking for monitoring

**Implementation**:
```python
from Scripts.Infrastructure.robust_web_search import create_robust_search

# Initialize at workflow start
search = create_robust_search("Logs/Reviewer/Cache/WebSearch")

# For each file BP search:
result = search.search(query)
if result['source'] == 'cache':
    # Use cached results
    best_practices_info = result['results']
else:
    # New search performed
    best_practices_info = result['results']
```

### 3. Web Search Diagnostic
**Location**: `Scripts/Infrastructure/test_web_search.py`

**Usage**: Pre-flight check to verify web search functionality.

**Implementation**:
```bash
# Run before starting workflow
python Scripts/Infrastructure/test_web_search.py
```

## Integration with Reviewer BP App Scanner Workflow

### Phase 4 Enhancement

**Before Current Step 32**: Add infrastructure setup

```
- 32. **INFRASTRUCTURE SETUP**: 
  - Initialize efficient report writer using Scripts/Infrastructure/efficient_report_writer.py
  - Initialize robust web search using Scripts/Infrastructure/robust_web_search.py
  - Create cache directory at Logs/Reviewer/Cache/WebSearch
  - Run diagnostic check using Scripts/Infrastructure/test_web_search.py
```

**Replace Current Documentation Step**:

```
- 37. Document specific changes needed using efficient report writer:
  - Use writer.append_file_analysis() instead of edit tool
  - Include web search source (cache vs live) in documentation
  - Track cache statistics for performance monitoring
  - Write to SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md (not incremental-SCAN-REPORT)
```

**Enhanced Web Search Step**:

```
- 30. **CRITICAL REQUIREMENT**: For each file, perform **{BP}** web search with robust infrastructure:
  - Use robust_web_search.py for caching and rate limiting
  - Implement 2-second delay between searches (automatic via rate limiter)
  - Log cache hit/miss statistics for monitoring
  - Fallback to cached results if live search fails
```

## Rate Limiting Strategy

### Recommended Delays
- **Between same-type searches**: 2 seconds (automatic via rate limiter)
- **Between different search providers**: 1 second
- **After cache miss**: 2 seconds
- **After cache hit**: 0 seconds (immediate)

### Search Query Optimization
- Group similar searches to use cached results
- Use specific, targeted queries rather than broad ones
- Cache common best practice queries (e.g., "Python __init__.py best practices")

## Cache Management

### Cache Duration
- **Default**: 24 hours
- **Best Practices Queries**: 7 days (changes slowly)
- **Technology-Specific Queries**: 24 hours (changes frequently)

### Cache Location
- **Directory**: `Logs/Reviewer/Cache/WebSearch`
- **File Format**: JSON files with MD5 hash keys
- **Automatic Cleanup**: Expired files removed on access

## Monitoring and Statistics

### Key Metrics to Track
- Total searches performed
- Cache hit rate
- Average search time
- Failed searches count

### Progress Reporting
Include in **PRINT** commands:
```
"File [N]/[TOTAL]: [file_path] - BP search: [cache/live] - Cache hit rate: [X]%"
```

## Troubleshooting

### Web Search Failures
1. **Check network connectivity**
2. **Verify cache directory permissions**
3. **Review rate limiting settings**
4. **Test with diagnostic tool**

### Cache Issues
1. **Clear cache directory** if corrupted
2. **Check disk space** for cache storage
3. **Verify JSON encoding** of cache files

### Performance Issues
1. **Monitor cache hit rate** - should be >30%
2. **Check rate limiting delays** - adjust if too slow
3. **Review file writing performance** - use efficient writer

## Implementation Checklist

- [ ] Run web search diagnostic before workflow
- [ ] Initialize efficient report writer
- [ ] Initialize robust web search with caching
- [ ] Create cache directory structure
- [ ] Implement rate limiting (2-second delays)
- [ ] Add progress reporting with cache statistics
- [ ] Test with small batch of files (5-10)
- [ ] Monitor cache hit rate during execution
- [ ] Verify all files receive BP search
- [ ] Validate report generation

## Example Workflow Integration

```python
# Phase 4 Setup
from Scripts.Infrastructure.efficient_report_writer import create_writer
from Scripts.Infrastructure.robust_web_search import create_robust_search

writer = create_writer("Logs/Reviewer/BP/App", "SCAN-REPORT")
search = create_robust_search("Logs/Reviewer/Cache/WebSearch")

# For each file
for file_number, file_path in enumerate(files, 1):
    # SCAN file
    scan_results = scan_file(file_path)
    
    # BP Search with robust infrastructure
    bp_result = search.search(f"{file_type} best practices 2024")
    bp_info = bp_result['results']
    
    # Document with efficient writer
    analysis = {
        'type': file_type,
        'complexity': complexity,
        'compliance_status': status,
        'scan_results': scan_results,
        'best_practices_research': f"Source: {bp_result['source']}",
        'modularity_violations': violations,
        'best_practices_issues': issues,
        'specific_changes_needed': changes,
        'severity': severity,
        'actionable_recommendations': recommendations
    }
    writer.append_file_analysis(file_number, file_path, analysis)
    
    # Progress report
    cache_stats = search.get_stats()
    print(f"File {file_number}/{len(files)}: {file_path}")
    print(f"BP Search: {bp_result['source']} - Cache hit rate: {cache_stats['cache_hit_rate']}")
```

## Success Criteria

- Web search failure rate < 5%
- Cache hit rate > 30%
- Report writing time reduced by 50%
- All 140 files receive BP search
- No workflow stops due to web search issues
- User visibility maintained throughout process