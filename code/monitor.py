import subprocess
import asyncio
from models import Monitoring_Template

async def ping(host: str, ping_count: int, timeout: int) -> bool:
    """
    Returns True if host is reachable, False otherwise.
    """
    try:
        result = await asyncio.create_subprocess_exec(
            "ping", 
            "-c", str(ping_count), 
            "-W", str(timeout), 
            
            host,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        await result.communicate()
        return result.returncode == 0
    
    except Exception:
        return False