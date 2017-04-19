---
title: Dev Info
---

# Dev Info

When using this 'service' in your own projects, acknowledgement would be appreciated!

Also, please set your User Agent string to something unique to your project, so I can identify it in logs.

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