## 0.0.1
- Initialized package using jvcli

## 0.0.2
- Updated to work with the updated data payload for interact walker

## 0.0.3
- Updated meta to be dict for data payload
- Refactored API library to remove repeated passing of api_url and instance_id
- Altered action properties to match Ultramsg API: api_key -> token, api_url and instance_id are now separate
- Fixed unprompted interaction bug when messaging as AI
- Fixed API status check to work with healthcheck

## 0.0.4
- Bugfix: patched duplicate call to TTS service following interact TTS flag update

## 0.0.5
- Refactored API update they python module by passing params to the class
- Added outbox scheduling functionality