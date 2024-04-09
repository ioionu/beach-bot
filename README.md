# Mastodon bot that toots gigs in Sydney

## Run Local

`pip install -r requirements.txt`

`cp .env.example .env.prod`

Edit `.env.prod` with server url and app token.

`set -o allexport; source .env.prod; set +o allexport; ./beachbot.py`

##  Deploy

Install piku https://github.com/piku/piku. Install https://piku.github.io/manage.html for setting environment variables.

`git remote add piku piku@some.server:beach-bot`

`git push piku main`

```piku config:set `cat .env.prod` ```
