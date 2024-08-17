# API Design

## APIs

# GET
- Health Ping
GET /v1/ping

- API to get the long URL for a short URL
GET /v1/urls/{shortUrl}
Response:
301
Location: <LONG_URL>


# POST

- Create a short URL for a long URL. This will be a sync API
  
```
POST /v1/urls
  Body:
  {
    longUrl: <LONG_URL>,
    expiry: DD-MM-YYYY-hh:mm
  }

  Response: 
  200 OK
  {
    shortUrl: <SHORT_URL>
    longURL: <LONG_URL>,
    expiry: DD-MM-YYYY-hh:mm
  }
```  

# DELETE
- Delete a shortened URL
  DELETE /v1/urls/<shortUrl>

  Response:
  200 OK