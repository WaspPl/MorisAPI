import asyncio
async def executeCommand() -> str:
    await asyncio.sleep(1)
    return "command response"

async def getLLMResponse(content) -> str:
    return content + " llm response"

async def sendDataToDisplays():
    return