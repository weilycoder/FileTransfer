# 文件传输器

[![Release](https://img.shields.io/github/v/release/weilycoder/FileTransfer)](https://github.com/weilycoder/FileTransfer/releases/)
[![github](https://img.shields.io/badge/github-FileTransfer-blue?logo=github)](https://github.com/weilycoder/FileTransfer)
[![Test PyPI](https://img.shields.io/badge/Test_PyPI-FileTransfer-blue?logo=pypi)](https://test.pypi.org/project/weily-FileTransfer/)
[![sata-license](https://img.shields.io/badge/License-SATA-green)](https://github.com/zTrix/sata-license)
![Stars](https://img.shields.io/github/stars/weilycoder/FileTransfer)
![Forks](https://img.shields.io/github/forks/weilycoder/FileTransfer)

用于在学校机房传输文件。

使用命令行启动，不带任何参数默认以上一次启动设置启动（读取配置文件），使用 `--mode client` 启动客户端，`--mode server` 启动服务端。前者有 UI，后者仅在命令行显示简单日志。

具体地，使用 `-h` / `--help` 查看详细信息：

```plain
usage: <Filename> [-h] [--mode {client,server}] [-i HOST] [-p POST] [--timeout TIMEOUT] [--superpasswd SUPERPASSWD] [-b BUF]

Launch the File Transfer.

optional arguments:
  -h, --help            show this help message and exit
  --mode {client,server}
                        Specify the launch mode.
  -i HOST, --host HOST  set the server name
  -p POST, --post POST  set the communication port
  --timeout TIMEOUT     set the timeout in second
  --superpasswd SUPERPASSWD
                        set a super password, only effective when starting in server mode
  -b BUF, --buf BUF     set buffer size, which must be greater than or equal to 1024
```

另外，使用 `weily-FileTransfer/server.py` 和 `weily-FileTransfer/client.py` 启动可以直接启动服务端或客户端；默认设置是上一次服务端或客户端启动的设置。使用这两个脚本启动不会将启动模式写入配置文件。

## 细节

实现了 4 种请求：获取文件列表、上传文件、删除文件、下载文件。

实现了简单的权限控制：若上传文件时指定了非空密码，则删除文件或下载文件时要提供相同密码，或者提供超级密码。

![Demo](https://github.com/weilycoder/FileTransfer/blob/main/demo.png)

## 下载

项目上传了 Test PyPI，你可以运行以下命令下载最新版，或者从 Release 页面获取。

```bash
pip install -i https://test.pypi.org/simple/ weily-FileTransfer
```

## Bugs

详见 [issues 相关页面](https://github.com/weilycoder/FileTransfer/issues/1)。

## 许可证和声明

项目文件没有特殊声明的，使用 [SATA](https://github.com/zTrix/sata-license) 许可证，如果你使用了我的项目并觉得它有用，请为我点赞。

SATA 基于 MIT 许可证，允许你在保留原始版权通知和许可条款的前提下，自由地使用、复制、修改、合并、出版发行、散布、再授权和/或销售软件及其副本。
