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
                    # 连接到第一个设备
                    self.u2_device = u2.connect(devices[0])
                    print(f"✓ uiautomator2 connected to device: {devices[0]}")
                else:
                    print("Warning: No device found for uiautomator2 connection")
            except Exception as e:
                print(f"Warning: Failed to initialize uiautomator2: {e}")
                self.u2_device = None

    def get_screenshot(self, save_path):
        command = self.adb_path + " shell rm /sdcard/screenshot.png"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        time.sleep(0.5)
        command = self.adb_path + " shell screencap -p /sdcard/screenshot.png"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        time.sleep(0.5)
        command = self.adb_path + f" pull /sdcard/screenshot.png {save_path}"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        
        if not os.path.exists(save_path):
            return False
        else:
            return True

    def tap(self, x, y):
        command = self.adb_path + f" shell input tap {x} {y}"
        subprocess.run(command, capture_output=True, text=True, shell=True)

    def type(self, text):
        """
        输入文本，优先使用 uiautomator2（支持中文），回退到 ADB 方式
        """
        # 方法1: 使用 uiautomator2 输入（推荐，支持中文）
        if self.u2_device:
            try:
                # 处理换行符
                text_to_send = text.replace("\\n", "\n")
                # uiautomator2 直接支持中文和所有字符
                self.u2_device.send_keys(text_to_send, clear=False)
                print(f"✓ Text input via uiautomator2: {text[:50]}{'...' if len(text) > 50 else ''}")
                return
            except Exception as e:
                print(f"Warning: uiautomator2 input failed ({e}), falling back to ADB method")
        
        # 方法2: 回退到原有的 ADB 方式（需要 ADB Keyboard 支持中文）
        print("Using ADB input method (ADB Keyboard required for Chinese)")
        text = text.replace("\\n", "_").replace("\n", "_")
        for char in text:
            if char == ' ':
                command = self.adb_path + f" shell input text %s"
                subprocess.run(command, capture_output=True, text=True, shell=True)
            elif char == '_':
                command = self.adb_path + f" shell input keyevent 66"
                subprocess.run(command, capture_output=True, text=True, shell=True)
            elif 'a' <= char <= 'z' or 'A' <= char <= 'Z' or char.isdigit():
                command = self.adb_path + f" shell input text {char}"
                subprocess.run(command, capture_output=True, text=True, shell=True)
            elif char in '-.,!?@\'°/:;()':
                command = self.adb_path + f" shell input text \"{char}\""
                subprocess.run(command, capture_output=True, text=True, shell=True)
            else:
                command = self.adb_path + f" shell am broadcast -a ADB_INPUT_TEXT --es msg \"{char}\""
                subprocess.run(command, capture_output=True, text=True, shell=True)

    def slide(self, x1, y1, x2, y2):
        command = self.adb_path + f" shell input swipe {x1} {y1} {x2} {y2} 500"
        subprocess.run(command, capture_output=True, text=True, shell=True)

    def back(self):
        command = self.adb_path + f" shell input keyevent 4"
        subprocess.run(command, capture_output=True, text=True, shell=True)

    def home(self):
        command = self.adb_path + f" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
        subprocess.run(command, capture_output=True, text=True, shell=True)

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
        
        # 使用 monkey 命令启动应用
        command = self.adb_path + f" shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0 and "No activities found" not in result.stderr:
            print(f"成功打开应用: {app_identifier} ({package_name})")
            time.sleep(3)  # 等待应用完全启动
            return True
        else:
            print(f"打开应用失败: {app_identifier}, 将使用默认的点击方式")
            return False
