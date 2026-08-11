# Windows 用户从零安装 WSL2 和 CRISPRMatch

本教程适用于尚未安装 WSL 的 Windows 11 用户。CRISPRMatch 当前按照
Linux/WSL 环境打包，暂不支持直接在原生 Windows 命令行中运行。Windows 用户应通过
WSL2、Ubuntu 和 WSLg 启动图形界面。

## 一、安装前准备

建议配置：

- Windows 11，已安装系统更新；
- 64 位 Intel/AMD 处理器；
- 至少 8 GB 内存；
- 系统盘至少保留 15 GB 空间；
- BIOS/UEFI 中已启用 Intel VT-x 或 AMD-V 虚拟化；
- 能访问 GitHub 和 conda 软件源的网络。

可以在“任务管理器 → 性能 → CPU”中查看“虚拟化”是否显示为“已启用”。

## 二、安装 WSL2 和 Ubuntu 24.04

以管理员身份打开 PowerShell：在开始菜单搜索 `PowerShell`，右键选择“以管理员身份运行”。

执行：

```powershell
wsl --install -d Ubuntu-24.04
```

安装完成后重新启动 Windows。

如果提示 WSL 已经安装，但没有 Ubuntu，可先查看可用发行版：

```powershell
wsl --list --online
wsl --install -d Ubuntu-24.04
```

## 三、完成 Ubuntu 首次初始化

重启后，从开始菜单打开 `Ubuntu 24.04`，或在 PowerShell 中执行：

```powershell
wsl -d Ubuntu-24.04
```

首次启动会要求设置 Linux 用户名和密码。输入密码时终端不会显示字符，这是正常现象。
这个密码以后用于执行 `sudo`，不必与 Windows 密码相同。

回到 Windows PowerShell，检查安装状态：

```powershell
wsl --status
wsl -l -v
```

应看到类似：

```text
NAME            STATE           VERSION
Ubuntu-24.04    Running         2
```

如果 `VERSION` 是 `1`，转换为 WSL2：

```powershell
wsl --set-version Ubuntu-24.04 2
```

然后更新 WSL/WSLg：

```powershell
wsl --update
wsl --shutdown
```

重新打开 Ubuntu 终端。

## 四、安装基础工具

以下命令均在 Ubuntu/WSL 终端中运行：

```bash
sudo apt update
sudo apt install -y git curl ca-certificates
```

注意区分终端：带 `PS C:\...>` 的是 Windows PowerShell；形如
`user@computer:~$` 的是 Ubuntu/WSL。后续 Linux 命令应在 Ubuntu 中运行。

## 五、安装 Miniforge

在 Ubuntu 中运行：

```bash
cd /tmp
curl -L -o Miniforge3.sh \
  https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3.sh -b -p "$HOME/miniforge3"
"$HOME/miniforge3/bin/conda" init bash
source ~/.bashrc
```

确认 conda 可用：

```bash
conda --version
```

国内网络可优先使用清华镜像。CRISPRMatch 的环境只使用 `conda-forge` 和
`bioconda`，可以设置 channel alias：

```bash
conda config --set channel_alias \
  https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
conda config --set channel_priority strict
conda config --set show_channel_urls yes
```

如果镜像同步暂时缺少指定版本，可恢复官方地址：

```bash
conda config --remove-key channel_alias
```

## 六、下载 CRISPRMatch

推荐把项目放在 WSL 的 Linux 主目录中，文件访问速度通常优于 `/mnt/c/`：

```bash
cd ~
git config --global http.version HTTP/1.1
git clone https://github.com/xietiansong/CRISPRMatch-new.git
cd CRISPRMatch-new
```

如果仓库仍为私有，需要仓库管理员添加 Collaborator，并按 GitHub 提示完成浏览器认证。
公开仓库不需要登录即可克隆。

## 七、创建完整运行环境

在项目根目录运行：

```bash
conda env create -f environment.yml
conda activate crisprmatch
```

该环境会同时安装：

- Python 和 PyQt5；
- BWA；
- samtools；
- FLASH；
- pandas、NumPy、SciPy、Matplotlib、pysam 和 pyfaidx；
- CRISPRMatch 本身及测试工具。

安装过程需要下载较多软件包，请等待命令正常结束，不要直接关闭终端。

## 八、验证安装

保持 `crisprmatch` 环境处于激活状态，运行：

```bash
crisprmatch --version
command -v bwa
command -v samtools
command -v flash
bwa 2>&1 | head
samtools --version | head
flash --version
pytest
pytest -m integration
```

预期看到 `crisprmatch 0.1.0`，且常规测试和外部工具测试均通过。

## 九、启动图形界面

主分析界面：

```bash
crisprmatch
```

optimized 双 Barcode 拆分界面：

```bash
crisprmatch-split
```

FLASH 双端 reads 合并界面：

```bash
crisprmatch-merge
```

Windows 11 的 WSLg 会直接显示 Linux 图形窗口，不需要另装 X Server。

## 十、日常使用

以后每次重启电脑，只需打开 Ubuntu，然后运行：

```bash
conda activate crisprmatch
cd ~/CRISPRMatch-new
crisprmatch-split
```

更新项目：

```bash
cd ~/CRISPRMatch-new
git pull --ff-only
conda env update -n crisprmatch -f environment.yml --prune
conda activate crisprmatch
```

## 十一、WSL 无法访问 GitHub

如果出现以下错误：

```text
GnuTLS recv error (-110)
The TLS connection was non-properly terminated
```

先强制 Git 使用 HTTP/1.1：

```bash
git config --global http.version HTTP/1.1
git clone https://github.com/xietiansong/CRISPRMatch-new.git
```

如果仍然失败，可在 Windows PowerShell 中下载：

```powershell
cd "$HOME\Downloads"
git -c http.version=HTTP/1.1 clone https://github.com/xietiansong/CRISPRMatch-new.git
```

然后在 Ubuntu 中复制到 Linux 主目录。把 `<Windows用户名>` 替换为实际用户名：

```bash
cp -a "/mnt/c/Users/<Windows用户名>/Downloads/CRISPRMatch-new" \
  "$HOME/CRISPRMatch-new"
cd "$HOME/CRISPRMatch-new"
```

如果使用代理，WSL 中的 `127.0.0.1` 不一定代表 Windows 主机。应根据代理软件设置
WSL 支持或使用 Windows 端 Git。不要通过关闭 SSL 验证解决问题：

```text
不要运行：git config --global http.sslVerify false
```

## 十二、常见故障

### `0x80370102` 或提示虚拟机无法启动

先确认 BIOS/UEFI 已启用 CPU 虚拟化。然后在管理员 PowerShell 中运行：

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
wsl --set-default-version 2
```

重启 Windows 后重新安装 Ubuntu。

### `conda: command not found`

```bash
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda init bash
source ~/.bashrc
```

### 图形界面没有出现

先在 Windows PowerShell 中运行：

```powershell
wsl --update
wsl --shutdown
```

重新打开 Ubuntu，并检查：

```bash
echo "$DISPLAY"
test -d /mnt/wslg && echo "WSLg OK"
```

如果仍失败，记录启动命令的完整错误信息后提交 Issue。

### `PackagesNotFoundError`

确认 `environment.yml` 中的 channel 是 `conda-forge` 和 `bioconda`，并尝试切回官方
channel alias。不要把 Linux 环境文件拿到原生 Windows conda 中创建，因为 BWA、samtools
和 FLASH 按 Linux/WSL 环境解析。

## 十三、卸载

只删除 CRISPRMatch conda 环境：

```bash
conda deactivate
conda env remove -n crisprmatch
```

删除环境不会影响 GitHub 仓库。项目源代码目录可以保留，以后重新创建环境即可。
