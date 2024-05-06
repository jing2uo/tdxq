FROM python
WORKDIR /root/
RUN rm -rf /etc/apt/sources.list* &&  \
    echo "deb http://mirrors.ustc.edu.cn/debian sid main contrib non-free" > /etc/apt/sources.list && \
    apt update && apt install wget gcc unrar make file pkg-config libpq-dev -y && apt clean

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -O talib.tar.gz && \
    tar xf talib.tar.gz && cd ta-lib && ./configure --prefix=/usr && make && make install

RUN wget http://www.tdx.com.cn/products/autoup/cyb/linuxtool.rar -O linuxtool.rar && \
    unrar x linuxtool.rar && rm linuxtool.rar && \
    mv v4/datatool /usr/bin/ && chmod a+x /usr/bin/datatool

WORKDIR /qtdx
COPY . .
RUN pip install -i https://mirrors.ustc.edu.cn/pypi/web/simple --no-cache-dir -r requirements.txt
