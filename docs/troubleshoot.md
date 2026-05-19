# Troubleshooting Documentation Example

This document provides a template for troubleshooting common issues in a project. Each issue includes a description, solution steps, and helpful tips.

---

## Issue 1: Cannot Connect to Production Database from Local Machine

**Description:**  
Unable to connect directly to the production database instance from your local environment.

**Solution:**  
Use AWS Systems Manager Session Manager to create a secure tunnel.

**Steps:**
1. **Start Port Forwarding Session**
    ```sh
    aws ssm start-session --region <region> \
      --target i-<EC2_ID> \
      --document-name AWS-StartPortForwardingSessionToRemoteHost \
      --parameters "host=['<db-endpoint>'],portNumber=['<db-port>'],localPortNumber=['<local-port>']"
    ```
2. **Verify Local Port**
    ```sh
    lsof -iTCP:<local-port> -sTCP:LISTEN
    ```
3. **Test Database Connection**
    ```sh
    psql "host=127.0.0.1 port=<local-port> dbname=<db> user=<user> sslmode=require"
    ```

**Tips:**  
- For Docker, use `host.docker.internal` instead of `localhost` in your DB URI.

---

## Issue 2: "UnauthorizedOperation" Error When Managing EC2 from Lambda

**Description:**  
Lambda function fails with an error like:  
`An error occurred (UnauthorizedOperation) when calling the DescribeInstances operation: ...`

**Solution:**  
Ensure the Lambda's execution role has the required EC2 permissions (e.g., `DescribeInstances`, `StartInstances`, `StopInstances`).

---

## Issue 3: NGINX "400 Bad Request Header or Cookie Too Large"

**Description:**  
After logging in, a "400 Bad Request Header or Cookie too large" error appears from NGINX.

**Solution:**  
Clear cookies for the site in your browser. If error persists, check NGINX configuration for `large_client_header_buffers`.

---

## Issue 4: Database connection unexpected kill

**Description:**
Prod database connection experiences unexpected kill.

**Solution:**
Make sure a new pool is used when commit to database.

---

## Issue 5: 502 Gateway Error on prod

**Description:**
Getting 502 Gateway Error when routing /auth/oauth2callback, while everything works fine with local testing.

**Solution:**
- Modify on nginx config, make sure it has:
    ```sh
    # In the 443 server/location / block you should see:
    #   proxy_set_header X-Forwarded-Proto $scheme;
    #   proxy_set_header X-Forwarded-Host $host;
    #   proxy_set_header X-Forwarded-Port $server_port;
    #   proxy_http_version 1.1;
    #   proxy_redirect off;
    ```
- Modify on Gunicorn, make sure it has good amount workers to process work
    ```Dockerfile
    ["gunicorn","-w","3","--threads","4","-b","0.0.0.0:5000","--timeout","90","--graceful-timeout","30","--forwarded-allow-ips=*","run:app"]
    ```

**Tips:**
- Make sure the database connection is open
- Make sure the instance connection is open
- Make sure you can consult with ChatGPT

---

## Issue 6: Error connect to EC2 with first login

**Description:**
Unable to SSH connect EC2 instance in first login. Error message may like "Permissions 0644 for <access-key> are too open."

**Solution:**
Run command line where the key sits in
```sh
chmod 600 <key-file-path>
```

**Tips:**
- Permission `0644` means owner can read/write, others can only read.
- Permission 0600 means only the owner can read/write, others have no permissions.

---

## Issue 7: Error when start a ssm-session

**Description:**
Error when start a ssm-session.

**Solution:**
1. make sure the IAM has the corrent trust relationship
2. make sure the role is available through IMDSv2
3. try fully stop and restart the jumper instance
4. make sure the IAM role outbounds allow HTTP and HTTPS
5. make sure the local port number is matched

---

## Issue 8: 504 Gateway Time-out error

**Description:**
Getting 504 gateay time-out error after pushing the new release on prod. (Usually it should be the database connection error.)

**Solution:**
1. take the callback uri from logs and `curl` it within prod server to check if the issue is from the callback authentication
2. if provides response, the backend app is working fine
3. test through localhost with a ssm-session opened up to see if database is alive
4. make sure the wanted RDS instance / cluster is connected to the web server
5. make sure the web server and RDS server are in the same VPC
6. ask GPT

---

## Issue 9: Update Domain Name

**Description:**
The elastic IP needs to be mapped to another domain name due to internal team decision.

**Solution:**
1. Log into instance
2. Shut down Docker containers
    - `docker-compose down --remove-orphans`
3. Update files
    - .env
        - Update redirect url
    -  docker-compose.yml
        - Mount folder
        - !!!! **DO NOT** mount files. It will create as folders, resulting certificate being a folder not a file and cause nginx container keeps restarting
    - nginx.conf
        - Update server name
        - Comment out return 301, open http for generating certificate; move route location under http
            - `location / { return 301 https://$host$request_uri; }`
4. Copy files to instance
5. Start nginx
    - `docker-compose up -d nginx`
6. Generate certificate
    - `sudo certbot certonly --webroot -w /var/www/certbot -d <new domain name> --force-renewal`
7. Confirm the key formats correctly. It should have `----BEGIN CERTIFICATE----`
    - `sudo head -n 2 /path/to/certificate/key`
8. Update nginx.conf
    - Add back return 301 to secure https
9. Update frontend
    - Update redirect url on client.js
    - Rebuild npm
    - Copy files to instance 
        - `scp -i -r /path/to/local/folder/* /var/www/frontend/`
10. Restart or rebuild containers
    - `docker-compose down --remove-orphans`
    - `docker-compose -f docker-compose.yml up -d`
11. Check containers status
    - `docker ps`
12. Remove old certificate if needed
    - `sudo certbot delete`

---

## Issue 10:

> Add more issues as needed, following this format.

---
