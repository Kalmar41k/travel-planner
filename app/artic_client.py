import httpx

BASE = "https://api.artic.edu/api/v1"


async def fetch_artwork(external_id: int) -> dict | None:
    url = f"{BASE}/artworks/{external_id}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        if resp.status_code == 200:
            return resp.json()
    return None
