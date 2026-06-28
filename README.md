# Thyroid Cancer Detection App

## Setup

This app is configured for local deployment only, using SQLite by default.

### Local setup (SQLite)

1. Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Run the app:

```powershell
python app.py
```

3. Open the app in your browser:

```text
http://127.0.0.1:5000
```

The default local database is stored in `thyroid_app.db`.

### Optional local MySQL setup

If you want to run the app against a local MySQL instance, set these environment variables before starting the app:

```powershell
$env:MYSQL_HOST = 'localhost'
$env:MYSQL_PORT = '3306'
$env:MYSQL_USER = 'thyroid'
$env:MYSQL_PASSWORD = 'YourThyroidDbPassword'
$env:MYSQL_DB = 'thyroid_db'
$env:SECRET_KEY = 'your_secret_key_here'
```

Then run the app as usual:

```powershell
python app.py
```

If MySQL is configured and `mysql-connector-python` is installed, the app will use MySQL automatically.

## Docker deployment

A local containerized deployment is included with `Dockerfile` and `docker-compose.yml`.

1. Build and start the app locally:

```powershell
cd "c:\Users\Sanketh.S\OneDrive\Desktop\thyroid cancer detection"
docker compose up --build
```

2. Open the app at:

```text
http://127.0.0.1:5000
```

3. To stop the deployment:

```powershell
docker compose down
```

The included `docker-compose.yml` creates:
- `db`: MySQL 8.0 with `thyroid_db` and user `thyroid`
- `web`: Flask app served by Gunicorn on port `5000`

> This repository is configured for local deployment only. Remote deployment files such as `render.yaml`, `Procfile`, and the `deploy/` helper scripts are not required for local use.
