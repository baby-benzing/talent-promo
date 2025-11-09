# Guidelines for AI Agents Working on This Project

## Documentation Guidelines

### DO NOT Create Excessive Documentation Files
- ❌ **DO NOT** create multiple documentation files (README_ISSUE.md, IMPLEMENTATION_ISSUE.md, QUICKSTART_ISSUE.md, etc.)
- ❌ **DO NOT** create CHANGELOG files for minor updates
- ❌ **DO NOT** create tutorial or guide files unless explicitly requested
- ✅ **DO** update existing README.md if documentation is needed
- ✅ **DO** add docstrings and comments in code
- ✅ **DO** create brief inline documentation only when necessary

### Documentation Priority
1. **Code comments** - Primary documentation lives in the code
2. **Docstrings** - For functions, classes, and modules
3. **Existing README** - Update if necessary
4. **New .md files** - Only if explicitly requested by user

## Development Rules

### Code Over Documentation
- Write clean, self-documenting code
- Let the code speak for itself
- Add comments only where logic is complex or non-obvious

### Minimalist Approach
- One README per major component (if needed)
- No duplicate documentation
- No "getting started" guides unless requested
- No implementation logs or changelogs for features

## Issue Implementation

When implementing an issue:
1. ✅ Write the code
2. ✅ Write tests
3. ✅ Update existing docs if they exist
4. ❌ Do NOT create multiple new documentation files
5. ❌ Do NOT write extensive tutorials

## Testing
- Manual test scripts are OK for quick validation
- Automated tests are required
- No test documentation files needed

---

**Summary**: Code and tests first. Documentation only when explicitly needed or requested.

