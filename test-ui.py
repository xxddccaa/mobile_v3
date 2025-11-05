import uiautomator2 as u2
from PIL import Image, ImageDraw
import numpy as np

# 连接设备
d = u2.connect()

# 截图
screenshot = d.screenshot(format='pillow')

# 在图片上标记坐标点
draw = ImageDraw.Draw(screenshot)

# 要标记的坐标
x, y = 230, 2256

# 画一个红色的圆圈标记这个点
radius = 20
draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
             outline='red', width=5)

# 画一个十字标记
cross_size = 40
draw.line([x-cross_size, y, x+cross_size, y], fill='red', width=3)
draw.line([x, y-cross_size, x, y+cross_size], fill='red', width=3)

# 在坐标点旁边添加文字说明
draw.text((x+30, y-30), f'({x}, {y})', fill='red')

# 保存图片
screenshot.save('coordinate_marker.png')
print(f'截图已保存到 coordinate_marker.png')
print(f'坐标点 ({x}, {y}) 已用红色标记')

# 显示图片（如果你有显示环境）
screenshot.show()