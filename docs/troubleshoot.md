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

## Issue 5: 

> Add more issues as needed, following this format.

---

