电脑环境：

### 安装 qwen 模型所需的依赖项

```
uv pip install qwen_agent qwen_vl_utils numpy uiautomator2
```

**说明**：安装 uiautomator2 后，**无需安装 ADB Keyboard**，即可直接输入中文。首次连接设备时，uiautomator2 会自动在手机上安装 ATX-agent 服务。

### 准备通过ADB连接你的移动设备
1. 下载 [Android Debug Bridge](https://developer.android.com/tools/releases/platform-tools?hl=en)（ADB）。
2. 在你的移动设备上开启“USB调试”或“ADB调试”，它通常需要打开开发者选项并在其中开启。如果是HyperOS系统需要同时打开 "[USB调试(安全设置)](https://github.com/user-attachments/assets/05658b3b-4e00-43f0-87be-400f0ef47736)"。
3. 通过数据线连接移动设备和电脑，在手机的连接选项中选择“传输文件”。
4. 用下面的命令来测试你的连接是否成功: ```/path/to/adb devices```。如果输出的结果显示你的设备列表不为空，则说明连接成功。
5. 如果你是用的是MacOS或者Linux，请先为 ADB 开启权限: ```sudo chmod +x /path/to/adb```。
6.  ```/path/to/adb```在Windows电脑上将是```xx/xx/adb.exe```的文件格式，而在MacOS或者Linux则是```xx/xx/adb```的文件格式。


### （可选）在你的移动设备上安装 ADB 键盘
**注意**：如果已安装 uiautomator2，则**无需**安装 ADB Keyboard。以下步骤仅在未安装 uiautomator2 的情况下需要：

1. 下载 ADB 键盘的 [apk](https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk) 安装包。
2. 在设备上点击该 apk 来安装。
3. 在系统设置中将默认输入法切换为 "ADB Keyboard"。



```powershell
python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "帮我整理所有与李荣浩相关的微博动态" --add_info "整理某东西的微博动态的操作：1. 微博应用图标不在可见范围内, 使用 open_app 微博 动作直接打开微博应用（无需滑动），2. 点击发现按钮。 3. 输入搜索词，但不要打开智搜开关。 4. 点击搜索按钮。 5. 在搜索结果里再去点击智搜按钮，进入到智搜的结果页面。 6. 点击左下角的 继续问智搜。 7. 点击右下方的'向下箭头'的按钮。 8. 点击复制按钮，点击复制按钮的动作描述要写成 点击复制按钮，点击后就不需要任何操作了，退出agent。"
```


