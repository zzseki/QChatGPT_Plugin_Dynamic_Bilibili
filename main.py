import threading
import time
import asyncio
from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import os
import requests
import httpx
import logging
import re
from mirai import Image, MessageChain, Plain
from plugins.QChatGPT_Plugin_Dynamic_Bilibili.dynamic import get_information

stop_thread = False
thread = None
text = ''
api_token = 'YOUR_TOKEN'  # 请将这里的'YOUR_TOKEN'替换为你实际获取的token
# 注册插件
@register(name="Dynamic_Bilibili", description="获取b站up的动态推送", version="0.1", author="zzseki")
class B_Live(BasePlugin):
    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.logger = logging.getLogger(__name__)

    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext, **kwargs):
        global thread
        global stop_thread
        receive_text = ctx.event.text_message
        pattern = re.compile(r"#开启动态推送")
        match = pattern.search(receive_text)

        if match:
            # await self.main(ctx)
            if thread is None or not thread.is_alive():
                thread = threading.Thread(target=self.run_in_thread, args=(ctx,), daemon=True)
                thread.start()
            else:
                self.ap.logger.info("线程已经在运行中，跳过启动。")
                await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("动态推送已开启，无需重复开启")], False)
            ctx.prevent_default()
        else:
            pattern = re.compile(r"#关闭动态推送")
            match = pattern.search(receive_text)
            if match:
                if thread is not None and thread.is_alive():
                    await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("正在关闭动态推送......")], False)
                    stop_thread = True
                    thread.join()  # 等待线程结束
                    self.ap.logger.info("动态推送线程关闭")
                    await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("已关闭动态推送")], False)
                else:
                    await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("未开启动态推送，无需关闭")], False)
                ctx.prevent_default()
            else:
                pattern = re.compile(r"#关注up.*\[(\d+)\]")
                match = pattern.search(receive_text)
                if match:
                    id = match.group(1)
                    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UID.txt"), "r", encoding="utf-8") as file:
                        existing_ids = file.read().splitlines()  # 读取所有ID并按行分割
                    if id not in existing_ids:
                        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UID.txt"), "a", encoding="utf-8") as file:
                            file.write(id + f"\n")
                        await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("关注成功")], False)
                        await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("注意需要关闭并重新开启动态推送功能才会生效")], False)
                    else:
                        await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("此up已在关注列表中，无需重复添加")], False)
                    ctx.prevent_default()
                pattern = re.compile(r"#取消关注up.*\[(\d+)\]")
                match = pattern.search(receive_text)
                if match:
                    id_to_remove = match.group(1)
                    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "UID.txt")

                    # 读取当前UID.txt中的内容
                    with open(file_path, "r", encoding="utf-8") as file:
                        lines = file.readlines()

                    # 过滤掉要删除的ID
                    updated_lines = [line for line in lines if line.strip() != id_to_remove]

                    # 写回文件，更新内容
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.writelines(updated_lines)

                    await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("取消关注成功")], False)
                    await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("注意需要关闭并重新开启动态推送功能才会生效")], False)
                    ctx.prevent_default()

    def run_in_thread(self, ctx):
        asyncio.run(self.main(ctx))  # 在独立线程中运行异步函数

    async def main(self, ctx):
        global stop_thread
        global text
        global processes
        # await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("正在开启动态推送......")], False)
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "UID.txt")
        with open(file_path, "r", encoding="utf-8") as file:
            ids = [line.strip() for line in file if line.strip()]
        if not ids:
            await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("开启失败，关注up数量为0\n请发送'#关注up[UID]'以添加关注")], False)
        else:
            for id in ids:
                get_information(id)
            time.sleep(10)
            # 清除历史文本
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "path.txt"), 'w') as file:
                pass
            await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [("成功开启动态推送")], False)
            while not stop_thread:
                for id in ids:
                    get_information(id)
                    time.sleep(10)
                    if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), "path.txt")):
                        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "path.txt"), "r",
                                  encoding="utf-8") as file:
                            lines = file.readlines()
                            try:
                                if text != lines[-1].replace("\n", ""):
                                    text = lines[-1].replace("\n", "")
                                    self.ap.logger.info(text)
                                    if re.search('.png', text):
                                        # 设置 API Token 和上传图片的路径
                                        global api_token
                                        file_path = text

                                        # 设置请求头和文件
                                        headers = {
                                            'Authorization': api_token
                                        }
                                        files = {
                                            'smfile': open(file_path, 'rb')
                                        }

                                        # 发起 POST 请求上传图片
                                        response = requests.post('https://sm.ms/api/v2/upload', headers=headers,
                                                                 files=files)
                                        if response.status_code == 200:
                                            inf = response.json()
                                            image_url = inf['data']['url']
                                            ctx.add_return("reply", [Image(url=image_url)])
                                            await ctx.send_message(target_type='group', target_id=123456789, message=MessageChain([Image(url=image_url)]))
                                    # else:
                                    #     # await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, [(text)],False)
                                    #     await ctx.send_message(target_type='group', target_id=123456789, message=text)
                            except:
                                continue
                time.sleep(60)
    # 插件卸载时触发
    def __del__(self):
        pass
