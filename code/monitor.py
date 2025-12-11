import subprocess
import asyncio

async def ping(host: str) -> bool:
    """
    Returns True if host is reachable, False otherwise.
    """
    try:
        result = await asyncio.create_subprocess_exec(
            "ping", "-c", "1", host,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        await result.communicate()
        return result.returncode == 0
    except Exception:
        return False