# AWS S3 tools and clients
## S3fs
S3fs是基于FUSE的文件系统，允许Linux和macOS挂载KS3存储桶在本地文件系统
- https://github.com/s3fs-fuse/s3fs-fuse
## CloudBerry
CloudBerry Explorer 是业界开发的一Windows 下直接通过 CloudBerry Explorer 来接入并管理对象存储的文件浏览器。
- https://www.msp360.com/explorer/windows/
## S3 Browser
S3 Browser是一种易于使用和强大的Amazon S3免费客户端。
- https://s3browser.com/ 
## MinIO Client
Minio Client 简称mc，是minio服务器的客户端，对ls，cat，cp，mirror，diff，find等UNIX命令提供了一种替代方案，它支持文件系统和兼容Amazon S3的云存储服务（AWS Signature v2和v4）。
- https://min.io/docs/minio/linux/reference/minio-mc.html
- https://github.com/minio/mc
## Rclone
Rclone是一个的命令行工具，用于管理云存储上的文件，支持在不同对象存储、网盘间同步上传、下载数据。
- https://rclone.org/
- https://github.com/rclone/rclone

## S3 cmd
S3cmd 是免费的命令行工具和客户端，用于在 Amazon S3 和其他兼容 S3 协议的对象存储中上传、下载和管理数据。
- https://s3tools.org/s3cmd
- https://github.com/s3tools/s3cmd

## ExpanDrive
ExpanDrive 是一款支持多种云存储服务的文件管理工具，支持将云存储挂载为本地磁盘，支持Windows和macOS。
- https://www.expandrive.com/

## Goofys
**warning:** 2 年没更新了维护了
Goofys是一个开源的使用Go编写的存储桶挂载工具，允许Linux和macOS挂载KS3存储桶在本地文件系统
- https://github.com/kahing/goofys

使用mac m3 根据官方文档安装goofys 失败了

```shell
brew install --cask osxfuse
==> Purging files for version 3.11.2 of Cask osxfuse
Error: Failure while executing; `/usr/bin/sudo -u root -E LOGNAME=xiaowely USER=xiaowely USERNAME=xiaowely -- /usr/sbin/installer -pkg /opt/homebrew/Caskroom/osxfuse/3.11.2/Extras/FUSE\ for\ macOS\ 3.11.2.pkg -target /` exited with 1. Here's the output:
installer: Error - The FUSE for macOS installation package is not compatible with this version of macOS.

咨询 claude 提示使用 macfuse 替代 osxfuse
brew install --cask macfuse # install success

brew install goofys
Error: goofys has been disabled because it does not build! It was disabled on 2024-02-12.
```
download the goofys binary from the release page and install it manually`
```shell
wget https://github.com/kahing/goofys/releases/latest/download/goofys

chmod +x goofys
~/.aws/credentials
[default]
aws_access_key_id =  MY-SECRET-ID
aws_secret_access_key = MY-SECRET-KEY
$ .goofys <bucket> <mountpoint>
2025/01/22 03:10:08.273005 main.FATAL Unable to mount file system, see syslog for details
```


