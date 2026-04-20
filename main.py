# ============================================================
# astrbot_plugin_qqprofile_ex
# 基于 Zhalslar 的 astrbot_plugin_qqprofile (v1.1.3) 修改
# 原项目地址: https://github.com/Zhalslar/astrbot_plugin_qqprofile
# 原项目协议: AGPL-3.0
#
# 修改内容:
#   - 新增 AI 自主行为工具 (llm_tool): 自动改签名、状态、昵称
#   - 新增定时状态切换功能
#   - 新增对应的配置面板选项
#
# 修改者: 菀菀
# ============================================================

import asyncio
import astrbot.api.message_components as Comp
from astrbot import logger
from astrbot.api.event import filter
from astrbot.api.star import Context, Star
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.platform import AstrMessageEvent
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)
from astrbot.core.star.filter.permission import PermissionType
from astrbot.core.star.star_tools import StarTools
from astrbot.api.all import llm_tool

from .status import status_mapping
from .utils import download_image, get_nickname


class QQProfileExPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.conf = config
        self.curr_nickname = None
        self.curr_status = None
        self.curr_signature = None
        self.avatar_dir = StarTools.get_data_dir("astrbot_plugin_qqprofile_ex") / "avatar"
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
        self._schedule_task = None
        self._bot_instance = None

        # 启动定时状态切换
        if self.conf.get("enable_schedule", False):
            self._schedule_task = asyncio.create_task(self._status_schedule_loop())
            logger.info("[QQProfileEx] 定时状态切换已启动")

    # ==========================================
    # AI 自主行为工具 (新增功能)
    # ==========================================

    @llm_tool(name="change_my_signature")
    async def auto_set_signature(self, event: AstrMessageEvent, signature: str):
        """
        当你的心情、想法发生变化时，调用此工具修改你的QQ个性签名。

        Args:
            signature (string): 新的QQ个性签名内容。
        """
        if not self.conf.get("auto_signature", True):
            return "签名自动修改功能已关闭。"
        if isinstance(event, AiocqhttpMessageEvent):
            old_signature = self.curr_signature or "未知"
            await event.bot.set_self_longnick(longNick=signature)
            self.curr_signature = signature
            logger.info(f"[QQProfileEx] 签名已修改为: {signature}")
            return f"签名修改成功。从「{old_signature}」改为「{signature}」。请继续你的日常回复，不必特意提及你改了签名。"
        return "当前平台暂不支持修改签名。"

    @llm_tool(name="change_my_status")
    async def auto_set_status(self, event: AstrMessageEvent, status: str):
        """
        当你去睡觉、执行任务、玩游戏或情绪起伏时，调用此工具修改QQ在线状态。

        Args:
            status (string): 支持的状态包括：在线、隐身、离开、忙碌、Q我吧、请勿打扰、睡觉中、游戏中、学习中、吃饭中、听歌中等。
        """
        if not self.conf.get("auto_status", True):
            return "状态自动修改功能已关闭。"
        if isinstance(event, AiocqhttpMessageEvent):
            params = status_mapping.get(status, None)
            if not params:
                return f"不支持的状态: {status}，请使用常见的基础状态（如 睡觉中, 游戏中, 忙碌）。"
            old_status = self.curr_status or "未知"
            await event.bot.set_online_status(
                status=params[0], ext_status=params[1], battery_status=0
            )
            self._bot_instance = event.bot
            self.curr_status = status
            logger.info(f"[QQProfileEx] 状态已修改为: {status}")
            return f"状态修改成功。从「{old_status}」改为「{status}」。请继续你的日常回复，不必特意提及你改了状态。"
        return "当前平台暂不支持修改状态。"

    @llm_tool(name="change_my_nickname")
    async def auto_set_nickname(self, event: AstrMessageEvent, nickname: str):
        """
        当你想要改变自己的称呼、或者根据情境调整昵称时，调用此工具修改你的QQ昵称。
        比如心情好的时候加个后缀、节日的时候换个应景的昵称。

        Args:
            nickname (string): 新的QQ昵称。
        """
        if not self.conf.get("auto_nickname", True):
            return "昵称自动修改功能已关闭。"
        if isinstance(event, AiocqhttpMessageEvent):
            old_nickname = self.curr_nickname or "未知"
            await event.bot.set_qq_profile(nickname=nickname)
            self.curr_nickname = nickname
            logger.info(f"[QQProfileEx] 昵称已修改为: {nickname}")
            return f"昵称修改成功。从「{old_nickname}」改为「{nickname}」。请继续你的日常回复，不必特意提及你改了昵称。"
        return "当前平台暂不支持修改昵称。"

    # ==========================================
    # 定时状态切换 (新增功能)
    # ==========================================

    async def _status_schedule_loop(self):
        """定时状态切换循环"""
        while True:
            try:
                await asyncio.sleep(60)
                if not self._bot_instance:
                    continue

                import datetime
                now = datetime.datetime.now()
                hour = now.hour
                schedule_raw = self.conf.get("status_schedule", "{}")
                try:
                    import json as _json
                    schedule = _json.loads(schedule_raw) if isinstance(schedule_raw, str) else schedule_raw
                except Exception:
                    schedule = {}

                if not schedule:
                    continue

                target_status = None
                for time_range, status_name in schedule.items():
                    try:
                        parts = time_range.split("-")
                        start_hour = int(parts[0])
                        end_hour = int(parts[1])
                        if start_hour <= end_hour:
                            if start_hour <= hour < end_hour:
                                target_status = status_name
                                break
                        else:  # 跨午夜，如 23-7
                            if hour >= start_hour or hour < end_hour:
                                target_status = status_name
                                break
                    except (ValueError, IndexError):
                        continue

                if target_status:
                    params = status_mapping.get(target_status, None)
                    if params:
                        await self._bot_instance.set_online_status(
                            status=params[0], ext_status=params[1], battery_status=0
                        )
                        logger.debug(f"[QQProfileEx] 当前{hour}点, 状态切换为: {target_status}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[QQProfileEx] 定时切换异常: {e}")
                await asyncio.sleep(300)

    # ==========================================
    # 辅助方法 (来自原版)
    # ==========================================

    async def get_curr_persona_id(self, event: AstrMessageEvent) -> str | None:
        """获取当前会话的人格ID"""
        umo = event.unified_msg_origin
        cid = await self.context.conversation_manager.get_curr_conversation_id(umo)
        if not cid:
            return
        conversation = await self.context.conversation_manager.get_conversation(
            unified_msg_origin=umo,
            conversation_id=cid,
            create_if_not_exists=True,
        )
        if (
            conversation
            and conversation.persona_id
            and conversation.persona_id != "[%None]"
        ):
            return conversation.persona_id

        # 兜底
        if persona_v3 := self.context.persona_manager.selected_default_persona_v3:
            persona_id = persona_v3.get("name")
            if persona_id and persona_id != "[%None]":
                return persona_id

    # ==========================================
    # 手动指令 (来自原版)
    # ==========================================

    @filter.permission_type(PermissionType.ADMIN)
    @filter.command("设置头像")
    async def set_avatar(self, event: AiocqhttpMessageEvent):
        "将引用的图片设置为头像"
        chain = event.get_messages()
        img_url = None
        for seg in chain:
            if isinstance(seg, Comp.Image):
                img_url = seg.url
                break
            elif isinstance(seg, Comp.Reply):
                if seg.chain:
                    for reply_seg in seg.chain:
                        if isinstance(reply_seg, Comp.Image):
                            img_url = reply_seg.url
                            break
        if not img_url:
            yield event.plain_result("需要引用一张图片")
            return

        await event.bot.set_qq_avatar(file=img_url)
        yield event.plain_result("我换头像啦~")
        if persona_id := await self.get_curr_persona_id(event):
            save_path = self.avatar_dir / f"{persona_id}.jpg"
            try:
                await download_image(img_url, str(save_path))
                logger.debug(f"头像已保存到：{str(save_path)}")
            except Exception as e:
                logger.error(f"保存头像失败：{e}")

    @filter.permission_type(PermissionType.ADMIN)
    @filter.command("设置签名")
    async def set_longnick(
        self, event: AiocqhttpMessageEvent, longnick: str | None = None
    ):
        """设置Bot的签名，并同步空间（可在QQ里关掉）"""
        if not longnick:
            yield event.plain_result("没提供新签名呢")
            return
        await event.bot.set_self_longnick(longNick=longnick)
        yield event.plain_result(f"我签名已更新：{longnick}")

    @filter.permission_type(PermissionType.ADMIN)
    @filter.command("设置状态")
    async def set_status(
        self, event: AiocqhttpMessageEvent, status_name: str | None = None
    ):
        """设置Bot的在线状态"""
        if not status_name:
            yield event.plain_result("没提供新状态呢")
            return
        params = status_mapping.get(status_name, None)
        if not params:
            yield event.plain_result(f"状态【{status_name}】暂未支持")
            return
        await event.bot.set_online_status(
            status=params[0], ext_status=params[1], battery_status=0
        )
        self._bot_instance = event.bot
        yield event.plain_result(f"我状态已更新为【{status_name}】")

    @filter.permission_type(PermissionType.ADMIN)
    @filter.command("设置昵称")
    async def set_nickname(
        self, event: AiocqhttpMessageEvent, nickname: str | None = None
    ):
        """设置Bot的昵称"""
        nickname = nickname or await self.get_curr_persona_id(event)
        if not nickname:
            yield event.plain_result("未输入新昵称")
            return
        await event.bot.set_qq_profile(nickname=nickname)
        self.curr_nickname = nickname
        yield event.plain_result(f"我昵称已改为【{nickname}】")

    async def sync_nickname_and_avatar(
        self, event: AiocqhttpMessageEvent, persona_id: str
    ):
        """在请求 LLM 前同步bot昵称与人格名"""

        if not self.curr_nickname:
            if new_nickname := await get_nickname(event):
                self.curr_nickname = new_nickname

        if self.curr_nickname != persona_id:
            self.curr_nickname = persona_id

            await event.bot.set_qq_profile(nickname=persona_id)
            logger.debug(f"已同步bot的昵称为：{persona_id}")
            avatar_path = self.avatar_dir / f"{persona_id}.jpg"
            if avatar_path.exists():
                await event.bot.set_qq_avatar(file=str(avatar_path))
                logger.debug(f"已同步bot的头像为：{str(avatar_path)}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("切换人格")
    async def change_persona(
        self, event: AiocqhttpMessageEvent, persona_id: str | None = None
    ):
        # 确定目标人格ID
        if persona_id:
            target_persona = next(
                (
                    p
                    for p in self.context.provider_manager.personas
                    if p["name"] == persona_id
                ),
                None,
            )
            if not target_persona:
                yield event.plain_result(f"【{persona_id}】人格不存在")
                return
            target_persona_id = target_persona["name"]
        else:
            target_persona_id = await self.get_curr_persona_id(event)
            if not target_persona_id:
                return

        # 切换人格
        await self.context.conversation_manager.update_conversation_persona_id(
            event.unified_msg_origin, target_persona_id
        )
        yield event.plain_result(f"已切换人格【{target_persona_id}】")

        # 同步昵称和头像（如果配置允许）
        if self.conf["sync_name"]:
            await self.sync_nickname_and_avatar(event, target_persona_id)

        event.stop_event()

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("人格列表", alias={"查看人格列表"})
    async def list_persona(
        self, event: AiocqhttpMessageEvent, persona_id: str | None = None
    ):
        """查看人格列表"""
        msg = ""
        for persona in self.context.provider_manager.personas:
            msg += f"\n\n【{persona['name']}】:\n{persona['prompt']}"
        yield event.plain_result(msg.strip())
        return
