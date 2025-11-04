#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
成功执行的微博搜索整理任务参考示例
从 20251104_151055 日志中提取

可以将此示例添加到 ADD_INFO 中，让模型参考成功的执行模式
"""

# 完整的成功执行示例（9个步骤）
SUCCESSFUL_EXECUTION_REFERENCE = """
以下是一个成功完成微博搜索整理任务的完整执行示例，请参考这个执行模式：

=== Step 1: 打开微博应用 ===
### Thought ###
To achieve the user's request of organizing all Weibo posts related to "黄金第2天," I need to first open the Weibo app. The current screen shows the home screen with various apps, but the Weibo app is not visible. Therefore, the next logical step is to use the `open_app` action to directly open the Weibo app.

### Action ###
{'action': 'open_app', 'text': '微博'}

### Description ###
Open the Weibo app using the `open_app` action.


=== Step 2: 点击搜索图标 ===
### Thought ###
To achieve the current subgoal, I need to activate the search function. The magnifying glass icon at the bottom center of the screen is likely the search button. Clicking this will allow me to proceed with entering the search term "黄金第2天".

### Action ###
{'action': 'click', 'coordinate': [546, 2247]}

### Description ###
Click on the magnifying glass icon.


=== Step 3: 激活搜索框 ===
### Thought ###
The current screen shows the Weibo app with a search bar at the top. The next step in the plan is to click on the search box to activate it and bring up the keyboard so that I can type "黄金第2天". Since the search bar is visible, clicking on it will allow me to proceed with typing the query.

### Action ###
{'action': 'click', 'coordinate': [364, 178]}

### Description ###
Click on the search box.


=== Step 4: 输入搜索关键词 ===
### Thought ###
The search box is already activated, and the ADB Keyboard is on. The next step is to type "黄金第2天" into the search box as per the user's request.

### Action ###
{'action': 'type', 'text': '黄金第2天'}

### Description ###
Type "黄金第2天" into the search box.


=== Step 5: 点击搜索按钮 ===
### Thought ###
The user has already typed "黄金第2天" into the search box. The next step is to initiate the search by clicking the '搜索' button, which will display the search results. This aligns with the current subgoal of initiating the search.

### Action ###
{'action': 'click', 'coordinate': [940, 326]}

### Description ###
Click the '搜索' button.


=== Step 6: 等待搜索结果并切换到智搜标签 ===
### Thought ###
The search results for "黄金第2天" are displayed, but the '智搜' tab is currently showing the top related posts. To access the '继续问智搜' feature, I need to ensure I'm on the correct tab. I see a "话题" tab button at the top left. However, the '智搜' tab should be near the top of the screen. Since the current screen does not clearly show the '智搜' tab button, I should look for it or wait for the page to fully load.

After reviewing the screen more carefully, I notice there's a button labeled "回到首页" (Return to Homepage) at the bottom, which suggests that we are not on the main search results page yet. The next action should be to click on the '智搜' tab button if it's visible, or to navigate to the section where '继续问智搜' is available.

Looking at the screen again, I can see the '智搜' label in the interface, and I should click on it to proceed.

### Action ###
{'action': 'click', 'coordinate': [254, 296]}

### Description ###
Click on the '智搜' tab button.


=== Step 7: 点击向下箭头到底部 ===
### Thought ###
The current screen shows the search results for "黄金第2天" with a detailed summary from 微博智搜. The next step is to scroll down to find the copy icon. However, according to the additional information provided, I should click the downward arrow icon in the bottom right corner to navigate directly to the bottom of the page where the copy icon is located. This approach is preferred over scrolling because it's faster and more reliable.

Looking at the current screen, I need to locate the downward arrow icon. Typically, such icons are found at the bottom right corner of the screen. Since the screen doesn't clearly show the downward arrow icon yet, it might be necessary to wait for the page to fully load or to look for other visible elements that indicate the presence of the downward arrow.

Upon closer inspection of the screen, I can see there is a downward arrow icon at the bottom right corner of the screen (coordinate approximately [230, 2256]). Clicking this icon will help navigate to the bottom of the page.

### Action ###
{'action': 'click', 'coordinate': [230, 2256]}

### Description ###
Click the downward arrow icon in the bottom right corner.


=== Step 8: 等待加载后再次点击向下箭头 ===
### Thought ###
The current screen shows the search results for "黄金第2天" with detailed information provided by the智搜 feature. According to the plan, the next step is to click the downward arrow icon in the bottom right corner to navigate to the bottom of the page where the copy icon is located.

Looking at the current screen, I can see there is a downward arrow icon at the bottom right corner (approximately at coordinate [978, 1790]). Clicking this will allow me to scroll down to the bottom of the page where the copy icon should be available.

### Action ###
{'action': 'click', 'coordinate': [978, 1790]}

### Description ###
Click the downward arrow icon in the bottom right corner to navigate to the bottom of the page.


=== Step 9: 点击复制按钮 ===
### Thought ###
The current screen shows the search results for "黄金第2天" with detailed information. The next step in the plan is to click the copy icon on the left side at the bottom of the screen. This will allow me to copy the content, which is the final step before providing the answer to the user.

Looking at the current screen, I can see there is a copy icon at the bottom left corner (approximately at coordinate [86, 1650]). This is the icon I need to click to copy the relevant Weibo posts.

### Action ###
{'action': 'click', 'coordinate': [86, 1650]}

### Description ###
Click the copy icon on the left side at the bottom of the screen.


=== 执行结果 ===
任务成功完成！复制了包含"黄金第2天"所有相关微博动态的完整内容到剪贴板。

关键成功要素：
1. 使用 open_app 动作直接打开微博应用（不是通过滑动和点击图标）
2. 按照步骤依次激活搜索：点击搜索图标 → 点击搜索框 → 输入关键词 → 点击搜索
3. 切换到"智搜"标签获取整理好的内容
4. 通过点击向下箭头（不是滑动）快速到达页面底部
5. 点击左侧的复制按钮（不是右侧的分享按钮）
"""


# 简化版操作步骤提示（可以替换或补充现有的 ADD_INFO）
SIMPLIFIED_STEPS_WITH_EXAMPLES = """
This is the operation steps for searching and organizing Weibo posts for users (should follow these steps to retrieve 微博动态):

【成功案例参考】：以下步骤已在实际测试中验证成功

1. Open weibo app using {'action': 'open_app', 'text': '微博'}
   - 必须使用 open_app 动作打开APP
   - 禁止使用点击和滑动去打开APP
   - 禁止计划：Swipe up or scroll through the home screens to find the Weibo app

2. Click on the magnifying glass icon (搜索图标)
   - 参考坐标：[546, 2247]（实际案例中的位置）
   - 图标通常在底部中间位置

3. Click the search box to activate it
   - 参考坐标：[364, 178] 或 [378, 176]
   - 必须点击搜索框让输入法键盘选项出现在屏幕上
   - 屏幕底部会显示 "ADB Keyboard {on}"

4. Type the search content
   - 使用 {'action': 'type', 'text': '搜索关键词'}
   - 不需要考虑清除输入框中的默认文本，输入时会自动消失

5. Click '搜索' button
   - 参考坐标：[940, 326]
   - 不要点击 '智搜' 切换开关

6. Click the '智搜' tab button on the search results page
   - 参考坐标：[254, 296]
   - 在搜索结果页面的顶部标签栏中

7. Wait if needed, then click '继续问智搜'
   - 如果页面还在加载，可能需要等待 1-3 秒

8. Click the downward arrow icon in the bottom right corner
   - 参考坐标：[230, 2256] 或 [978, 1790]
   - 禁止计划：Scroll down the page
   - 向下箭头可以直接到UI底部，比滑动更快更准确
   - 如果屏幕没有出现向下箭头，使用 {'action': 'wait', 'time': 1-3} 等待

9. Click the copy icon on the left (not the '分享' icon on the right)
   - 参考坐标：[86, 1650]
   - 复制按钮在最底部的左侧
   - 需要确认向下箭头已经被点击（点击后才会显示复制按钮）
   - 禁止点击右上角的+号icon

【重要提示】
- 每个步骤都需要等待操作完成后再进行下一步
- 点击搜索框后，确认键盘已激活（看到 "ADB Keyboard {on}"）
- 使用向下箭头而不是滑动，可以更快更准确地到达底部
- 复制按钮在左侧，分享按钮在右侧，不要混淆

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


if __name__ == "__main__":
    print("="*80)
    print("成功执行参考示例")
    print("="*80)
    print("\n=== 完整版本 ===")
    print(SUCCESSFUL_EXECUTION_REFERENCE)
    print("\n\n=== 简化版本（带参考坐标）===")
    print(SIMPLIFIED_STEPS_WITH_EXAMPLES)

