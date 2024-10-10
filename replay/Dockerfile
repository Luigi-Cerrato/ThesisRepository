
FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ARG NGINX_VERSION=1.18.0
ARG RTMP_MODULE_VERSION=1.2.2

ENV PATH $PATH:/usr/local/nginx/sbin

# Install required packages
RUN apt-get update && apt-get install -q -y --no-install-recommends \
    pciutils wget curl unzip libbz2-dev net-tools dnsutils ifupdown procps iputils-ping apache2 telnet \
    build-essential libpcre3 libpcre3-dev zlib1g-dev libssl-dev python3-pyftpdlib tcpreplay tcpdump nano ethtool \
    python3-setuptools scapy tshark python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and extract nginx and nginx-rtmp-module
RUN wget -c http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz -O - | tar -xz && \
    wget -c --no-check-certificate https://github.com/arut/nginx-rtmp-module/archive/v${RTMP_MODULE_VERSION}.tar.gz -O - | tar -xz

# Build and install nginx with rtmp module
WORKDIR /nginx-${NGINX_VERSION}

RUN ./configure --add-module=/nginx-rtmp-module-${RTMP_MODULE_VERSION} --with-debug \
    --http-log-path=/var/log/nginx/access.log \
    --error-log-path=/var/log/nginx/error.log \
    --conf-path=/etc/nginx/conf/nginx.conf && \
    make && make install

# Add configuration files and scripts
ADD nginx.conf /etc/nginx/conf/nginx.conf
ADD ftp_server.py prep.sh fragment_pcap.py normal_IoT_2Finale.pcap MITM_normal1Finale.pcap injection_normal1Finale.pcap / 

# Make scripts executable
RUN chmod +x /ftp_server.py /prep.sh /fragment_pcap.py

WORKDIR /

# Set the default command to run prep.sh
CMD ["/prep.sh"]