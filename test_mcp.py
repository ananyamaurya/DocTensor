import json
from doctensor.mcp_server import mcp

async def run():
    print("Listing tools...")
    for tool in mcp._tools:
        print(f"- {tool.name}")
        
    print("\nCalling get_document_metadata...")
    res = await mcp.call_tool("get_document_metadata", {"file_path": "testImages/01190197_01190199.jpg"})
    print(res)

import asyncio
asyncio.run(run())
