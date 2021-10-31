## Prerequisite

- Docker

## Download Virtual Box

- image url

```
ssh -p 3022 demo@localhost
su -
```

## Install Docker into Ubuntu

```
sudo apt-get update -y
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
 echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install docker-ce docker-ce-cli containerd.io -y
sudo docker run hello-world
```

### If you can't install docker-ed

```
apt-cache madison docker-ce # find version
sudo apt-get install docker-ce=<VERSION_STRING> docker-ce-cli=<VERSION_STRING> containerd.io
```

## Install cluster package

- Install `k3d`

```
wget -q -O - https://raw.githubusercontent.com/rancher/k3d/main/install.sh | bash
```

- Install `kubectl` command line

```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
chmod +x kubectl
mkdir -p ~/.local/bin/kubectl
mv ./kubectl ~/.local/bin/kubectl
```

> source from https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/

- Clone example project

```
git clone git@github.com:louis70109/cloud_edge_summit_chatops.git
```

### 狀況排除

you may see the fail message.

use blow command line to create SHA key

```
ssh-keygen
cat .ssh/id_rsa.pub
```

copy your public key to GitHub page and git clone again.

## Apply example to cluster

```
cd cloud_edge_summit_chatops/
k3d cluster create testcluster --agents 1 -p "31110-31112:31110-31112@server:0"
kubectl create ns kube-ops
kubectl apply -f prometheus/
kubectl apply -f api/
# kubectl apply -f bot_proxy/
```

- `prometheus/`: 收集 Metrics 使用
- `api/`: 測試用的 API
- `bot_proxy/`: 即時查看的 chatbot

open new terminal

```
npx ngrok http --authtoken 'YOUR_NGROK_TOKEN' -region=ap --host-header=rewrite IP:31112
```

refs: https://ngrok.com/docs

## Install Python

```
sudo add-apt-repository ppa:deadsnakes/ppa
```
## Testing

Use following code by Bash

```
for VARIABLE in 1 .. 100
do
        curl localhost:31110; sleep 1s
done
```

## Other 

Mac user:

```
brew install k3d
brew install kubectl
```

Prometheus query:

- rate(process_cpu_seconds_total{job="service"}[1m])
