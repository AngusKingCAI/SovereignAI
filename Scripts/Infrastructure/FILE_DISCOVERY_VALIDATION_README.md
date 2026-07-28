# File Discovery Validation Infrastructure

## Purpose
Pre-flight validation script to ensure comprehensive directory coverage before code scanning workflows. Prevents governance failures where scanners miss entire directories.

## Problem Solved
The initial App/ directory scan claimed 186 files (100% complete) but missed 37 files across 5 key directories (cli/, phone/, tui/, txt/, web/). This infrastructure prevents such governance failures.

## BP Research
Based on 2026 code scanner file discovery validation best practices:
- Establish baseline of expected directory structure
- Cross-check discovered files against expected structure  
- Fail-fast if directory structure doesn't match expected baseline
- Use automated validation as pre-flight check before scanning

## Usage

### Create Baseline (First Time)
```bash
python Scripts/Infrastructure/file_discovery_validation.py C:/SovereignAI/App --create-baseline Scripts/Infrastructure/app_directory_baseline.json
```

### Validate Against Baseline (Pre-Flight Check)
```bash
python Scripts/Infrastructure/file_discovery_validation.py C:/SovereignAI/App --baseline Scripts/Infrastructure/app_directory_baseline.json
```

### Validate Specific Directories
```bash
python Scripts/Infrastructure/file_discovery_validation.py C:/SovereignAI/App --expected-dirs "C:/SovereignAI/App/cli,C:/SovereignAI/App/phone,C:/SovereignAI/App/tui,C:/SovereignAI/App/txt,C:/SovereignAI/App/web"
```

## Integration with Reviewer Workflow

### Before Running Best Practice Scanner
1. Run validation script as pre-flight check
2. If validation fails, scanner workflow should not proceed
3. If validation passes, scanner can proceed with confidence

### Example Integration
```bash
# Pre-flight validation
python Scripts/Infrastructure/file_discovery_validation.py C:/SovereignAI/App --baseline Scripts/Infrastructure/app_directory_baseline.json

# Only proceed if validation passes (exit code 0)
if [ $? -eq 0 ]; then
    # Run scanner workflow
    echo "Validation passed - proceeding with scan"
fi
```

## Baseline Management

### Update Baseline When Directory Structure Changes
If new directories are added to App/, update the baseline:
```bash
python Scripts/Infrastructure/file_discovery_validation.py C:/SovereignAI/App --create-baseline Scripts/Infrastructure/app_directory_baseline.json
```

### Current Baseline Status
- **Total Directories**: 53
- **Total Files**: 209
- **Missing Directories**: 0
- **Validation Status**: PASSED

## Cross-Platform Compatibility
- Uses Python pathlib for cross-platform path handling
- Normalizes paths for consistent comparison across Windows/Linux/Mac
- Handles different path separators and case sensitivity

## Exit Codes
- **0**: Validation passed - directory structure is complete
- **1**: Validation failed - missing directories detected or discovery error

## Output Format
The script generates a human-readable report showing:
- Target directory
- Total files discovered
- Expected vs discovered directories
- Missing directories (if any)
- Validation status
- Detailed error messages (if any)

## Infrastructure Location
- **Script**: `Scripts/Infrastructure/file_discovery_validation.py`
- **Baseline**: `Scripts/Infrastructure/app_directory_baseline.json`
- **Documentation**: `Scripts/Infrastructure/FILE_DISCOVERY_VALIDATION_README.md`

## Maintenance
This infrastructure should be updated when:
- New directories are added to App/
- Directory structure changes significantly
- Baseline validation thresholds need adjustment
- Cross-platform compatibility issues arise