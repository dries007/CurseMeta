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

- Any key in any JSON file starting with an underscore is to be treated as optional.
- Any file/data you find that is not specified in here should be treated as non-stable.
- All static content is served gzipped. Accept this whenever possible.
- There is a 1h cache expiry on all content, content may also be cached by Cloudflare.
  Don't bypass this when it's not necessary.

<small>[Credits & Legal](/)</small>

## Table of content

[TOC]

## Routing

- Order of tried files:
  1. `$uri`
  2. `$uri.html`
  3. `$uri/`
- Indexes:
  1. `index.html`
  2. `index.json`
  3. 403 (Directory indexes are disabled.)

## Raw data

+ These files are *big*. (+50Mb for complete)
+ Please contact me **before** using this in a project.
+ Please use as compressed files, in gzip (`.gz`), bzip2 (`.bz2`) and xz (`.xz`).

Links:

- [`raw_complete.json`](/raw_complete.json)
  - [`raw_complete.json.gz`](/raw_complete.json.gz)
  - [`raw_complete.json.bz2`](/raw_complete.json.bz2)
  - [`raw_complete.json.xz`](/raw_complete.json.xz)
- [`raw_mods.json`](/raw_mods.json)
  - [`raw_mods.json.gz`](/raw_mods.json.gz)
  - [`raw_mods.json.bz2`](/raw_mods.json.bz2)
  - [`raw_mods.json.xz`](/raw_mods.json.xz)
- [`raw_modpacks.json`](/raw_modpacks.json)
  - [`raw_modpacks.json.gz`](/raw_modpacks.json.gz)
  - [`raw_modpacks.json.bz2`](/raw_modpacks.json.bz2)
  - [`raw_modpacks.json.xz`](/raw_modpacks.json.xz)

## List of all ProjectIDs
[`/index.json`](/index.json)

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

## List of all Mods or Modpack ProjectIDs
[`/mods.json`](/mods.json) and [`/modpacks.json`](/modpacks.json)

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

## Download/owner Statistics
[`/stats.json`](/stats.json)

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
        "downloads": {
            // Download count per type
            "Mods": 2346689297.0, // Floating for range. 
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

## Daily, weekly, monthly downloads
[`/daily.json`](/daily.json), [`/weekly.json`](/weekly.json) and [`/monthly.json`](/monthly.json)

Projects with 0 downloads in the time span may be omitted.
The actual delta may vary from 1, 7 or 30 days, you can calculate it with the provided timestamps.

```json
{
    "then_timestamp": 1515102689,  // Start timestamp
    "now_timestamp": 1517695648, // End timestamp
    "then_timestamp_human": "2018-01-04 21:51:29 UTC",  // Do not parse this!
    "now_timestamp_human": "2018-02-03 22:07:28 UTC",  // Do not parse this!
    "delta": {
        // Map of projectID -> download count.
        // if count is 0, the project may be omitted
        "32080": 58842,
        "32123": 55504,
        "32195": 26,
        "32274": 748078,
        "32286": 7,
        "32392": 53
    }
}
```

## History

### Available data point
[`/history/index.json`](/history/index.json)

```json
{
    "timestamp": 1505127365, // Seconds based timestamp from Curse
    "timestamp_human": "2017-09-11 10:56:05 UTC", // Do not parse this!
    "history": [
        // List of every timestamp with data available.
        // Do not cache this without also caching the timestamp data.
        // Timestamps may be removed.
        1504891405,
        1505127365
    ]
}
```

### Download count at timestamp
[`/history/<timestamp>.json`](/history/1505131870.json)

```json
{
    "32159": 854.0, // Key: ProjectID (int), Value: Downloads (floating for range)
    "32195": 1063.0,
    "32274": 23226216.0,
    "32286": 425.0
    // One for every projectID
}
```

## Project Files

Overview:

- [`/<ProjectID>.json`](/226294.json)
- [`/<ProjectID>/`](/226294/)
  - [`/<ProjectID>/index.json`](/226294/index.json) (same as the directory URL)
  - [`/<ProjectID>/files.json`](/226294/files.json)
  - [`/<ProjectID>/fileid.json`](/226294/2222653.json)
  
### Project metadata
[`<ProjectID>.json`](/226294.json)

Curse Project metadata

Removed:

- `LatestFiles.*.Modules`: Contains (unspecified) fingerprint data per folder inside a package.

Notes:

- Inside `GameVersionLatestFiles`, `GameVesion` is misspelled. This is a Curse typo.

### Project fileId list
[`<ProjectID>/index.json`](/226294/index.json) (also served at [`<ProjectID>/`](/226294/) )

```json
{
    "ids": [
        2222367,
        2222432
        // List of available FileIDs
    ],
    "type": "Mods", // One of the Curse types
    // Data below is copied from Project metadata (<ProjectID>.json)
    "Summary": "No more will you need to type out shaped or shapeless recipes.... EVER!",
    "PrimaryAuthorName": "DoubleDoorDevelopment",
    "Name": "MineTweaker RecipeMaker"
}
```

### Project file object
[`/<ProjectID>/<FileID>.json`](/226294/2222653.json)

Curse File metadata

Removed:

- `Modules`: Contains (unspecified) fingerprint data per folder inside a package.

Notes:

- **Optionally** added `_Project`, to allow limited project info with less requests.
- It's possible to request archived or deleted files with this endpoint.
  Those files will generate some behind the scenes requests that cause a load time of up to a few seconds.
  Increase your timeouts accordingly.

### Project file object list
[`/<ProjectID>/files.json`](/226294/files.json)

Json array of Project file objects. Don't use this if you just need 1 file's info.

Notes:

- Only available (non-archived or deleted) files are listed here.
