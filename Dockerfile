FROM python:3.8 AS tg_bot_base

RUN mkdir -p ~/.pip \
    && echo "[global]\nindex-url = https://pypi.mirrors.ustc.edu.cn/simple/" | tee ~/.pip/pip.conf \
    && git config --global http.sslverify false \
    && sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

FROM tg_bot_base

COPY tg_stats_bot /app
WORKDIR /app
RUN mkdir -p session
RUN mkdir -p db
ENTRYPOINT [ "python", "run.py" ]
