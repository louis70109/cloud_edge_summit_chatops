## Prerequisite
- Docker
- MacOS first
  - Linux
  - Windows

```
brew install k3d
brew install kubectl
k3d cluster create nijiacluster --agents 1 -p "31110-31111:31110-31111@server:0"
kubectl create ns kube-ops
kubectl apply -f prometheus/
kubectl apply -f api/
```
Prometheus query:
- rate(process_cpu_seconds_total{job="service"}[1m]) 