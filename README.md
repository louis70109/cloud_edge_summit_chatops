## Prerequisite

- Docker
- Terminal

## 下載 Virtual Box 的映像檔

- image url

```
ssh -p 3022 demo@localhost
su -
```

## 在 Ubuntu 上安裝 Docker

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

### 如果有遇到無法安裝 docker-ed 的問題

```
apt-cache madison docker-ce # find version
sudo apt-get install docker-ce=<VERSION_STRING> docker-ce-cli=<VERSION_STRING> containerd.io
```

## 安裝 cluster 相關套件

- 安裝 `k3d`

```
wget -q -O - https://raw.githubusercontent.com/rancher/k3d/main/install.sh | bash
```

- 安裝 `kubectl` command line

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

如果是第一次透過 VM 拉取 GitHub 資源可能會出現無法拉取的資訊

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
```

- `prometheus/`: 收集 Metrics 使用
- `api/`: 測試用的 API

## 在 VM 中安裝 Python

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
apt install python3-pip
sudo apt install python3.8
```

### 透過 bot-proxy 建立 LINE Bot 到 VM 中

```
cd bot_proxy/
mv .env.example .env # vim to edit it
python3 api.py
```


### 在本機 Mac || Windows 開啟一個視窗並使用以下指令

> 需要安裝 NodeJS

```
npx ngrok http --authtoken 'YOUR_NGROK_TOKEN' -region=ap --host-header=rewrite IP:31112
```

refs: https://ngrok.com/docs

## 測試 - 持續呼叫 API 

Use following code at another Terminal by Bash

```
while [ 1 ]
do
        curl IP:31110; sleep 1s
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
