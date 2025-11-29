# Route Guide System – Best‑Practice Prompt (for Coding Agent)

## 1. Route Input and Retrieval
- User provides:
  - `source_address` (origin)  
  - `destination_address` (destination)
- Use **Google Maps Directions API** to fetch a **driving route**.
- Represent the route as an **ordered list of addresses of junctions / intersections / waypoints**.
- **Do NOT** use or output turn-by-turn text such as “turn left/right”.  
  Only structured addresses or place names per junction.

---

## 2. Per‑Address Agents  
For **each address** in the route, sequentially execute these four agents:

### 1. Video Agent
- Finds a relevant **YouTube video** for the specific address/place.  
- **Output**: YouTube URL + short title/description.

### 2. Music Agent
- Finds a **song** that fits the address or atmosphere (from **YouTube or Spotify**).  
- **Output**: Track URL + short explanation.

### 3. Info Agent
- Retrieves a **historical story, fun fact, or relevant textual info** about the address or nearby landmark.  
- **Output**: brief written summary (few sentences) + optional reference URL.

### 4. Choice Agent
- Receives the three outputs (Video, Music, Info).  
- Selects **one** final recommendation based on relevance and usefulness.  
- **Output**: chosen item with:
  - `type` (`video` | `music` | `info`)
  - title (if relevant)
  - URL or text
  - reason for the selection

---

## 3. Final Output Format
Return a structured JSON-like object:

```json
{
  "source": "<source_address>",
  "destination": "<destination_address>",
  "stops": [
    {
      "address": "<full_address_1>",
      "choice": {
        "type": "video | music | info",
        "title": "<title if applicable>",
        "content": "<URL or text>",
        "reason": "<why this was chosen>"
      }
    },
    {
      "address": "<full_address_2>",
      "choice": { ... }
    }
  ]
}
```

Only the **Choice Agent’s** selected item is shown to the user for each address along the route.
