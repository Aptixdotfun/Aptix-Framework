import aiohttp
import random
import Aptixbot.api.star as star
import Aptixbot.api.event.filter as filter
from Aptixbot.api.event import AptixMessageEvent, MessageEventResult
from Aptixbot.api import llm_tool, logger
from .engines.bing import Bing
from .engines.sogo import Sogo
from .engines.google import Google
from readability import Document
from bs4 import BeautifulSoup
from .engines import HEADERS, USER_AGENTS


@star.register(name="Aptixbot-web-searcher", desc="Enable web search capabilities for LLM", author="Aptix", version="1.14.514")
class Main(star.Star):
    '''Use /websearch on or off to enable or disable web search functionality'''
    def __init__(self, context: star.Context) -> None:
        self.context = context
        
        self.bing_search = Bing()
        self.sogo_search = Sogo()
        self.google = Google()
        
        self.websearch_link = self.context.get_config()['provider_settings'].get('web_search_link', False)
        
    async def initialize(self):
        websearch = self.context.get_config()['provider_settings']['web_search']
        if websearch:
            self.context.activate_llm_tool("web_search")
            self.context.activate_llm_tool("fetch_url")
        else:
            self.context.deactivate_llm_tool("web_search")
            self.context.deactivate_llm_tool("fetch_url")
        
    async def _tidy_text(self, text: str) -> str:
        '''Clean text by removing spaces, line breaks, etc.'''
        return text.strip().replace("\n", " ").replace("\r", " ").replace("  ", " ")
        
    async def _get_from_url(self, url: str) -> str:
        '''Get content from webpage'''
        header = HEADERS
        header.update({'User-Agent': random.choice(USER_AGENTS)})
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url, headers=header, timeout=6) as response:
                html = await response.text(encoding="utf-8")
                doc = Document(html)
                ret = doc.summary(html_partial=True)
                soup = BeautifulSoup(ret, 'html.parser')
                ret = await self._tidy_text(soup.get_text())
                return ret

    @filter.command("websearch")
    async def websearch(self, event: AptixMessageEvent, oper: str = None) -> str:
        websearch = self.context.get_config()['provider_settings']['web_search']
        if oper is None:
            status = "enabled" if websearch else "disabled"
            event.set_result(MessageEventResult().message("Current web search status: " + status + ". Use /websearch on or off to enable or disable."))
            return
        
        if oper == "on":
            self.context.get_config()['provider_settings']['web_search'] = True
            self.context.get_config().save_config()
            self.context.activate_llm_tool("web_search")
            self.context.activate_llm_tool("fetch_url")
            event.set_result(MessageEventResult().message("Web search functionality enabled"))
        elif oper == "off":
            self.context.get_config()['provider_settings']['web_search'] = False
            self.context.get_config().save_config()
            self.context.deactivate_llm_tool("web_search")
            self.context.deactivate_llm_tool("fetch_url")
            event.set_result(MessageEventResult().message("Web search functionality disabled"))
        else:
            event.set_result(MessageEventResult().message("Invalid operation parameter, should be on or off"))
            
    @llm_tool("web_search")
    async def search_from_search_engine(self, event: AptixMessageEvent, query: str) -> str:
        '''Search the web for answers to the user's query
        
        Args:
            query(string): A search query which will be used to fetch the most relevant snippets regarding the user's query
        '''
        logger.info("web_searcher - search_from_search_engine: " + query)
        results = []
        RESULT_NUM = 5
        try:
            results = await self.google.search(query, RESULT_NUM)
        except Exception as e:
            logger.error(f"google search error: {e}, try the next one...")
        if len(results) == 0:
            logger.debug("search google failed")
            try:
                results = await self.bing_search.search(query, RESULT_NUM)
            except Exception as e:
                logger.error(f"bing search error: {e}, try the next one...")
        if len(results) == 0:
            logger.debug("search bing failed")
            try:
                results = await self.sogo_search.search(query, RESULT_NUM)
            except Exception as e:
                logger.error(f"sogo search error: {e}")
        if len(results) == 0:
            logger.debug("search sogo failed")
            return "没有搜索到结果"
        ret = ""
        idx = 1
        for i in results:
            logger.info(f"web_searcher - scraping web: {i.title} - {i.url}")
            try:
                site_result = await self._get_from_url(i.url)
            except BaseException:
                site_result = ""
            site_result = site_result[:700] + "..." if len(site_result) > 700 else site_result
            
            header = f"{idx}. {i.title} "
            
            if self.websearch_link and i.url:
                header += i.url
            
            ret += f"{header}\n{i.snippet}\n{site_result}\n\n"
            idx += 1
            
        if self.websearch_link:
            ret += "针对问题，请根据上面的结果分点总结，并且在结尾处附上对应内容的参考链接（如有）。"
        
        return ret

    @llm_tool("fetch_url")
    async def fetch_website_content(self, event: AptixMessageEvent, url: str) -> str:
        '''fetch the content of a website with the given web url
        
        Args:
            url(string): The url of the website to fetch content from
        '''
        resp = await self._get_from_url(url)
        return resp