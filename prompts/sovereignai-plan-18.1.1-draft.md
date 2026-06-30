# Plan 18.1.1 — Fix Options Tab Click Handler

## Description
Hotfix to fix Options panel tab navigation. The first tab button had duplicate `class` attributes which prevented click handlers from working.

## Changes
- Fixed `web/templates/index.html` line 116: combined duplicate `class="options-tab" class="active"` into single `class="options-tab active"`

## Testing
- Manual verification that tabs are clickable in browser
