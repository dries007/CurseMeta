# CurseMeta API v1

**Work In Progress** Not available yet. 

URL prefix: `https://cursemeta.dries007.net/api/v1`

This is not a document for the existing static file infrastructure. It's meant as a design document for a query API that would allow server side processing and selective querying of data.

This style of API is inspired by the [Jenkins API](https://jenkins.dries007.net/api). It allows you to selectively fetch data, for example:

- Partial request example [here](https://jenkins.dries007.net/job/D3Backend/api/json?tree=lastStableBuild%5Bnumber%2Cartifacts%5B%2A%5D%5D)
- The same request, unfiltered, [here](https://jenkins.dries007.net/job/D3Backend/api/json)
- Json madness [here](https://jenkins.dries007.net/job/CrayCrafting/api/json?tree=%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5B%2A%5D%5D%5D%5D%5D%5D%5D%5D%5D%5D%5D%5D%5D%5D%5D) (can take a couple of seconds)

Ideas
-----

- Any Id -> Any field
- Filename -> projectID & fileID
- Multi input -> multi output
