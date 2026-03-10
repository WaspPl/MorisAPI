import asyncio
from pathlib import Path
from fastapi import HTTPException, status
import subprocess

async def executeCommand(script_path: Path, arguments_string: str) -> str:
    if not script_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script file not found."
        )
    try:
        result = subprocess.run(
            ["python", str(script_path), arguments_string],
            capture_output=True,
            text=True,
            check=True
            )
        return result.stdout

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Script crashed: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System error: {str(e)}"
        )
async def getLLMResponse(content: str = None) -> str:
    return ' '.join([content,"llm response"])

async def sendDataToDisplays() -> None:
    await asyncio.sleep(10)
    print('sent')
    return