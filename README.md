# 快手直播自动弹幕机器人

![](https://img.shields.io/badge/Python-3.8%2B-blue) ![](https://img.shields.io/badge/Selenium-Edge-green) ![](https://img.shields.io/badge/rich-终端美化-orange)

## 项目简介

本项目是一个基于 Selenium + Edge 浏览器的快手直播间自动弹幕机器人，支持多弹幕池、权重混合、进度持久化、终端美化与详细日志，适合自动化运营、互动娱乐等场景。

## 主要特性

- [x] 支持扫码/本地 Edge 浏览器复用登录
- [x] 进入直播间自动重试与人工确认
- [x] 多弹幕池（顺序/随机/权重混合）
- [x] 弹幕池一号进度持久化
- [x] 弹幕发送间隔及浮动随机
- [x] rich 终端美化输出，日志详细
- [x] 全局 config.toml 配置
- [x] run.cmd 一键启动，自动设置终端 UTF-8

## 安装方法

1. 安装依赖：
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```
   或手动安装：
   ```bash
   pip install selenium rich toml
   ```
2. 下载并配置 Edge WebDriver，确保版本与本地 Edge 浏览器一致。
3. 配置 `config.toml`（参考下方配置说明）。
4. Windows 用户可直接双击 `run.cmd` 启动。

## 配置说明（config.toml 示例）

```toml
[account]
username = "" # 可留空，推荐扫码或本地 Edge 登录
password = "" # 可留空
edgedriver_path = "C:/path/to/msedgedriver.exe"
reuse_local_login = true
user_data_dir = "C:/Users/你的用户名/AppData/Local/Microsoft/Edge/User Data"

[live]
room_url = "https://live.kuaishou.com/u/xxxx"

[danmu]
interval = 5
interval_float = 2
contents = ["666", "主播加油", "关注走一波"]
pool_weight = 2

[danmu_pool2]
pool_weight = 1
pool = [
  { content = "快手最强弹幕", weight = 2 },
  { content = "互动走一波", weight = 1 }
]
```

## 使用方法

1. 启动脚本：
   - Windows：双击 `run.cmd` 或命令行执行 `python main.py`
2. 按提示扫码或本地 Edge 复用登录
3. 人工确认进入直播间后，自动循环发送弹幕
4. 日志与终端输出均有详细弹幕池、序号、循环等信息

## 运行截图

> ![终端美化示例](https://user-images.githubusercontent.com/your_screenshot.png)

## 常见问题

- rich 未安装：请用 `pip install rich` 安装
- Edge 驱动版本不符：请确保 msedgedriver.exe 与本地 Edge 浏览器版本一致
- 页面结构变动导致弹幕无法发送：可适当调整 XPATH 或反馈 issue

## 鸣谢

- [rich](https://github.com/Textualize/rich) 终端美化
- [selenium](https://github.com/SeleniumHQ/selenium) 自动化驱动
- [toml](https://github.com/uiri/toml) 配置解析

---

> 本项目仅供学习与交流，严禁用于任何违法用途。