# 🌦️ Real-Time Weather Data Pipeline

> An end-to-end automated data pipeline on AWS that ingests live weather data from 4 Indian cities every hour, transforms it, stores it in a data warehouse, and visualizes it on a dashboard.

---

## 📌 Project Overview

Weather data changes every hour. This project builds a fully automated pipeline that:
- **Ingests** live weather data from the OpenWeatherMap API every hour
- **Stores** raw JSON data in Amazon S3 (Data Lake)
- **Transforms** nested JSON into structured rows using AWS Glue + PySpark
- **Loads** clean data into Amazon Redshift Serverless (Data Warehouse)
- **Orchestrates** the entire pipeline automatically using Apache Airflow on EC2
- **Visualizes** temperature trends, humidity, and wind speed using AWS QuickSight

---

## 🏗️ Architecture

![Architecture Diagram](architecture.png)

```
OpenWeatherMap API
       ↓ HTTP Request every hour
AWS Lambda (Python)
       ↓ Raw JSON
AWS S3 (Data Lake)
       ↓ Read & Transform
AWS Glue + PySpark (ETL)
       ↓ Clean Rows via JDBC
Amazon Redshift Serverless (Data Warehouse)
       ↓ Query
AWS QuickSight (Dashboard)

Apache Airflow (hosted on EC2)
       ↓ Orchestrates
Lambda → Glue automatically every hour
```

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Data Source | OpenWeatherMap API |
| Ingestion | AWS Lambda (Python 3.14) |
| Scheduling | Amazon EventBridge |
| Storage | Amazon S3 |
| Transformation | AWS Glue + PySpark |
| Data Warehouse | Amazon Redshift Serverless |
| Orchestration | Apache Airflow (on EC2) |
| Dashboard | AWS QuickSight |
| IAM & Security | AWS IAM Roles, Environment Variables |

---

## 📁 Project Structure

```
weather-pipeline/
├── ingestion/
│   └── lambda_function.py       # Lambda function to fetch & save weather data
├── transformation/
│   └── glue_job.py              # PySpark script to clean & load data to Redshift
├── orchestration/
│   └── weather_dag.py           # Airflow DAG to orchestrate the pipeline
├── sql/
│   └── create_tables.sql        # Redshift table schema
├── architecture.png             # Architecture diagram
└── README.md
```

---

## 🌍 Cities Covered

- Kochi
- Bangalore
- Mumbai
- Delhi

---

## ⚙️ Setup & Deployment

### Prerequisites
- AWS Account (Free Tier)
- OpenWeatherMap API Key (free at [openweathermap.org](https://openweathermap.org/api))
- Python 3.8+

---

### Phase 0 — Accounts Setup
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api) → get free API key
2. Create AWS Free Tier account at [aws.amazon.com/free](https://aws.amazon.com/free)
3. Create an IAM user and use it instead of root user

---

### Phase 1 — Data Ingestion (AWS Lambda)

**Create S3 Bucket:**
- Name: `weather-pipeline-yourname`
- Region: `ap-south-1`

**Deploy Lambda:**
1. AWS Console → Lambda → Create Function
2. Runtime: Python 3.14
3. Paste `lambda_function.py`
4. Add Environment Variables:
   - `API_KEY` → your OpenWeatherMap key
   - `BUCKET_NAME` → your S3 bucket name
5. Attach IAM Role with `AmazonS3FullAccess`
6. Add EventBridge trigger: `rate(1 hour)`

**Lambda saves data to S3 at:**
```
raw/weather/Kochi/2026-01-01-10-00-00.json
raw/weather/Bangalore/2026-01-01-10-00-00.json
raw/weather/Mumbai/2026-01-01-10-00-00.json
raw/weather/Delhi/2026-01-01-10-00-00.json
```

---

### Phase 2 — Transformation (AWS Glue + Redshift)

**Create Redshift Table:**
```sql
CREATE TABLE IF NOT EXISTS weather_data (
    city         VARCHAR(100),
    country      VARCHAR(10),
    temperature  FLOAT,
    feels_like   FLOAT,
    humidity     INT,
    wind_speed   FLOAT,
    description  VARCHAR(200),
    recorded_at  TIMESTAMP
);
```

**Create Glue IAM Role:**
- Trusted entity: Glue
- Policies: `AmazonS3FullAccess` + `AmazonRedshiftFullAccess`
- Name: `glue-weather-role`

**Deploy Glue Job:**
1. AWS Console → Glue → ETL Jobs → Create Job
2. Type: Spark script editor
3. Paste `glue_job.py`
4. Add Job Parameters:
   - `--REDSHIFT_PASSWORD` → your Redshift password
5. Run the job and verify in Redshift:

```sql
SELECT * FROM weather_data ORDER BY recorded_at DESC LIMIT 10;
```

---

### Phase 3 — Orchestration (Apache Airflow on EC2)

**Launch EC2 Instance:**
- AMI: Amazon Linux 2023
- Instance type: t2.medium
- Security group: port 22 (SSH) + port 8080 (Airflow UI)

**Install Airflow:**
```bash
# SSH into EC2
ssh -i "airflow.pem" ec2-user@your-ec2-public-ip

# Setup
sudo dnf update -y
sudo dnf install python3-pip -y
pip3 install virtualenv
python3 -m virtualenv airflow_env
source airflow_env/bin/activate
export AIRFLOW_HOME=~/airflow

# Install Airflow
pip install "apache-airflow==2.7.0" apache-airflow-providers-amazon

# Initialise
airflow db init

# Create admin user
airflow users create \
  --username admin \
  --password admin \
  --firstname Your \
  --lastname Name \
  --role Admin \
  --email you@email.com

# Start
airflow webserver --port 8080 --daemon
airflow scheduler --daemon
```

**Access Airflow UI:**
```
http://your-ec2-public-ip:8080
```

**Deploy DAG:**
```bash
mkdir ~/airflow/dags
vi ~/airflow/dags/weather_dag.py
```

**Set up AWS Connection in Airflow UI:**
- Admin → Connections → Edit `aws_default`
- Add your AWS Access Key ID and Secret Access Key
- Extra: `{"region_name": "ap-south-1"}`

**Trigger DAG:**
- Enable `weather_pipeline` DAG
- Click ▶ Trigger DAG
- Both tasks turn green ✅

---

### Phase 4 — Dashboard (AWS QuickSight)

1. AWS Console → QuickSight → Sign up (30-day free trial)
2. Connect to Redshift Serverless
3. Create dataset from `weather_data` table
4. Build visuals:
   - 📈 Line chart: Temperature trends over time per city
   - 📊 Bar chart: Average humidity by city
   - 🌡️ KPI card: Latest temperature reading

---

## 🔑 Key Concepts

| Concept | Explanation |
|---|---|
| Serverless | Lambda & Glue run without managing servers |
| Data Lake | S3 stores raw unstructured JSON cheaply |
| Data Warehouse | Redshift stores clean structured data for analytics |
| ETL | Extract from API → Transform in Glue → Load to Redshift |
| Orchestration | Airflow automates and monitors the whole pipeline |
| JDBC | Protocol used by PySpark to connect to Redshift |
| Environment Variables | Secrets stored safely outside of code |
| Idempotency | Running pipeline twice shouldn't create duplicate data |

---

## ⚠️ Known Limitations & Future Improvements

- **Duplicate data risk** — Glue uses `append` mode. Future fix: implement MERGE/upsert using city + timestamp as composite key
- **Double triggering** — EventBridge and Airflow both trigger Lambda. Fix: remove EventBridge and let only Airflow orchestrate
- **No data quality checks** — Future fix: add `df.dropna()` and schema validation in Glue
- **EC2 RAM** — t2.medium recommended for Airflow in production
- **Hardcoded Redshift endpoint** — Future fix: move to Glue job parameters

---

## 📊 Sample Output

```
city        country  temperature  feels_like  humidity  wind_speed  description       recorded_at
Kochi       IN       28.64        31.96       70        7.22        scattered clouds  2026-03-07 10:00:00
Bangalore   IN       33.60        31.16       13        3.86        clear sky         2026-03-07 10:00:00
Mumbai      IN       27.89        29.51       62        9.58        clear sky         2026-03-07 10:00:00
Delhi       IN       34.77        32.13       10        0.93        clear sky         2026-03-07 10:00:00
```

---

## 📄 LinkedIn Description

**Tools:** OpenWeatherMap API, AWS Lambda, Amazon EventBridge, Amazon S3, AWS Glue (ETL Jobs – PySpark), Amazon Redshift Serverless, Apache Airflow (EC2), AWS QuickSight

**Summary:** Built an end-to-end real-time weather data pipeline on AWS to ingest, transform, and visualize live weather data across 4 Indian cities. Implemented a serverless ingestion layer using AWS Lambda scheduled hourly via Amazon EventBridge, storing raw JSON responses in an S3 data lake. Performed ETL transformations using AWS Glue with PySpark to flatten nested JSON structures and load clean structured data into Amazon Redshift Serverless. Orchestrated the full pipeline using Apache Airflow hosted on EC2, automating Lambda → Glue execution with retry logic and failure monitoring. Visualized temperature trends, humidity patterns, and wind speed metrics using AWS QuickSight.

---

## 👩‍💻 Author

**Fathimath Najiya CK**
- AWS Certified Solutions Architect – Associate
- AWS Certified Cloud Practitioner
- [LinkedIn](#) | [GitHub](#)
