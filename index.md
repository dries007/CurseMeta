---
title: Curse Meta
---
# Curse Meta

**Not production ready.**

All generated with publicly available data from Minecraft's CurseFoge.

This is meant to be updated hourly, since that's the rate at which CurseForge updates.

## Features

- JSON based index: [`index.json`](index.json)
- Every `/projectID.json` JSON file has the CurseForge project metadata.
- Every `/projectID/` folder has:
  - A JSON based index: `/projectid/index.json`
  - The CurseForge project description: `/projectid/description.html`
  - A list of all CurseForge file metadata: `/projectid/files.json`
  - Two files per `fileID`:
    - The changelog: `/projectid/fileID.changelog.html`
    - The CurseForge file metadata: `/projectid/fileID.changelog.html`

## Example

- [`/projectID.json`](/226294.json)
- [`/projectID/`](/226294/)
  - [`/projectID/files.json`](/226294/files.json)
  - [`/projectID/description.html`](/226294/description.html)
  - [`/projectID/fileid.json`](/226294/2222653.json)
  - [`/projectID/fileid.changelog.html`](/226294/2222653.changelog.html)

**PS:** If you are going to be browsing this site in a browser, install a [JSON Viewer](https://chrome.google.com/webstore/detail/json-viewer/gbmdgpbipfallnflgajpaliibnhdgobh)!

_Maintained by [Dries007](https://dries007.net). Source code on [Github](https://github.com/dries007/curseMeta)._

_Thanks to [NikkyAI's alpacka-meta](https://github.com/NikkyAI/alpacka-meta) for the interaction with CurseForge's API._
