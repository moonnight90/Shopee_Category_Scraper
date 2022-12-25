import asyncio,httpx

class Asynio_Requests():
    def __init__(self) -> None:
        self.URLS = []
        self.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
    
    def add_links(self,links:list): 
        # self.URLS.extend(links)
        self.URLS = links
    async def get_response(self,client:httpx.AsyncClient,url,params={},payload={}):
        # print(url,params)

        while True:
            try:
                res = await client.get(url,params=params,timeout=5)
                break
            except Exception as e: pass
        return res.json()
    async def main(self):
        async with httpx.AsyncClient(headers=self.headers) as client:
            task = []
            for url in self.URLS:
                task.append(asyncio.create_task(self.get_response(client,url['url'],params=url['params'])))
            results = await asyncio.gather(*task)
        return results
    def run(self):
        return asyncio.get_event_loop().run_until_complete(self.main())
