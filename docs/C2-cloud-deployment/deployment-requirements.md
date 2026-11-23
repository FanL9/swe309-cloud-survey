# Cloud Deployment Requirements

## 1. Introduction

This document defines the technical and operational requirements for deploying the questionnaire system to a cloud environment.

The purpose is to identify the resources, configurations and conditions required for a reliable cloud deployment. These requirements will guide the deployment plan and service configuration in C2.

The final implementation will depend on the cloud platform recommended in B1 and the questionnaire application developed in C1.

## 2. Application Hosting Requirements

The cloud environment must provide a suitable hosting service for the questionnaire application.

The hosting service should:

- Support the programming language and runtime used by the application.
- Allow the application to be deployed and updated.
- Provide sufficient CPU and memory resources.
- Support external access through a public endpoint or domain.
- Support application health checks where available.
- Provide application logs for troubleshooting.
- Allow the service to restart or recover after failures.

The final hosting method, runtime version and deployment configuration will be confirmed after the C1 application is completed and the B1 platform selection is finalised.

## 3. Data Storage and Persistence Requirements

The system must preserve submitted questionnaire responses.

The deployment environment should:

- Provide persistent storage for questionnaire data.
- Ensure submitted responses remain available after application restarts.
- Prevent temporary application storage from being used as the only location for important data.
- Restrict database and storage access to authorised services.
- Support data backup and recovery.
- Allow authorised administrators to retrieve or export questionnaire data.

The final storage solution must be compatible with the database and data persistence method implemented in C1.

## 4. Network and Connectivity Requirements

The deployed application must be accessible to authorised users through the internet.

The deployment should:

- Provide a public endpoint or domain for accessing the questionnaire.
- Support HTTPS for encrypted communication.
- Allow necessary application traffic while restricting unnecessary network access.
- Enable communication between the application and its database or storage services.
- Avoid exposing internal database services directly to the public internet.

The exact network configuration will depend on the selected cloud provider and hosting architecture.

## 5. Security and Access Control Requirements

The cloud deployment must protect application resources and submitted data.

The following requirements should be considered:

- Use HTTPS to protect data transmitted between users and the application.
- Apply the principle of least privilege to cloud resource permissions.
- Restrict administrative access to authorised personnel.
- Store passwords, API keys and other secrets securely.
- Prevent sensitive credentials from being committed to the GitHub repository.
- Restrict database and storage access to authorised application services.
- Avoid exposing sensitive questionnaire information in application logs.

The final identity and access management configuration will be determined by the selected cloud platform.

## 6. Monitoring and Logging Requirements

The deployment should provide sufficient monitoring and logging capabilities to identify operational problems.

The system should support:

- Recording application startup and shutdown events.
- Recording successful and unsuccessful questionnaire submissions where appropriate.
- Recording application errors and exceptions.
- Monitoring CPU and memory utilisation.
- Monitoring request volume and response time.
- Monitoring application and database availability.
- Providing alerts for important service failures.

The monitoring configuration should be adjusted according to the capabilities of the selected cloud platform.

## 7. Scalability and Performance Requirements

The cloud environment should be able to handle normal questionnaire usage and temporary increases in traffic.

The deployment should:

- Provide sufficient resources for expected user traffic.
- Support scaling where available.
- Monitor resource utilisation during periods of increased demand.
- Apply input validation to reject invalid submissions.
- Consider database capacity and connection limits.
- Avoid unnecessary resource consumption.

Actual performance targets and scaling configurations should be determined after the application architecture and expected workload are confirmed.

## 8. Backup and Recovery Requirements

The deployment must consider how questionnaire data can be recovered following accidental deletion, system failure or other incidents.

The proposed requirements include:

- Regularly backing up persistent questionnaire data.
- Restricting access to backup files.
- Defining a procedure for restoring data.
- Verifying that data remains available after application restarts.
- Testing backup restoration where possible.

The backup frequency and retention period will be determined according to the selected storage service and project requirements.

## 9. Operational and Cost Requirements

The deployment should be manageable within the operational and financial constraints of the project.

The following requirements should be considered:

- Prefer services available under eligible free-tier or student programmes.
- Avoid unnecessary paid services and resource upgrades.
- Confirm whether a payment card or billing account is required before deployment.
- Monitor resource consumption to avoid unexpected charges.
- Use a deployment approach that can be maintained by a small development team.
- Document deployment steps so that the system can be maintained by other team members.

No paid cloud resources should be activated without confirming the project's budget and obtaining the necessary approval.

## 10. Dependencies and Information Required

Several technical details must be confirmed before the final cloud deployment can be implemented.

| Required Information | Responsible Member | Purpose |
|---|---|---|
| Final cloud platform recommendation | Member 1 (B1) | Determine the deployment environment |
| Selected hosting and storage services | Member 1 (B1) | Identify suitable cloud resources |
| Application programming language | Member 4 (C1) | Confirm runtime compatibility |
| Runtime and dependency versions | Member 4 (C1) | Prepare the execution environment |
| Application startup command | Member 4 (C1) | Configure application deployment |
| Listening port | Member 4 (C1) | Configure network access |
| Database and persistence method | Member 4 (C1) | Configure persistent storage |
| Environment variables | Member 4 (C1) | Configure application settings |
| Health-check endpoint | Member 4 (C1) | Verify application availability |

## 11. Current Status and Limitations

At the current project stage, these requirements represent the proposed deployment criteria rather than a completed cloud implementation.

The following items remain pending:

- Confirmation of the cloud platform through B1.
- Completion and verification of the questionnaire application through C1.
- Confirmation of the application's runtime, dependencies and storage requirements.
- Selection of the final cloud services.
- Actual deployment and cloud environment testing.

These requirements will be updated when the necessary information becomes available.
