#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行微博搜索整理的 Python 脚本
Usage: python run_weibo_search.py [search_keyword]
Example: python run_weibo_search.py "宁浩"
"""

import subprocess
import sys
import time

try:
    import uiautomator2 as u2
    U2_AVAILABLE = True
except ImportError:
    U2_AVAILABLE = False
    print("Warning: uiautomator2 not installed. Will skip closing app step.")

# 默认参数配置
DEFAULT_CONFIG = {
    "adb_path": r"D:\platform-tools\adb.exe",
    "api_key": "123",
    "base_url": "http://10.142.18.204:8006/v1",
    "model": "owl32b",
    "search_keyword": "刘一博"
}

# 操作步骤说明
ADD_INFO = """

# 微博操作

以下是为用户检索和整理微博动态的操作步骤（请依次执行以下步骤以获取微博动态）：
1. 打开微博应用。
2. 点击放大镜图标（发现）。
3. 点击搜索框以激活，激活后可以看到底部有"Clear Text"按钮。
4. 输入用户想要搜索的内容（不需要考虑清除输入框内的默认文字，输入时默认文字会自动消失）。
5. 点击“搜索”按钮，不要点击“智搜”切换开关。
6. 在搜索结果页点击最底下的放大镜图标（问智搜）。
7. 点击右下角的向下箭头图标。
8. 点击复制图标。


关键成功要素：
1. 使用 open_app 动作直接打开微博应用（不是通过滑动和点击图标）
2. 按照步骤依次激活搜索：点击搜索图标 → 点击搜索框 → 输入关键词 → 点击搜索
3. 切换到"智搜"标签获取整理好的内容
4. 通过点击向下箭头快速到达页面底部，否则就用下滑滑到最底下。
5. 点击左侧的复制按钮（不是右侧的分享按钮）

# 小红书操作

以下是为用户检索和整理小红书内容的操作步骤（请依次执行以下步骤以获取小红书内容）：
1. 使用 {'action': 'open_app', 'text': 'xiaohongshu'} 动作直接打开小红书APP，禁止使用点击或滑动的方式去打开APP，务必使用 open_app 动作，严禁类似“滑动屏幕或滚动桌面查找小红书应用”等计划。
2. 点击放大镜图标。
3. 点击搜索框以激活。
4. 输入用户想要搜索的内容（不需要考虑清除输入框内的默认文字，输入时默认文字会自动消失）。
5. 然后点击搜索按钮。
6. 然后点击“问一问”标签按钮。

关键成功要素：
1. 使用 open_app 动作直接打开小红书应用（不是通过滑动和点击图标）
2. 按照步骤依次激活搜索：点击搜索图标 → 点击搜索框 → 输入关键词 → 点击搜索
3. 切换到"问一问"标签获取相关内容

# 动作约束

所有可以返回的动作类型：
- {"action": "click", "coordinate": [x, y]}
- {"action": "type", "text": "要输入的文本"}
- {"action": "swipe", "coordinate": [x1, y1], "coordinate2": [x2, y2]}
- {"action": "long_press", "coordinate": [x, y]}
- {"action": "system_button", "button": "按钮名称"}
- {"action": "open_app", "text": "应用名称"}
- {"action": "answer", "text": "答案内容"}
- {"action": "wait", "time": 秒数}

"""


def close_weibo_app(adb_path):
    """
    使用 uiautomator2 关闭微博应用
    
    Args:
        adb_path: ADB 可执行文件路径
    """
    if not U2_AVAILABLE:
        print("[SKIP] uiautomator2 未安装，跳过关闭微博应用步骤")
        return
    
    weibo_package = "com.sina.weibo"
    
    print("=" * 50)
    print("准备关闭微博应用...")
    print("=" * 50)
    
    try:
        # 获取设备序列号
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
        
        if not devices:
            print("[WARNING] 未找到连接的设备")
            return
        
        # 连接到第一个设备
        device = u2.connect(devices[0])
        print(f"[OK] 已连接到设备: {devices[0]}")
        
        # 关闭微博应用
        device.app_stop(weibo_package)
        print(f"[OK] 成功关闭微博应用 ({weibo_package})")
        
        # 等待一下确保应用完全关闭
        print("等待 2 秒确保应用完全关闭...")
        time.sleep(2)
        print("[OK] 准备就绪\n")
        
    except Exception as e:
        print(f"[WARNING] 关闭微博应用失败: {e}")
        print("继续执行任务...\n")


def run_weibo_search(search_keyword=None, **kwargs):
    """
    运行微博搜索整理任务
    
    Args:
        search_keyword: 搜索关键词，默认为配置中的值
        **kwargs: 其他参数覆盖默认配置
            - adb_path: ADB 路径
            - api_key: API 密钥
            - base_url: API 基础地址
            - model: 模型名称
    """
    # 合并配置
    config = DEFAULT_CONFIG.copy()
    config.update(kwargs)
    
    if search_keyword:
        config["search_keyword"] = search_keyword
    
    # 先关闭微博应用，确保从干净的状态开始
    close_weibo_app(config["adb_path"])
    
    # 构建指令
    instruction = f"帮我整理所有与{config['search_keyword']}相关的微博动态。"
    
    # 构建命令
    cmd = [
        "D:\python_envs\py313\Scripts\python",
        "run_mobileagentv3.py",
        "--adb_path", config["adb_path"],
        "--api_key", config["api_key"],
        "--base_url", config["base_url"],
        "--model", config["model"],
        "--instruction", instruction,
        "--add_info", ADD_INFO
    ]
    
    # 打印配置信息
    print("=" * 50)
    print("运行微博搜索整理任务")
    print("=" * 50)
    print(f"搜索关键词: {config['search_keyword']}")
    print(f"ADB路径: {config['adb_path']}")
    print(f"API地址: {config['base_url']}")
    print(f"模型: {config['model']}")
    print(f"指令内容: {instruction}")
    print("=" * 50)
    print()
    
    # 打印完整命令（调试用）
    print("执行命令:")
    print(" ".join([f'"{arg}"' if " " in arg else arg for arg in cmd]))
    print()
    
    # 执行命令
    try:
        subprocess.run(cmd, check=True)
        print("\n任务完成！")
    except subprocess.CalledProcessError as e:
        print(f"\n任务执行失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n任务被用户中断")
        sys.exit(1)


if __name__ == "__main__":
    # 从命令行参数获取搜索关键词
    search_keyword = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 可以在这里修改默认参数
    # 例如：
    # run_weibo_search(
    #     search_keyword="宁浩",
    #     api_key="your_api_key",
    #     base_url="http://your-api-url/v1",
    #     model="your_model"
    # )
    
    run_weibo_search(search_keyword)