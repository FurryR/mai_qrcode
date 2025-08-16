#!/bin/sh

ARCH="$(uname -m)"

case "$ARCH" in
    x86_64)
        wget -O /tmp/wechat.deb "https://dldir1v6.qq.com/weixin/Universal/Linux/WeChatLinux_x86_64.deb"
        ;;
    aarch64)
        wget -O /tmp/wechat.deb "https://dldir1v6.qq.com/weixin/Universal/Linux/WeChatLinux_arm64.deb"
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac