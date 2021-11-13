# 手把手透過 LINE Bot 打造出雲端的 ChatOps

## 事前準備

- Virtual Box
  - 版本：v6.1.28
  - [下載處](https://www.virtualbox.org/wiki/Downloads)
- NodeJS: v14.15.5
- Python: 3.9
- 終端機
  - iTerm
  - WSL2

## 下載 Virtual Box 的映像檔

[Google Drive](https://drive.google.com/file/d/14OxBvbDGd1ue4dooP9HPcXov5-EB1TQG/view?usp=sharing)


```
ssh -p 3022 demo@VM_IP
su -
```

> 為展示方便使用 Root 權限，於伺服器上要做好權限管理喔！

### 取得 VM IP

```
ifconfig | grep 1
```

## 在 Ubuntu 上安裝 Docker + netools (ifconfig)

```
sudo apt-get update -y
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release net-tools -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install docker-ce docker-ce-cli containerd.io -y
sudo docker run hello-world
```

## 在 VM 中安裝 Python 環境

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update -y
sudo apt-get install python3-pip -y
sudo apt-get install python3.8 -y
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

- Clone 範例專案

```
git clone https://github.com/louis70109/cloud_edge_summit_chatops.git
```

### 狀況排除

如果是第一次透過 VM 拉取 GitHub 資源可能會出現無法拉取的資訊

使用以下指令來建立 SHA

```
ssh-keygen
cat .ssh/id_rsa.pub
```

複製公鑰到 GitHub 的 settings 上

## 把範例程式 Apply 到 k3d cluster

```
cd cloud_edge_summit_chatops/
k3d cluster create testcluster --agents 1 -p "31110-31112:31110-31112@server:0"
kubectl create ns kube-ops
kubectl apply -f prometheus/
kubectl apply -f api/
```

- `prometheus/`: 收集 Metrics 使用
- `api/`: 測試用的 API

### 透過 bot-proxy 建立 LINE Bot 到 VM 中，當中間層 LINE 與 Cluster 溝通橋樑

```
cd bot_proxy/
mv .env.example .env # vim to edit it
pip3 install -r requirements.txt --user
python3 api.py
```

### 在本機 Mac || Windows 開啟一個視窗並使用以下指令

> 需要安裝 NodeJS, 以及到 ngrok 官網上註冊會員
> NodeJS 下載： https://nodejs.org/zh-tw/download/

```
npx ngrok http --authtoken 'YOUR_NGROK_TOKEN' -region=ap --host-header=rewrite IP:8000
```

refs: https://ngrok.com/docs

## 測試 - 持續呼叫 API

透過下列的 Bash 來持續呼叫範例 Item API 的 Deployment

```
while [ 1 ]
do
        curl IP:31110/items; sleep 1s
        curl -X POST IP:31110/items; sleep 1s
        curl -X POST IP:31110/items\?name=1; sleep 1s
done
```

> 再透過 chatbot 看看狀態吧！

![](https://github.com/louis70109/cloud_edge_summit_chatops/blob/master/readme_images/chatbot_result.png)

## 延伸

可以透過 [lens](https://github.com/lensapp/lens) 或 k9s 相關的工具來查看目前 Cluster 內的狀態，以下為透過 k9s 看的狀態

![](https://github.com/louis70109/cloud_edge_summit_chatops/blob/master/readme_images/k3d.png)

### 取得 namespace 下的內容

因為有建立 namespace，因此敲指令時都要加上 `-n`

```
kubectl get pods -n kube-ops
kubectl get svc -n kube-ops
```

### Mac 用戶

如果你是使用 Mac，可以透過 brew 來安裝 k3d 以及 kubectl 於環境

```
brew install k3d
brew install kubectl
```

### Prometheus query:

- rate(process_cpu_seconds_total{job="service"}[1m])

## LICENSE

[MIT](https://github.com/louis70109/cloud_edge_summit_chatops/blob/master/LICENSE)

歡迎分享出去給更多人參考使用！
