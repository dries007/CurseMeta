FROM microsoft/dotnet:sdk

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fcgiwrap \
    && rm -rf /var/lib/apt/lists/*

ENV XDG_CACHE_HOME /
ENV XDG_CONFIG_HOME /

RUN git clone https://github.com/NikkyAI/alpacka-meta.git \
    && cd alpacka-meta \
    && dotnet restore

RUN mkdir /cgi && chmod 777 /cgi && mkdir /alpacka.meta && chmod og+r /alpacka.meta
COPY getinfo.sh /cgi/getinfo.sh
COPY run.sh /run.sh
# COPY curse.yaml /alpacka.meta/curse.yaml
RUN chmod +x /run.sh && chmod 777 /cgi/getinfo.sh

CMD /run.sh
