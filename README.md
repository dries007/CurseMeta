# CurseMeta v2

Now with 100% LESS C# voodoo.

The old version is under the `full_docker` branch.

## Required software

1. Setup a venv with `pip install -r requirements.txt`
2. Run a redis instance. DB 1 and 2 are used for live and staging.

## Licence

[EUPL v1.2](LICENCE.txt)


## Web icons

The website uses Font Awesome **Pro** 5. (Dries007's personal license)

The FA files must be added in `Frontend/static`, to `css` and `js`.
They CAN NOT be checked into version control. 

Some of the icons may be missing with the free version.


## Maintaining a live environment

`~/purge-cache.sh` should contain a script that purges any external caches.

First time you need to also run `python -mFrontend db init`

### `~/live`
```bash
cd ${PATH_TO_ENVIRONMENT}

. venv/bin/activate
export PYTHONPATH=`pwd`
export CONFIG_ENV="live"

NAME="venv LIVE"
COLOR="$(tput setaf 1)"
BOLD="$(tput bold)"
RESET="$(tput sgr0)"
export PS1="\[${BOLD}\][\u \[${COLOR}\]${NAME}\[${RESET}${BOLD}\] \W]$\[${RESET}\] "

cd run
```

### `~/update-live.sh`
```bash
#!/bin/bash
set -o errexit # Exit at first error
. ~/live # activate live env + cd to run + prompt + PYTHONPATH + CONFIG_ENV
git pull
pip install -qr ../requirements.txt
# update DB
python -mFrontend db migrate
python -mFrontend db upgrade
# Reload everything
touch ../config/*.ini
~/purge-cache.sh
```
