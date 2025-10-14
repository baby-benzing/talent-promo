# Temporal Workflows

This directory contains Temporal workflow definitions for the Talent Promo application.

## Setup

Install dependencies:

```bash
cd apps/api
pip install -r requirements.txt
```

## Development

Start Temporal dev server (temporalite):

```bash
temporal server start-dev
```

Run workers:

```bash
cd apps/api
python -m temporal.worker
```
