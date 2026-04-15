# Ejemplos de API

## Chat

`POST /api/chat`

```json
{
  "question": "Why are users getting 401 after the SSO provider change?",
  "retrieval_strategy": "hybrid_rerank",
  "use_query_rewrite": true
}
```

## Ingesta

`POST /api/ingest/upload` — multipart `file`.

## Feedback

`POST /api/feedback`

```json
{
  "query_id": "uuid",
  "rating": 1,
  "comment": "optional"
}
```

## Dashboard

`GET /api/analytics/dashboard`
