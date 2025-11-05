#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化脚本：将 operator.json 中的 response 内容渲染到图片上
"""

import json
import os
import sys
import argparse
import base64
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re


def wrap_text(text, font, max_width):
    """将文本按指定宽度换行，支持中英文混合"""
    lines = []
    paragraphs = text.split('\n')
    
    for para in paragraphs:
        if not para.strip():
            lines.append('')
            continue
        
        # 检测是否为中文文本（包含中文字符）
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', para))
        
        if has_chinese:
            # 中文文本：按字符处理
            current_line = ''
            for char in para:
                test_line = current_line + char
                bbox = font.getbbox(test_line)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
            
            if current_line:
                lines.append(current_line)
        else:
            # 英文文本：按单词处理
            words = para.split(' ')
            current_line = ''
            
            for word in words:
                test_line = current_line + (' ' if current_line else '') + word
                bbox = font.getbbox(test_line)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    # 如果单个词就超过宽度，按字符分割
                    if font.getbbox(word)[2] - font.getbbox(word)[0] > max_width:
                        chars = list(word)
                        temp_line = ''
                        for char in chars:
                            test_char = temp_line + char
                            if font.getbbox(test_char)[2] - font.getbbox(test_char)[0] <= max_width:
                                temp_line = test_char
                            else:
                                if temp_line:
                                    lines.append(temp_line)
                                temp_line = char
                        current_line = temp_line
                    else:
                        current_line = word
            
            if current_line:
                lines.append(current_line)
    
    return lines


def decode_base64_image(image_url):
    """从base64 data URL中解码图片"""
    if not image_url.startswith('data:image'):
        return None
    
    # 提取base64数据部分
    header, data = image_url.split(',', 1)
    try:
        image_data = base64.b64decode(data)
        img = Image.open(io.BytesIO(image_data))
        return img
    except Exception as e:
        print(f"警告：无法解码base64图片: {e}")
        return None


def extract_coordinates(response_text):
    """从response文本中提取点击坐标
    
    Args:
        response_text: response文本内容
        
    Returns:
        list: 坐标列表，每个元素为 [x, y]
    """
    coordinates = []
    seen_coords = set()  # 用于去重
    
    # 匹配各种可能的格式：
    # Action: {"action": "click", "coordinate": [978, 2046]}  (JSON格式，双引号)
    # Action: {'action': 'click', 'coordinate': [978, 2046]}  (Python字典格式，单引号)
    # Action: {"action":"click","coordinate":[978,2046]}
    # coordinate: [978, 2046]
    # 等等
    
    # 方法1: 尝试匹配 Action 对象（支持单引号和双引号，支持多行）
    # 匹配双引号格式
    action_pattern1 = r'Action\s*:\s*\{[^}]*?"coordinate"\s*:\s*\[(\d+)\s*,\s*(\d+)\][^}]*?\}'
    matches = re.finditer(action_pattern1, response_text, re.IGNORECASE | re.DOTALL)
    for match in matches:
        x, y = int(match.group(1)), int(match.group(2))
        coord_key = (x, y)
        if coord_key not in seen_coords:
            coordinates.append([x, y])
            seen_coords.add(coord_key)
    
    # 匹配单引号格式（Python字典格式）
    action_pattern2 = r"Action\s*:\s*\{[^}]*?'coordinate'\s*:\s*\[(\d+)\s*,\s*(\d+)\][^}]*?\}"
    matches = re.finditer(action_pattern2, response_text, re.IGNORECASE | re.DOTALL)
    for match in matches:
        x, y = int(match.group(1)), int(match.group(2))
        coord_key = (x, y)
        if coord_key not in seen_coords:
            coordinates.append([x, y])
            seen_coords.add(coord_key)
    
    # 方法2: 尝试匹配单独的 coordinate 字段（可能是独立的一行）
    # 匹配双引号
    coord_pattern1 = r'"coordinate"\s*:\s*\[(\d+)\s*,\s*(\d+)\]'
    matches = re.finditer(coord_pattern1, response_text, re.IGNORECASE)
    for match in matches:
        x, y = int(match.group(1)), int(match.group(2))
        coord_key = (x, y)
        if coord_key not in seen_coords:
            coordinates.append([x, y])
            seen_coords.add(coord_key)
    
    # 匹配单引号
    coord_pattern2 = r"'coordinate'\s*:\s*\[(\d+)\s*,\s*(\d+)\]"
    matches = re.finditer(coord_pattern2, response_text, re.IGNORECASE)
    for match in matches:
        x, y = int(match.group(1)), int(match.group(2))
        coord_key = (x, y)
        if coord_key not in seen_coords:
            coordinates.append([x, y])
            seen_coords.add(coord_key)
    
    # 方法3: 尝试匹配更复杂的 JSON/Python 对象（可能跨多行）
    # 这个方法用于匹配可能被方法1和方法2遗漏的复杂格式
    try:
        # 尝试找到包含 coordinate 的 JSON 对象（支持嵌套，双引号）
        json_pattern1 = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*"coordinate"\s*:\s*\[(\d+)\s*,\s*(\d+)\][^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.finditer(json_pattern1, response_text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            json_str = match.group(0)
            try:
                data = json.loads(json_str)
                if 'coordinate' in data and isinstance(data['coordinate'], list) and len(data['coordinate']) == 2:
                    x, y = int(data['coordinate'][0]), int(data['coordinate'][1])
                    coord_key = (x, y)
                    if coord_key not in seen_coords:
                        coordinates.append([x, y])
                        seen_coords.add(coord_key)
            except json.JSONDecodeError:
                # 如果 JSON 解析失败，直接使用正则提取的坐标
                x, y = int(match.group(1)), int(match.group(2))
                coord_key = (x, y)
                if coord_key not in seen_coords:
                    coordinates.append([x, y])
                    seen_coords.add(coord_key)
        
        # 尝试找到包含 coordinate 的 Python 字典对象（单引号）
        # 注意：对于单引号格式，我们直接提取坐标，不尝试解析
        json_pattern2 = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*'coordinate'\s*:\s*\[(\d+)\s*,\s*(\d+)\][^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        matches = re.finditer(json_pattern2, response_text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            # 直接使用正则提取的坐标（因为单引号不是有效的JSON）
            x, y = int(match.group(1)), int(match.group(2))
            coord_key = (x, y)
            if coord_key not in seen_coords:
                coordinates.append([x, y])
                seen_coords.add(coord_key)
    except Exception:
        pass
    
    return coordinates


def draw_coordinates(img, coordinates, base_image_width=None, base_image_height=None):
    """在图片上绘制坐标标记
    
    Args:
        img: PIL Image 对象
        coordinates: 坐标列表，每个元素为 [x, y]
        base_image_width: 基础图片的宽度（如果坐标是相对于基础图片的）
        base_image_height: 基础图片的高度（如果坐标是相对于基础图片的）
    """
    if not coordinates:
        return
    
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size
    
    for idx, coord in enumerate(coordinates):
        x, y = coord[0], coord[1]
        
        # 如果提供了基础图片尺寸，坐标应该是相对于基础图片的
        # 否则假设坐标是相对于整个图片的
        if base_image_width is not None and base_image_height is not None:
            # 确保坐标在基础图片范围内
            if x < 0 or x >= base_image_width or y < 0 or y >= base_image_height:
                print(f"警告：坐标 [{x}, {y}] 超出基础图片范围 [{base_image_width}, {base_image_height}]")
                continue
        
        # 确保坐标在图片范围内
        if x < 0 or x >= img_width or y < 0 or y >= img_height:
            print(f"警告：坐标 [{x}, {y}] 超出图片范围 [{img_width}, {img_height}]")
            continue
        
        # 绘制坐标标记：红色圆圈 + 十字线
        marker_radius = 15
        line_length = 30
        
        # 绘制十字线（红色，较粗）
        draw.line([(x - line_length, y), (x + line_length, y)], fill='red', width=3)
        draw.line([(x, y - line_length), (x, y + line_length)], fill='red', width=3)
        
        # 绘制外圈（红色，较粗）
        draw.ellipse([x - marker_radius, y - marker_radius, x + marker_radius, y + marker_radius],
                     outline='red', width=3)
        
        # 绘制内圈（白色填充）
        draw.ellipse([x - marker_radius + 2, y - marker_radius + 2, x + marker_radius - 2, y + marker_radius - 2],
                     fill='red', outline='red')
        
        # 绘制坐标文本（在标记旁边）
        coord_text = f"({x}, {y})"
        try:
            # 尝试使用较小字体
            font = ImageFont.load_default()
            text_bbox = font.getbbox(coord_text)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # 文本位置：在标记右下方
            text_x = x + marker_radius + 5
            text_y = y + marker_radius + 5
            
            # 如果文本超出图片边界，调整位置
            if text_x + text_width > img_width:
                text_x = x - text_width - marker_radius - 5
            if text_y + text_height > img_height:
                text_y = y - text_height - marker_radius - 5
            
            # 绘制文本背景（白色半透明）
            bg_padding = 2
            draw.rectangle([text_x - bg_padding, text_y - bg_padding,
                           text_x + text_width + bg_padding, text_y + text_height + bg_padding],
                          fill='white', outline='red', width=1)
            
            # 绘制文本
            draw.text((text_x, text_y), coord_text, fill='red', font=font)
        except Exception as e:
            print(f"警告：无法绘制坐标文本: {e}")


def visualize_response(response_text, output_path, font_path, step_id=None, base_image=None):
    """将response文本渲染到图片上
    
    Args:
        response_text: 要渲染的文本内容
        output_path: 输出图片路径
        font_path: 字体文件路径
        step_id: 步骤ID（可选）
        base_image: 基础图片（如果提供，文字会叠加在这张图片上）
    """
    # 字体设置
    font_size = 24
    title_font_size = 32
    line_spacing = 10
    padding = 40
    
    try:
        title_font = ImageFont.truetype(font_path, title_font_size)
        body_font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"警告：无法加载字体文件 {font_path}，使用默认字体: {e}")
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    
    # 解析response文本
    sections = {}
    current_section = None
    current_content = []
    
    lines = response_text.split('\n')
    
    for line in lines:
        if line.startswith('### ') and line.endswith(' ###'):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line.replace('###', '').strip()
            current_content = []
        else:
            if current_section:
                current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # 如果没有解析到sections，直接使用原始文本
    if not sections:
        sections = {'Response': response_text}
    
    # 提取坐标信息
    coordinates = extract_coordinates(response_text)
    if coordinates:
        print(f"检测到 {len(coordinates)} 个坐标点: {coordinates}")
    
    # 计算所需文字区域尺寸
    max_width = 1200
    temp_img = Image.new('RGB', (max_width, 100))
    temp_draw = ImageDraw.Draw(temp_img)
    
    text_height = padding
    
    # 添加标题（如果有step_id）
    if step_id is not None:
        title_height = title_font.getbbox(f"Step {step_id}")[3] - title_font.getbbox(f"Step {step_id}")[1]
        text_height += title_height + line_spacing * 2
    
    # 计算每个section的高度
    for section_name, section_content in sections.items():
        # 标题高度
        section_title_height = title_font.getbbox(section_name)[3] - title_font.getbbox(section_name)[1]
        text_height += section_title_height + line_spacing
        
        # 内容高度
        content_lines = wrap_text(section_content, body_font, max_width - padding * 2)
        for line in content_lines:
            if line:
                line_height = body_font.getbbox(line)[3] - body_font.getbbox(line)[1]
            else:
                line_height = font_size * 0.5
            text_height += line_height + line_spacing
        
        text_height += padding
    
    text_height += padding
    
    # 如果有基础图片，使用它作为背景；否则创建新图片
    if base_image is not None:
        # 转换基础图片为RGB模式（如果必要）
        if base_image.mode != 'RGB':
            base_image = base_image.convert('RGB')
        img = base_image.copy()
        img_width, img_height_orig = img.size
        
        # 如果文字区域需要更多空间，扩展图片
        if text_height > img_height_orig:
            # 创建扩展后的图片
            new_img = Image.new('RGB', (img_width, int(img_height_orig + text_height)), color='white')
            new_img.paste(img, (0, 0))
            img = new_img
            img_height = img_height_orig + int(text_height)
            text_start_y = img_height_orig  # 文字从原图底部开始
        else:
            img_height = img_height_orig
            text_start_y = 0  # 文字从顶部开始（覆盖在图片上）
    else:
        # 创建新图片
        img_width = max_width
        img_height = int(text_height)
        img = Image.new('RGB', (img_width, img_height), color='white')
        text_start_y = 0
    
    draw = ImageDraw.Draw(img)
    
    # 如果有基础图片且文字要覆盖在图片上，绘制半透明背景框让文字更清晰
    if base_image is not None and text_start_y == 0:
        overlay_height = min(int(text_height), img_height)
        overlay = Image.new('RGBA', (img_width, overlay_height), (255, 255, 255, 200))
        img.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(img)
    
    # 绘制坐标标记（如果有坐标且存在基础图片）
    # 注意：坐标标记应该在最后绘制，这样它们会显示在最上层，不会被半透明背景遮挡
    if coordinates and base_image is not None:
        # 坐标是相对于基础图片的，所以传递基础图片的尺寸
        base_img_width, base_img_height = base_image.size
        # 在基础图片区域绘制坐标标记
        draw_coordinates(img, coordinates, base_img_width, base_img_height)
    elif coordinates:
        # 如果没有基础图片但有坐标，也在图片上绘制（假设坐标是相对于图片的）
        draw_coordinates(img, coordinates)
    
    # 绘制内容
    y_position = text_start_y + padding
    
    # 绘制标题
    if step_id is not None:
        title_text = f"Step {step_id}"
        draw.text((padding, y_position), title_text, fill='black', font=title_font)
        y_position += title_font.getbbox(title_text)[3] - title_font.getbbox(title_text)[1] + line_spacing * 2
    
    # 绘制各个section
    for section_name, section_content in sections.items():
        # 绘制section标题
        section_title = f"### {section_name} ###"
        draw.text((padding, y_position), section_title, fill='blue', font=title_font)
        y_position += title_font.getbbox(section_title)[3] - title_font.getbbox(section_title)[1] + line_spacing
        
        # 绘制section内容
        content_lines = wrap_text(section_content, body_font, max_width - padding * 2)
        for line in content_lines:
            if line:
                draw.text((padding * 2, y_position), line, fill='black', font=body_font)
                line_height = body_font.getbbox(line)[3] - body_font.getbbox(line)[1]
            else:
                line_height = font_size * 0.5
            y_position += int(line_height) + line_spacing
        
        y_position += padding
    
    # 保存图片
    img.save(output_path, 'PNG')
    print(f"已保存图片: {output_path}")


def find_directory(search_path):
    """查找目录，支持模糊匹配"""
    path = Path(search_path)
    
    # 如果直接存在，直接返回
    if path.exists() and path.is_dir():
        return path
    
    # 尝试在当前工作目录下查找
    current_dir = Path.cwd()
    possible_path = current_dir / search_path
    if possible_path.exists() and possible_path.is_dir():
        return possible_path
    
    # 如果是相对路径且包含logs，尝试在logs目录下查找
    if 'logs' in str(search_path) or search_path.startswith('logs'):
        logs_dir = current_dir / 'logs'
        if logs_dir.exists():
            # 提取目录名部分
            dir_name = Path(search_path).name if '/' in str(search_path) or '\\' in str(search_path) else search_path
            # 尝试查找匹配的目录
            for subdir in logs_dir.iterdir():
                if subdir.is_dir() and (dir_name in subdir.name or subdir.name.startswith(dir_name.split('_')[0])):
                    return subdir
    
    # 最后尝试：如果路径是文件名的一部分，在当前目录及其子目录中搜索
    if not path.exists():
        search_name = Path(search_path).name
        # 在logs目录中搜索
        logs_dir = current_dir / 'logs'
        if logs_dir.exists():
            for subdir in logs_dir.iterdir():
                if subdir.is_dir() and search_name in subdir.name:
                    return subdir
    
    return None


def is_already_processed(directory_path):
    """检查目录是否已经处理过
    
    Args:
        directory_path: 要检查的目录路径
    
    Returns:
        bool: 如果已处理则返回True，否则返回False
    """
    visualized_dir = directory_path / 'visualized_responses'
    if not visualized_dir.exists():
        return False
    
    # 检查是否有生成的图片
    png_files = list(visualized_dir.glob('step_*_response.png'))
    return len(png_files) > 0


def process_directory(directory_path, output_dir=None, font_path=None, skip_processed=True):
    """处理目录下所有的operator.json文件
    
    Args:
        directory_path: 要处理的目录路径
        output_dir: 输出目录路径，如果为None则使用默认路径（目录下的visualized_responses子目录）
        font_path: 字体文件路径，如果为None则自动查找
        skip_processed: 是否跳过已处理的目录
    
    Returns:
        bool: 成功返回True，失败返回False
    """
    directory = find_directory(directory_path)
    
    if directory is None:
        print(f"错误：找不到目录: {directory_path}")
        print(f"当前工作目录: {Path.cwd()}")
        print("\n提示：")
        print("1. 请使用绝对路径")
        print("2. 或者使用相对路径，如 'logs/20251103_100240_...'")
        print("3. 或者只输入目录名的一部分进行匹配")
        return False
    
    # 检查是否已经处理过
    if skip_processed and is_already_processed(directory):
        print(f"跳过已处理的目录: {directory.name}")
        return True
    
    print(f"处理目录: {directory.absolute()}")
    
    # 查找字体文件
    if font_path is None:
        font_path = Path(__file__).parent / 'Arial-Unicode-MS.ttf'
        if not font_path.exists():
            print(f"警告：字体文件不存在: {font_path}")
            print("将在当前目录和上级目录中查找...")
            # 尝试在当前目录查找
            possible_fonts = [
                directory / 'Arial-Unicode-MS.ttf',
                Path(__file__).parent.parent / 'Arial-Unicode-MS.ttf',
                Path.cwd() / 'Arial-Unicode-MS.ttf',
            ]
            for pf in possible_fonts:
                if pf.exists():
                    font_path = pf
                    break
            else:
                print("错误：找不到字体文件 Arial-Unicode-MS.ttf")
                return False
    else:
        font_path = Path(font_path)
        if not font_path.exists():
            print(f"错误：指定的字体文件不存在: {font_path}")
            return False
    
    print(f"使用字体文件: {font_path.absolute()}")
    
    # 创建输出目录
    if output_dir is None:
        output_dir = directory / 'visualized_responses'
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"输出目录: {output_dir.absolute()}")
    
    # 查找所有step目录
    step_dirs = sorted([d for d in directory.iterdir() if d.is_dir() and d.name.startswith('step_')],
                       key=lambda x: int(x.name.split('_')[1]) if x.name.split('_')[1].isdigit() else 999)
    
    if not step_dirs:
        print(f"警告：在 {directory} 中没有找到 step_ 开头的子目录")
        return False
    
    processed_count = 0
    
    for step_dir in step_dirs:
        operator_json = step_dir / 'operator.json'
        
        if not operator_json.exists():
            print(f"跳过：{operator_json} 不存在")
            continue
        
        try:
            with open(operator_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            response_text = data.get('response', '')
            step_id = data.get('step_id', None)
            
            if not response_text:
                print(f"警告：{operator_json} 中没有response字段")
                continue
            
            # 从messages中提取base64图片
            base_image = None
            if 'messages' in data and isinstance(data['messages'], list):
                for message in data['messages']:
                    if message.get('role') == 'user' and 'content' in message:
                        content = message['content']
                        if isinstance(content, list):
                            for item in content:
                                if item.get('type') == 'image_url' and 'image_url' in item:
                                    image_url = item['image_url'].get('url', '')
                                    if image_url:
                                        base_image = decode_base64_image(image_url)
                                        if base_image:
                                            print(f"已从 {operator_json.name} 中提取基础图片")
                                            break
                        if base_image:
                            break
            
            # 生成输出文件名
            step_num = step_dir.name.split('_')[1] if '_' in step_dir.name else 'unknown'
            output_filename = f"step_{step_num}_response.png"
            output_path = output_dir / output_filename
            
            # 可视化
            visualize_response(response_text, output_path, str(font_path), step_id, base_image)
            processed_count += 1
            
        except Exception as e:
            print(f"处理 {operator_json} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n完成！共处理 {processed_count} 个文件")
    print(f"所有结果图片已保存到: {output_dir.absolute()}")
    return True


def process_batch_directories(parent_dir, font_path=None, skip_processed=True):
    """批量处理父目录下的所有子目录
    
    Args:
        parent_dir: 父目录路径（例如 logs 目录）
        font_path: 字体文件路径，如果为None则自动查找
        skip_processed: 是否跳过已处理的目录
    """
    parent_path = Path(parent_dir)
    
    if not parent_path.exists():
        print(f"错误：父目录不存在: {parent_dir}")
        return
    
    if not parent_path.is_dir():
        print(f"错误：指定的路径不是目录: {parent_dir}")
        return
    
    print(f"开始批量处理目录: {parent_path.absolute()}")
    print(f"跳过已处理: {'是' if skip_processed else '否'}")
    print("=" * 80)
    
    # 获取所有子目录（按名称排序）
    subdirs = sorted([d for d in parent_path.iterdir() if d.is_dir()])
    
    if not subdirs:
        print(f"警告：在 {parent_path} 中没有找到子目录")
        return
    
    print(f"找到 {len(subdirs)} 个子目录\n")
    
    total_count = len(subdirs)
    success_count = 0
    skipped_count = 0
    failed_count = 0
    
    for idx, subdir in enumerate(subdirs, 1):
        print(f"\n[{idx}/{total_count}] 处理: {subdir.name}")
        print("-" * 80)
        
        # 检查是否包含 step_ 子目录（快速判断是否为有效的任务目录）
        has_step_dirs = any(d.is_dir() and d.name.startswith('step_') for d in subdir.iterdir())
        
        if not has_step_dirs:
            print(f"跳过：目录中没有 step_ 子目录")
            skipped_count += 1
            continue
        
        # 处理目录
        result = process_directory(subdir, None, font_path, skip_processed)
        
        if result:
            if skip_processed and is_already_processed(subdir):
                # 如果是因为已处理而成功，计入跳过数
                if not any(d.is_dir() and d.name.startswith('step_') for d in subdir.iterdir()):
                    skipped_count += 1
                else:
                    success_count += 1
            else:
                success_count += 1
        else:
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("批量处理完成！")
    print(f"总计: {total_count} 个目录")
    print(f"成功: {success_count} 个")
    print(f"跳过: {skipped_count} 个")
    print(f"失败: {failed_count} 个")
    print("=" * 80)


if __name__ == '__main__':
    # 设置UTF-8编码以支持中文输出
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description='将 operator.json 中的 response 内容可视化渲染到图片上',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单个目录处理
  python visualize_operator.py "logs/20251103_100240_帮我整理所有与'黄金"
  python visualize_operator.py "logs/20251103_100240_帮我整理所有与'黄金" --output "output_images"
  python visualize_operator.py "logs/20251103_100240_帮我整理所有与'黄金" --font "fonts/Arial-Unicode-MS.ttf"
  
  # 批量处理 logs 目录下所有子目录
  python visualize_operator.py logs --batch
  python visualize_operator.py "D:/path/to/logs" --batch
  python visualize_operator.py logs --batch --no-skip
  
结果图片默认保存在: <输入目录>/visualized_responses/
        """
    )
    
    parser.add_argument(
        'directory',
        type=str,
        help='要处理的目录路径（包含step_X子目录的目录，或使用 --batch 模式时为父目录）'
    )
    
    parser.add_argument(
        '-b', '--batch',
        action='store_true',
        help='批量处理模式：处理指定目录下的所有子目录'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='输出目录路径（默认：<输入目录>/visualized_responses/，批量模式下不可用）'
    )
    
    parser.add_argument(
        '-f', '--font',
        type=str,
        default=None,
        help='字体文件路径（默认：自动查找工程目录下的Arial-Unicode-MS.ttf）'
    )
    
    parser.add_argument(
        '--no-skip',
        action='store_true',
        help='不跳过已处理的目录（默认会跳过已有 visualized_responses 的目录）'
    )
    
    args = parser.parse_args()
    
    # 根据模式处理
    if args.batch:
        # 批量处理模式
        if args.output:
            print("警告：批量模式下不支持 --output 参数，将忽略")
        
        skip_processed = not args.no_skip
        process_batch_directories(args.directory, args.font, skip_processed)
    else:
        # 单个目录处理模式
        skip_processed = not args.no_skip
        process_directory(args.directory, args.output, args.font, skip_processed)

