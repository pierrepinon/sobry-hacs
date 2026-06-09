# Changelog

## [Unreleased]

### Added
- Added constants for API response keys (`KEY_COLOR`, `KEY_COLOR_LABEL`, `KEY_PRICE`, `KEY_TIME`) in `const.py`
- Added timeout configuration (`API_TIMEOUT = 30s`) for all API requests

### Changed
- **API Client**: Improved error handling in `api.py`:
  - Added `aiohttp.ClientTimeout` to all requests
  - Wrapped all API calls in try/except blocks to catch `aiohttp.ClientError`
  - More descriptive error messages for connection issues
- **Coordinator**: Optimized cache management in `coordinator.py`:
  - Cache purge now happens once per day instead of every 15 minutes
  - Simplified docstrings and comments
  - Removed redundant comments explaining implementation details
- **Sensors**: Refactored `sensor.py`:
  - Replaced hardcoded sensor names with `translation_key` for proper i18n support
  - Set `_attr_has_entity_name = True` to use translation system
  - Removed unused `_next_24h_slots()` method and `prices` attribute
  - Used constants from `const.py` for API response keys
- **Config Flow**: Improved error handling in `config_flow.py`:
  - More specific error messages based on exception type
  - Better distinction between connection errors and authentication errors

### Removed
- Removed unused import `aiohttp` from `config_flow.py`
- Removed redundant docstring in `SobryContractCoordinator`
- Removed `prices` attribute from `SobryCurrentPriceSensor.extra_state_attributes`

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
