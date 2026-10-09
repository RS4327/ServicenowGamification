# ServiceNow Gamification Dashboard — API Documentation



> **Last updated:** 2026-08-25  

> Reflects the full Manager Dashboard redesign (6 KPIs, priority charts, alerts, gamification summary, badges, performance distribution) and the Data-Source Switching architecture.



---



## Overview



| Item | Value |

|------|-------|

| Base URL | Configured via `.env`: `VITE_API_BASE_URL=http://your-server/api/v1` |

| Auth | Bearer token in `Authorization: Bearer <token>` header |

| Content-Type | `application/json` |

| Data source | Controlled by `VITE_DATA_SOURCE` — see **Data-Source Architecture** below |



### Standard Response Envelope



Every endpoint wraps its payload in:



**Success:**

```json

{ "success": true, "data": { ... } }

```



**Failure:**

```json

{ "success": false, "error": "Descriptive error message" }

```



---



## Data-Source Architecture



The frontend implements a three-tier data access pattern:



```

Dashboard → Data Access Layer → Primary: Database → Fallback: Repository Snapshot

```



Controlled by a single env var:



| `VITE_DATA_SOURCE` | Behaviour |

|--------------------|-----------|

| `snapshot` *(default)* | Skips all API calls. Returns the versioned snapshot in `src/data/sampleData.js`. Safe for demos and offline use. |

| `database` | Calls the real API. If the database is unreachable, automatically falls back to the snapshot and sets the UI badge to **⚠ DB Offline**. |



The frontend displays a live indicator badge in the topbar:



| Badge | Colour | Meaning |

|-------|--------|---------|

| 📦 Snapshot | Blue | Configured snapshot mode |

| 🗄️ Database | Green | Live database, healthy |

| ⚠️ DB Offline | Red | Database mode but unreachable — snapshot in use |



**Backend team note:** When `VITE_DATA_SOURCE=database` and the server is available, the app calls every endpoint below. Your server only needs to handle these requests; the frontend handles all fallback logic.



---



## 1. Authentication



### `POST /auth/login`



Authenticate a user and receive a session token.



**Request body:**

```json

{

  "username": "beth.anglin",

  "password": "secret",

  "role": "agent"

}

```



`role` must be `"manager"` or `"agent"`.



**Response `data`:**

```json

{

  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",

  "user": {

    "id": "usr_001",

    "name": "Beth Anglin",

    "role": "agent",

    "avatar": "BA"

  }

}

```



---



### `POST /auth/logout`



Invalidate the current session token.



**Response `data`:**

```json

{ "message": "Logged out" }

```



---



### `GET /auth/me`



Return the profile of the authenticated user.



**Response `data`:**

```json

{

  "id": "usr_001",

  "name": "Beth Anglin",

  "role": "agent",

  "avatar": "BA"

}

```



---



## 2. Manager Dashboard



> All `/dashboard/manager/*` endpoints require role `"manager"`. Return `403` for agent tokens.



### `GET /dashboard/manager/stats`



Six KPI cards at the top of the Manager Dashboard.



**Response `data`:**

```json

{

  "totalIncidents": 59,

  "slaCompliance": 6.78,

  "fcr": 37.29,

  "avgMTTR": 860.49,

  "reopenRate": 14.41,

  "customerRating": 4.32,

  "incidentsTrend": 12.3,

  "slaTrend": 5.2,

  "fcrTrend": 8.7,

  "mttrTrend": -3.1,

  "reopenTrend": -1.8,

  "ratingTrend": 4.6,

  "period": "Apr 21 – May 19, 2025"

}

```



| Field | Type | Notes |

|-------|------|-------|

| `totalIncidents` | number | Count of incidents in the reporting period |

| `slaCompliance` | number | SLA compliance % |

| `fcr` | number | First Contact Resolution % |

| `avgMTTR` | number | Average Mean Time to Resolve (hours) |

| `reopenRate` | number | Percentage of incidents reopened |

| `customerRating` | number | Average customer satisfaction (out of 5) |

| `*Trend` | number | % change vs previous period. **Negative = worse** for mttrTrend and reopenTrend (higher is bad). |

| `period` | string | Human-readable label shown in the UI, e.g. `"Apr 21 – May 19, 2025"` |



---



### `GET /dashboard/manager/incidents-over-time`



Line chart data — incident volume over time.



**Query params:**



| Param | Values | Default |

|-------|--------|---------|

| `period` | `weekly` \| `monthly` | `monthly` |



**Response `data`:**

```json

[

  { "date": "Apr 21", "incidents": 42 },

  { "date": "Apr 28", "incidents": 38 },

  { "date": "May 5",  "incidents": 55 },

  { "date": "May 12", "incidents": 70 },

  { "date": "May 19", "incidents": 60 }

]

```



---



### `GET /dashboard/manager/sla-trend`



Dual line chart — SLA compliance and FCR trend over time.



**Query params:** same as `incidents-over-time`.



**Response `data`:**

```json

[

  { "date": "Apr 21", "sla": 15.2, "fcr": 30.1 },

  { "date": "Apr 28", "sla": 12.8, "fcr": 33.4 },

  { "date": "May 5",  "sla": 14.1, "fcr": 35.2 },

  { "date": "May 12", "sla": 13.9, "fcr": 32.8 },

  { "date": "May 19", "sla": 11.5, "fcr": 37.29 }

]

```



---



### `GET /dashboard/manager/incidents-by-state`



Donut chart — incident distribution by resolution state.



**Response `data`:** array format consumed directly by the pie chart:

```json

[

  { "name": "Resolved", "value": 38 },

  { "name": "Closed",   "value": 29 },

  { "name": "Open",     "value": 33 }

]

```



---



### `GET /dashboard/manager/top-agents`



Table of top-performing agents ranked by FCR with incident count and trend.



**Query params:**



| Param | Values | Default |

|-------|--------|---------|

| `limit` | integer | `5` |

| `metric` | `fcr` \| `sla` \| `mttr` \| `points` | `fcr` |



**Response `data`:**

```json

[

  { "name": "Fred Luddy",                   "fcr": 92.45, "incidents": 142, "trend": 6.2,  "trendUp": true },

  { "name": "Gulrez Fulsath",               "fcr": 76.38, "incidents": 118, "trend": 4.1,  "trendUp": true },

  { "name": "AIT Service Level Management", "fcr": 65.73, "incidents": 96,  "trend": 2.8,  "trendUp": true },

  { "name": "AVV_SeedDriver2",              "fcr": 58.94, "incidents": 87,  "trend": 1.3,  "trendUp": true },

  { "name": "Vamsi",                        "fcr": 43.21, "incidents": 65,  "trend": 2.7,  "trendUp": false }

]

```



| Field | Type | Notes |

|-------|------|-------|

| `fcr` | number | FCR % |

| `incidents` | number | Total incidents in period |

| `trend` | number | Absolute % change |

| `trendUp` | boolean | `true` = improvement, `false` = degradation |



---



### `GET /dashboard/manager/mttr-by-priority`



Bar chart — average MTTR broken down by incident priority (P1–P4).



**Response `data`:**

```json

[

  { "priority": "P1", "hours": 220.45  },

  { "priority": "P2", "hours": 480.32  },

  { "priority": "P3", "hours": 850.67  },

  { "priority": "P4", "hours": 1250.80 }

]

```



---



### `GET /dashboard/manager/sla-by-priority`



Bar chart — SLA compliance % by incident priority (P1–P4).



**Response `data`:**

```json

[

  { "priority": "P1", "compliance": 11.21 },

  { "priority": "P2", "compliance": 8.67  },

  { "priority": "P3", "compliance": 6.34  },

  { "priority": "P4", "compliance": 3.92  }

]

```



---



## 3. Alerts



### `GET /alerts`



Recent system alerts shown in the Manager Dashboard alert panel.



**Query params:**



| Param | Default |

|-------|---------|

| `limit` | `3` |



**Response `data`:**

```json

[

  {

    "id": 1,

    "title": "High MTTR for Priority 1 incidents",

    "desc": "Average MTTR exceeded threshold",

    "time": "10 min ago",

    "level": "critical"

  },

  {

    "id": 2,

    "title": "Low SLA Compliance",

    "desc": "SLA compliance below 7%",

    "time": "25 min ago",

    "level": "warning"

  },

  {

    "id": 3,

    "title": "High Reopen Rate",

    "desc": "Reopen rate above 14%",

    "time": "1 hour ago",

    "level": "info"

  }

]

```



| `level` | UI colour | Icon |

|---------|-----------|------|

| `critical` | Red | ⚠ triangle |

| `warning` | Amber | ⚠ triangle |

| `info` | Blue | ℹ circle |



---



## 4. Gamification



### `GET /gamification/summary`



High-level gamification metrics for the Manager Dashboard summary card.



**Response `data`:**

```json

{

  "totalAgents": 25,

  "totalPoints": 125680,

  "badgesAwarded": 156,

  "activeChallenges": 8

}

```



---



### `GET /badges/top`



Top badges currently being awarded across all agents.



**Query params:**



| Param | Default |

|-------|---------|

| `limit` | `3` |



**Response `data`:**

```json

[

  { "id": 1, "name": "SLA Champion",      "desc": "Awarded to 8 agents",  "color": "#f59e0b", "icon": "star"  },

  { "id": 2, "name": "First Call Hero",   "desc": "Awarded to 10 agents", "color": "#10b981", "icon": "check" },

  { "id": 3, "name": "Resolution Master", "desc": "Awarded to 7 agents",  "color": "#8b5cf6", "icon": "clock" }

]

```



`icon` is one of: `"star"`, `"check"`, `"clock"` — maps to an SVG icon in the UI.



---



### `GET /performance/distribution`



Donut chart — workforce split by performance tier.



**Response `data`:**

```json

[

  { "name": "High Performers",    "value": 40, "color": "#10b981" },

  { "name": "Average Performers", "value": 40, "color": "#3b82f6" },

  { "name": "Low Performers",     "value": 20, "color": "#f59e0b" }

]

```



`value` is a percentage (must sum to 100).



---



## 5. Agent Dashboard



> `/dashboard/agent/*` endpoints are scoped to the authenticated agent. Agents can only see their own data.



### `GET /dashboard/agent/stats`



**Response `data`:**

```json

{

  "myIncidents": 7,

  "slaCompliance": 0,

  "fcr": 57.14,

  "mttr": 359.44

}

```



---



### `GET /dashboard/agent/performance-trend`



**Response `data`:**

```json

[

  { "date": "Apr 21", "sla": 0, "fcr": 50    },

  { "date": "Apr 28", "sla": 0, "fcr": 55    },

  { "date": "May 5",  "sla": 0, "fcr": 52    },

  { "date": "May 12", "sla": 0, "fcr": 57    },

  { "date": "May 19", "sla": 0, "fcr": 57.14 }

]

```



---



### `GET /dashboard/agent/incidents-by-state`



**Response `data`:**

```json

[

  { "name": "Resolved", "value": 4 },

  { "name": "Closed",   "value": 2 },

  { "name": "Open",     "value": 1 }

]

```



---



### `GET /dashboard/agent/recent-incidents`



**Query params:** `limit` (default `5`)



**Response `data`:**

```json

[

  { "id": "INC0010001", "shortDesc": "Issue with email access", "state": "Resolved", "openedAt": "2025-05-20" },

  { "id": "INC0010002", "shortDesc": "VPN not connecting",      "state": "Open",     "openedAt": "2025-05-18" }

]

```



`state`: `"Resolved"` | `"Closed"` | `"Open"`



---



### `GET /dashboard/agent/badges`



Badges earned by the authenticated agent.



**Response `data`:**

```json

[

  { "id": 1, "name": "Quick Resolve", "description": "Resolved 5 incidents under 1 hour", "color": "#3b82f6", "earnedAt": "2025-04-15T00:00:00Z" }

]

```



---



## 6. Leaderboard



### `GET /leaderboard`



**Query params:**



| Param | Values | Default |

|-------|--------|---------|

| `metric` | `fcr` \| `sla` \| `mttr` \| `points` | `points` |

| `period` | `week` \| `month` \| `quarter` | `month` |



**Response `data`:**

```json

[

  { "rank": 1, "name": "Fred Luddy",        "fcr": 80,    "slaCompliance": 20,  "mttr": 81.63,  "points": 950 },

  { "rank": 2, "name": "Guillermo Fröhlich","fcr": 100,   "slaCompliance": 100, "mttr": 24,     "points": 910 },

  { "rank": 5, "name": "Beth Anglin",       "fcr": 57.14, "slaCompliance": 0,   "mttr": 359.44, "points": 720 }

]

```



---



## 7. AI Insights



### `GET /insights`



**Query params:** `role` — `manager` | `agent`



**Response `data`:**

```json

[

  {

    "id": 1,

    "title": "SLA Compliance is Low",

    "description": "Current SLA compliance rate of 6.78% is critically below the target of 90%.",

    "impact": "High",

    "icon": "warning",

    "recommendation": [

      "Review all open incidents older than 4 hours",

      "Redistribute workload from overloaded agents",

      "Implement automated escalation rules"

    ]

  }

]

```



| Field | Values |

|-------|--------|

| `impact` | `"High"` \| `"Medium"` \| `"Low"` |

| `icon` | `"warning"` \| `"clock"` \| `"refresh"` \| `"star"` |



---



## 8. Performance Charts



### `GET /performance/charts`



**Query params:** `period` — `this_month` | `last_month` | `quarter`



**Response `data`:**

```json

[

  { "date": "Apr 21", "mttr": 400,    "sla": 0, "fcr": 50,    "incidents": 1 },

  { "date": "Apr 28", "mttr": 380,    "sla": 0, "fcr": 55,    "incidents": 0 },

  { "date": "May 19", "mttr": 359.44, "sla": 0, "fcr": 57.14, "incidents": 1 }

]

```



---



## 9. Agents Management *(Manager only)*



### `GET /agents`



**Query params:**



| Param | Description |

|-------|-------------|

| `search` | Name partial match |

| `status` | `Active` \| `Away` \| `""` (all) |



**Response `data`:**

```json

[

  { "id": 1, "name": "Fred Luddy", "role": "Senior Agent", "fcr": 80, "slaCompliance": 20, "mttr": 81.63, "points": 950, "status": "Active" }

]

```



---



### `GET /agents/:id`



Full profile with history.



**Response `data`:** same as list item, plus:

```json

{

  "history": [

    { "date": "2025-05-01", "fcr": 78, "sla": 18, "mttr": 84 }

  ]

}

```



---



## 10. Goals *(Agent)*



### `GET /goals`



**Response `data`:**

```json

[

  { "id": 1, "title": "FCR Goal", "description": "Achieve FCR of 80%", "current": 57.14, "target": 80, "unit": "%", "color": "#f59e0b" },

  { "id": 4, "title": "MTTR Reduction", "description": "Reduce MTTR below 200 hrs", "current": 359.44, "target": 200, "unit": "hrs", "color": "#8b5cf6", "invert": true }

]

```



`invert: true` — progress % is calculated as `(target - current) / target` (lower current = better).



---



### `PUT /goals/:id`



**Request body:** `{ "target": 85 }`  

**Response `data`:** updated goal object.



---



## 11. Badges *(Agent)*



### `GET /badges`



**Response `data`:**

```json

{

  "earned": [

    { "id": 1, "name": "Quick Resolve",  "description": "Resolved 5 incidents under 1 hour",         "color": "#3b82f6" },

    { "id": 2, "name": "FCR Achiever",   "description": "Maintained FCR above 50% for a month",      "color": "#10b981" },

    { "id": 3, "name": "SLA Watcher",    "description": "Monitored and escalated 10 SLA-risk tickets","color": "#f59e0b" }

  ],

  "locked": [

    { "id": 4, "name": "Speed Demon",    "description": "Resolve 10 incidents in under 30 minutes each" },

    { "id": 5, "name": "Perfect Week",   "description": "Achieve 100% FCR and SLA for an entire week"   },

    { "id": 6, "name": "Century Club",   "description": "Resolve 100 incidents in a single month"        }

  ]

}

```



---



## 12. Reports



### `GET /reports/list`



**Response `data`:**

```json

[

  { "id": "sla_summary", "label": "SLA Summary",      "formats": ["pdf", "csv"] },

  { "id": "fcr_report",  "label": "FCR Report",        "formats": ["pdf", "csv"] },

  { "id": "agent_perf",  "label": "Agent Performance", "formats": ["pdf", "csv", "xlsx"] }

]

```



---



### `POST /reports/generate`



**Request body:**

```json

{ "type": "sla_summary", "period": "this_month", "format": "pdf" }

```



**Response `data`:**

```json

{ "downloadUrl": "https://your-server/reports/download/abc123.pdf" }

```



---



## 13. Settings



### `GET /settings/profile`



```json

{

  "displayName": "Beth Anglin",

  "email": "beth.anglin@company.com",

  "notifications": { "email": true, "sla": true, "leaderboard": false }

}

```



### `PUT /settings/profile`



**Body:** `{ "displayName": "...", "email": "..." }` — returns updated profile.



### `PUT /settings/notifications`



**Body:** `{ "email": true, "sla": false, "leaderboard": true }` — returns updated notifications object.



---



## Error Codes



| HTTP Status | Meaning | When it occurs |

|-------------|---------|----------------|

| `200` | OK | Request succeeded |

| `201` | Created | Resource created (e.g. report generated) |

| `400` | Bad Request | Missing / invalid body or query params |

| `401` | Unauthorized | Missing or expired Bearer token |

| `403` | Forbidden | Valid token but insufficient role (e.g. agent hitting manager endpoint) |

| `404` | Not Found | Resource doesn't exist |

| `500` | Internal Server Error | Unexpected server-side failure |



---



## Notes for Backend Team



- **Timestamps** — All date/time fields must be ISO 8601: `2025-05-20T14:30:00Z`.

- **Date labels** — Chart `date` fields are human-readable strings (`"Apr 21"`, `"May 5"`) matching the UI labels exactly.

- **Pagination** — Append `?page=1&limit=20` to list endpoints. Response should include `"meta": { "page": 1, "limit": 20, "total": 100 }` alongside `"data"`.

- **CORS** — Allow `http://localhost:5173` for local dev. Add the production domain before deployment.

- **Rate limiting** — 100 req/min per token recommended starting point.

- **Role enforcement** — `/dashboard/manager/*`, `/agents`, `/gamification/*`, `/alerts` must return `403` for agent tokens.

- **Data-source switching** — The frontend silently falls back to the bundled snapshot on any API error. Partial backend rollouts (some endpoints ready, others not) are safe — unimplemented endpoints will fall back automatically.

- **Snapshot reference** — The canonical sample payloads in this document exactly match `src/data/sampleData.js` in the repository. Use these as acceptance-test fixtures.

