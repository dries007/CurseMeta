http://localhost:5000/api/graphql?raw&query={__type(name:%22Addon%22){fields{name,description}}}
```json

  "data": {
    "__type": {
      "fields": [
        {
          "name": "lastUpdate",
          "description": null
        },
        {
          "name": "addonId",
          "description": null
        },
        {
          "name": "gameId",
          "description": null
        },
        {
          "name": "name",
          "description": null
        },
        {
          "name": "category",
          "description": null
        },
        {
          "name": "downloads",
          "description": null
        },
        {
          "name": "score",
          "description": null
        },
        {
          "name": "primaryAuthorName",
          "description": null
        },
        {
          "name": "id",
          "description": "The ID of the object."
        }
      ]
    }
  }
}
```


http://localhost:5000/api/graphql?query={addons{addonId,name,category,primaryAuthorName}}
http://localhost:5000/api/graphiql?raw&query={addons{addonId,name,category,primaryAuthorName}}