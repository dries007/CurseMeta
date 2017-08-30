FROM microsoft/dotnet

RUN apt-get update && apt-get upgrade \
    && apt-get install -y --no-install-recommends \
        fcgiwrap \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /cgi && chmod 777 /cgi
COPY getinfo.sh /cgi/getinfo.sh
COPY run.sh /run.sh
RUN mkdir -p /root/.config/alpacka.meta
COPY curse.yaml /root/.config/alpacka.meta/curse.yaml
RUN chmod +x /run.sh && chmod 777 /cgi/getinfo.sh

CMD /run.sh
