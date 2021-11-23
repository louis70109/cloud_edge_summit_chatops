# 手把手透過 LINE Bot 打造出雲端的 ChatOps

- 透過 K3D 本地端部署 Kubernetes 集群
- 快速打造並且上線自己的官方帳號 (LINE Bot)
- 透過 LINE Bot 來監控 Kubernetes 集群狀況

## 事前準備

大家可以使用 Mac、Windows、Linux 各種作業系統，在這次的工作坊中會在 Docker 裡面建置 Cluster 的環境，並且透過電腦的終端機來操作環境內的服務。

- Virtual Box
  - 版本：v6.1.28
  - [下載處](https://www.virtualbox.org/wiki/Downloads)
- [NodeJS](https://nodejs.org/zh-tw/download/): v14.15.5
- Python: 3.9
- 終端機
  - iTerm
  - WSL2

## 下載 Virtual Box 的映像檔 (Optional)

[Google Drive](https://drive.google.com/drive/folders/1y_UAXphvMcl8-wSdfJaD2kyhq4Q8XMHZ?usp=sharing)

把 Virtual Box 網路從 **NAT** 改成 **橋接介面卡**

```
ssh demo@VM_IP  # default pwd 123456
sudo passwd root
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

## LINE Bot 官方帳號建立

- 至 [LINE Developer Console](https://developers.line.biz/console/) 註冊一個 LINE Bot
- 先建立 Provider
- 接著建立 Messaging API(LINE Bot)
- 更改**自動回應**的設定
- 頁面先保留起來

![](https://github.com/louis70109/Screen-LINE-Bullets/blob/master/LINE-bot-step.jpg)

### 狀況排除

- 如再更改 Official Account Manager 中的**進階設定**時沒看到任何的 LINE Bot 資訊
- 請先在 OA Manager 中先建立一支 LINE Bot 後
- 再重新於 Developer Console 中建立 LINE Bot 重新一次流程即可

![](https://github.com/louis70109/cloud_edge_summit_chatops/blob/master/readme_images/oa_manager.png)

## 透過 bot-proxy 建立 LINE Bot 到 VM 中，當中間層 LINE 與 Cluster 溝通橋樑

```
cd bot_proxy/
mv .env.example .env # vim to edit it
pip3 install -r requirements.txt --user
python3 api.py
```

## 在本機 Mac || Windows 開啟一個視窗並使用以下指令

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
