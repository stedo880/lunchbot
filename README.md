# lunchbot ![test](https://github.com/vikpe/lunchbot/workflows/test/badge.svg?branch=master)
> A Discord bot for coordinating lunches

## Configuration

**Environment variables**
* `ANNOUNCEMENT`: `1` (enable) or `0` (disable) automatic posting of lunch message. Defaults to `0`.
* `LUNCHBOT_TOKEN`: Bot token (found in Discord developer settings)

**config.json**

Various configuration options.
 
## Development

### Setup

**1. Clone repo**
```bash
git clone https://github.com/stedo880/lunchbot.git
cd lunchbot
```

**2. Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
python -m pip install -r requirements.txt -r requirements_dev.txt 
```

### Run tests
```bash
python -m pytest tests.py --cov --disable-warnings
```

### Code formatting (black)
```bash
black .
```
