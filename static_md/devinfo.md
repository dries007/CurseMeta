---
title: CurseMeta - Usage Info
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

# Usage info

When using this website in your own projects, acknowledgement would be appreciated!

**Please set your `User Agent` to something unique to your project, so I can identify it in logs.**

To save bandwidth all JSON data is minified, and not all metadata is retained.

If you are going to be browsing this site in a browser, install a [JSON Viewer](https://chrome.google.com/webstore/detail/json-viewer/gbmdgpbipfallnflgajpaliibnhdgobh)!

The JSON data is updated periodically, ideally hourly. (Just as fast as the Twitch launcher.)

## Features

**Any key in any JSON file starting with an underscore is to be treated as optional. It may or may not be present.!**

- JSON based file index: [`index.json`](index.json)
  - A `timestamp` (and `timestamp_human`) of last update.
  - Lists of all `mods`, `modpacks` project ids.
  - A list of all project `ids`.
- A list of all [`mods.json`](mods.json) and [`modpacks.json`](modpacks.json), for easy searchability.
  - These files are an `Id` to `Name`, `PrimaryAuthorName`, `Summary`, `WebSiteURL`, `GameVersionLatestFiles` map. ( `ProjectFileName` is removed from the `GameVersionLatestFiles` objects.)
  - They are meant for search services, to avoid having to download unnecessary data.
  - If you'd like to see a key added, open an issue with a strong use-case please.
- A `/projectID.json` JSON file for every project.
  - Has the (stripped) CurseForge project metadata.
- A `/projectID/` folder with:
  - A JSON based index: `/projectid/index.json`
    - The project `type` (comma separated list of `mod`, `modpack`, and or `UNKNOWN`)
    - A list of ids of all known files of this project.
    - The `Name`, `PrimaryAuthorName` and `Summary` items. 
  - A metadata file per `fileID`: `/projectid/fileID.json`
    - The `_Project` key contains metadata about the project this file belongs to, to avoid having to make multiple requests. **It is optional.** 
  - A list of all CurseForge's files metadata: `/projectid/files.json`
    - _Please don't use this file if you only need one file's metadata._
- The 'raw' data from CurseForge:
  - `raw_complete.json`, `raw_mods.json` and `raw_modpacks.json`.
    _Only available as compressed files, in gzip (`.gz`), bzip2 (`.bz2`) and xz (`.xz`)._ 

## Example Links

- [`/index.json`](index.json)
- [`/mods.json`](mods.json)
- [`/modpacks.json`](modpacks.json)
- [`/projectID.json`](/226294.json)
- [`/projectID/`](/226294/)
  - [`/projectID/index.json`](/226294/index.json) (same as the directory URL)
  - [`/projectID/files.json`](/226294/files.json)
  - [`/projectID/fileid.json`](/226294/2222653.json)

## Changes

_This is only a partial change log. Changes before May 1st, 2017 are not logged._

## August 30, 2017

- Massive re-write, now everything is handled on our side, no more relying on git synced data.
  This means much quicker update times and hopefully no more extended periods of out-of-date data.
- Added `GameVersionLatestFiles` to mods/modspacks JSON files, `ProjectFileName` is removed.
- Several fields are no longer filtered out, like `PopularityScore` and `DownloadCount`.
- Added `raw_complete.json`, `raw_mods.json` and `raw_modpacks.json` (only compressed). 

## August 13, 2017

- Added the optional `_Project` key to the `fileid.json` files.
  Requested by reddit user joonatoona to eliminate extra HTTP requests.
- `Name`, `PrimaryAuthorName` and `Summary` added to `/projectid/index.json` and to `_Project` in `fileid.json`.

## August 12, 2017

- Changed timestamp in `/index.json` to reflect actual last update, if possible.
  Uses last git commit timestamp.

### May 13, 2017

- Added Markdown script (and css) for easier changed to the info pages.

### May 6, 2017
- Added `mods.json` and `modpacks.json`
- Added [search](/search) page.

### May 1, 2017
- Removed .html files
- Added modpacks & mods id lists in `/index.json`
