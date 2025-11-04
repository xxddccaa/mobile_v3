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
python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "帮我整理所有与'黄金第2天'相关的微博动态" --add_info "整理某东西的微博动态的操作如下，全程不需要滚动操作：1. 微博应用图标不在可见范围内, 使用 open_app 微博 动作直接打开微博应用（无需滑动）。 2. 点击发现 icon。 3. 输入搜索词，但不要打开智搜开关。 4. 点击橙色的搜索按钮。 5. 在搜索结果里再去点击上方Tab里出现的智搜按钮，进入到智搜的结果页面。 6. 点击左下角的 继续问智搜 ，点击一次即可，再次出现就不要点击。 7. 关闭可能会弹出来的弹窗，然后点击右下方出现的'向下箭头'的 icon 按钮到内容的最底部，而不要使用滚动操作去滚动到最底部。 8. 点击屏幕最左边的下方的复制按钮，点击复制按钮的动作描述（Action description）要写成 点击复制按钮，之后就退出agent。"
```


```powershell
python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "帮我整理所有与李荣浩相关的微博动态" --add_info "整理某东西的微博动态的操作：1. 微博应用图标不在可见范围内, 使用 open_app 微博 动作直接打开微博应用（无需滑动），2. 点击发现按钮。 3. 输入搜索词，但不要打开智搜开关。 4. 点击搜索按钮。 5. 在搜索结果里再去点击智搜按钮，进入到智搜的结果页面。 6. 点击左下角的 继续问智搜。 7. 点击右下方的'向下箭头'的按钮。 8. 点击复制按钮，点击复制按钮的动作描述要写成 点击复制按钮，点击后就不需要任何操作了，退出agent。"
```

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击复制icon按钮" --add_info "按照指示完成操作后就退出agent。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击右下方的'向下箭头'的按钮，点击复制按钮，点击复制按钮的动作描述要写成 点击复制按钮。" --add_info "按照指示完成操作后就退出agent。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博，在微博发现里输入'爱情'进行搜索" --add_info "按照指示完成操作后就退出agent。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "使用 open_app 微博 动作直接打开微博应用（无需滑动）。" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "使用 open_app 微博 动作直接打开微博应用（无需滑动或者点击）。" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击发现icon。" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击智搜。" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击'继续问智搜'。" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "使用 open_app 微博 动作直接打开微博应用" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "使用open_app动作直接打开微博应用" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "使用微博的发现（使用open_app动作直接打开微博应用）搜索'范冰冰'。" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "使用微博的发现（使用open_app动作直接打开微博应用）搜索'梁朝伟'，在搜索结果页点击'智搜'。" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "当前是'智搜'的搜索结果页，点击底部的'继续问智搜'。" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "当前是'继续问智搜'的详情对话页，点击右下方的'向下箭头'。" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "当前是'继续问智搜'的详情对话页，点击右下方的'向下箭头'，然后点击复制icon。" --add_info "按照指示完成操作后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "帮我整理所有与'黄金第2天'相关的微博动态" --add_info "整理某东西的微博动态的操作如下，全程不需要滚动操作：1. 微博应用图标不在可见范围内, 使用 open_app 微博 动作直接打开微博应用（无需滑动）。 2. 点击发现 icon。 3. 输入搜索词，但不要打开智搜开关。 4. 点击橙色的搜索按钮。 5. 在搜索结果里再去点击上方Tab里出现的智搜按钮，进入到智搜的结果页面。 6. 点击左下角的 继续问智搜 ，点击一次即可，再次出现就不要点击。 7. 关闭可能会弹出来的弹窗，然后点击右下方出现的'向下箭头'的 icon 按钮到内容的最底部，而不要使用滚动操作去滚动到最底部。 8. 点击屏幕最左边的下方的复制按钮，点击复制按钮的动作描述（Action description）要写成 点击复制按钮，之后就退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击发现，搜索'电脑'。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击发现，搜索'梁静茹'。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击发现，搜索'邓超',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博，点击发现，搜索'北京 天气',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。使用open_app动作直接打开微博应用，所有APP都是使用open_app动作直接打开，无需滑动或者点击。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博（所有APP都是使用open_app动作直接打开），点击发现，搜索'黄金',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头，然后点击复制。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。使用open_app动作直接打开微博应用，所有APP都是使用open_app动作直接打开，无需滑动或者点击。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博（所有APP都是使用open_app动作直接打开），点击发现，搜索'黄金',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头，然后点击复制。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。使用open_app动作直接打开微博应用，所有APP都是使用open_app动作直接打开，无需滑动或者点击。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博（所有APP都是使用open_app动作直接打开），点击发现，搜索'黄金第5天',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头，然后点击复制。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。使用open_app动作直接打开微博应用，所有APP都是使用open_app动作直接打开，无需滑动或者点击。有弹窗的情况优先关闭弹窗。有时候智搜对话页里需要一些时间等待，才会出现向下箭头。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博（所有APP都是使用open_app动作直接打开），点击发现，搜索'加勒比',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头，然后点击复制。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。使用open_app动作直接打开微博应用，所有APP都是使用open_app动作直接打开，无需滑动或者点击。有弹窗的情况优先关闭弹窗。有时候智搜对话页里需要一些时间等待，才会出现向下箭头。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击'复制icon'" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。使用open_app动作直接打开微博应用，所有APP都是使用open_app动作直接打开，无需滑动或者点击。有弹窗的情况优先关闭弹窗。有时候智搜对话页里需要一些时间等待，才会出现向下箭头。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击'分享icon'" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。使用open_app动作直接打开微博应用，所有APP都是使用open_app动作直接打开，无需滑动或者点击。有弹窗的情况优先关闭弹窗。有时候智搜对话页里需要一些时间等待，才会出现向下箭头。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博（所有APP都是使用open_app动作直接打开），点击发现，搜索'明星',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头，然后点击复制'icon'（禁止点'分享icon'）。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。使用open_app动作直接打开微博应用，所有APP都是使用open_app动作直接打开，无需滑动或者点击。有弹窗的情况优先关闭弹窗。有时候智搜对话页里需要一些时间等待，才会出现向下箭头。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博（所有APP都是使用open_app动作直接打开），点击发现，搜索'周杰伦',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头，然后点击复制'icon'（禁止点'分享icon'）。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。使用open_app动作直接打开微博应用，所有APP都是使用open_app动作直接打开，无需滑动或者点击。有弹窗的情况优先关闭弹窗。有时候智搜对话页里需要一些时间等待，才会出现向下箭头。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博（所有APP都是使用open_app动作直接打开），点击发现，搜索'黄金第1天',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头，然后点击复制'icon'（禁止点'分享icon'）。" --add_info "按照指示完成操作后就退出agent。所有type操作无需考虑原始文本是否清除，输入文本默认就会清除原始的文本，无需点击清除文本按钮。使用open_app动作直接打开微博应用，所有APP都是使用open_app动作直接打开，无需滑动或者点击。有弹窗的情况优先关闭弹窗。有时候智搜对话页里需要一些时间等待，才会出现向下箭头。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "帮我整理所有与'结晶体'相关的微博动态" --add_info "为用户搜索整理微博动态的操作步骤为：打开微博（用open_app动作直接打开微博，禁止滚动和点击），点击发现，输入搜索词，点击搜索，在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头（可能需要多次点击，点击后此箭头消失），然后点击复制'icon'（禁止点'分享icon'），任务结束退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头（可能需要多次点击，点击后此箭头消失），然后点击复制'icon'（禁止点'分享icon'），任务结束退出agent。" --add_info "任务名：帮我整理所有与'结晶体'相关的微博动态。已经完成一部分了，按我说的操作完成剩下的即可。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博（所有APP都是使用open_app动作直接打开），点击发现，搜索'林依晨',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头，然后点击复制'icon'（禁止点'分享icon'）。" --add_info "这个其实就是为用户搜索整理微博动态的操作步骤，用户原始命令：帮我整理所有与'林依晨'相关的微博动态"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博（所有APP都是使用open_app动作直接打开），点击发现，搜索'邓超',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头，然后点击左边的复制'icon'（不是点右边的'分享icon'）。" --add_info "这个其实就是为用户搜索整理微博动态的操作步骤，用户原始命令：帮我整理所有与'邓超'相关的微博动态。点击复制的操作描述要写为中文：点击复制按钮。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开微博（所有APP都是使用open_app动作直接打开），点击发现，搜索'孙颖莎',在搜索结果页点击'智搜'按钮，然后点击最底下的'继续问智搜'进入智搜对话页，点击右下方的向下箭头，然后点击左边的复制'icon'（不是点右边的'分享icon'）。" --add_info "这个其实就是为用户搜索整理微博动态的操作步骤，用户原始命令：帮我整理所有与'孙颖莎'相关的微博动态。点击复制的操作描述要写为中文：点击复制按钮。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open Weibo (all apps should be opened using the open_app action directly {'action': 'open_app', 'text': '微博'}), click the '发现' button (do not click the '智搜' toggle switch), search for '成龙', click the '智搜' button on the search results page, then click the '继续问智搜' button at the bottom to enter the 智搜 conversation page, click the downward arrow icon in the bottom right corner, then click the copy 'icon' on the left (not the '分享' icon on the right)." --add_info "This is the operation steps for searching and organizing Weibo posts for users. Original user command: 帮我整理所有与'成龙'相关的微博动态。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open Weibo (all apps should be opened using the open_app action directly {'action': 'open_app', 'text': '微博'}), click the '发现' button (do not click the '智搜' toggle switch), search for '周星驰​', click the '智搜' button on the search results page, then click the '继续问智搜' button at the bottom to enter the 智搜 conversation page, click the downward arrow icon in the bottom right corner, then click the copy 'icon' on the left (not the '分享' icon on the right)." --add_info "This is the operation steps for searching and organizing Weibo posts for users. Original user command: 帮我整理所有与'周星驰​'相关的微博动态。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open Weibo (all apps should be opened using the open_app action directly {'action': 'open_app', 'text': '微博'}), click the '发现' button (do not click the '智搜' toggle switch), search for '莱昂纳多', click the '智搜' button on the search results page, then click the '继续问智搜' button at the bottom to enter the 智搜 conversation page, click the downward arrow icon in the bottom right corner, then click the copy 'icon' on the left (not the '分享' icon on the right)." --add_info "This is the operation steps for searching and organizing Weibo posts for users. Original user command: 帮我整理所有与'莱昂纳多'相关的微博动态。That is to say, users should follow these steps to retrieve 微博动态."

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open Weibo (all apps should be opened using the open_app action directly {'action': 'open_app', 'text': '微博'}), click the '发现' button, type 'Lady Gaga​' (then click '搜索', do not click the '智搜' toggle switch), click the '智搜' button on the search results page, then click the '继续问智搜' button at the bottom to enter the 智搜 conversation page, click the downward arrow icon in the bottom right corner, then click the copy 'icon' on the left (not the '分享' icon on the right)." --add_info "This is the operation steps for searching and organizing Weibo posts for users. Original user command: 帮我整理所有与'Lady Gaga​'相关的微博动态。That is to say, users should follow these steps to retrieve 微博动态."

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open Weibo (all apps should be opened using the open_app action directly {'action': 'open_app', 'text': '微博'}), click the '发现' button, Click the search box and type '刘德华​' (then click '搜索', do not click the '智搜' toggle switch), click the '智搜' button on the search results page, then click the '继续问智搜' button at the bottom to enter the 智搜 conversation page, click the downward arrow icon in the bottom right corner, then click the copy 'icon' on the left (not the '分享' icon on the right)." --add_info "This is the operation steps for searching and organizing Weibo posts for users. Original user command: 帮我整理所有与刘德华​相关的微博动态。That is to say, users should follow these steps to retrieve 微博动态."


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "帮我整理所有与宁浩​相关的微博动态。" --add_info "This is the operation steps for searching and organizing Weibo posts for users: 1. Open weibo app using {'action': 'open_app', 'text': 'weibo'},  禁止使用点击和滑动去打开APP，必须使用open_app动作打开APP，禁止这么计划：Swipe up or scroll through the home screens to find the Weibo app.  2. Click on the magnifying glass icon. 3. Click the search box to activate search box. 必须点击搜索框让输入法键盘选项出现在屏幕上，不然是不可以输入东西的.  4. type the content that the user wants to search for (No need to consider clearing the default text in the input box.The text will automatically disappear when typing.).  5. then click '搜索', do not click the '智搜' toggle switch. 6. click the '智搜' tab botton on the search results page. 7. click the '继续问智搜' box button at the bottom to enter the 智搜 conversation page. 8. click the downward arrow icon in the bottom right corner, 禁止这么计划：Scroll down the page， 因为向下箭头直接就可以到UI底部了。 9. click the copy 'icon' on the left (not the '分享' icon on the right).  That is to say, users should follow these steps to retrieve 微博动态. 返回的点击动作格式必须满足类似这样的格式Action: {"action": "click", "coordinate": [253, 296]}"





小红书

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "This is the operation steps for searching and organizing xiaohongshu posts for users: Open xiaohongshu (all apps should be opened using the open_app action directly, for example {'action': 'open_app', 'text': 'xiaohongshu'}, No scrolling or clicking), click the '放大镜' icon button, Click the search box and type the content that the user wants to search for (then click '搜索'), click the '问一问' tab botton on the search results page, finish agent.  That is to say, users should follow these steps to retrieve 小红书动态." --add_info "帮我整理所有与谷爱凌​相关的小红书动态。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open xiaohongshu" --add_info "all apps should be opened using the open_app action directly, for example {'action': 'open_app', 'text': 'xiaohongshu'}, No scrolling or clicking"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open xiaohongshu" --add_info "all apps should be opened using the open_app action directly, for example {'action': 'open_app', 'text': 'xiaohongshu'}"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "打开小红书" --add_info "all apps should be opened using the open_app action directly, for example {'action': 'open_app', 'text': 'xiaohongshu'}"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Click 放大镜 icon botton" --add_info "这是搜索动态的一个中间步骤，完成后退出agent。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Click on the search box, type Jay Chou (No need to consider clearing the default text in the input box.The text will automatically disappear when typing.), and then click the search button." --add_info "This is an intermediate step for searching content and will exit the agent upon completion."

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Click on the magnifying glass icon, Click on the search box, type 周杰伦 (No need to consider clearing the default text in the input box.The text will automatically disappear when typing.), and then click the search button." --add_info "This is an intermediate step for searching content and will exit the agent upon completion."

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Click on the magnifying glass icon, Click on the search box, type 林依晨 (No need to consider clearing the default text in the input box.The text will automatically disappear when typing.), and then click the search button. then click 问一问 tab botton. " --add_info "This is an intermediate step for searching content and will exit the agent upon completion."

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open xiaohongshu app using {'action': 'open_app', 'text': 'xiaohongshu'},  No click or swipe action, Click on the magnifying glass icon, Click on the search box, type 黄金 (No need to consider clearing the default text in the input box.The text will automatically disappear when typing.), and then click the search button. then click 问一问 tab botton. " --add_info "This is an intermediate step for searching content and will exit the agent upon completion. 打开APP的动作必须用open_app action。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open xiaohongshu app using {'action': 'open_app', 'text': 'xiaohongshu'},  No click or swipe action, Click on the magnifying glass icon, Click on the search box, type 黄金走势 (No need to consider clearing the default text in the input box.The text will automatically disappear when typing.), and then click the search button. then click 问一问 tab botton. " --add_info "This is an intermediate step for searching content and will exit the agent upon completion. 打开APP的动作必须用open_app action。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open xiaohongshu app using {'action': 'open_app', 'text': 'xiaohongshu'},  No click or swipe action, Click on the magnifying glass icon, Click on the search box, type 朗朗 (No need to consider clearing the default text in the input box.The text will automatically disappear when typing.), and then click the search button. then click 问一问 tab botton. " --add_info "This is an intermediate step for searching xiaonghongshu content and will exit the agent upon completion. 打开APP的动作必须用open_app action。"


python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open xiaohongshu app using {'action': 'open_app', 'text': 'xiaohongshu'},  No click or swipe action, Click on the magnifying glass icon, Click on the search box, type 白银 (No need to consider clearing the default text in the input box.The text will automatically disappear when typing.), and then click the search button. then click 问一问 tab botton. " --add_info "This is an intermediate step for searching xiaonghongshu content and will exit the agent upon completion. 打开APP的动作必须用open_app action。"

python run_mobileagentv3.py --adb_path "D:\platform-tools\adb.exe" --api_key "123" --base_url "http://10.142.18.204:8006/v1" --model "owl32b" --instruction "Open xiaohongshu app using {'action': 'open_app', 'text': 'xiaohongshu'},  No click or swipe action, Click on the magnifying glass icon, Click on the search box, type 稀有金属 (No need to consider clearing the default text in the input box.The text will automatically disappear when typing.), and then click the search button. then click 问一问 tab botton. " --add_info "This is an intermediate step for searching xiaonghongshu content and will exit the agent upon completion. 打开APP的动作必须用open_app action。"


