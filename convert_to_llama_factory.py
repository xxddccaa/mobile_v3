#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 Mobile Agent 日志转换为 Llama Factory 训练格式
支持多模态数据（图片+文本）
"""

import json
import base64
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
from io import BytesIO


def extract_base64_from_url(image_url: str) -> str:
    """从 data:image/png;base64,... 格式中提取纯 base64 字符串"""
    if image_url.startswith('data:image'):
        _, data = image_url.split(',', 1)
        return data
    return image_url


def extract_text_from_content(content: List[Dict]) -> str:
    """从 content 列表中提取文本内容"""
    texts = []
    for item in content:
        if item.get('type') == 'text':
            texts.append(item.get('text', ''))
    return '\n'.join(texts)


def extract_images_from_content(content: List[Dict]) -> List[str]:
    """从 content 列表中提取图片（base64）"""
    images = []
    for item in content:
        if item.get('type') == 'image_url':
            image_url = item.get('image_url', {}).get('url', '')
            if image_url:
                base64_str = extract_base64_from_url(image_url)
                images.append(base64_str)
    return images


def convert_to_alpaca_format(
    messages: List[Dict],
    response: str,
    step_id: Optional[int] = None,
    log_dir: str = "",
    step_name: str = ""
) -> Dict[str, Any]:
    """转换为 Alpaca 格式
    
    Alpaca 格式：
    {
        "instruction": "...",
        "input": "...",  # 可选
        "output": "...",
        "images": ["base64_string"]  # 可选，多模态，统一使用列表格式
    }
    """
    if not messages:
        return None
    
    # 提取用户输入和图片
    user_message = None
    images = []
    
    for msg in messages:
        if msg.get('role') == 'user':
            user_message = msg
            content = msg.get('content', [])
            if isinstance(content, list):
                images = extract_images_from_content(content)
            break
    
    if not user_message:
        return None
    
    # 构建 instruction（用户输入文本）
    content = user_message.get('content', [])
    if isinstance(content, list):
        instruction = extract_text_from_content(content)
    else:
        instruction = str(content)
    
    # 构建样本
    sample = {
        "instruction": instruction,
        "output": response
    }
    
    # 如果有图片，添加图片字段（统一使用列表格式）
    if images:
        sample["images"] = images
    
    # 添加元数据（可选）
    if step_id is not None:
        sample["id"] = f"{log_dir}_{step_name}_step{step_id}"
    
    return sample


def convert_to_sharegpt_format(
    messages: List[Dict],
    response: str,
    step_id: Optional[int] = None,
    log_dir: str = "",
    step_name: str = ""
) -> Dict[str, Any]:
    """转换为 ShareGPT 格式
    
    ShareGPT 格式：
    {
        "conversations": [
            {"from": "human", "value": "text<image><image>..."},
            {"from": "gpt", "value": "..."}
        ]
    }
    
    注意：对于多模态模型，图片需要用 <image> 标记表示，图片在文本后面
    """
    if not messages:
        return None
    
    conversations = []
    images = []
    
    # 处理用户消息
    for msg in messages:
        if msg.get('role') == 'user':
            content = msg.get('content', [])
            if isinstance(content, list):
                # 提取文本和图片
                text_parts = []
                for item in content:
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif item.get('type') == 'image_url':
                        image_url = item.get('image_url', {}).get('url', '')
                        if image_url:
                            base64_str = extract_base64_from_url(image_url)
                            images.append(base64_str)
                            # 添加 <image> 标记（图片在文本后面）
                            text_parts.append('<image>')
                
                # 合并文本和图片标记
                if text_parts:
                    value = ''.join(text_parts)
                    conversations.append({
                        "from": "human",
                        "value": value
                    })
            else:
                conversations.append({
                    "from": "human",
                    "value": str(content)
                })
            break
    
    # 添加助手回复
    if response:
        conversations.append({
            "from": "gpt",
            "value": response
        })
    
    if not conversations:
        return None
    
    sample = {
        "conversations": conversations
    }
    
    # 如果有图片，添加图片字段（统一使用列表格式）
    if images:
        sample["images"] = images
    
    # 添加元数据（可选）
    if step_id is not None:
        sample["id"] = f"{log_dir}_{step_name}_step{step_id}"
    
    return sample


def process_json_file(
    json_file: Path,
    format_type: str,
    log_dir: str = "",
    step_name: str = ""
) -> Optional[Dict[str, Any]]:
    """处理单个 JSON 文件"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = data.get('messages', [])
        response = data.get('response', '')
        step_id = data.get('step_id', None)
        
        if not messages or not response:
            return None
        
        # 根据格式类型转换
        if format_type == 'alpaca':
            return convert_to_alpaca_format(
                messages, response, step_id, log_dir, step_name
            )
        elif format_type == 'sharegpt':
            return convert_to_sharegpt_format(
                messages, response, step_id, log_dir, step_name
            )
        else:
            raise ValueError(f"Unknown format type: {format_type}")
            
    except Exception as e:
        print(f"Error processing {json_file}: {e}")
        return None


def extract_samples_from_log_dir(
    log_dir: Path,
    format_type: str,
    agent_types: List[str] = ['manager', 'operator', 'reflector']
) -> List[Dict[str, Any]]:
    """从单个日志目录中提取样本"""
    samples = []
    log_dir_name = log_dir.name
    
    # 查找所有 step 目录
    step_dirs = sorted(
        [d for d in log_dir.iterdir() if d.is_dir() and d.name.startswith('step_')],
        key=lambda x: int(x.name.split('_')[1]) if x.name.split('_')[1].isdigit() else 999
    )
    
    for step_dir in step_dirs:
        step_name = step_dir.name
        
        # 处理不同类型的 agent
        for agent_type in agent_types:
            json_file = step_dir / f"{agent_type}.json"
            if json_file.exists():
                sample = process_json_file(
                    json_file, format_type, log_dir_name, step_name
                )
                if sample:
                    # 添加 agent_type 标识
                    sample['agent_type'] = agent_type
                    samples.append(sample)
    
    return samples


def convert_logs_to_llama_factory(
    logs_dir: str,
    output_dir: str,
    format_type: str = 'alpaca',
    agent_types: List[str] = None,
    separate_by_agent: bool = False
):
    """将日志目录转换为 Llama Factory 格式
    
    Args:
        logs_dir: 日志根目录
        output_dir: 输出目录
        format_type: 格式类型，'alpaca' 或 'sharegpt'
        agent_types: 要处理的 agent 类型列表，默认 ['manager', 'operator', 'reflector']
        separate_by_agent: 是否按 agent 类型分别保存文件
    """
    logs_path = Path(logs_dir)
    output_path = Path(output_dir)
    
    if not logs_path.exists():
        print(f"错误：日志目录不存在: {logs_dir}")
        return
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    if agent_types is None:
        agent_types = ['manager', 'operator', 'reflector']
    
    # 获取所有日志目录
    log_dirs = [d for d in logs_path.iterdir() if d.is_dir()]
    
    print(f"找到 {len(log_dirs)} 个日志目录")
    print(f"格式类型: {format_type}")
    print(f"Agent 类型: {agent_types}")
    
    all_samples = []
    samples_by_agent = {agent: [] for agent in agent_types}
    
    # 处理每个日志目录
    for log_dir in log_dirs:
        print(f"处理: {log_dir.name}")
        samples = extract_samples_from_log_dir(log_dir, format_type, agent_types)
        
        all_samples.extend(samples)
        
        # 按 agent 类型分组
        for sample in samples:
            agent_type = sample.get('agent_type', 'unknown')
            if agent_type in samples_by_agent:
                samples_by_agent[agent_type].append(sample)
    
    # 保存结果
    if separate_by_agent:
        # 按 agent 类型分别保存
        for agent_type, samples in samples_by_agent.items():
            if samples:
                output_file = output_path / f"{agent_type}_{format_type}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(samples, f, ensure_ascii=False, indent=2)
                print(f"保存 {len(samples)} 个 {agent_type} 样本到 {output_file}")
    else:
        # 保存所有样本到一个文件
        output_file = output_path / f"all_{format_type}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_samples, f, ensure_ascii=False, indent=2)
        print(f"保存 {len(all_samples)} 个样本到 {output_file}")
        
        # 也保存统计信息
        stats = {
            "total_samples": len(all_samples),
            "samples_by_agent": {
                agent: len(samples) for agent, samples in samples_by_agent.items()
            },
            "format_type": format_type
        }
        
        stats_file = output_path / "statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"统计信息保存到 {stats_file}")
    
    print(f"\n完成！输出目录: {output_path.absolute()}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='将 Mobile Agent 日志转换为 Llama Factory 训练格式'
    )
    
    parser.add_argument(
        '--logs_dir',
        type=str,
        default='logs',
        help='日志目录路径（默认: logs）'
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        default='llama_factory_data',
        help='输出目录路径（默认: llama_factory_data）'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['alpaca', 'sharegpt'],
        default='alpaca',
        help='输出格式类型：alpaca 或 sharegpt（默认: alpaca）'
    )
    
    parser.add_argument(
        '--agents',
        type=str,
        nargs='+',
        choices=['manager', 'operator', 'reflector'],
        default=['manager', 'operator', 'reflector'],
        help='要处理的 agent 类型（默认: 全部）'
    )
    
    parser.add_argument(
        '--separate',
        action='store_true',
        help='按 agent 类型分别保存文件'
    )
    
    args = parser.parse_args()
    
    convert_logs_to_llama_factory(
        logs_dir=args.logs_dir,
        output_dir=args.output_dir,
        format_type=args.format,
        agent_types=args.agents,
        separate_by_agent=args.separate
    )

