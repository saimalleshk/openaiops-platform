# OpenAIOps Platform — Environment Baseline

## Objective
Build an open-source, locally hosted platform to practice application
delivery, DevOps, SRE, observability, and AIOps engineering.

## Host Environment
- Operating system: Windows with WSL2
- Linux distribution: Ubuntu 26.04.1 LTS
- Linux kernel: 6.18.54.1-microsoft-standard-WSL2
- CPU: 4 logical processors
- Memory: 7.7 GiB total; 5.7 GiB available at discovery
- Root filesystem: approximately 953 GB available

## Development Tools
- Python: 3.14.4
- Git: 2.53.0
- Docker: 29.8.2
- kubectl: 1.36.1
- Terraform: not installed at discovery

## Kubernetes
- Context: docker-desktop
- Node: desktop-control-plane
- Initial node status: Ready

## Existing Workloads
The cluster already contains transaction-risk workloads,
workloads in the funny namespace, and Prometheus in monitoring.
These resources must not be modified or deleted by this project.

## Engineering Constraints
- Prefer open-source tools.
- Run locally before considering cloud deployment.
- Introduce services incrementally due to limited memory.
- Isolate project resources in a dedicated directory and namespace.
- Validate each stage before proceeding.

## Initial Architecture Direction
Python API -> PostgreSQL -> Docker -> Kubernetes ->
OpenTelemetry and Prometheus/Grafana -> AIOps analytics.

Architecture and technology choices will be refined as each stage is validated.
