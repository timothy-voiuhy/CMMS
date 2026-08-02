# Deprecated Code

This directory contains deprecated code from the old CMMS implementation:

- **Desktop/** - Old PyQt/PySide desktop application code
- **CMMSPortals/** - Old Django-based backend implementation

This code is kept for reference only and should not be used in the new ICMS system.

## Migration Notes

Useful code has been migrated to:
- Business logic → `Backend/services/`
- Database models → `Backend/models/`
- Utilities → `Backend/utils/` and `Shared/utils/`
- Configuration → `Shared/config/`
