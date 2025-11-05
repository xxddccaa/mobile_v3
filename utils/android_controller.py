import os
import time
import subprocess
from .controller import Controller

try:
    import uiautomator2 as u2
    U2_AVAILABLE = True
except ImportError:
    U2_AVAILABLE = False
    print("Warning: uiautomator2 not installed. Chinese input will require ADB Keyboard.")

class AndroidController(Controller):
    def __init__(self, adb_path):
        self.adb_path = adb_path
        self.u2_device = None
        self.device_id = None
        self.tap_duration_ms = 200  # 默认“点击”持续时长（使用同点 swipe 实现）
        
        # 尝试初始化 uiautomator2
        if U2_AVAILABLE:
            try:
                # 从 adb_path 获取设备序列号（如果指定了的话）
                result = subprocess.run(
                    f"{adb_path} devices",
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                # 解析设备列表
                lines = result.stdout.strip().split('\n')
                devices = []
                for line in lines[1:]:  # 跳过第一行 "List of devices attached"
                    if '\tdevice' in line:
                        device_id = line.split('\t')[0]
                        devices.append(device_id)
                
                if devices:
                    # 连接到第一个设备，并记录 device_id（用于 ADB -s 绑定）
                    self.device_id = devices[0]
                    self.u2_device = u2.connect(self.device_id)
                    print(f"✓ uiautomator2 connected to device: {self.device_id}")
                else:
                    print("Warning: No device found for uiautomator2 connection")
            except Exception as e:
                print(f"Warning: Failed to initialize uiautomator2: {e}")
                self.u2_device = None

    def get_screenshot(self, save_path):
        """
        获取设备截图
        优先使用 uiautomator2（如果可用），否则使用 ADB 命令
        """
        # 方法1: 使用 uiautomator2 截图（推荐，更稳定）
        if self.u2_device:
            try:
                # 确保保存目录存在
                save_dir = os.path.dirname(save_path)
                if save_dir and not os.path.exists(save_dir):
                    os.makedirs(save_dir, exist_ok=True)
                
                # 使用 uiautomator2 截图
                screenshot = self.u2_device.screenshot()
                screenshot.save(save_path)
                
                if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                    return True
                else:
                    print(f"Warning: uiautomator2 screenshot saved but file is empty or missing")
            except Exception as e:
                print(f"Warning: uiautomator2 screenshot failed ({e}), falling back to ADB method")
        
        # 方法2: 使用 ADB 命令截图（备用方案）
        try:
            # 确保保存目录存在
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
            
            # 删除旧的截图文件
            rm_command = f"{self.adb_path}{f' -s {self.device_id}' if self.device_id else ''} shell rm -f /sdcard/screenshot.png"
            rm_result = subprocess.run(rm_command, capture_output=True, text=True, shell=True)
            if rm_result.returncode != 0:
                print(f"Warning: Failed to remove old screenshot: {rm_result.stderr}")
            time.sleep(0.3)
            
            # 截图到设备
            screencap_command = f"{self.adb_path}{f' -s {self.device_id}' if self.device_id else ''} shell screencap -p /sdcard/screenshot.png"
            screencap_result = subprocess.run(screencap_command, capture_output=True, text=True, shell=True)
            if screencap_result.returncode != 0:
                print(f"Error: screencap command failed: {screencap_result.stderr}")
                return False
            time.sleep(0.5)
            
            # 从设备拉取截图
            pull_command = f"{self.adb_path}{f' -s {self.device_id}' if self.device_id else ''} pull /sdcard/screenshot.png \"{save_path}\""
            pull_result = subprocess.run(pull_command, capture_output=True, text=True, shell=True)
            if pull_result.returncode != 0:
                print(f"Error: pull command failed: {pull_result.stderr}")
                return False
            
            # 验证文件是否存在且不为空
            if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                return True
            else:
                print(f"Error: Screenshot file missing or empty: {save_path}")
                return False
                
        except Exception as e:
            print(f"Error: Screenshot failed with exception: {e}")
            return False

    def tap(self, x, y):
        """
        点击屏幕坐标
        优先使用 ADB 命令（更稳定），uiautomator2 作为备用
        """
        # 方法1: 使用 ADB 短时同点 swipe（更稳，部分设备对 tap 边缘/底部不灵敏）
        try:
            command = f"{self.adb_path}{f' -s {self.device_id}' if self.device_id else ''} shell input swipe {x} {y} {x+2} {y+2} {self.tap_duration_ms}"
            t0 = time.time()
            print(f"[TAP] ADB swipe-as-tap start: device={self.device_id or 'default'} coord=({x},{y}) dur={self.tap_duration_ms}ms")
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            dt = int((time.time() - t0) * 1000)
            if result.returncode == 0:
                if result.stdout.strip():
                    print(f"[TAP] ADB success (swipe-as-tap). cost={dt}ms stdout={result.stdout.strip()}")
                else:
                    print(f"[TAP] ADB success (swipe-as-tap). cost={dt}ms")
                time.sleep(0.2)
                return
            else:
                print(f"[TAP] Warning: ADB swipe-as-tap failed. cost={dt}ms code={result.returncode} stderr={result.stderr.strip()}")
                print(f"[TAP] Fallback to uiautomator2.click")
        except Exception as e:
            print(f"[TAP] Warning: ADB swipe-as-tap raised exception: {e}. Fallback to uiautomator2.click")
        
        # 方法2: 使用 uiautomator2 点击（备用方案）
        if self.u2_device:
            try:
                t0 = time.time()
                print(f"[TAP] uiautomator2.click start: device={self.device_id or 'default'} coord=({x},{y})")
                self.u2_device.click(x, y)
                dt = int((time.time() - t0) * 1000)
                print(f"[TAP] uiautomator2.click success. cost={dt}ms")
                time.sleep(0.2)
            except Exception as e:
                print(f"[TAP] Error: uiautomator2 click failed: {e}")

    def set_tap_duration(self, duration_ms: int):
        """
        设置点击（同点 swipe）持续时长，单位毫秒。
        说明：某些机型/区域对极短点击不敏感，适度增加可提高命中率（如 180~250ms）。
        """
        try:
            duration_ms = int(duration_ms)
            if duration_ms < 50:
                print(f"[TAP] Notice: tap duration too small ({duration_ms}ms), adjusted to 50ms")
                duration_ms = 50
            if duration_ms > 1000:
                print(f"[TAP] Notice: tap duration too large ({duration_ms}ms), adjusted to 1000ms")
                duration_ms = 1000
            self.tap_duration_ms = duration_ms
            print(f"[TAP] Tap duration set to {self.tap_duration_ms}ms")
        except Exception as e:
            print(f"[TAP] Warning: invalid duration '{duration_ms}', keep {self.tap_duration_ms}ms. err={e}")

    def type(self, text):
        """
        输入文本，优先使用 uiautomator2（支持中文），回退到 ADB 方式
        输入前会先清空输入框中的现有文本
        """
        # 方法1: 使用 uiautomator2 输入（推荐，支持中文）
        if self.u2_device:
            try:
                # 处理换行符
                text_to_send = text.replace("\\n", "\n")
                
                # 启用快速输入法（FastInputIME）- 对中文输入很重要
                try:
                    self.u2_device.set_fastinput_ime(True)
                    time.sleep(0.1)  # 等待输入法切换
                except Exception as ime_err:
                    print(f"Warning: Failed to set FastInputIME: {ime_err}, continuing anyway...")
                
                # 清空输入框并输入文本（一步完成，更稳定）
                try:
                    # 使用 clear_text() + send_keys() 的组合方式（最可靠）
                    self.u2_device.clear_text()
                    time.sleep(0.2)  # 等待清空完成
                    self.u2_device.send_keys(text_to_send)
                    time.sleep(0.2)  # 等待输入完成
                    
                    print(f"✓ Text input via uiautomator2: {text[:50]}{'...' if len(text) > 50 else ''}")
                    return
                    
                except AttributeError:
                    # 如果没有 clear_text 方法，使用 send_keys 的 clear 参数
                    print("Using send_keys with clear=True (fallback method)")
                    self.u2_device.send_keys(text_to_send, clear=True)
                    time.sleep(0.3)
                    
                    print(f"✓ Text input via uiautomator2: {text[:50]}{'...' if len(text) > 50 else ''}")
                    return
                    
            except Exception as e:
                error_msg = str(e)
                print(f"Warning: uiautomator2 input failed ({error_msg})")
                print(f"  Input text: {text}")
                print(f"  Falling back to ADB method...")
                # 不 return，继续执行 ADB 方法
        
        # 方法2: 回退到原有的 ADB 方式（需要 ADB Keyboard 支持中文）
        print("Using ADB input method (ADB Keyboard required for Chinese)")
        print(f"Warning: ADB method may not support Chinese characters. Text to input: '{text}'")
        
        # 检查是否包含中文字符
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
        if has_chinese:
            print("Error: Text contains Chinese characters, but ADB method requires ADB Keyboard.")
            print("Please ensure uiautomator2 is working properly or install ADB Keyboard.")
            print("Attempting to input anyway, but Chinese characters may fail...")
        
        # 先清空输入框：全选 + 删除
        try:
            # Ctrl+A (全选) - keycode 113
            command = self.adb_path + f" shell input keyevent 113"
            subprocess.run(command, capture_output=True, text=True, shell=True)
            time.sleep(0.1)
            # Delete (删除) - keycode 67
            command = self.adb_path + f" shell input keyevent 67"
            subprocess.run(command, capture_output=True, text=True, shell=True)
            time.sleep(0.2)
        except Exception as e:
            print(f"Warning: Failed to clear input field: {e}")
        
        # 输入文本
        text = text.replace("\\n", "_").replace("\n", "_")
        successful_chars = 0
        failed_chars = []
        
        for char in text:
            try:
                if char == ' ':
                    command = self.adb_path + f" shell input text %s"
                    result = subprocess.run(command, capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        successful_chars += 1
                elif char == '_':
                    command = self.adb_path + f" shell input keyevent 66"
                    result = subprocess.run(command, capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        successful_chars += 1
                elif 'a' <= char <= 'z' or 'A' <= char <= 'Z' or char.isdigit():
                    command = self.adb_path + f" shell input text {char}"
                    result = subprocess.run(command, capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        successful_chars += 1
                    else:
                        failed_chars.append(char)
                elif char in '-.,!?@\'°/:;()':
                    command = self.adb_path + f" shell input text \"{char}\""
                    result = subprocess.run(command, capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        successful_chars += 1
                    else:
                        failed_chars.append(char)
                else:
                    # 中文字符或其他特殊字符，需要 ADB Keyboard
                    command = self.adb_path + f" shell am broadcast -a ADB_INPUT_TEXT --es msg \"{char}\""
                    result = subprocess.run(command, capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        successful_chars += 1
                    else:
                        failed_chars.append(char)
                time.sleep(0.05)  # 每个字符之间稍作延迟
            except Exception as e:
                failed_chars.append(char)
                print(f"Warning: Failed to input character '{char}': {e}")
        
        if failed_chars:
            print(f"Warning: Failed to input {len(failed_chars)} characters: {failed_chars}")
            print(f"Successfully input {successful_chars}/{len(text)} characters")

    def slide(self, x1, y1, x2, y2):
        """
        滑动屏幕
        优先使用 ADB 命令（更稳定），uiautomator2 作为备用
        """
        # 方法1: 使用 ADB 命令滑动（主要方案，更稳定）
        try:
            command = f"{self.adb_path}{f' -s {self.device_id}' if self.device_id else ''} shell input swipe {x1} {y1} {x2} {y2} 500"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return
            else:
                print(f"Warning: ADB swipe failed, trying uiautomator2")
        except Exception as e:
            print(f"Warning: ADB swipe failed ({e}), trying uiautomator2")
        
        # 方法2: 使用 uiautomator2 滑动（备用方案）
        if self.u2_device:
            try:
                self.u2_device.swipe(x1, y1, x2, y2, duration=0.5)
            except Exception as e:
                print(f"Error: uiautomator2 swipe also failed ({e})")

    def back(self):
        """
        按返回键
        优先使用 ADB 命令（更稳定），uiautomator2 作为备用
        """
        # 方法1: 使用 ADB 命令按键（主要方案，更稳定）
        try:
            command = f"{self.adb_path}{f' -s {self.device_id}' if self.device_id else ''} shell input keyevent 4"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return
            else:
                print(f"Warning: ADB back failed, trying uiautomator2")
        except Exception as e:
            print(f"Warning: ADB back failed ({e}), trying uiautomator2")
        
        # 方法2: 使用 uiautomator2 按键（备用方案）
        if self.u2_device:
            try:
                self.u2_device.press("back")
            except Exception as e:
                print(f"Error: uiautomator2 back also failed ({e})")

    def home(self):
        """
        按 Home 键
        优先使用 ADB 命令（更稳定），uiautomator2 作为备用
        """
        # 方法1: 使用 ADB 命令按键（主要方案，更稳定）
        try:
            command = f"{self.adb_path}{f' -s {self.device_id}' if self.device_id else ''} shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return
            else:
                print(f"Warning: ADB home failed, trying uiautomator2")
        except Exception as e:
            print(f"Warning: ADB home failed ({e}), trying uiautomator2")
        
        # 方法2: 使用 uiautomator2 按键（备用方案）
        if self.u2_device:
            try:
                self.u2_device.press("home")
            except Exception as e:
                print(f"Error: uiautomator2 home also failed ({e})")

    def get_clipboard(self):
        """
        获取粘贴板内容
        :return: str 粘贴板内容，如果获取失败返回 None
        """
        # 方法1: 使用 uiautomator2 获取（推荐）
        if self.u2_device:
            try:
                clipboard_text = self.u2_device.clipboard
                return clipboard_text
            except Exception as e:
                print(f"Warning: uiautomator2 clipboard access failed ({e}), trying ADB method")
        
        # 方法2: 使用 ADB 命令获取（备用方案）
        try:
            # 注意：直接通过 ADB 获取剪贴板内容可能需要特殊权限
            # 如果 uiautomator2 可用，优先使用 uiautomator2
            print("Warning: Could not retrieve clipboard content via uiautomator2")
            return None
        except Exception as e:
            print(f"Error getting clipboard content: {e}")
            return None

    def open_app(self, app_identifier):
        """
        打开应用，支持应用名或包名
        :param app_identifier: 应用名（如'微博'）或包名（如'com.sina.weibo'）
        :return: bool 是否成功
        """
        # 常见应用包名映射
        APP_PACKAGES = {
            '微博': 'com.sina.weibo',
            'weibo': 'com.sina.weibo',
            '微信': 'com.tencent.mm',
            'wechat': 'com.tencent.mm',
            '抖音': 'com.ss.android.ugc.aweme',
            'douyin': 'com.ss.android.ugc.aweme',
            '小红书': 'com.xingin.xhs',
            'xiaohongshu': 'com.xingin.xhs',
            '淘宝': 'com.taobao.taobao',
            'taobao': 'com.taobao.taobao',
            '支付宝': 'com.eg.android.AlipayGphone',
            'alipay': 'com.eg.android.AlipayGphone',
            '哔哩哔哩': 'tv.danmaku.bili',
            'bilibili': 'tv.danmaku.bili',
            'b站': 'tv.danmaku.bili',
            'QQ': 'com.tencent.mobileqq',
            'qq': 'com.tencent.mobileqq',
            '京东': 'com.jingdong.app.mall',
            'jd': 'com.jingdong.app.mall',
            '拼多多': 'com.xunmeng.pinduoduo',
            'pinduoduo': 'com.xunmeng.pinduoduo',
            '今日头条': 'com.ss.android.article.news',
            'toutiao': 'com.ss.android.article.news',
            '网易云音乐': 'com.netease.cloudmusic',
            'netease': 'com.netease.cloudmusic',
            'QQ音乐': 'com.tencent.qqmusic',
            '百度': 'com.baidu.searchbox',
            'baidu': 'com.baidu.searchbox',
            '美团': 'com.sankuai.meituan',
            'meituan': 'com.sankuai.meituan',
            '饿了么': 'me.ele',
            'eleme': 'me.ele',
            '高德地图': 'com.autonavi.minimap',
            'gaode': 'com.autonavi.minimap',
            '知乎': 'com.zhihu.android',
            'zhihu': 'com.zhihu.android',
        }
        
        # 判断是应用名还是包名
        if app_identifier in APP_PACKAGES:
            package_name = APP_PACKAGES[app_identifier]
        elif '.' in app_identifier:  # 可能是包名
            package_name = app_identifier
        else:
            print(f"未知应用: {app_identifier}，尝试使用原始名称")
            package_name = app_identifier
        
        # 方法1: 使用 uiautomator2 打开应用（推荐，更稳定）
        if self.u2_device:
            try:
                self.u2_device.app_start(package_name)
                time.sleep(3)  # 等待应用完全启动
                print(f"成功打开应用: {app_identifier} ({package_name})")
                return True
            except Exception as e:
                print(f"Warning: uiautomator2 app_start failed ({e}), falling back to ADB method")
        
        # 方法2: 使用 ADB 命令打开应用（备用方案）
            command = f"{self.adb_path}{f' -s {self.device_id}' if self.device_id else ''} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0 and "No activities found" not in result.stderr:
            print(f"成功打开应用: {app_identifier} ({package_name})")
            time.sleep(3)  # 等待应用完全启动
            return True
        else:
            print(f"打开应用失败: {app_identifier}, 将使用默认的点击方式")
            return False
