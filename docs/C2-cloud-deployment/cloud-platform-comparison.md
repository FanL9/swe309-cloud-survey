# Cloud Platform Comparison

**Course:** SWE309
**Role:** Member 5 - C2 Cloud Deployment
**Research date:** 23 November 2026
**Status:** Preliminary comparison

## 1. Objective

This document compares two cloud providers using
different hosting models:

- Microsoft Azure Virtual Machines (IaaS)
- Google Cloud Run (PaaS / Serverless)

The comparison considers operational complexity,
student eligibility, regional availability, storage,
security, monitoring and cost.

## 2. Platform Comparison

| Criteria | Azure Virtual Machines | Google Cloud Run |
|---|---|---|
| Provider | Microsoft | Google |
| Service model | IaaS | PaaS / Serverless |
| OS management | Customer-managed | Provider-managed |
| Application runtime | Customer-configured | Container-based |
| Scaling | VM configuration or VM Scale Sets | Automatic scaling |
| Scale to zero | No, not for a normal VM | Supported |
| Persistent storage | Managed Disks or external database | External database or storage |
| Access control | Azure RBAC | Cloud IAM |
| Monitoring | Azure Monitor | Cloud Monitoring and Logging |
| Student offer | Azure for Students | Google Cloud Free Tier |
| Payment requirement | No credit card for eligible students | Billing account and valid payment method required |

## 3. Student Eligibility

### Microsoft Azure

Azure for Students provides eligible students
with USD 100 in credits for one year.

A credit card is not required.

Eligibility and service availability must be
verified before deployment.

### Google Cloud

Google Cloud provides a free usage tier for
selected services.

Cloud Run includes a monthly free usage allowance.

However, a valid Cloud Billing account is required.
The payment method requirement must be considered
before selecting this platform for actual deployment.

## 4. Regional Availability

Azure provides a Malaysia West region in Kuala Lumpur.

Google Cloud Run supports Singapore and Kuala Lumpur
regions.

The final region must be selected according to
service availability, latency and cost.

## 5. Preliminary Assessment

Azure is attractive because of its student credit
and no-credit-card eligibility.

Google Cloud Run is attractive because it reduces
infrastructure management and supports automatic
scaling to zero.

The final recommendation has not yet been made.

It must be aligned with the group's Part B-I
platform recommendation and verified pricing estimates.

## 6. Outstanding Research

- Verify exact student subscription eligibility.
- Verify the availability of required services.
- Compare database and object storage costs.
- Estimate monthly costs using official pricing calculators.
- Compare access control and monitoring features.
- Confirm the final recommendation with the group.

## 7. Sources

1. Microsoft Azure for Students:
   https://learn.microsoft.com/azure/education-hub/about-azure-for-students

2. Google Cloud Run Pricing:
   https://cloud.google.com/run/pricing

3. Google Cloud Free Tier:
   https://docs.cloud.google.com/free/docs/free-cloud-features

4. Azure Regions:
   https://learn.microsoft.com/azure/reliability/regions-list
