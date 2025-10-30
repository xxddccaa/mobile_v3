# encoding=utf-8
"""
Mobile Agent API 简单测试脚本
直接调用 API 接口执行任务
"""
import requests
import json
import time


def execute_mobile_agent_task():
    """执行 Mobile Agent 任务"""
    
    print("="*80)
    print("Mobile Agent API 测试")
    print("="*80)
    print("\n正在调用 API 接口...")
    
    # API 地址
    url = "http://localhost:8003/mobile_agent/execute"
    
    # 请求参数（完整参数）
    data = {
        "adb_path": r"D:\platform-tools\adb.exe",
        "api_key": "123",
        "base_url": "http://10.142.18.204:8006/v1",
        "model": "owl32b",
        "instruction": "帮我整理所有与李荣浩相关的微博动态",
        "add_info": "整理某东西的微博动态的操作：1. 微博应用图标不在可见范围内, 使用 open_app 微博 动作直接打开微博应用（无需滑动），2. 点击发现按钮。 3. 输入搜索词，但不要打开智搜开关。 4. 点击搜索按钮。 5. 在搜索结果里再去点击智搜按钮，进入到智搜的结果页面。 6. 点击左下角的 继续问智搜。 7. 点击右下方的'向下箭头'的按钮。 8. 点击复制按钮，点击复制按钮的动作描述要写成 点击复制按钮，点击后就不需要任何操作了，退出agent。",
        "timeout": 600,
        "requestId": f"test-{int(time.time())}"
    }
    
    print(f"\n请求参数:")
    print(f"  - API 地址: {url}")
    print(f"  - 任务指令: {data['instruction']}")
    print(f"  - 模型: {data['model']}")
    print(f"  - 超时: {data['timeout']} 秒")
    print(f"  - RequestId: {data['requestId']}")
    
    try:
        print("\n开始执行任务，请稍候...")
        print("-"*80)
        
        start_time = time.time()
        
        # 发送 POST 请求
        response = requests.post(url, json=data, timeout=700)
        
        elapsed_time = time.time() - start_time
        
        print(f"\n任务执行完成！")
        print(f"耗时: {elapsed_time:.2f} 秒")
        print(f"HTTP 状态码: {response.status_code}")
        print("-"*80)
        
        # 解析响应
        result = response.json()
        
        print(f"\nAPI 响应:")
        print(f"  - 响应码: {result.get('code')}")
        print(f"  - 消息: {result.get('message')}")
        print(f"  - 执行时间: {result.get('execution_time', 0):.2f} 秒")
        
        # 检查是否成功
        if result.get('code') == 200:
            print("\n✓ 任务执行成功！")
            
            # 获取粘贴板内容与精简内容
            data_field = result.get('data', {})
            clipboard_content = data_field.get('clipboard_content')
            clipboard_summary = data_field.get('clipboard_summary')
            
            if clipboard_content:
                print(f"\n✓ 成功获取粘贴板内容")
                print(f"  - 内容长度: {len(clipboard_content)} 字符")
                
                # 保存到文件
                output_file = f"result_{data['requestId']}.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(clipboard_content)
                print(f"  - 已保存到: {output_file}")
                
                # 显示完整内容
                print("\n" + "="*80)
                print("粘贴板内容:")
                print("="*80)
                print(clipboard_content)
                print("="*80)
            
                # 显示精简内容（如果有）
                if clipboard_summary:
                    print("\n" + "="*80)
                    print("精简后内容:")
                    print("="*80)
                    print(clipboard_summary)
                    print("="*80)
                else:
                    print("\n⚠ 未返回精简内容 (clipboard_summary 为空)")
                
                return True
            else:
                print("\n⚠ 警告: 未获取到粘贴板内容")
                print(f"任务已完成，但没有复制内容")
                return False
        else:
            print(f"\n✗ 任务执行失败")
            print(f"错误信息: {result.get('detail')}")
            print(f"\n完整响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n✗ 请求超时（超过 700 秒）")
        return False
        
    except requests.exceptions.ConnectionError:
        print(f"\n✗ 连接失败")
        print("请确保 API 服务器已启动（运行: python api_server.py）")
        return False
        
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n提示：")
    print("  1. 请确保 API 服务已启动（python api_server.py）")
    print("  2. 请确保手机已通过 ADB 连接")
    print("  3. 任务执行可能需要几分钟，请耐心等待\n")
    
    # input("按 Enter 键开始执行任务...")
    
    success = execute_mobile_agent_task()
    
    if success:
        print("\n" + "="*80)
        print("✓ 测试成功完成！")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("✗ 测试失败")
        print("="*80)