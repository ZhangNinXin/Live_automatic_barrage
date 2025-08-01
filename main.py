
import toml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
import time
import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
import logging

class KuaishouDanmuBot:
    def __init__(self, username, password, edgedriver_path, reuse_local_login=False, user_data_dir=None):
        self.console = Console()
        self.logger = logging.getLogger("kuaishou")
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%H:%M:%S"))
        self.logger.handlers.clear()
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.username = username
        self.password = password
        self.reuse_local_login = reuse_local_login
        self.user_data_dir = user_data_dir
        options = Options()
        if self.reuse_local_login and self.user_data_dir:
            try:
                options.add_argument(f"--user-data-dir={self.user_data_dir}")
            except AttributeError:
                # 兼容老版本 selenium
                if hasattr(options, 'arguments'):
                    options.arguments.append(f"--user-data-dir={self.user_data_dir}")
        # 兼容极老版本 selenium：不支持 options 参数，需用 capabilities
        self.driver = webdriver.Edge(edgedriver_path, capabilities=options.to_capabilities())

    def login(self):
        self.driver.get('https://www.kuaishou.com/')
        self.console.rule("[bold green]快手弹幕机器人登录", style="green")
        self.console.print("[yellow]请在浏览器页面扫码或手动登录快手账号，登录完成后请在此窗口按回车继续...[/yellow]")
        self.console.input("[bold cyan]已登录后请按回车继续：[/bold cyan]")
        self.console.print("[green]已确认登录，继续后续操作。[/green]")

    def logout(self):
        # 退出当前账号，具体操作需根据快手页面结构调整
        try:
            avatar = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="user-info"]'))
            )
            avatar.click()
            logout_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "退出登录")]'))
            )
            logout_btn.click()
            self.console.print("[green]已退出当前账号，请重新登录...[/green]")
            time.sleep(2)
        except Exception as e:
            self.console.print(f"[red]退出账号失败: {e}[/red]")

    def enter_live_room(self, room_url, max_retry=2, wait_before=5):
        """
        进入直播间，支持重试与进入前等待，防止请求过快。
        返回True表示进入成功，False表示失败。
        """
        danmu_xpaths = [
            '//textarea[@placeholder="说点什么吧..."]',
            '//textarea[contains(@placeholder, "弹幕")]',
            '//textarea',
        ]
        for attempt in range(1, max_retry+1):
            if wait_before > 0:
                self.console.print(f"[yellow]等待 {wait_before} 秒后进入直播间...[/yellow]")
                time.sleep(wait_before)
            self.driver.get(room_url)
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="live-room-container"]'))
                )
                found = False
                for xpath in danmu_xpaths:
                    try:
                        WebDriverWait(self.driver, 8).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        found = True
                        break
                    except Exception:
                        continue
            except Exception as e:
                self.console.print(f"[red]第{attempt}次进入直播间失败: {e}[/red]")
            self.console.print("[bold yellow]【人工确认】请在浏览器中检查是否已成功进入直播间。[/bold yellow]")
            confirm = input("是否成功进入直播间？（Y/N）：").strip().lower()
            if confirm == 'y':
                self.console.print("[green]已确认进入直播间[/green]")
                return True
            else:
                self.console.print("[yellow]用户确认未进入直播间，准备重试...[/yellow]")
            if attempt == max_retry:
                self.console.print("[red]多次尝试进入直播间失败，请检查网络或页面结构。[/red]")
                return False
            else:
                self.console.print("[yellow]准备重试...[/yellow]")
                time.sleep(3)

    def send_danmu(self, danmu_list, interval=5, interval_float=0, max_retry=3):
        # 多种输入框和发送按钮 XPATH 组合，提升兼容性
        input_xpaths = [
            '//textarea[@placeholder="说点什么吧..."]',
            '//textarea[contains(@placeholder, "弹幕")]',
            '//textarea',
            '//input[@placeholder="说点什么吧..."]',
            '//input[contains(@placeholder, "弹幕")]',
            '//input',
        ]
        send_btn_xpaths = [
            '//button[.//span[contains(text(), "发送")]]',
            '//button[contains(text(), "发送")]',
            '//button[@type="button" and not(@disabled)]',
            '//div[contains(@class, "danmaku-send") or contains(@class, "send-btn") or contains(@class, "sendButton")]',
            '//span[contains(text(), "发送")]/ancestor::button',
        ]
        while True:
            for danmu in danmu_list:
                # 计算本次弹幕的随机间隔
                if interval_float > 0:
                    real_interval = random.uniform(max(0, interval - interval_float), interval + interval_float)
                else:
                    real_interval = interval
                for attempt in range(1, max_retry+1):
                    try:
                        # 依次尝试多种输入框
                        input_box = None
                        for xpath in input_xpaths:
                            try:
                                input_box = WebDriverWait(self.driver, 4).until(
                                    EC.presence_of_element_located((By.XPATH, xpath))
                                )
                                break
                            except Exception:
                                continue
                        if not input_box:
                            raise Exception("未找到弹幕输入框，请检查页面结构")
                        # 先点击输入框确保聚焦
                        try:
                            input_box.click()
                        except Exception:
                            pass
                        input_box.clear()
                        input_box.send_keys(danmu)
                        # 依次尝试多种发送按钮
                        send_btn = None
                        for btn_xpath in send_btn_xpaths:
                            try:
                                send_btn = WebDriverWait(self.driver, 3).until(
                                    EC.element_to_be_clickable((By.XPATH, btn_xpath))
                                )
                                break
                            except Exception:
                                continue
                        sent = False
                        if send_btn:
                            try:
                                send_btn.click()
                                sent = True
                            except Exception:
                                # 尝试用JS强制点击
                                try:
                                    self.driver.execute_script("arguments[0].click();", send_btn)
                                    sent = True
                                except Exception:
                                    pass
                        # 如果按钮找不到或点击无效，尝试回车发送
                        if not sent:
                            try:
                                from selenium.webdriver.common.keys import Keys
                                input_box.send_keys("\n")
                                sent = True
                            except Exception:
                                pass
                        # 检查弹幕是否已发出（输入框内容被清空）
                        time.sleep(1)
                        try:
                            value = input_box.get_attribute("value") or input_box.text
                        except Exception:
                            value = ""
                        if sent and (not value or value.strip() == ""):
                            print(f"已发送弹幕: {danmu}，本次间隔 {real_interval:.2f} 秒")
                            time.sleep(real_interval)
                            break
                        else:
                            raise Exception("弹幕未成功发出，输入框内容未清空")
                    except Exception as e:
                        print(f"第{attempt}次发送弹幕失败: {e}")
                        if attempt == max_retry:
                            print("多次尝试发送弹幕失败，跳过本条。")
                        else:
                            print("准备重试...")
                            time.sleep(2)

    def run(self, room_url, danmu_list, enter_wait=5):
        self.login()
        # 登录后再进入直播间
        enter_success = self.enter_live_room(room_url, wait_before=enter_wait)
        if enter_success:
            self.send_danmu(danmu_list)
        else:
            print("进入直播间失败，程序终止。")


def load_config(path="config.toml"):
    config = toml.load(path)
    account = config["account"]
    reuse_local_login = account.get("reuse_local_login", False)
    username = account.get("username", "")
    password = account.get("password", "")
    edgedriver_path = account["edgedriver_path"]
    user_data_dir = account.get("user_data_dir", None)
    room_url = config["live"]["room_url"]
    interval = config["danmu"].get("interval", 5)
    interval_float = config["danmu"].get("interval_float", 0)
    danmu_list = config["danmu"]["contents"]
    pool1_weight = config["danmu"].get("pool_weight", 1)
    # 加载弹幕池2
    danmu_pool2 = []
    pool2_weight = 1
    if "danmu_pool2" in config:
        pool2_weight = config["danmu_pool2"].get("pool_weight", 1)
        if "pool" in config["danmu_pool2"]:
            danmu_pool2 = config["danmu_pool2"]["pool"]
    # 新增：自动刷新开关
    auto_refresh_on_fail = config.get("feature", {}).get("auto_refresh_on_fail", False)
    return username, password, edgedriver_path, room_url, danmu_list, interval, interval_float, reuse_local_login, user_data_dir, danmu_pool2, pool1_weight, pool2_weight, auto_refresh_on_fail

if __name__ == '__main__':
    username, password, edgedriver_path, room_url, danmu_list, interval, interval_float, reuse_local_login, user_data_dir, danmu_pool2, pool1_weight, pool2_weight, auto_refresh_on_fail = load_config()
    bot = KuaishouDanmuBot(
        username=username,
        password=password,
        edgedriver_path=edgedriver_path,
        reuse_local_login=reuse_local_login,
        user_data_dir=user_data_dir
    )
    enter_wait = 2
    # 弹幕池一号进度持久化文件
    import os, json
    progress_file = "danmu1_progress.json"
    def load_progress():
        if os.path.exists(progress_file):
            try:
                with open(progress_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("idx", 0)
            except Exception:
                return 0
        return 0
    def save_progress(idx):
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump({"idx": idx}, f)
    # 新弹幕循环逻辑：每次按池权重决定从哪个池发，池1顺序且进度持久化，池2按权重随机
    def danmu_mix_gen():
        idx = load_progress()
        pool2_contents = [item["content"] for item in danmu_pool2]
        pool2_weights = [item.get("weight", 1) for item in danmu_pool2]
        loop_count = 0
        while True:
            pool_choice = random.choices([1,2], weights=[pool1_weight, pool2_weight], k=1)[0]
            if pool_choice == 1 and danmu_list:
                if idx >= len(danmu_list):
                    idx = 0
                    loop_count += 1
                danmu = danmu_list[idx]
                idx += 1
                save_progress(idx)
                yield {"content": danmu, "pool": 1, "idx": idx, "loop": loop_count+1, "total": len(danmu_list)}
            elif pool_choice == 2 and pool2_contents:
                danmu2_idx = random.choices(range(len(pool2_contents)), weights=pool2_weights, k=1)[0]
                danmu2 = pool2_contents[danmu2_idx]
                yield {"content": danmu2, "pool": 2, "idx": danmu2_idx+1, "loop": None, "total": len(pool2_contents)}
            else:
                if danmu_list:
                    if idx >= len(danmu_list):
                        idx = 0
                        loop_count += 1
                    danmu = danmu_list[idx]
                    idx += 1
                    save_progress(idx)
                    yield {"content": danmu, "pool": 1, "idx": idx, "loop": loop_count+1, "total": len(danmu_list)}
                elif pool2_contents:
                    danmu2_idx = random.choices(range(len(pool2_contents)), weights=pool2_weights, k=1)[0]
                    danmu2 = pool2_contents[danmu2_idx]
                    yield {"content": danmu2, "pool": 2, "idx": danmu2_idx+1, "loop": None, "total": len(pool2_contents)}
                else:
                    yield {"content": "", "pool": 0}
    danmu_gen = danmu_mix_gen()
    def send_danmu_mix(self, danmu_list, interval=interval, interval_float=interval_float, max_retry=3):
        input_xpaths = [
            '//textarea[@placeholder="说点什么吧..."]',
            '//textarea[contains(@placeholder, "弹幕")]',
            '//textarea',
            '//input[@placeholder="说点什么吧..."]',
            '//input[contains(@placeholder, "弹幕")]',
            '//input',
        ]
        send_btn_xpaths = [
            '//button[.//span[contains(text(), "发送")]]',
            '//button[contains(text(), "发送")]',
            '//button[@type="button" and not(@disabled)]',
            '//div[contains(@class, "danmaku-send") or contains(@class, "send-btn") or contains(@class, "sendButton")]',
            '//span[contains(text(), "发送")]/ancestor::button',
        ]
        consecutive_fail = 0
        while True:
            danmu_info = next(danmu_gen)
            danmu = danmu_info.get("content", "")
            if not danmu:
                continue
            pool = danmu_info.get("pool", 0)
            idx = danmu_info.get("idx", None)
            loop = danmu_info.get("loop", None)
            total = danmu_info.get("total", None)
            if interval_float > 0:
                real_interval = random.uniform(max(0, interval - interval_float), interval + interval_float)
            else:
                real_interval = interval
            pool_str = "一号弹幕池" if pool == 1 else ("二号弹幕池" if pool == 2 else "未知")
            extra = ""
            if pool == 1:
                extra = f"[循环第{loop}轮/共{total}条/当前第{idx}条]"
            elif pool == 2:
                extra = f"[共{total}条/当前第{idx}条]"
            success = False
            for attempt in range(1, max_retry+1):
                try:
                    input_box = None
                    for xpath in input_xpaths:
                        try:
                            input_box = WebDriverWait(self.driver, 4).until(
                                EC.presence_of_element_located((By.XPATH, xpath))
                            )
                            break
                        except Exception:
                            continue
                    if not input_box:
                        raise Exception("未找到弹幕输入框，请检查页面结构")
                    try:
                        input_box.click()
                    except Exception:
                        pass
                    input_box.clear()
                    input_box.send_keys(danmu)
                    send_btn = None
                    for btn_xpath in send_btn_xpaths:
                        try:
                            send_btn = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, btn_xpath))
                            )
                            break
                        except Exception:
                            continue
                    sent = False
                    if send_btn:
                        try:
                            send_btn.click()
                            sent = True
                        except Exception:
                            try:
                                self.driver.execute_script("arguments[0].click();", send_btn)
                                sent = True
                            except Exception:
                                pass
                    if not sent:
                        try:
                            from selenium.webdriver.common.keys import Keys
                            input_box.send_keys("\n")
                            sent = True
                        except Exception:
                            pass
                    time.sleep(1)
                    try:
                        value = input_box.get_attribute("value") or input_box.text
                    except Exception:
                        value = ""
                    if sent and (not value or value.strip() == ""):
                        msg = Text(f"已发送弹幕: ", style="bold green")
                        msg.append(f"{danmu}", style="bold yellow")
                        msg.append(f"  [来源: {pool_str}] {extra}", style="cyan")
                        msg.append(f"  间隔: {real_interval:.2f} 秒", style="magenta")
                        self.console.print(msg)
                        self.logger.info(f"弹幕[{pool_str}]{extra}: {danmu}")
                        time.sleep(real_interval)
                        success = True
                        break
                    else:
                        raise Exception("弹幕未成功发出，输入框内容未清空")
                except Exception as e:
                    self.console.print(f"[red]第{attempt}次发送弹幕失败: {e}[/red]")
                    self.logger.error(f"第{attempt}次发送弹幕失败: {e}")
                    if attempt == max_retry:
                        self.console.print("[red]多次尝试发送弹幕失败，跳过本条。[/red]")
                        self.logger.error("多次尝试发送弹幕失败，跳过本条。")
                    else:
                        self.console.print("[yellow]准备重试...[/yellow]")
                        time.sleep(2)
            if success:
                consecutive_fail = 0
            else:
                consecutive_fail += 1
                # 检查是否需要自动重进直播间
                if auto_refresh_on_fail and consecutive_fail >= 3:
                    self.console.print("[bold red]检测到连续三条弹幕均发送失败，自动重新进入直播间...[/bold red]")
                    self.logger.warning("连续三条弹幕均发送失败，自动重新进入直播间")
                    self.driver.get(room_url)
                    time.sleep(10)
                    consecutive_fail = 0
    import types
    bot.send_danmu = types.MethodType(send_danmu_mix, bot)
    bot.run(room_url, danmu_list)



