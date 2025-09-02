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
```sh
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose
```

#### (Optional) Run Docker without sudo
```sh
sudo usermod -aG docker $USER
```
Then re-login or run: newgrp docker




## C. Pull & Configure the App
```sh
cd ~
git clone https://github.com/your-org/prime_webtool.git
cd prime_webtool
```
- Edit config.py for production:
- Use IAM role or environment variables for S3
- Set DB URI to your production database

## D. Deploy with Docker Compose
```sh
docker-compose up -d --build
docker ps   # confirm containers are running
```
## E. (Optional) Use Host Nginx as Reverse Proxy
1.	Install Nginx: `sudo apt install -y nginx`
2.	Copy nginx.conf to /etc/nginx/sites-enabled/prime_webtool
      - Adjust proxy_pass to http://localhost:8000 (or your app port).
3.	Restart Nginx: `sudo systemctl restart nginx`

## F. Enable HTTPS with Let’s Encrypt
```sh
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain.com -d www.your.domain.com --agree-tos -m your@email.com
```
Follow prompts to issue and auto-renew certificates.
- `-d` specifies what domains to include in the certificate
- `--agree-tos` automatically agree to Let's Encrypt's Terms of Service
- `-m your@email.com`: email for important renewal/expiration notifications from Let's Encrypt
