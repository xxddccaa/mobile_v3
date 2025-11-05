import uiautomator2 as u2
from PIL import Image, ImageDraw
import time

# 连接设备
print("正在连接设备...")
d = u2.connect()
print("设备连接成功！")

# 要测试的点击坐标
x, y = 230, 2256
print(f"\n准备点击坐标: ({x}, {y})")

# 点击前截图
print("点击前截图...")
screenshot_before = d.screenshot(format='pillow')
screenshot_before.save('before_click.png')
print("点击前截图已保存: before_click.png")

# 在截图上标记点击位置
draw = ImageDraw.Draw(screenshot_before)
radius = 20
draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
             outline='red', width=5)
cross_size = 40
draw.line([x-cross_size, y, x+cross_size, y], fill='red', width=3)
draw.line([x, y-cross_size, x, y+cross_size], fill='red', width=3)
draw.text((x+30, y-30), f'点击点: ({x}, {y})', fill='red')
screenshot_before.save('before_click_marked.png')
print("已标记点击位置: before_click_marked.png")

# 执行点击
print(f"\n正在点击坐标 ({x}, {y})...")
try:
    d.click(x, y)
    print("✓ 点击命令执行成功！")
    time.sleep(2)  # 等待2秒让界面响应
except Exception as e:
    print(f"✗ 点击失败: {e}")

# 点击后截图
print("\n点击后截图...")
screenshot_after = d.screenshot(format='pillow')
screenshot_after.save('after_click.png')
print("点击后截图已保存: after_click.png")

print("\n" + "="*50)
print("测试完成！")
print("="*50)
print("生成的文件：")
print("  1. before_click.png - 点击前截图")
print("  2. before_click_marked.png - 标记了点击位置的截图")
print("  3. after_click.png - 点击后截图")
print("\n请对比 before_click.png 和 after_click.png 来验证点击效果")

