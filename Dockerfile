FROM python:3.6 AS tg_bot_base
RUN mkdir ~/.pip
RUN echo "[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple" | tee ~/.pip/pip.conf
COPY requirements /tmp/requirements
RUN pip install -r /tmp/requirements

FROM tg_bot_base

COPY tg_bot /app
WORKDIR /app
RUN mkdir -p session
RUN mkdir -p db
ENTRYPOINT [ "python", "run.py" ]