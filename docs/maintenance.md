# Maintenance
This document provide a list of infrastructure maintenance routines and describe the automations used to manage AWS resources efficiently.

- Contents covered:

    1. [Backups](#1-backups)
    2. [Monitoring & Alerts]
    3. [Patching & Updates](#patching--updates)
    4. [Database Maintenance]
    5. [Security Maintenance]
    6. [Resource Scaling & Cost Management](#)
    7. [Certificate & Domain Renewal](#certificate--domain-renewal)
    8. [Housekeeping Tasks](#8-housekeeping-tasks)
    9. [Audit & Compliance](#)
    10. [Incident Response & Reporting](#)


## 1. Backups

### Current Status
No automated backup processes are currently in place for this repository’s resources.  
**Recommendation:** As the project grows or if other contributors join, consider implementing automated backups for critical files and data.

### Manual Backup Instructions

#### 1. Code Repository
- The source code is backed up automatically via GitHub.

#### 2. Configuration and Environment Files

**Files to Backup:**
- `config/` directory (if present)
- `.env` and any `.env.*` files
- Any other files containing critical secrets or configuration

**How to Backup:**
1. **Copy the files to a secure location:**  
   - Use a secure USB drive, encrypted external disk, or a private, access-restricted cloud storage service (such as an encrypted Google Drive folder or AWS S3 bucket with strict permissions).
   - Example (local copy):  
     ```sh
     cp .env config/* ~/secure-backups/myproject-$(date +%F).tar.gz
     ```
2. **Encrypt sensitive backups:**  
   - Use tools like `gpg` or encrypt the storage location to prevent unauthorized access.
   - Example:  
     ```sh
     tar czf - .env config/ | gpg -c > myproject-backup-$(date +%F).tar.gz.gpg
     ```
3. **Regularity:**  
   - Perform this backup after any significant configuration change, or at least weekly during active development.

**Important:**  
Never commit `.env` or other sensitive config files to your public git repository.

### Restore Instructions

To restore:
1. Decrypt and extract the backup to your project directory.
2. Verify permissions and paths before restarting the application.

### Future Improvements

- Consider adding automated backup scripts and secure cloud storage as the project grows.
- Document any automated backup solutions here when implemented.


## Resource Scaling & Cost Management
### Automations used on AWS - Schedulers

Schedulers are used to stop and start EC2 instances and RDB instance automatically on a recurring schedule.

- The role asigned to a scheduler has to have permission to assume role and invoke lambda function since we're using lambda function to control instances.

```json

```

This script initializes the automation tool and runs a sample task. Replace `"example_task"` with your specific task name.


## Certificate & Domain Renewal
### TLS/SSL Certificate (Let’s Encrypt via Certbot)

The web server uses **Let's Encrypt** to enable HTTPS. Certificate management is handled using **Certbot**.

- **Certbot** is used to request and renew certificates.
- **Nginx** serves as the reverse proxy and handles HTTPS.
- Certificates are validated using the **HTTP-01 challenge** (Nginx serves the required validation files).
- Currently manual renewal and reload is performed.
- Cerficiates and renewal logs are stored in the shared volume:
    ```
    /etc/letsencrypt
    ```
- Commands to manually renew and reload:
    ```bash
    # check if certbot is installed
    which certbot

    # check any container(s) using what port
    docker ps
    sudo lsof -i :80

    # stop the relevant container(s)
    docker stop <container_name_or_id>

    # renew
    sudo certbot renew

    # restart containers
    docker start <container_name_or_id>
    ```
    - Alternative (stopping server not required):
        ```
        sudo certbot renew --webroot -w /path/to/your/webroot
        ```

        Replace `/path/to/your/webroot` with the directory your website serves static files from (e.g., the root directory in your Docker container mapped to the host).

- The renew should happen regularly.


### Roles and Policies


## 8. Housekeeping Tasks
 
### Checklist to verity TLS, nginx, and proxy headers
1. SSL is good + HTTP -> HTTPS redirects
    ```sh
    # TLS cert info
    echo | openssl s_client -connect prime.kines.umich.edu:443 -servername prime.kines.umich.edu 2>/dev/null | openssl x509 -noout -subject -issuer -dates

    # HTTPS returns 200
    curl -sS https://prime.kines.umich.edu -o /dev/null -w "%{http_code}\n"

    # HTTP redirects to HTTPS and shows Location header
    curl -sI http://prime.kines.umich.edu | sed -n '1p;/^Location/p'
    ```
2. nginx is actually using the prod config + forwarding proto
    ```sh
    # Dump the running nginx config from inside the container
    docker exec -it prime_webtool_nginx_1 nginx -T | sed -n '1,200p'
    # In the 443 server/location / block you should see:
    #   proxy_set_header X-Forwarded-Proto $scheme;
    #   proxy_set_header X-Forwarded-Host $host;
    #   proxy_set_header X-Forwarded-Port $server_port;
    #   proxy_http_version 1.1;
    #   proxy_redirect off;
    ```
3. Gunicorn is trusting forwarded headers
    ```sh
    # Check the gunicorn command line has --forwarded-allow-ips=*
    docker exec -it prime_webtool_web_1 ps -ef | grep gunicorn | grep -v grep

    # And the env var (belt & suspenders) - optional
    docker exec -it prime_webtool_web_1 env | grep FORWARDED_ALLOW_IPS
    ```
4. Quick OAuth plumbing sanity
    ```sh
    # The app should 302 to Google when starting login
    curl -sI https://prime.kines.umich.edu/auth/login | sed -n '1p;/^Location/p'
    ```
5. confirm gunicorn workers
    ```sh
    docker exec -it prime_webtool_web_1 ps -ef | grep gunicorn
    # Should include: -w 3 --threads 4 --timeout 90 --graceful-timeout 30
    ```



## 