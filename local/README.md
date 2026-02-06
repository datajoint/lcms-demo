# Local Development Setup

Run a local MySQL database for development and testing.

## Quick Start

```bash
# Start the database
docker compose up -d

# Check status
docker compose ps

# Stop the database
docker compose down

# Stop and remove data
docker compose down -v
```

## Default Credentials

- **Host**: localhost
- **Port**: 3306
- **User**: datajoint
- **Password**: datajoint

## Using with lcms-demo

```python
from lcms_demo.config import use_local_database
use_local_database()

from lcms_demo import subject, session, scan
```
