# CurseMeta v3

Yey for version 3 I guess? 

Now with 100% less C# and 100% less SOAP mess! Yay for that!

**This service is hosted on [cursemeta.dries007.net](https://cursemeta.dries007.net/).**
The staging environment (a testing ground) will be live on [staging_cursemeta.dries007.net](https://staging_cursemeta.dries007.net/).

## Purpose

+ Primary focus of this project is Minecraft, but any other curse sub-site/section should work.
+ Easy access to statistical data about anything on CurseForge.
+ Access for third party launchers, such as [The Superior Minecraft Launcher MultiMC](https://multimc.org) ([who already use this project](https://multimc.org/posts/0-6-update.html)),
+ Access for server installer tools, so they can install Curse modpacks in one go.
+ Better online search.

## Useful resources

+ [Join my discord server and ask for CurseMeta access.](https://discord.gg/zCQaCAA)
+ [A (particularly useful) decompiled class from the Twitch launcher](http://ix.io/1bll/C#)
+ A (partial) history of CurseMeta sits in [this](https://gist.github.com/dries007/10d8dc05a6fc5d1e700404cdd4446d21) gist.

## Dev setup

This is a complex piece of software, it requires the following services:

+ Postgresql (database)
+ Redis (cache) 
+ Celery (task handling, uses redis)
+ Nginx (webserver)
+ Uwsgi (python-nginx binding)

See `config.py` for more details on what needs running and how. 

This service uses Font Awesome *Pro*, their CDN is tied to my domain.
If you want the icons either buy a license (quite cheap) or swap out the pro 
for a free version and remove the non free icons.

## Licence

[EUPL v1.2](LICENCE.txt)
