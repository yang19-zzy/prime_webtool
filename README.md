# PRIME Webtool

PRIME Webtool is a Flask-based data-management and visualization platform for processing, merging, and exploring health and performance metrics collected from multiple sources (e.g., COSMED, DEXA).

📚 See [docs/](docs/) for full project documentation.

## Features
- Tracker form submission and notification for data management
- Interactive Data Viewer with table and column selection  
- OAuth2 login (Google/UMICH)  


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


