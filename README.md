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

### Decompiling a .NET app

This information may be useful when conducting research on .NET applications.

You'll need a Windows (VM, _obviously_) with:

+ [dotPeek](https://www.jetbrains.com/decompiler/)
+ [de4dot](https://github.com/0xd4d/de4dot)
+ The target program 

My folder layout:
+ Project
  + `de4dot` (unpacked zip)
    + `de4dot.exe`
  + `output`
  + `target` (folder with exe and dlls)

Steps:

1. Run the program to make it self-update and close it out completely.
2. Nuke any old output.
3. Copy over all files from the program folder to an output folder.
4. Open a batch prompt.
5. Run `de4dot\de4dot.exe -r target -ro output --dont-rename`.
6. Wait.
7. Open the output folder with dotPeek.
8. Enjoy poking around.

## Licence

[EUPL v1.2](LICENCE.txt)
