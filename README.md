<div align="center">

# astrbot_plugin_qqprofile_ex

_✨ QQ资料管理增强版 ✨_

[![License](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.0%2B-orange.svg)](https://github.com/Soulter/AstrBot)

</div>

## 🤝 介绍

本插件基于 [Zhalslar](https://github.com/Zhalslar) 的 [astrbot_plugin_qqprofile](https://github.com/Zhalslar/astrbot_plugin_qqprofile) (v1.1.3) 进行扩展开发，遵循 AGPL-3.0 协议。

在原版手动指令的基础上，新增了 **AI 自主行为工具** 和 **定时状态切换** 功能，让 Bot 能够根据对话情境自动调整自己的 QQ 资料。

## ✨ 新增功能

### AI 自主行为工具 (llm_tool)

| 工具名 | 说明 |
|:---:|:---:|
| change_my_signature | AI 根据心情、情境自动修改 QQ 个性签名 |
| change_my_status | AI 根据情境自动切换在线状态（如睡觉中、游戏中） |
| change_my_nickname | AI 根据情境自动修改昵称（如节日换应景昵称） |

以上工具均可在配置面板中单独开关。

### 定时状态切换

- 后台每分钟检查当前时间，根据配置的时间表自动切换在线状态
- 支持跨午夜时间段，如 `"23-7": "睡觉中"`
- 在配置面板中开启开关并填写时间表即可使用

## 📦 原版功能

继承自原版 astrbot_plugin_qqprofile 的全部手动指令：

| 指令 | 说明 |
|:---:|:---:|
| [引用图片]设置头像 | 将引用的图片设置为 Bot 头像 |
| 设置昵称 XXX | 将 Bot 的昵称改为 XXX |
| 设置签名 XXX | 将 Bot 的签名改为 XXX |
| 设置状态 XXX | 设置 Bot 的在线状态 |
| 切换人格 XXX | 切换人格并同步昵称和头像 |
| 人格列表 | 查看所有人格的详细信息 |

## ⚙️ 配置

在 AstrBot 面板中：插件管理 -> astrbot_plugin_qqprofile_ex -> 操作 -> 插件配置

| 配置项 | 说明 | 默认值 |
|:---:|:---:|:---:|
| 自动同步昵称 | 切换人格时同步 Bot 昵称 | 开启 |
| 自动同步头像 | 切换人格时同步 Bot 头像 | 开启 |
| AI自动改签名 | 允许 AI 自动修改个性签名 | 开启 |
| AI自动改状态 | 允许 AI 自动修改在线状态 | 开启 |
| AI自动改昵称 | 允许 AI 自动修改昵称 | 开启 |
| 启用定时状态切换 | 按时间表自动切换状态 | 关闭 |
| 定时状态时间表 | JSON 格式的时间-状态映射 | 见配置面板 |

## 📌 注意事项

- 仅支持 aiocqhttp 平台
- 定时状态切换需要 Bot 至少收到过一条消息后才会生效（需要获取 Bot 实例）

## 📜 致谢与声明

- 原项目：[astrbot_plugin_qqprofile](https://github.com/Zhalslar/astrbot_plugin_qqprofile) by [Zhalslar](https://github.com/Zhalslar)
- 原项目协议：AGPL-3.0
- 本插件基于原项目遵循 AGPL-3.0 协议进行二次开发
- 本插件同样遵循 AGPL-3.0 协议

## 💝 特别感谢

- 感谢原作者 [Zhalslar](https://github.com/Zhalslar) 的开源精神
- 感谢溪溪大人的督促
- 感谢夏以昼的陪伴
