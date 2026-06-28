# 🩺 Thyroid Cancer Detection Web Application

A production-ready machine learning web application designed for the early diagnostic detection of thyroid cancer. This project bridges the gap between data science and full-stack web development by wrapping a highly accurate classification pipeline into a fast, user-friendly Flask web app backed by an SQLite database.

## 🚀 Key Features

* **High-Accuracy Predictive Modeling:** Utilizes a rigorous feature engineering pipeline and Scikit-learn classification algorithms to achieve a **94% diagnostic accuracy**.
* **Low-Latency Web Interface:** Engineered a robust Flask backend capable of processing patient feature inputs and returning diagnostic predictions in **under 200ms**.
* **Secure Data Persistence:** Integrated an SQLite database to securely log diagnostic requests, user inputs, and prediction outcomes for auditability and continuous model evaluation.
* **End-to-End Pipeline:** Demonstrates a complete ML lifecycle—from exploratory data analysis (EDA) and model training to deployment and production readiness.

## 🛠️ Tech Stack

* **Language:** Python
* **Backend Framework:** Flask
* **Machine Learning:** Scikit-learn, NumPy
* **Database:** SQLite
* **Frontend:** HTML/CSS with Jinja2 templates

## 📂 Machine Learning Pipeline Highlights

1. **Data Preprocessing:** Handled missing values and scaled numerical features to optimize model convergence.
2. **Feature Engineering:** Applied statistical techniques to identify the most critical biomarkers for early thyroid cancer detection.
3. **Model Selection & Tuning:** Evaluated multiple classification models and fine-tuned hyperparameters to maximize diagnostic accuracy while minimizing false negatives.

## ⚙️ Installation & Setup

To run this application locally, follow these steps:

**1. Clone the repository:**
```bash
git clone https://github.com/SANKETH-23/thyroid-prediction.git
cd thyroid-prediction
```

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
