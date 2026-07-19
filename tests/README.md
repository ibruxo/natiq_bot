# Tests

This directory contains automated tests for the bot.

## Current coverage

- provider navigation behavior
- random ayah formatting
- rate limiting behavior

## Run tests

```bash
pytest -q
```

## Notes

- Keep tests deterministic and small.
- Prefer fixture-like local data over network access.
- Add tests for any user-visible behavior or bug fix.
