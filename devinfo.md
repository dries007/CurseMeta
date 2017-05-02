---
title: CurseMeta - Usage Info
---

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
- A `/projectID.json` JSON file for every project.
  - Has the (stripped) CurseForge project metadata.
- A `/projectID/` folder with:
  - A JSON based index: `/projectid/index.json`
    - The project `type` (comma separated list of `mod`, `modpack`, and or `UNKNOWN`)
  - A metadata file per `fileID`:  `/projectid/fileID.json`
  - A list of all CurseForge's files metadata: `/projectid/files.json`
    + _Please don't use this file if you only need one file's metadata._

## Example

- [`/projectID.json`](/226294.json)
- [`/projectID/`](/226294/)
  - [`/projectID/index.json`](/226294/index.json) (same as the directory URL)
  - [`/projectID/files.json`](/226294/files.json)
  - [`/projectID/fileid.json`](/226294/2222653.json)

## Changes

_This is only a partial change log. Changes before May 1st, 2017 are not logged._

### May 1st, 2017

- Removed .html files
- Added modpacks & mods id lists in `/index.json`