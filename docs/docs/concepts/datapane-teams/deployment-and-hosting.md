# Deployment and Hosting

Datapane Teams is a client-server architecture consisting of a local, open source Python library and a hosted server component.&#x20;

For Datapane’s server component, we provide the following deployment options:

**Managed Hosting** is suitable if:

* You want to start immediately
* You don't want to manage Datapane on your infrastructure
* You want an out-of-the-box, secure solution
* You want to get automatic updates with all the latest features

**Self-hosted** is suitable if:

* You don't want any data to leave your infrastructure (e.g. HIPAA, SOC2)
* You want to deploy, manage, upgrade, and configure Datapane yourself&#x20;

**Managed - Customer VPC** is suitable if:

* You want us to deploy, manage, optimize, and update Datapane for you on your own VPC on your cloud platform
* You need on-premise but don’t have internal DevOps resource

## Managed Hosting

* Runs on Datapane's infrastructure
* Deployed by Datapane
* Auto-scaling Kubernetes
* Updates and migrations managed by us
* Data leaves your infrastructure

### Overview

Datapane provides a managed instance on a custom domain. Datapane provisions the customer an isolated instance with its own single-tenant web-server and an isolated database. Data is stored on a single-tenant Google Cloud Storage bucket, which is encrypted at rest.&#x20;

Datapane will upgrade, administer, and maintain the server. Core data leaves the customer’s network and enters the Datapane network where it is protected by the security measures below.

### Security Measures

* Binary data and assets are stored on Google Cloud Storage, and user data and report metadata is stored in Google Cloud SQL (isolated per customer). In both mechanisms, data is encrypted at rest. For technical information, see the [Google Cloud FAQs](https://cloud.google.com/sql/faq#encryption).&#x20;
* Scripts are stored on single-tenant Google Cloud Storage buckets which are encrypted at rest. Execution of scripts happens in an isolated environment which is namespaced to the tenancy and is fully sandboxed.
* Our endpoints are TLS/SSL only
* We use audit logs on Google Cloud to provide an audit trail over infrastructure and the Datapane platform, allowing security analysis and audit access
* Datapane API requests are authenticated using secure private tokens over TLS/SSL.
* Each user has a private account which is not shared with other instances and operates in a separate database. Users cannot authenticate across tenancies.
* Secure signed URLs can be generated for reports, automatically expire after a user-defined period, and can revoked on request.

## Self-hosted (Docker)

* Run on your infrastructure
* Docker-compose deployment
* Deployed by you
* Updates and migrations managed by you
* Telemetry data leaves your infrastructure

{% hint style="info" %}
For instructions for self-hosting Datapane, please see [https://github.com/datapane/datapane-onpremise](https://github.com/datapane/datapane-onpremise)
{% endhint %}

### Overview

Datapane provides a docker-compose setup which customers can deploy on their own cloud or server environment. Core data never leaves the customer’s network, although telemetry data will leave the network for billing and analytics purposes.&#x20;

Extensive documentation is provided, and deploying, administering, and maintaining the server is the responsibility of the customer.&#x20;

This may include:&#x20;

* Installing the docker-compose services
* Keeping the server up-to-date
* Managing storage, database, and cache backends&#x20;
* Creating SSL certificates and load balancers

## **Enterprise (Cloud-first on-premise)**&#x20;

### **Overview**

* Run on your infrastructure
* AMI/Kubernetes/docker-compose
* Can be deployed and managed by Datapane
* Updates/migrations managed by Datapane
* No data leaves your infrastructure

Datapane deploys, manages, and maintains a server on your private VPC. No telemetry data will leave your network. Datapane will customize the Datapane instance for your specific requirements, including (but not limited to):

* Optimized database, blob storage, cache support using your cloud provider primitives (e.g. RDS, S3)
* Authentication and authorization integrations
* HTTPS/TLS gateway support and setup
* Email alerting and reporting integrations
* Custom cloud region deployments

Datapane’s team will update and maintain the server based on pre-agreed upgrade policy. Solutions engineering for Datapane Apps and Report building and custom integrations and services can be provided.
