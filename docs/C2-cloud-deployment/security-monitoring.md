# Security, Monitoring and Reliability

## 1. Introduction

This document describes the proposed security, monitoring and reliability measures for the cloud deployment of the questionnaire system.

The main objectives are to protect submitted data, control access to system resources, monitor application performance and maintain service availability during periods of increased traffic.

The measures described in this document represent the proposed cloud deployment design. Actual implementation will depend on the final cloud platform selected in B1 and the application implementation completed in C1.

## 2. HTTPS and Data Protection

### 2.1 HTTPS Communication

The deployed questionnaire system should use HTTPS to protect communication between users and the application.

- All external HTTP requests should be redirected to HTTPS.
- TLS encryption should be enabled to protect data transmitted between users and the server.
- A valid SSL/TLS certificate should be configured for the application domain.
- Insecure HTTP access should not be used for submitting questionnaire responses.

### 2.2 Data Protection

Questionnaire responses may contain information submitted by participants. Therefore, appropriate measures should be applied to protect stored data.

- Database access should be restricted to authorised application services.
- Sensitive configuration values should not be stored directly in source code.
- Data should be stored using an appropriate persistent storage service.
- Backups should be protected against unauthorised access.
- Only necessary questionnaire information should be collected and retained.

The specific database and storage security settings will be determined after the application architecture and cloud platform are confirmed.

## 3. Access Control and Permissions

The cloud deployment should follow the principle of least privilege.

- Only authorised administrators should have permission to manage cloud resources.
- The application should access databases and storage services using dedicated service identities or credentials.
- Database credentials and API keys should be stored using the cloud provider's secret management mechanism or equivalent secure configuration.
- Public users should only be able to access the questionnaire functions intended for them.
- Administrative operations, such as modifying deployment settings or accessing stored response data, should be restricted.

Permissions should be reviewed periodically to ensure that users and services only retain the access necessary for their responsibilities.

The exact identity and access management configuration will depend on the cloud provider selected in B1.

## 4. Monitoring and Logging

Monitoring is necessary to identify application failures, performance problems and unusual activity.

### 4.1 Application Logging

The application should record important operational events, including:

- Application startup and shutdown.
- Successful questionnaire submissions.
- Invalid submission attempts.
- Application errors and exceptions.
- Database connection failures.

Logs should help administrators investigate problems without exposing sensitive questionnaire information.

Passwords, secret keys and unnecessary personal information should not be written into application logs.

### 4.2 System Monitoring

The deployment should monitor the following indicators:

| Monitoring Metric | Purpose |
|---|---|
| CPU utilisation | Identify excessive processing load |
| Memory utilisation | Detect memory pressure |
| Request count | Understand application usage |
| Response time | Identify slow requests |
| Error rate | Detect application failures |
| Database availability | Check database connectivity |

Alerts should be configured for important failures, such as application unavailability, repeated request errors or database connection problems.

The specific monitoring tools and alert thresholds will be configured according to the selected cloud platform.

## 5. Peak Traffic Handling

The questionnaire system should be designed to handle temporary increases in user traffic.

The following measures are proposed:

- Use application-level scaling where supported by the selected hosting service.
- Monitor CPU, memory, request volume and response time during periods of high traffic.
- Configure suitable resource limits to prevent excessive resource consumption.
- Use request validation to reject invalid submissions before they consume unnecessary processing resources.
- Apply request rate limiting where appropriate to reduce excessive or abusive requests.

If the selected platform supports automatic scaling, the service may increase its available application instances according to traffic demand.

However, scaling the application does not automatically guarantee database scalability. Database capacity and connection limits should also be considered.

## 6. Backup and Recovery

Persistent questionnaire data should be protected against accidental loss and service failures.

The proposed measures include:

- Use persistent database or storage services rather than temporary application storage.
- Configure regular backups where supported by the selected cloud service.
- Restrict access to backup files.
- Define a recovery procedure for restoring data after a failure.
- Test backup restoration periodically.

The application should also be tested after a service restart to verify that previously submitted questionnaire responses remain available.

## 7. Current Implementation Status

The measures in this document describe the proposed cloud deployment design. They should not be interpreted as proof that cloud security or monitoring features have already been implemented.

| Feature | Current Status |
|---|---|
| HTTPS configuration | Proposed; pending cloud deployment |
| Cloud access control | Proposed; pending platform selection |
| Secure secret management | Proposed; pending deployment configuration |
| Application logging | To be confirmed with C1 implementation |
| Cloud monitoring and alerts | Proposed; pending platform selection |
| Automatic scaling | Proposed; subject to platform capabilities |
| Persistent cloud storage | Pending application and platform integration |
| Backup and recovery | Proposed; pending implementation and testing |

## 8. Dependencies and Next Steps

The final configuration of these measures depends on information from other project members:

- **Member 1 (B1):** Final cloud provider recommendation, selected hosting services, storage services and available monitoring features.
- **Member 4 (C1):** Application runtime, database implementation, logging behaviour, health-check endpoint and data persistence requirements.
- **Member 5 (C2):** Integrate the confirmed information into the deployment configuration and verify the security and monitoring arrangements.

After the application and cloud platform are confirmed, the proposed measures should be updated to reflect the actual deployment configuration and test results.
