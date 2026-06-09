# Changelog

## [0.4.0] - 2026-06-10

### ✨ New Features
- Added comprehensive unit tests for API client, coordinator, and sensors
- Added GitHub Actions workflows for CI/CD (test, lint, release)

### 🔧 Improvements
- **API Client**: Enhanced error handling with timeouts and connection error catching
- **Coordinator**: Optimized cache management (purge once per day instead of every 15 minutes)
- **Sensors**: Proper internationalization using `translation_key` instead of hardcoded names
- **Documentation**: Enhanced README with badges, detailed features, advanced automation examples, and troubleshooting guide
- **Manifest**: Added metadata for better HACS integration (country, integration_type, data)

### 📝 Documentation
- Added CONTRIBUTING.md with development guidelines
- Added comprehensive README with:
  - Installation instructions (HACS and manual)
  - Complete entity reference table
  - Multiple automation examples
  - Troubleshooting section
  - Data privacy statement
- Added development requirements file

### 🐛 Bug Fixes
- Fixed import issues in config_flow.py
- Removed unused code and imports
- Fixed line length and style issues

### 📊 Code Quality
- 100% flake8 compliance
- Type hints added where missing
- Constants defined for API response keys
- Better exception handling throughout

## [0.3.0] - 2026-05-17

### Changed
- Renamed device with "Sobry" prefix (see [#2](https://github.com/pierrepinon/sobry-hacs/issues/2))

## [0.2.0] - 2026-05-16

### Added
- Initial release of Sobry Home Assistant integration
- Support for current price sensor with 15-minute slots
- Multi-contract support
- Automatic pre-fetch of next-day prices at 14:00
- OTP-based authentication flow
