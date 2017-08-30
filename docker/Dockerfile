FROM microsoft/dotnet:1.1.2-sdk

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cron \
        fcgiwrap \
        python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /alpacka-meta

# Restore seperate, as per example: https://github.com/dotnet/dotnet-docker-samples/blob/master/dotnetapp-dev/Dockerfile
COPY alpacka-meta-fork/alpacka.meta.csproj ./
RUN dotnet restore

COPY alpacka-meta-fork/. ./
RUN dotnet publish -c Release -o out
# dll is now in /alpacka-meta/out/alpaca-meta.dll

# Login info
WORKDIR /root/.config/alpacka.meta
COPY curse.yaml ./

# prep cron
COPY crontab /etc/cron.d/hello-cron
RUN chmod 0644 /etc/cron.d/hello-cron
RUN touch /var/log/cron.log

WORKDIR /root
# Python module
COPY CurseMeta ./
# Run & CGI scripts
COPY *.sh ./
RUN chmod +x *.sh

# Start on-demand fetch, run 1 complete, start cron
CMD spawn-fcgi -s /data/fcgiwrap.socket /usr/sbin/fcgiwrap && chmod og+rw /data/fcgiwrap.socket \
    && ~/run.sh Complete \
    && cron && tail -f /var/log/cron.log
