# Version 1.0.3

Maintenance and CI/CD stability release.

## Key Changes
- **CI/CD Stabilization**: Updated GitHub Actions CI workflow to include system dependencies (`libcairo2-dev`, `pkg-config`, etc.) required for PDF generation.
- **Forensic Integrity Checks**: Implemented stricter validation in the PDF export pipeline to prevent corrupted or empty reports (now requires a non-empty Forensic Evidence Log).
- **Test Suite Updates**: Refactored the test suite to align with the new Forensic Artifact structure.
- **Version Synchronization**: Unified versioning across package entry points, CLI, and build scripts.
