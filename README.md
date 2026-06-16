# Firmware Analyzer

Small Flask application for scanning firmware archives for authentication tokens that match the pattern `<Tkn###AAAAATkn>`. The app supports both synchronous analysis and an asynchronous job-based flow with polling.

## What It Does

- uploads a firmware archive through the HTTP API
- extracts nested ZIP/TAR archives into a job-specific temporary folder
- scans all extracted files for token matches
- writes the per-file report to `output.csv`
- returns aggregate token counts as JSON through polling

## Requirements

- Python 3.11+
- pip

## Install

```bash
pip install -r requirements.txt
```

## Run

Start the application from the project root:

```bash
python run.py
```

By default, the app listens on `http://0.0.0.0:8080`.

You can override the port with the `PORT` environment variable:

```bash
set PORT=5000
python run.py
```

## Run With Docker

Build the image from the project root:

```bash
docker build -t firmware-analyzer .
```

Run the container and publish port `8080`:

```bash
docker run --rm -p 8080:8080 firmware-analyzer
```

The container uses the same `python run.py` startup command defined in the Dockerfile.

## API

- `GET /health` - health check
- `POST /analyse` - submit a firmware archive for analysis
- `GET /analyse/<job_id>` - poll job status and results

## Tests

Run the test suite with:

```bash
python -m pytest -q
```

## Notes

- Uploaded files and extracted content are stored under `temp_firmware/<job_id>/`
- The retained report for each job is `output.csv`
- Job state is kept in memory, so it is lost if the process restarts