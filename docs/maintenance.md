# Maintenance
This document provide a list of infrastructure maintenance routines and describe the automations used to manage AWS resources efficiently.

- Contents covered:

    1. [Backups](#backups)
    2. [Monitoring & Alerts]
    3. [Patching & Updates](#patching--updates)
    4. [Database Maintenance]
    5. [Security Maintenance]
    6. [Resource Scaling & Cost Management](#)
    7. [Certificate & Domain Renewal](#certificate--domain-renewal)
    8. [Housekeeping Tasks](#)
    9. [Audit & Compliance](#)
    10. [Incident Response & Reporting](#)


## Backups

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





## Patching & Updates
### Scheduled Maintenance

A scheduled maintenance is needed when a feature update is required. Check the lab calendar before switch to maintenance server.

**How to build a maintenance page**
1. **Create static page locally**
    - Create a `index.html` file
    - Create a `nginx/maintenance.conf` file
2. **Create a small EC2 instance and use the same set of inbound rules as the prod server**
    - A `t3.nano` with Amazon 2023 is good enough
    - Inbound 22 (SSH) from UM IP, 80 and 443 from 0.0.0.0/0
    - Install nginx
        ```sh
        sudo dnf install -y nginx
        sudo systemctl enable --now nginx
        ```
    - Copy static files (scp files to /home/ec2-user first, then move to dir accordingly for conveniance)
        ```sh
        sudo mkdir -p /var/www/maintenance
        sudo cp maintenance/index.html /var/www/maintenance/index.html
        sudo chown -R root:root /var/www/maintenance
        sudo chmod -R a=rX /var/www/maintenance
        sudo cp nginx/maintenance.conf /etc/nginx/conf.d/maintenance.conf
        ```
    - Test and reload
        ```sh
        sudo nginx -t
        sudo systemctl reload nginx
        ```
3. **HTTPS certificate on maintenance instance**
    - Copy prod certs to maintenance server
        ```sh
        # on prod 
        sudo tar czf letsencrypt-certs.tar.gz -C /etc/letsencrypt live/prime.kines.umich.edu archive/prime.kines.umich.edu renewal/prime.kines.umich.edu.conf
        # on local machine
        scp -i <prod-public-key> ubuntu@<prod-public-ip>:/home/ubuntu/letsencrypt-certs.tar.gz . 
        scp -i <maintenance-public-key> letsencrypt-certs.tar.gz ec2-user@<maintenance-public-ip>:/home/ec2-user/tmp/letsencrypt-certs.tar.gz          
        # on maintenance
        sudo tar xzf /home/ec2-user/tmp/letsencrypt-certs.tar.gz -C /etc/letsencrypt
        ```








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





## 