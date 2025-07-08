#!/bin/bash
# 下载DocumentDB SSL证书
echo "下载DocumentDB SSL证书..."
wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -O rds-combined-ca-bundle.pem
echo "证书下载完成"
