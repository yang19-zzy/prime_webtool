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

<br>
<br>

# Deploy Staging Env
1. Create a staging instance and a staging database
2. Install essential elements
      ```sh
      sudo dnf update -y

      # install git to clone repo
      sudo dnf install git -y

      # install docker
      sudo dnf install docker -y
      sudo systemctl enable docker
      sudo systemctl start docker
      sudo chkconfig docker on #make docker autostart
      sudo usermod -aG docker $USER

      # install docker compose -> https://medium.com/@fredmanre/how-to-configure-docker-docker-compose-in-aws-ec2-amazon-linux-2023-ami-ab4d10b2bcdc
      #sudo dnf install docker-compose-plugin -y =>this raise error of "No match for argument"
      sudo mkdir -p /usr/libexec/docker/cli-plugins/
      sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose
      sudo chmod +x /usr/libexec/docker/cli-plugins/docker-compose
      docker compose version
      sudo chmod 666 /var/run/docker.sock #run this if "permission denied" when build
      ```
2. Clone git repository
      ```sh
      #rm -rf primr_webtool #run this if needed => remove existing directory
      git clone --single-branch --branch <staging-branch-name> <webtool-repository-url>
      ```
3. Copy staing files to the instance
      ```sh
      scp -i </path/to/your-key-pair.pem> </path/to/local/file> ec2-user@ec2-3-218-226-67.compute-1.amazonaws.com:</path/to/remote/directory>
      ```
      - files should be:
            - `.env`
            - `docker-compose.yml`
            - `Dockerfile`
            - `nginx/nginx.conf`
4. Generate a certificate
      ```sh
      sudo python3 -m venv /opt/certbot/
      sudo /opt/certbot/bin/pip install --upgrade pip
      sudo /opt/certbot/bin/pip install certbot certbot-nginx
      sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot

      sudo certbot --nginx
      ```