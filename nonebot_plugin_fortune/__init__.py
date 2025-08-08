from typing import Annotated

from ncatbot.core import MessageChain, Image
from ncatbot.utils import get_log

from .config import FortuneConfig, FortuneThemesDict, fortune_check
from .data_source import FortuneManager, fortune_manager


logger = get_log()
__fortune_version__ = "v0.4.12"
__fortune_usages__ = f"""
[今日运势/抽签/运势] 一般抽签
[xx抽签]     指定主题抽签
[指定xx签] 指定特殊角色签底，需要自己尝试哦~
[设置xx签] 设置群抽签主题
[重置主题] 重置群抽签主题
[主题列表] 查看可选的抽签主题
[查看主题] 查看群抽签主题""".strip()

# __plugin_meta__ = PluginMetadata(
#     name="今日运势",
#     description="抽签！占卜你的今日运势🙏",
#     usage=__fortune_usages__,
#     type="application",
#     homepage="https://github.com/MinatoAquaCrews/nonebot_plugin_fortune",
#     config=FortuneConfig,
#     extra={
#         "author": "KafCoppelia <k740677208@gmail.com>",
#         "version": __fortune_version__,
#     },
# )

# general_divine = on_command("今日运势", aliases={"抽签", "运势"}, permission=GROUP, priority=8)
# specific_divine = on_regex(r"^[^/]\S+抽签$", permission=GROUP, priority=8)
# limit_setting = on_regex(r"^指定(.*?)签$", permission=GROUP, priority=8)
# change_theme = on_regex(
#     r"^设置(.*?)签$",
#     permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
#     priority=8,
#     block=True,
# )
# reset_themes = on_regex(
#     "^重置(抽签)?主题$",
#     permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
#     priority=8,
#     block=True,
# )
# themes_list = on_fullmatch("主题列表", permission=GROUP, priority=8, block=True)
# show_themes = on_regex("^查看(抽签)?主题$", permission=GROUP, priority=8, block=True)


async def showTheme(gid: str):
    theme: str = fortune_manager.get_group_theme(gid)
    return f"当前群抽签主题：{FortuneThemesDict[theme][0]}"


async def ThemeList():
    return FortuneManager.get_available_themes()


async def generalDivine(arg: str, gid: str, uid: str) -> str|MessageChain:
    if "帮助" in arg[-2:]:
        return __fortune_usages__

    is_first, image_file, title, text = fortune_manager.divine(gid, uid, None, None)
    if image_file is None:
        return "今日运势生成出错……"

    if not is_first:
        msg = MessageChain(["你今天抽过签了，再给你看一次哦🤗\n", Image(str(image_file))])
    else:
        logger.info(f"User {uid} | Group {gid} 占卜了今日运势")
        msg = MessageChain(["✨今日运势✨\n", Image(str(image_file))])

    return msg


async def specificDivine(
    user_themes: str, gid: str, uid: str
):
    user_theme: str = user_themes[:-2]
    if len(user_theme) < 1:
        return "输入参数错误"

    for theme in FortuneThemesDict:
        if user_theme in FortuneThemesDict[theme]:
            if not FortuneManager.theme_enable_check(theme):
                return "该抽签主题未启用~"
            else:
                is_first, image_file, title, text = fortune_manager.divine(gid, uid, theme, None)
                if image_file is None:
                    return "今日运势生成出错……"

                if not is_first:
                    msg = MessageChain(["你今天抽过签了，再给你看一次哦🤗\n", Image(str(image_file))])
                else:
                    logger.info(f"User {uid} | Group {gid} 占卜了今日运势")
                    msg = MessageChain(["✨今日运势✨\n", Image(str(image_file))])

            return msg

    return "还没有这种抽签主题哦~"


async def change_theme(
    gid: str,
    user_theme: str
):
    for theme in FortuneThemesDict:
        if user_theme in FortuneThemesDict[theme]:
            if not fortune_manager.divination_setting(theme, gid):
                return "该抽签主题未启用~"
            else:
                return "已设置当前群抽签主题~"

    return "还没有这种抽签主题哦~"


async def limit_setting(limit: str, gid: str, uid: str):
    logger.warning("指定签底抽签功能将在 v0.5.x 弃用")

    if limit == "随机":
        is_first, image_file, title, text = fortune_manager.divine(gid, uid, None, None)
        if image_file is None:
            return "今日运势生成出错……"
    else:
        spec_path = fortune_manager.specific_check(limit)
        if not spec_path:
            return "还不可以指定这种签哦，请确认该签底对应主题开启或图片路径存在~"
        else:
            is_first, image_file, title, text = fortune_manager.divine(gid, uid, None, spec_path)
            if image_file is None:
                return "今日运势生成出错……"

    if not is_first:
        msg = MessageChain(["你今天抽过签了，再给你看一次哦🤗\n", Image(str(image_file))])
    else:
        logger.info(f"User {uid} | Group {gid} 占卜了今日运势")
        msg = MessageChain(["✨今日运势✨\n", Image(str(image_file))])

    return msg


async def reset_themes(gid: str):
    if not fortune_manager.divination_setting("random", gid):
        return "重置群抽签主题失败！"

    return "已重置当前群抽签主题为随机~"


# 清空昨日生成的图片
def cleanOutPics():
    FortuneManager.clean_out_pics()
    logger.info("昨日运势图片已清空！")
