---
title: CurseMeta - Developer Info
description: CurseForge metadata for third party integrations
keywords: Curse,CurseForge,Minecraft,MinecraftForge,Forge,Mods,Modpacks
author: Dries007
robots: index, nofollow
revisit-after: 14 days
viewport: width=device-width, initial-scale=1.0
---
<!--
    Copyright 2017 Dries007

    Licensed under the EUPL, Version 1.1 only (the "Licence");
    You may not use this work except in compliance with the Licence.
    You may obtain a copy of the Licence at:
    
    https://joinup.ec.europa.eu/software/page/eupl5
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the Licence is distributed on an "AS IS" basis,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the Licence for the specific language governing
    permissions and limitations under the Licence.
-->

# Developer info

When using this website in your own projects, acknowledgement would be appreciated!

**Please set your `User Agent` to something unique to your project, so I can identify it in logs.**

If you are going to be browsing this site in a browser, install a [JSON Viewer](https://chrome.google.com/webstore/detail/json-viewer/gbmdgpbipfallnflgajpaliibnhdgobh)!

See [schemas](schemas) for more information about the data available.

## Changelog

_This is only a partial change log. Changes before May 1st, 2017 are not logged._

### 9, 10, 11 September 2017
- Added statistics and history.
- Added more developers docs and moved some of it to the schemas page.

### 7 September 2017

- Round of fixes of on demand file fetching
    - Including fixed texture packs causing havoc.
- Added `PackageType` and `Path` to `_Project`, so you can detect texture packs and put them in the right place. 

### 30 August 2017

- Massive re-write, now everything is handled on our side, no more relying on git synced data.
  This means much quicker update times and hopefully no more extended periods of out-of-date data.
- Added `GameVersionLatestFiles` to mods/modspacks JSON files, `ProjectFileName` is removed.
- Several fields are no longer filtered out, like `PopularityScore` and `DownloadCount`.
- Added `raw_complete.json`, `raw_mods.json` and `raw_modpacks.json` (only compressed). 

### 13 August 2017

- Added the optional `_Project` key to the `fileid.json` files.
  Requested by reddit user joonatoona to eliminate extra HTTP requests.
- `Name`, `PrimaryAuthorName` and `Summary` added to `/projectid/index.json` and to `_Project` in `fileid.json`.

### 12 August 2017

- Changed timestamp in `/index.json` to reflect actual last update, if possible.
  Uses last git commit timestamp.

### 13 May 2017

- Added Markdown script (and css) for easier changed to the info pages.

### 6 May 2017
- Added `mods.json` and `modpacks.json`
- Added [search](/search) page.

### 1 May 2017
- Removed .html files
- Added modpacks & mods id lists in `/index.json`

<small>[Credits & Legal](/)</small>
