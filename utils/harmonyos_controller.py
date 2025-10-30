import os
import time
import subprocess
from .controller import Controller

class HarmonyOSController(Controller):
    def __init__(self, hdc_path):
        self.hdc_path = hdc_path

    def get_screenshot(self, save_path):
        command = self.hdc_path + " shell rm /data/local/tmp/screenshot.png"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        time.sleep(0.5)
        command = self.hdc_path + " shell uitest screenCap -p /data/local/tmp/screenshot.png"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        time.sleep(0.5)
        command = self.hdc_path + " file recv /data/local/tmp/screenshot.png " + save_path
        subprocess.run(command, capture_output=True, text=True, shell=True)
        time.sleep(0.5)

        if not os.path.exists(save_path):
            return False
        else:
            return True

    def tap(self, x, y):
        command = self.hdc_path + f" shell uitest uiInput click {x} {y}"
        subprocess.run(command, capture_output=True, text=True, shell=True)

    def type(self, text):
        text = text.replace("\\n", "_").replace("\n", "_")
        for char in text:
            if char == ' ':
                command = self.adb_path + f" shell uitest uiInput keyEvent 2050"
                subprocess.run(command, capture_output=True, text=True, shell=True)
            elif char == '_':
                command = self.hdc_path + f" shell uitest uiInput keyEvent 2054"
                subprocess.run(command, capture_output=True, text=True, shell=True)
            elif 'a' <= char <= 'z' or 'A' <= char <= 'Z' or char.isdigit():
                command = self.hdc_path + f" shell uitest uiInput inputText 1 1 {char}"
                subprocess.run(command, capture_output=True, text=True, shell=True)
            elif char in '-.,!?@\'°/:;()':
                command = self.hdc_path + f" shell uitest uiInput inputText 1 1 \"{char}\""
                subprocess.run(command, capture_output=True, text=True, shell=True)
            else:
                command = self.hdc_path + f" shell uitest uiInput inputText 1 1 {char}"
                subprocess.run(command, capture_output=True, text=True, shell=True)

    def slide(self, x1, y1, x2, y2):
        command = self.hdc_path + f" shell uitest uiInput swipe {x1} {y1} {x2} {y2} 500"
        subprocess.run(command, capture_output=True, text=True, shell=True)

    def back(self):
        command = self.hdc_path + " shell uitest uiInput keyEvent Back"
        subprocess.run(command, capture_output=True, text=True, shell=True)

    def home(self):
        command = self.hdc_path + " shell uitest uiInput keyEvent Home"
        subprocess.run(command, capture_output=True, text=True, shell=True)

    def open_app(self, app_identifier):
        """
        打开应用，支持应用名或包名
        :param app_identifier: 应用名或包名
        :return: bool 是否成功
        """
        # 常见应用包名映射（HarmonyOS）
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
        }
        
        # 判断是应用名还是包名
        if app_identifier in APP_PACKAGES:
            package_name = APP_PACKAGES[app_identifier]
        elif '.' in app_identifier:
            package_name = app_identifier
        else:
            print(f"未知应用: {app_identifier}，尝试使用原始名称")
            package_name = app_identifier
        
        # HarmonyOS 使用 aa start 命令启动应用
        command = self.hdc_path + f" shell aa start -a MainAbility -b {package_name}"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"成功打开应用: {app_identifier} ({package_name})")
            time.sleep(3)
            return True
        else:
            print(f"打开应用失败: {app_identifier}, 将使用默认的点击方式")
            return False
