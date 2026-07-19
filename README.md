# Project Name

A Telegram bot that engages users with daily Quranic content and other Islamic topics.

---

## Project Charter

Project Charter is available in [`bot.md`](bot.md).

---

## Installation & Running

### With Docker (recommended)

```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
cp .env.example .env
# edit .env with your settings
docker compose up -d --build
```

The bot service will start inside Docker Compose using your configured environment.

### Other methods

You can also run the project without Docker by creating a virtual environment, installing the project and development dependencies, and then starting the bot manually.

### Development

For faster local development without Docker:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements-dev.txt
uv pip install -e .
python -m app
```

### Testing

Execute the test suite with:

```bash
pytest -q
```
