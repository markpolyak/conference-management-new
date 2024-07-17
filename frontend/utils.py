from typing import Literal
import aiohttp
import cfg


async def fetch(method: Literal["POST", "GET"], path: str | None = None, params: dict | None = None, data: dict | None = None):

    url = f"http://{cfg.SERVER_HOST}:{cfg.SERVER_PORT}"

    if path:
        url += path

    if(method == "GET"):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    print(f"Failed to fetch data: {response.status}")
                    return None
                
    if(method == "POST"):

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    print(f"Failed to fetch data: {response.status}")
                    errMsg = await response.json()
                    raise Exception(errMsg["message"])
                
async def download_file(dest: str, path: str):
    
    url = f"http://{cfg.SERVER_HOST}:{cfg.SERVER_PORT}"
    
    if path:
        url += path
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(dest, 'wb') as f:
                    f.write(await response.read())
            else:
                raise Exception(f"Failed to download file: {response.status}")