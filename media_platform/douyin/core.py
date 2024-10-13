import asyncio
import os
import random
import pickle
from asyncio import Task
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import (BrowserContext, BrowserType, Page,
                                  async_playwright)

import config
from base.base_crawler import AbstractCrawler
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from store import douyin as douyin_store
from tools import utils
from var import crawler_type_var, source_keyword_var

from .client import DOUYINClient
from .exception import DataFetchError
from .field import PublishTimeType
from .login import DouYinLogin


class DouYinCrawler(AbstractCrawler):
    context_pages: List[Page]
    dy_clients: List[DOUYINClient]
    browser_contexts: List[BrowserContext]

    def __init__(self) -> None:
        self.index_url = "https://www.douyin.com"
        self.dy_clients = []
        self.browser_contexts = []
        self.context_pages = []

    async def start(self) -> None:
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:
            ip_proxy_pool = await create_ip_pool(config.IP_PROXY_POOL_COUNT, enable_validate_ip=True)
            ip_proxy_info: IpInfoModel = await ip_proxy_pool.get_proxy()
            _, httpx_proxy_format = self.format_proxy_info(ip_proxy_info)

        async with async_playwright() as playwright:
            chromium = playwright.chromium
            
            # 为每个账户创建独立的浏览器上下文
            for i in range(config.DY_CLIENT_COUNT):
                browser_context: BrowserContext = await self.launch_browser(
                    chromium,
                    None,
                    user_agent=None,
                    headless=config.HEADLESS,
                    user_data_dir=f"browser_data_{i}"
                )
                self.browser_contexts.append(browser_context)
                
                context_page = await browser_context.new_page()
                await context_page.goto(self.index_url)
                self.context_pages.append(context_page)

                await browser_context.add_init_script(path="libs/stealth.min.js")
                dy_client = await self.create_douyin_client(httpx_proxy_format, i)
                if not await dy_client.pong(browser_context=self.browser_contexts[i]):
                    login_obj = DouYinLogin(
                        login_type=config.LOGIN_TYPE,
                        login_phone="",  # 你的手机号
                        browser_context=self.browser_contexts[i],
                        context_page=self.context_pages[i],
                        cookie_str=config.COOKIES
                    )
                    await login_obj.begin()
                    await dy_client.update_cookies(browser_context=self.browser_contexts[i])
                    
                # 如果没有之前的dy_clients，创建新的
                if not os.path.exists('dy_clients.pkl'):
                    dy_client = await self.create_douyin_client(httpx_proxy_format, i)
                    if not await dy_client.pong(browser_context=self.browser_contexts[i]):
                        login_obj = DouYinLogin(
                            login_type=config.LOGIN_TYPE,
                            login_phone="",  # 你的手机号
                            browser_context=self.browser_contexts[i],
                            context_page=self.context_pages[i],
                            cookie_str=config.COOKIES
                        )
                        await login_obj.begin()
                        await dy_client.update_cookies(browser_context=self.browser_contexts[i])
                    self.dy_clients.append(dy_client)

            # 保存dy_clients
            if not self.dy_clients:
                await self.save_dy_clients()

            crawler_type_var.set(config.CRAWLER_TYPE)
            if config.CRAWLER_TYPE == "search":
                await self.search()
            elif config.CRAWLER_TYPE == "detail":
                await self.get_specified_awemes()
            elif config.CRAWLER_TYPE == "creator":
                await self.get_creators_and_videos()

            utils.logger.info("[DouYinCrawler.start] Douyin Crawler finished ...")

    async def search(self) -> None:
        utils.logger.info("[DouYinCrawler.search] Begin search douyin keywords")
        dy_limit_count = 10
        if config.CRAWLER_MAX_NOTES_COUNT < dy_limit_count:
            config.CRAWLER_MAX_NOTES_COUNT = dy_limit_count
        start_page = config.START_PAGE
        for keyword in config.KEYWORDS.split(","):
            source_keyword_var.set(keyword)
            utils.logger.info(f"[DouYinCrawler.search] Current keyword: {keyword}")
            aweme_list: List[str] = []
            page = 0
            dy_search_id = ""
            while (
                page - start_page + 1
            ) * dy_limit_count <= config.CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    utils.logger.info(f"[DouYinCrawler.search] Skip {page}")
                    page += 1
                    continue
                try:
                    utils.logger.info(
                        f"[DouYinCrawler.search] search douyin keyword: {keyword}, page: {page}"
                    )
                    dy_client = random.choice(self.dy_clients)
                    posts_res = await dy_client.search_info_by_keyword(
                        keyword=keyword,
                        offset=page * dy_limit_count - dy_limit_count,
                        publish_time=PublishTimeType(config.PUBLISH_TIME_TYPE),
                        search_id=dy_search_id,
                    )
                except DataFetchError:
                    utils.logger.error(
                        f"[DouYinCrawler.search] search douyin keyword: {keyword} failed"
                    )
                    break

                page += 1
                if "data" not in posts_res:
                    utils.logger.error(
                        f"[DouYinCrawler.search] search douyin keyword: {keyword} failed，账号也许被风控了。"
                    )
                    break
                dy_search_id = posts_res.get("extra", {}).get("logid", "")
                for post_item in posts_res.get("data"):
                    try:
                        aweme_info: Dict = (
                            post_item.get("aweme_info")
                            or post_item.get("aweme_mix_info", {}).get("mix_items")[0]
                        )
                    except TypeError:
                        continue
                    aweme_list.append(aweme_info.get("aweme_id", ""))
                    await douyin_store.update_douyin_aweme(aweme_item=aweme_info)
            utils.logger.info(
                f"[DouYinCrawler.search] keyword:{keyword}, aweme_list:{aweme_list}"
            )
            await self.batch_get_note_comments(aweme_list)

    async def get_specified_awemes(self):
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_aweme_detail(aweme_id=aweme_id, semaphore=semaphore)
            for aweme_id in config.DY_SPECIFIED_ID_LIST
        ]
        aweme_details = await asyncio.gather(*task_list)
        for aweme_detail in aweme_details:
            if aweme_detail is not None:
                await douyin_store.update_douyin_aweme(aweme_detail)
        await self.batch_get_note_comments(config.DY_SPECIFIED_ID_LIST)


    async def get_aweme_detail(self, aweme_id: str, semaphore: asyncio.Semaphore) -> Any:
        async with semaphore:
            try:
                client_index = random.randint(0, len(self.dy_clients) - 1)
                dy_client = self.dy_clients[client_index]
                return await dy_client.get_video_by_id(aweme_id)
            except DataFetchError as ex:
                utils.logger.error(f"[DouYinCrawler.get_aweme_detail] Get aweme detail error: {ex}")
                return None
            except KeyError as ex:
                utils.logger.error(
                    f"[DouYinCrawler.get_aweme_detail] have not fund note detail aweme_id:{aweme_id}, err: {ex}")
                return None

    async def batch_get_note_comments(self, aweme_list: List[str]) -> None:
        if not config.ENABLE_GET_COMMENTS:
            utils.logger.info(
                f"[DouYinCrawler.batch_get_note_comments] Crawling comment mode is not enabled"
            )
            return

        task_list: List[Task] = []
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        for aweme_id in aweme_list:
            task = asyncio.create_task(
                self.get_comments(aweme_id=aweme_id, semaphore=semaphore), name=aweme_id
            )
            task_list.append(task)
        if len(task_list) > 0:
            await asyncio.wait(task_list)

    async def get_comments(self, aweme_id: str, semaphore: asyncio.Semaphore) -> None:
        async with semaphore:
            try:
                client_index = random.randint(0, len(self.dy_clients) - 1)
                dy_client = self.dy_clients[client_index]
                await dy_client.get_aweme_all_comments(
                    aweme_id=aweme_id,
                    crawl_interval=random.random(),
                    is_fetch_sub_comments=config.ENABLE_GET_SUB_COMMENTS,
                    callback=douyin_store.batch_update_dy_aweme_comments
                )
                utils.logger.info(
                    f"[DouYinCrawler.get_comments] aweme_id: {aweme_id} comments have all been obtained and filtered ...")
            except DataFetchError as e:
                utils.logger.error(f"[DouYinCrawler.get_comments] aweme_id: {aweme_id} get comments failed, error: {e}")

    async def get_creators_and_videos(self) -> None:
        utils.logger.info(
            "[DouYinCrawler.get_creators_and_videos] Begin get douyin creators"
        )
        for user_id in config.DY_CREATOR_ID_LIST:
            dy_client = random.choice(self.dy_clients)
            creator_info: Dict = await dy_client.get_user_info(user_id)
            if creator_info:
                await douyin_store.save_creator(user_id, creator=creator_info)

            all_video_list = await dy_client.get_all_user_aweme_posts(
                sec_user_id=user_id, callback=self.fetch_creator_video_detail
            )

            video_ids = [video_item.get("aweme_id") for video_item in all_video_list]
            await self.batch_get_note_comments(video_ids)

    async def fetch_creator_video_detail(self, video_list: List[Dict]):
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_aweme_detail(post_item.get("aweme_id"), semaphore)
            for post_item in video_list
        ]

        note_details = await asyncio.gather(*task_list)
        for aweme_item in note_details:
            if aweme_item is not None:
                await douyin_store.update_douyin_aweme(aweme_item)

    @staticmethod
    def format_proxy_info(
        ip_proxy_info: IpInfoModel,
    ) -> Tuple[Optional[Dict], Optional[Dict]]:
        playwright_proxy = {
            "server": f"{ip_proxy_info.protocol}{ip_proxy_info.ip}:{ip_proxy_info.port}",
            "username": ip_proxy_info.user,
            "password": ip_proxy_info.password,
        }
        httpx_proxy = {
            f"{ip_proxy_info.protocol}": f"http://{ip_proxy_info.user}:{ip_proxy_info.password}@{ip_proxy_info.ip}:{ip_proxy_info.port}"
        }
        return playwright_proxy, httpx_proxy

    async def create_douyin_client(self, httpx_proxy: Optional[str], index: int) -> DOUYINClient:
        cookie_str, cookie_dict = utils.convert_cookies(await self.browser_contexts[index].cookies())
        douyin_client = DOUYINClient(
            proxies=httpx_proxy,
            headers={
                "User-Agent": await self.context_pages[index].evaluate("() => navigator.userAgent"),
                "Cookie": cookie_str,
                "Host": "www.douyin.com",
                "Origin": "https://www.douyin.com/",
                "Referer": "https://www.douyin.com/",
                "Content-Type": "application/json;charset=UTF-8"
            },
            playwright_page=self.context_pages[index],
            cookie_dict=cookie_dict,
        )
        return douyin_client

    async def launch_browser(
            self,
            chromium: BrowserType,
            playwright_proxy: Optional[Dict],
            user_agent: Optional[str],
            headless: bool = True,
            user_data_dir: str = ""
    ) -> BrowserContext:
        if config.SAVE_LOGIN_STATE:
            user_data_dir = os.path.join(os.getcwd(), "browser_data",
                                         f"{config.USER_DATA_DIR}_{user_data_dir}")
            browser_context = await chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                accept_downloads=True,
                headless=headless,
                proxy=playwright_proxy,
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent
            )
            return browser_context
        else:
            browser = await chromium.launch(headless=headless, proxy=playwright_proxy)
            browser_context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent
            )
            return browser_context

    async def save_dy_clients(self):
        clients_data = []
        for i, client in enumerate(self.dy_clients):
            client_data = {
                'headers': client.headers,
                'cookie_dict': client.cookie_dict,
                'proxies': client.proxies,
                'user_data_dir': f"browser_data_{i}"
            }
            clients_data.append(client_data)
        
        with open('dy_clients.pkl', 'wb') as f:
            pickle.dump(clients_data, f)

    async def restore_dy_clients(self):
        with open('dy_clients.pkl', 'rb') as f:
            clients_data = pickle.load(f)
        
        for i, client_data in enumerate(iterable=clients_data):
            dy_client = DOUYINClient(
                proxies=client_data['proxies'],
                headers=client_data['headers'],
                playwright_page=self.context_pages[i],
                cookie_dict=client_data['cookie_dict']
            )
            self.dy_clients.append(dy_client)

    async def close(self) -> None:
        for browser_context in self.browser_contexts:
            await browser_context.close()
        utils.logger.info("[DouYinCrawler.close] All browser contexts closed ...")
