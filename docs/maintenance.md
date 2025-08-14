# Maintenance
This document provide a list of infrastructure maintenance routines and describe the automations used to manage AWS resources efficiently.

## Instances Security and Accessibility


## Automations used on AWS

### Schedulers

Schedulers are used to stop and start EC2 instances and RDB instance automatically on a recurring schedule.

- The role asigned to a scheduler has to have permission to assume role and invoke lambda function since we're using lambda function to control instances.

```json

```

This script initializes the automation tool and runs a sample task. Replace `"example_task"` with your specific task name.