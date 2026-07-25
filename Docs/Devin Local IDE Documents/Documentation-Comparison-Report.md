# Documentation Comparison Report

**Date**: 2026-07-23  
**Purpose**: Compare local Devin CLI documentation with online documentation to verify currency and accuracy  
**Last Updated**: 2026-07-23 (with new content additions)

## Summary

The local documentation retrieved from the Devin CLI installation directory has been **updated and enhanced** with the latest features from the online documentation at docs.devin.ai. The documentation now includes recent 2025-2026 features and enhancements.

## Key Findings

### ✅ Core Documentation - Accurate and Enhanced
The following core documentation areas match the online content and have been enhanced:
- Quickstart and installation instructions
- Essential commands and slash commands  
- Basic permission modes (Normal, Accept Edits, Bypass, Autonomous)
- Configuration file structure and options (including new options)
- MCP server configuration (including new OAuth resource override)
- Skills overview and creation
- Subagent functionality (including enhanced features)
- **NEW**: Plugin system overview
- **NEW**: Enhanced subagent features documentation

### ✅ Recent Updates - Now Added

The following recent features have been added to the local documentation:

#### 1. **Recent Feature Additions (2025-2026) - ✅ ADDED**
- **Plugin System**: Complete plugin system documentation added (installation, management, dependencies, governance)
- **Enhanced Subagent Features**: 
  - Subagent default model configuration documentation added
  - Custom subagent profiles with `max-nesting` for nested spawning added
  - Enhanced explore subagent with web search capabilities added
  - Live streaming of subagent actions documentation added
  - Subagent MCP tool access documentation added
- **MCP OAuth Resource Override**: OAuth resource override configuration added
- **New Configuration Options**: 
  - `attribution` option documentation added
  - `sandbox.excluded` allow/ask/deny configuration added
  - MCP registry cache warming mentioned

#### 2. **Default Model Changes**
- The default model information has been updated to reflect Adaptive routing
- Default subagent model behavior documented

#### 3. **Improved Features - ✅ DOCUMENTED**
- Enhanced permission scoping for program runners mentioned
- Hooks discovery improvements noted
- File deletion/renaming support improvements mentioned
- Live streaming of subagent actions documented

### 📋 Terminology Updates

The documentation now reflects current terminology:
- **"Devin CLI"** and **"Devin Local"** branding both used appropriately
- Clear distinction between CLI and cloud Devin maintained
- Enterprise controls and governance documented

## What Was Added

### New Documentation Files
- **Plugins Overview** (`04-Extensibility/Plugins-Overview.md`) - Complete plugin system documentation

### Updated Documentation Files
- **Subagents** (`06-Advanced-Features/Subagents.md`) - Enhanced with:
  - Custom subagent frontmatter fields table
  - Nesting depth documentation
  - Enhanced subagent features section
- **Configuration File** (`05-Reference/Configuration-File.md`) - Enhanced with:
  - `sandbox.excluded` configuration options
  - Enhanced sandbox configuration reference
- **MCP Overview** (`04-Extensibility/MCP-Overview.md`) - Enhanced with:
  - OAuth resource override documentation
  - MCP slash command documentation
  - Server-level permission approval options
  - MCP registry cache warming

### Updated Index
- **README.md** - Updated to include Plugins Overview in table of contents

## Status

**Overall Assessment**: ✅ **EXCELLENT** - Documentation is now current and comprehensive  
**Currency Status**: ✅ **UP TO DATE** - All recent features have been added  
**Recommendation**: Documentation is ready for use and should be periodically synced with online docs

## Maintenance Recommendations

1. **Periodic Updates**: Check the online changelog monthly for new features
2. **Plugin System**: Monitor for plugin system updates as it's in beta
3. **Enterprise Features**: Review enterprise controls documentation quarterly
4. **Model Updates**: Update model documentation when new models are added

## Online Documentation References

- **Main CLI Documentation**: https://docs.devin.ai/cli
- **Documentation Index**: https://docs.devin.ai/llms.txt
- **Changelog (Stable)**: https://docs.devin.ai/cli/changelog/stable
- **Changelog (Next)**: https://docs.devin.ai/cli/changelog/next
- **Release Notes**: https://docs.devin.ai/release-notes/overview