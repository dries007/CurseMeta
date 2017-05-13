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

Also, please set your `User Agent` to something unique to your project, so I can identify it in logs.

To save bandwidth all JSON data is minified, and not all metadata is retained.

If you are going to be browsing this site in a browser, install a [JSON Viewer](https://chrome.google.com/webstore/detail/json-viewer/gbmdgpbipfallnflgajpaliibnhdgobh)!

The JSON data is updated periodically, based on [this](https://github.com/NikkyAI/alpacka-meta-files) data.

## Features

- JSON based file index: [`index.json`](index.json)
  - A `timestamp` of last update
  - Lists of all `mods`, `modpacks` project ids
  - A list of all project `ids`.
- A list of all [`mods.json`](mods.json) and [`modpacks.json`](modpacks.json), for easy searchability.
  - These files are an `Id` to `Name`, `PrimaryAuthorName`, `Summary`, and `WebSiteURL` map.
  - They are meant for search services, to avoid having to download unnecessary data.
  - If you'd like to see a key added, open an issue with a strong use-case please.
- A `/projectID.json` JSON file for every project.
  - Has the (stripped) CurseForge project metadata.
- A `/projectID/` folder with:
  - A JSON based index: `/projectid/index.json`
    - The project `type` (comma separated list of `mod`, `modpack`, and or `UNKNOWN`)
  - A metadata file per `fileID`:  `/projectid/fileID.json`
  - A list of all CurseForge's files metadata: `/projectid/files.json`
    - _Please don't use this file if you only need one file's metadata._

## Example

- [`/projectID.json`](/226294.json)
- [`/projectID/`](/226294/)
  - [`/projectID/index.json`](/226294/index.json) (same as the directory URL)
  - [`/projectID/files.json`](/226294/files.json)
  - [`/projectID/fileid.json`](/226294/2222653.json)

## Changes

_This is only a partial change log. Changes before May 1st, 2017 are not logged._

### May 13th, 2017
- Added Markdown script (and css) for easier changed to the info pages.

### May 6th, 2017
- Added `mods.json` and `modpacks.json`
- Added [search](/search) page.

### May 1st, 2017
- Removed .html files
- Added modpacks & mods id lists in `/index.json`