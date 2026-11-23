# Cloud Deployment Basics

Course:SWE309 - Introduction to Cloud Computing  
Mission:Cloud Deployment  
Status:Initial learning and planning

## 1. Purpose

This document records the basic concepts required for the cloud deployment task and establishes an initial deployment checklist.

The objective is to understand how the survey application can be hosted, configured, secured, monitored and maintained in a cloud environment.

## 2. Basic Deployment Concepts

| Concept | Explanation | Relevance to the Survey System |
|---|---|---|
| Application | The software that provides the system functions | Accepts and validates survey responses |
| Runtime | The environment required to execute the application | Python version and required libraries |
| Container Image | A packaged application environment | Can package the application and its dependencies |
| Container | A running instance created from an image | Runs the survey application |
| Hosting Service | The platform that runs the application | Provides the environment for the survey system |
| Database | A structured system for storing records | Stores survey responses |
| Object Storage | Storage for files and exported data | Stores CSV exports and reports |
| Port | A network endpoint used by an application | Allows the hosting service to route requests |
| HTTPS | Encrypted communication over HTTP | Protects communication between users and the application |
| Monitoring | Collecting system health and performance information | Helps identify errors and resource usage |

## 3. Proposed Deployment Workflow

The initial deployment workflow is:

1. Obtain the application source code from the development team.
2. Confirm the programming language, runtime version and dependencies.
3. Confirm the application startup command and listening port.
4. Prepare the hosting environment.
5. Configure persistent data storage.
6. Configure environment variables and access permissions.
7. Enable HTTPS.
8. Test application availability and data persistence.
9. Configure logging and monitoring.
10. Record deployment evidence and limitations.

## 4. Important Deployment Considerations

### 4.1 Application and Runtime

The hosting environment must support the application's programming language and required dependencies.

The exact runtime version and startup command must be confirmed with the application developer.

### 4.2 Persistent Storage

Application files and persistent data should be considered separately.

The deployment design must ensure that survey responses remain available after an application restart or instance replacement.

### 4.3 Security

The deployment plan should consider:

- HTTPS for encrypted communication.
- Access control for authorised staff.
- Environment variables for application configuration.
- Secret management for credentials and sensitive values.
- Protection of personal data.

Actual credentials and secret values must never be committed to GitHub.

### 4.4 Monitoring

The proposed monitoring approach should consider:

- Application logs.
- Request errors.
- Application availability.
- CPU and memory usage.
- Request latency.
- Resource consumption.

### 4.5 Scaling

The hosting solution should be able to handle changes in the number of incoming requests.

The system should also release unnecessary resources when demand decreases, where the selected platform supports this feature.

## 5. Current Project Status

At this stage, the repository contains the project structure and deployment planning documents.

The actual survey application framework, runtime, startup command, port and persistent storage implementation have not yet been confirmed.

Therefore, no public-cloud deployment is claimed to have been completed.

## 6. Information Required Before Deployment

The following information must be confirmed with the application development team:

- Programming language and framework.
- Runtime version.
- Dependency installation instructions.
- Application startup command.
- Listening port.
- Persistent data directory or database configuration.
- Health-check endpoint, if available.
- Required environment variable names.

## 7. Next Actions

1. Continue learning Docker and container fundamentals.
2. Review the hosting and storage options proposed in the project architecture.
3. Confirm application requirements when the development code becomes available.
4. Prepare deployment configuration based on the final platform decision.
5. Perform deployment tests and collect evidence only after the application is ready.
