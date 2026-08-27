import asyncio
import httpx

from app.config import get_settings
from app.core.auth import JoblogicAuth


async def main():
    settings = get_settings()

    print("Identity URL:", settings.joblogic_identity_url)
    print("Client ID:", settings.joblogic_client_id)
    print("Scope:", settings.joblogic_scope)

    async with httpx.AsyncClient(timeout=30) as client:
        auth = JoblogicAuth(settings, client)

        try:
            token = await auth.get_access_token()

            print("\nOAuth SUCCESS!")
            print("Token received:", bool(token))
            print("Token length:", len(token) if token else 0)

        except Exception as e:
            print("\nOAuth FAILED!")
            print(type(e).__name__)
            print(str(e))


if __name__ == "__main__":
    asyncio.run(main())