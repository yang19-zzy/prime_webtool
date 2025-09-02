# Infrastructure Overview

This document summarizes the architecture and deployment infrastructure for the Flask app.


## ☁️ High-Level Diagram

```mermaid
graph TD
  Browser -->|HTTPS| Nginx
  Nginx -->|proxy_pass| Gunicorn
  Gunicorn --> FlaskApp
  FlaskApp -->|psycopg2| AWS RDS PostgreSQL
  FlaskApp -->|requests_oauthlib| Google OAuth2
```

## 🧱 Core Components

Layer              | Tool / Service            | Purpose
------------------ | ------------------------- | -----------------------------------------------
Web Server         | Nginx                     | SSL/TLS termination, reverse proxy
App Server         | Gunicorn                  | WSGI server for serving Flask app
App Framework      | Flask + Jinja2            | Web backend and HTML frontend rendering
Auth               | Google OAuth2             | Org-based login and role-based access
Secrets Mgmt       | AWS Secrets Manager       | Store DB credentials, OAuth client secrets, etc.
Database           | PostgreSQL                | Store user roles, form submissions, and metadata
Containerization   | Docker / Docker Compose   | Define and deploy services (Flask, Nginx, etc.)
Hosting            | EC2 (Ubuntu)              | Virtual server for app deployment and hosting


## 🔐 HTTPS with Nginx
- SSL cert from Let’s Encrypt (Certbot)
- Auto-renewal via cron or systemd timer
- Redirect all http to https