import httpx

from data.config import PROVIDERS_CODE, API_URL


async def get_provider_schedule_from_api(provider):
    provider_code = PROVIDERS_CODE.get(provider)
    if provider_code is None:
        raise ValueError(f"Unknown provider: {provider}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL.format(code=provider_code))
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError) as e:
        print(f"[{provider}] API error: {e}")
        return None
