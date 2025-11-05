#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量运行微博搜索整理的 Python 脚本
自动遍历明星列表，对每个明星执行微博搜索操作
Usage: python run_batch_weibo_search.py
"""

import time
from run_weibo_search import run_weibo_search

# 明星列表（按类别组织）
CELEBRITIES = {
    "知名歌手/音乐人": [
        "张杰", "李宇春", 
        "张靓颖", "林俊杰", "邓紫棋", "薛之谦", "华晨宇"
    ],
    "资深演员/前辈": [
        "成龙", "刘德华", "周润发", "巩俐", "陈道明", 
        "张国立", "李雪健", "刘晓庆", "潘虹", "斯琴高娃"
    ],
    "新锐演员/新生代": [
        "王鹤棣", "白鹿", "沈月", "赵露思", "宋亚轩", 
        "刘耀文", "张凌赫", "周也", "王楚然"
    ]
}

# 配置参数（可根据需要修改）
CONFIG = {
    "adb_path": r"D:\platform-tools\adb.exe",
    "api_key": "123",
    "base_url": "http://127.0.0.1:8006/v1",
    "model": "owl32b",
    "delay_between_searches": 5  # 每次搜索之间的延迟时间（秒）
}


def run_batch_search():
    """
    批量执行微博搜索任务
    """
    # 统计信息
    total_count = sum(len(celebrities) for celebrities in CELEBRITIES.values())
    current_count = 0
    success_count = 0
    failed_list = []
    
    print("=" * 60)
    print("批量微博搜索任务开始")
    print("=" * 60)
    print(f"总共需要搜索 {total_count} 位明星")
    print(f"每次搜索间隔: {CONFIG['delay_between_searches']} 秒")
    print("=" * 60)
    print()
    
    # 遍历每个类别
    for category, celebrities in CELEBRITIES.items():
        print(f"\n{'=' * 60}")
        print(f"类别: {category}")
        print(f"共 {len(celebrities)} 位明星")
        print("=" * 60)
        
        # 遍历该类别下的每位明星
        for celebrity in celebrities:
            current_count += 1
            
            print(f"\n[{current_count}/{total_count}] 正在搜索: {celebrity}")
            print("-" * 60)
            
            try:
                # 执行微博搜索
                run_weibo_search(
                    search_keyword=celebrity,
                    adb_path=CONFIG["adb_path"],
                    api_key=CONFIG["api_key"],
                    base_url=CONFIG["base_url"],
                    model=CONFIG["model"]
                )
                
                success_count += 1
                print(f"✓ {celebrity} 搜索完成")
                
                # 如果不是最后一个，等待一段时间再进行下一次搜索
                if current_count < total_count:
                    print(f"\n等待 {CONFIG['delay_between_searches']} 秒后继续下一个...")
                    time.sleep(CONFIG['delay_between_searches'])
                    
            except KeyboardInterrupt:
                print("\n\n任务被用户中断！")
                print(f"已完成: {success_count}/{total_count}")
                if failed_list:
                    print(f"失败列表: {', '.join(failed_list)}")
                return
                
            except Exception as e:
                print(f"✗ {celebrity} 搜索失败: {e}")
                failed_list.append(celebrity)
                
                # 失败后也等待一下再继续
                if current_count < total_count:
                    print(f"等待 {CONFIG['delay_between_searches']} 秒后继续下一个...")
                    time.sleep(CONFIG['delay_between_searches'])
    
    # 打印总结
    print("\n" + "=" * 60)
    print("批量搜索任务完成！")
    print("=" * 60)
    print(f"总计: {total_count} 位明星")
    print(f"成功: {success_count} 位")
    print(f"失败: {len(failed_list)} 位")
    
    if failed_list:
        print("\n失败的明星列表:")
        for celebrity in failed_list:
            print(f"  - {celebrity}")
    
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_batch_search()
    except KeyboardInterrupt:
        print("\n\n程序被用户终止")
    except Exception as e:
        print(f"\n程序执行出错: {e}")

