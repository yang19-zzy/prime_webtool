# PRIME Webtool

PRIME Webtool is a Flask-based data-management and visualization platform for processing, merging, and exploring health and performance metrics collected from multiple sources (e.g., COSMED, DEXA).


## Features
- Secure file upload (SFTP or web form)  
- ETL pipelines for data cleaning & transformation  
- AWS S3 integration with dynamic schema discovery  
- Interactive Data Viewer with schema/table/column selection  
- OAuth2 login (Google/UMICH)  
- Optional Dash dashboard embedding  
- Dockerized for easy deployment  


## Repository Structure
```
prime_webtool/
├── app/                             # Flask application package
│   ├── init.py
│   ├── blueprints/                  # Flask blueprints
│   ├── dash_dashboard/              # Dash app code (TO-DO⚠️)
│   ├── dash_viewer/                 # Dash viewer - served as database viewer
│   ├── db_DONOTUSE.py
│   ├── extensions.py                # S3, DB, OAuth setup
│   ├── models.py                    # SQLAlchemy models
│   ├── static/                      # JS/CSS assets
│   ├── templates/                   # Jinja2 templates
│   └── utils/                       # helper modules
├── certs/                           # self-signed certs (for local HTTPS)
│   ├── selfsigned.crt
│   └── selfsigned.key
├── CHANGELOG.md
├── config.py                        # Central config (S3, DB URI, secrets)
├── docker-compose.yml               # Production / default Docker Compose
├── docker-compose.dev.yml           # Development Docker Compose
├── Dockerfile                       # Build instructions for the web app
├── migrations/                      # Alembic database migrations (need reconsider⚠️)
├── nginx.conf                       # host Nginx config
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── run.py                           # app entrypoint
└── task_save_columns_as_statics.py  # Utility script (TO-DO: set up crontab or Actions⚠️)
```


## Getting Started (Local Development with Docker)

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-org/prime_webtool.git
   cd prime_webtool
   ```
2.	Install Docker & Docker Compose
      - macOS: `brew install docker docker-compose`
      - Linux: see your distro’s package manager or docs.docker.com
3.	Configure environment
      - Edit config.py (or set environment variables) to supply AWS S3 credentials, OAuth client IDs, and SQLALCHEMY_DATABASE_URI.
      - If you need HTTPS locally, place your cert/key in certs/ and refer to them in nginx.conf.
      ```
      mkdir certs
      openssl req -x509 -nodes -days 365 \
      -newkey rsa:2048 \
      -keyout certs/selfsigned.key \
      -out certs/selfsigned.crt \
      -subj "/CN=localhost"
      ```
4.	Bring up the containers
	   - Production-style (exposes port 80): `docker-compose up -d --build`
      - Development (with live-reload): `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build`


5.	Access the app
      - Open your browser at http://localhost/ (or https://localhost/ if you enabled HTTPS via nginx.conf).




# EC2 Deployment Handbook (Testing with Docker)
A step-by-step guide to spin up an EC2 instance and deploy PRIME Webtool in Docker containers.

## A. Launch an EC2 Instance
1.	AWS Console → EC2 → Launch Instance
2.	Choose an AMI: Ubuntu Server 22.04 LTS (or Amazon Linux 2)
3.	Instance type: t3.small (2 vCPU, 2 GiB RAM)
4.	Security Group:
      - SSH (22) from your IP
      - HTTP (80) and HTTPS (443) from anywhere
5.	Assign/create a key pair, then launch. Note the Public IPv4 address.


## B. Connect & Install Docker

```ssh -i /path/to/key.pem ubuntu@<EC2_PUBLIC_IP>```

### Update & install Docker
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose
```

#### (Optional) Run Docker without sudo
```
sudo usermod -aG docker $USER
```
Then re-login or run: newgrp docker




## C. Pull & Configure the App
```
cd ~
git clone https://github.com/your-org/prime_webtool.git
cd prime_webtool
```
- Edit config.py for production:
- Use IAM role or environment variables for S3
- Set DB URI to your production database

## D. Deploy with Docker Compose
```
docker-compose up -d --build
docker ps   # confirm containers are running
```
## E. (Optional) Use Host Nginx as Reverse Proxy
1.	Install Nginx: `sudo apt install -y nginx`
2.	Copy nginx.conf to /etc/nginx/sites-enabled/prime_webtool
      - Adjust proxy_pass to http://localhost:8000 (or your app port).
3.	Restart Nginx: `sudo systemctl restart nginx`

## F. Enable HTTPS with Let’s Encrypt
```
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain.com
```
Follow prompts to issue and auto-renew certificates.
