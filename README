# PRIME Webtool Repository README

## 1. Project Overview
PRIME Webtool is a data-management and visualization platform for processing, merging, and exploring health and performance metrics collected from multiple sources (e.g., COSMED, DEXA). It provides:

- **SFTP or web-based file upload** for raw data ingestion
- **ETL pipelines** for data cleaning and transformation
- **AWS S3 integration** to fetch, cache, and merge time-series datasets
- **Data Viewer** React-like interface (Dash/Streamlit) for schema-driven table selection and interactive filtering
- **OAuth2** user authentication (e.g., Google/UMICH login)


## 2. Features
- Dynamic folder and table discovery in S3
- Column-level selection via modal with checkbox UI
- Backend endpoints to preview schema and merge datasets
- Postgres trigger examples for auditing and timestamping
- Docker/Dash integration sample for rapid prototyping


## 3. Repository Structure
```
prime_webtool/
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── run.py            # Main Flask entrypoint + Dash mounting
│   ├── blueprints/
│   │   └── viewer/       # Data Viewer blueprint
│   │       └── routes.py
│   ├── extensions.py     # S3, DB, OAuth2 clients
│   ├── models.py         # SQLAlchemy models (e.g., TableColumns)
│   ├── templates/        # Jinja2 templates
│   └── static/
│       ├── js/           # dataViewer.js, test_tracker.js
│       └── css/          # Custom styles
├── config/
│   └── config.yaml       # App configuration (S3, OAuth, DB)
├── tools/                # ETL helpers, cleaners, mappers
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container definition (optional)
└── README.md             # This file
```


## 4. Getting Started (Local Development)

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-org/prime_webtool.git
   cd prime_webtool
   ```

2. **Create a Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   - Copy `config/config.example.yaml` → `config/config.yaml`
   - Fill in: S3 credentials, OAuth client ID/secret, DB URI, secret key.

4. **Run Flask app**
   ```bash
   export FLASK_APP=app/run.py
   flask run --host=0.0.0.0 --port=8000
   ```

5. **Access**
   - Open `http://localhost:8000/` in your browser.
   - Login via OAuth, then navigate to `/viewer` to use the Data Viewer.


## 5. Testing
- Use pytest for unit tests in `/tests`
- Run:
  ```bash
  pytest --cov=app
  ```


## 6. Contributing
- Fork the repo, create feature branch, submit pull request
- Write tests for new features, maintain code style (flake8)


## 7. License
MIT License. See [LICENSE](LICENSE) for details.

---

# Handbook: Deploying PRIME Webtool on AWS EC2 (Testing)

This guide walks you through launching an EC2 instance, setting up your Flask app, and testing it.

## A. Launch EC2 Instance

1. **AWS Console** → EC2 → Launch Instance
2. **Choose AMI**: Amazon Linux 2 or Ubuntu Server 22.04 LTS
3. **Instance Type**: t3.small (2 vCPU, 2 GiB RAM) for testing
4. **Configure Security Group**:
   - Allow SSH (TCP 22) from your IP
   - Allow HTTP (TCP 80) and HTTPS (TCP 443) from 0.0.0.0/0 for web traffic
5. **Key Pair**: Create/download or use existing
6. **Launch** and note the public IPv4 address

## B. Connect via SSH
```bash
ssh -i /path/to/key.pem ec2-user@<EC2_PUBLIC_IP>
# or ubuntu@ for Ubuntu AMI
```

## C. Install Dependencies
```bash
# Update OS
sudo yum update -y            # Amazon Linux
# OR sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Python, pip, venv
sudo yum install python3 -y    # Amazon Linux
# OR sudo apt install python3 python3-venv python3-pip -y

# Install Git
sudo yum install git -y
```

## D. Pull and Configure App
```bash
cd ~
git clone https://github.com/your-org/prime_webtool.git
cd prime_webtool
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and edit config
cp config/config.example.yaml config/config.yaml
# Use AWS IAM role/env for S3; put dummy DB URI if none
```

## E. Run the App (Test)
```bash
export FLASK_APP=app/run.py
flask run --host=0.0.0.0 --port=80
```
Visit: `http://<EC2_PUBLIC_IP>/` should show login page.

## F. (Optional) Set Up Production-Style Web Server

1. **Install Nginx & Gunicorn**
   ```bash
   sudo yum install nginx -y
   pip install gunicorn
   ```
2. **Create systemd Service** `/etc/systemd/system/prime_webtool.service`
   ```ini
   [Unit]
   Description=Gunicorn instance for PRIME Webtool
   After=network.target

   [Service]
   User=ec2-user
   Group=nginx
   WorkingDirectory=/home/ec2-user/prime_webtool
   Environment="PATH=/home/ec2-user/prime_webtool/venv/bin"
   ExecStart=/home/ec2-user/prime_webtool/venv/bin/gunicorn \
       --workers 3 \
       --bind unix:prime_webtool.sock \
       'app.run:server'

   [Install]
   WantedBy=multi-user.target
   ```
3. **Nginx Config** `/etc/nginx/conf.d/prime_webtool.conf`
   ```nginx
   server {
       listen 80;
       server_name YOUR_DOMAIN_OR_IP;

       location / {
           proxy_pass http://unix:/home/ec2-user/prime_webtool/prime_webtool.sock;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
4. **Start services**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start prime_webtool
   sudo systemctl enable prime_webtool
   sudo systemctl restart nginx
   ```

## G. Enable HTTPS (Let’s Encrypt)
```bash
sudo yum install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```
Follow prompts to issue and auto-renew certificates.

---

Now your PRIME Webtool is live on EC2 for further testing. Enjoy!

