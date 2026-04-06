import subprocess
import asyncio

async def ping(host: str, count: int = 5, timeout: int = 1) -> bool:
    """
    Returns True if host is reachable, False otherwise.
    """
    try:
        result = await asyncio.create_subprocess_exec(
            "ping", 
            "-c", str(count), 
            "-W", str(timeout),
            
            host,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        await result.communicate()
        return result.returncode == 0
    except Exception:
        return False