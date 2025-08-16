FROM docker.1ms.run/debian:latest
ARG DEB_REPO=http://deb.debian.org/debian
ARG PYPI_REPO=https://pypi.org/simple


RUN echo "Types: deb" > /etc/apt/sources.list.d/debian.sources && \
    echo "URIs: ${DEB_REPO}" >> /etc/apt/sources.list.d/debian.sources && \
    echo "Suites: trixie trixie-updates trixie-backports" >> /etc/apt/sources.list.d/debian.sources && \
    echo "Components: main contrib non-free non-free-firmware" >> /etc/apt/sources.list.d/debian.sources && \
    echo "Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg" >> /etc/apt/sources.list.d/debian.sources && \
    echo >> /etc/apt/sources.list.d/debian.sources
RUN echo "Types: deb" >> /etc/apt/sources.list.d/debian-security.sources && \
  echo "URIs: ${DEB_REPO}-security" >> /etc/apt/sources.list.d/debian-security.sources && \
  echo "Suites: trixie-security" >> /etc/apt/sources.list.d/debian-security.sources && \
  echo "Components: main contrib non-free non-free-firmware" >> /etc/apt/sources.list.d/debian-security.sources && \
  echo "Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg" >> /etc/apt/sources.list.d/debian-security.sources

RUN DEBIAN_FRONTEND='noninteractive' apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get install -y --no-install-recommends python3 python3-pip wget python3-pdm python3-dev python3-tk libzbar0t64 busybox git
RUN DEBIAN_FRONTEND='noninteractive' apt-get install -y --no-install-recommends xorg xserver-xorg-input-evdev xserver-xorg-input-all dbus-x11 tigervnc-standalone-server
RUN DEBIAN_FRONTEND='noninteractive' apt-get install -y --no-install-recommends libxkbcommon0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-render0 libxcb-image0 libxcb-render-util0 libxcb-keysyms1 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libpango-1.0-0 libcairo2 libasound2t64 libxdamage1
RUN DEBIAN_FRONTEND='noninteractive' apt-get install -y --no-install-recommends locales
COPY download_wechat.sh /download_wechat.sh
RUN chmod +x /download_wechat.sh
RUN /download_wechat.sh
RUN DEBIAN_FRONTEND='noninteractive' apt-get install -y /tmp/wechat.deb
RUN DEBIAN_FRONTEND='noninteractive' apt-get clean && rm -rf /var/lib/apt/lists/*
RUN rm /tmp/wechat.deb
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8

COPY app/pyproject.toml /app/pyproject.toml
RUN pdm config pypi.url "${PYPI_REPO}"
RUN cd /app && pdm install
COPY app/.env /app/.env
COPY app/src /app/src

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
