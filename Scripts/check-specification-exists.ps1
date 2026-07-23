# Hook script to check if specification exists and is accepted before allowing write/edit operations
# Exit code 2 blocks the operation
# Exit code 0 allows the operation

# Read JSON input from stdin
$inputJson = $Input | Out-String
if ([string]::IsNullOrEmpty($inputJson)) {
    # If no input, allow (for testing)
    exit 0
}

# Parse JSON
try {
    $data = $inputJson | ConvertFrom-Json
} catch {
    # If JSON parsing fails, allow (for testing)
    exit 0
}

# Get current phase from FOUNDING_ARCHITECTURE.md or default to Phase 0
$foundingArchPath = Join-Path $env:DEVIN_PROJECT_DIR "FOUNDING_ARCHITECTURE.md"
if (Test-Path $foundingArchPath) {
    $foundingArch = Get-Content $foundingArchPath -Raw
    $phaseMatch = [regex]::Match($foundingArch, "Current Phase: Phase (\d+)")
    $currentPhase = if ($phaseMatch.Success) { $phaseMatch.Groups[1].Value } else { "0" }
} else {
    $currentPhase = "0"
}

# Check if any specification exists for current phase
$specsDir = Join-Path $env:DEVIN_PROJECT_DIR "docs\specs"
$specFiles = Get-ChildItem $specsDir -Filter "phase-${currentPhase}-*.md" -ErrorAction SilentlyContinue

if (-not $specFiles) {
  Write-Output "No specification found for Phase ${currentPhase}. Write operations blocked."
  Write-Output "Create a specification in docs/specs/ before implementing."
  exit 2
}

# Check if any specification is accepted (not proposed)
$acceptedFound = $false
foreach ($specFile in $specFiles) {
  $content = Get-Content $specFile.FullName -Raw
  if ($content -match "(?i)status.*accepted") {
    $acceptedFound = $true
    break
  }
}

if (-not $acceptedFound) {
  Write-Output "Specification for Phase ${currentPhase} is still proposed. Write operations blocked."
  Write-Output "Get specification reviewed and accepted (change status to 'accepted') before implementing."
  exit 2
}

# Specification exists and is accepted
exit 0