---
title: CurseMeta - JSON Schemas
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

# JSON Schemas
## Table of content

[TOC]

## Overview

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
    - The project `type`
    - A list of ids of all known files of this project.
    - The `Name`, `PrimaryAuthorName` and `Summary` items. 
  - A metadata file per `fileID`: `/projectid/fileID.json`
    - The `_Project` key contains metadata about the project this file belongs to, to avoid having to make multiple requests. **It is optional.** 
  - A list of all CurseForge's files metadata: `/projectid/files.json`
    - _Please don't use this file if you only need one file's metadata._
- The 'raw' data from CurseForge:
  - `raw_complete.json`, `raw_mods.json` and `raw_modpacks.json`.
    - _Please use as compressed files, in gzip (`.gz`), bzip2 (`.bz2`) and xz (`.xz`)._

## Example Links

- [`/index.json`](index.json)
- [`/mods.json`](mods.json)
- [`/modpacks.json`](modpacks.json)
- [`/projectID.json`](/226294.json)
- [`/projectID/`](/226294/)
  - [`/projectID/index.json`](/226294/index.json) (same as the directory URL)
  - [`/projectID/files.json`](/226294/files.json)
  - [`/projectID/fileid.json`](/226294/2222653.json)

## Schemas / Examples
### [`/index.json`](/index.json)

```json
{
    "timestamp": 1505133164, // Seconds based timestamp from Curse
    "timestamp_human": "2017-09-11 12:32:44 UTC", // Do not parse this!
    "ids": [
        // List of all mods + modpacks ProjectIDs (int)
    ],
    "mods": [
        // List of all mods ProjectIDs (int)
    ],
    "modpacks":[
        // List of all modpacks ProjectIDs (int)
    ]
}
```

### [`/mods.json`](/mods.json) and [`/modpacks.json`](/modpacks.json)

```json
{
   "78608": { // ProjectID (int)
        "GameVersionLatestFiles": [
            {
                "FileType": "release", // Normally [release, beta, alpha]
                "GameVesion": "1.7.10", // Typo is Curse's fault
                "ProjectFileID": 2290760
            } // Zero or more. Possibly more than one per mc version, if FileType is different.
        ],
        "Name": "HoloInventory",
        "PrimaryAuthorName": "dries007", // = owner
        "Summary": "HoloInventory",
        "WebSiteURL": "https://mods.curse.com/mc-mods/minecraft/holoinventory"
    }
    // One for every mod/modpack
}
```

### [`/stats.json`](/stats.json)

'Types' are Curse CategorySection's Names, currently:

- Mods
- Texture Packs
- Worlds
- Modpacks

Not all keys must be present. May expand in the future.

```json
{
    "timestamp": 1505133164, // Seconds based timestamp from Curse
    "timestamp_human": "2017-09-11 12:32:44 UTC", // Do not parse this!
    "stats": {
        "project_count": {
            // Project count per type 
            "Mods": 7142,
            "Texture Packs": 1503,
            "Worlds": 2523,
            "Modpacks": 6524
        },
        "downloads": { // I think these numbers are floating because of range issues
            // Download count per type
            "Mods": 2346689297.0, 
            "Texture Packs": 42078333.0,
            "Worlds": 14133278.0,
            "Modpacks": 31279952.0
        },
        "version": {
            "1.0.0": {
                // Project count per type. Not all types are always present!
                // A Project is counted if it has at least one GameVersionLatestFiles.
                "Mods": 21,
                "Worlds": 15,
                "Texture Packs": 25
            } // More versions, not sorted!
        },
        "authors": {
            "dries007": { // username
                "owner": { // owner only projects
                    // ProjectID per type. Not all types are always present!
                    "Mods": [
                        78608,
                        256400,
                        267687
                    ]
                },
                "member": { // any member projects, incl owner
                    // ProjectID per type. Types don't have to be same as owner types
                    "Mods": [
                        78608,
                        78785,
                        274013
                    ],
                    "Modpacks": [
                        229729,
                        252469
                    ]
                }
            }
            // One per author. Not sorted.
        },
        "projects": {
            "78608": { // PorjectID (int)
                "name": "HoloInventory",
                "type": "Mods",
                "downloads": 737280.0,
                "score": 5857.12744140625 // Curse's magic popularity number
            }
            // One per project. Not sorted.
        }
    }
}
```

### History
#### [/history/index.json](/history/index.json)

```json
{
    "timestamp": 1505127365, // Seconds based timestamp from Curse
    "timestamp_human": "2017-09-11 10:56:05 UTC", // Do not parse this!
    "history": [
        // List of every timestamp with data available.
        // Do not cache this without also caching the timestamp data.
        // Timestamps may be removed when the amount of data becomes too large for hourly snapshots.
        1504891405,
        1505127365
    ]
}
```



<small>[Credits & Legal](/)</small>