from httpx import AsyncClient, HTTPStatusError, RequestError

from src.exceptions import ExceptionWithMessageForUser


async def fetch_html(url: str, client: AsyncClient) -> str:
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
    except (RequestError, HTTPStatusError) as e:
        raise ExceptionWithMessageForUser(
            message_for_user=f'Failed to fetch data from url: "f{url}"'
        ) from e
