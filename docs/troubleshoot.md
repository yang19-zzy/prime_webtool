# Troubleshooting Example

## Issue I
- Description: When ready for testing features/bugs on prod database instance, cannot connect to the database directly from local machines.
- Solution: Create a AWS Systems Manager Session to create a temporary tunnel to talk to prod instance.
- Command lines needed to create and verify session:
    - create a session
        ```
        aws ssm start-session --region <instance-region> \
        --target i-<EC2_ID> \
        --document-name AWS-StartPortForwardingSessionToRemoteHost \
        --parameters "host=['<rds-endpoint>'],portNumber=['<rds-port>'],localPortNumber=['<local-port>']"
        ```
    - verify port
        ```lsof -iTCP:5433 -sTCP:LISTEN```
    - verify connection on Mac
        ```psql "host=127.0.0.1 port=<local-port> dbname=<database> user=<read-only user> sslmode=require"```
- Tips:
    - If running app in Docker, make sure the DB_URI is referring `host.docker.internal` instead


## Issue II
- Description: Prod database connection experiences unexpected kill. 
    - Example: 
- Solution: Make sure a new pool is used when commit to database.
- Instructions: 
    -
- Tips:
    - 