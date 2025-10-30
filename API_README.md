# Mobile Agent v3 FastAPI 接口使用说明

## 项目简介

本项目提供了一个 FastAPI 接口，用于执行 Mobile Agent v3 的自动化任务，并返回执行结果（特别是粘贴板内容）。

## 安装依赖

### 方式一：使用 pip

```bash
pip install -r requirements.txt
```

### 方式二：使用 uv（推荐）

```bash
uv pip install -r requirements.txt
```

## 启动服务

### 方式一：直接启动

```bash
python api_server.py
```

服务将在 `http://0.0.0.0:8000` 启动

### 方式二：使用 uvicorn 启动（推荐用于生产环境）

```bash
# 开发模式（自动重载）
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

# 生产模式（多进程）
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 端点

### 1. 执行任务接口

**POST** `/mobile_agent/execute`

执行 Mobile Agent 自动化任务，并返回粘贴板内容。

#### 请求参数

```json
{
  "adb_path": "D:\\platform-tools\\adb.exe",  // ADB 工具路径（可选，有默认值）
  "api_key": "123",                           // API 密钥（可选，有默认值）
  "base_url": "http://10.142.18.204:8006/v1", // API 基础 URL（可选，有默认值）
  "model": "owl32b",                          // 模型名称（可选，有默认值）
  "instruction": "帮我整理所有与李荣浩相关的微博动态",  // 任务指令（必填）
  "add_info": "整理某东西的微博动态的操作：...",        // 附加信息（可选，有默认值）
  "timeout": 600,                             // 超时时间（秒，可选，默认 600）
  "requestId": "req-20250101-001"             // 请求 ID（可选）
}
```

#### 响应示例

**成功响应（200）：**

```json
{
  "code": 200,
  "message": "success",
  "error_code": 200,
  "detail": "success",
  "data": {
    "clipboard_content": "以下是关于歌手李荣浩的最新动态及相关信息整理：\n🔥 近期热点事件\n...",
    "has_clipboard": true,
    "stdout_preview": "...",
    "task_completed": true,
    "timestamp": "2025-10-30T16:51:43.123456"
  },
  "requestId": "req-20250101-001",
  "execution_time": 45.67
}
```

**错误响应（500）：**

```json
{
  "code": 500,
  "message": "发生了错误：执行任务失败",
  "error_code": 500,
  "detail": "发生了错误：返回码: 1, stderr: ...",
  "data": null
}
```

**超时响应（504）：**

```json
{
  "code": 504,
  "message": "发生了错误：任务执行超时",
  "error_code": 504,
  "detail": "发生了错误：任务执行超时（600秒）",
  "data": null
}
```

### 2. 健康检查接口

**GET** `/health`

检查服务是否正常运行。

#### 响应示例

```json
{
  "status": "healthy",
  "service": "Mobile Agent v3 API",
  "timestamp": "2025-10-30T16:51:43.123456"
}
```

### 3. API 信息接口

**GET** `/`

获取 API 基本信息和可用端点。

## 使用示例

### Python 请求示例

```python
import requests
import json

# API 地址
api_url = "http://localhost:8000/mobile_agent/execute"

# 请求数据（使用最简参数，其他使用默认值）
data = {
    "instruction": "帮我整理所有与李荣浩相关的微博动态",
    "requestId": "test-001"
}

# 发送请求
response = requests.post(api_url, json=data, timeout=700)

# 解析响应
result = response.json()

if result["code"] == 200:
    clipboard_content = result["data"]["clipboard_content"]
    print("任务执行成功！")
    print("粘贴板内容：")
    print(clipboard_content)
else:
    print(f"任务执行失败：{result['message']}")
```

### cURL 请求示例

```bash
curl -X POST "http://localhost:8000/mobile_agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "帮我整理所有与李荣浩相关的微博动态",
    "requestId": "test-001"
  }'
```

### JavaScript 请求示例

```javascript
const apiUrl = "http://localhost:8000/mobile_agent/execute";

const data = {
  instruction: "帮我整理所有与李荣浩相关的微博动态",
  requestId: "test-001"
};

fetch(apiUrl, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(result => {
    if (result.code === 200) {
      console.log("任务执行成功！");
      console.log("粘贴板内容：", result.data.clipboard_content);
    } else {
      console.error("任务执行失败：", result.message);
    }
  })
  .catch(error => {
    console.error("请求失败：", error);
  });
```

## API 文档

启动服务后，可以通过以下地址访问自动生成的 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 注意事项

1. **ADB 连接**：确保手机已通过 ADB 连接到电脑，并且 USB 调试已开启
2. **超时设置**：根据任务复杂度合理设置 timeout 参数，建议至少 300 秒
3. **并发限制**：由于涉及物理设备操作，建议避免并发请求，一次只执行一个任务
4. **日志查看**：任务执行日志保存在 `logs/` 目录下，按时间戳和任务指令命名
5. **错误处理**：如果任务失败，查看返回的 `detail` 字段获取详细错误信息

## 默认参数说明

以下参数都有默认值，可以根据实际情况修改：

| 参数名 | 默认值 | 说明 |
|--------|--------|------|
| adb_path | `D:\platform-tools\adb.exe` | ADB 工具路径 |
| api_key | `123` | LLM API 密钥 |
| base_url | `http://10.142.18.204:8006/v1` | LLM API 基础 URL |
| model | `owl32b` | 使用的模型名称 |
| add_info | 默认微博操作步骤 | 任务执行的附加信息 |
| timeout | 600 | 任务超时时间（秒） |

## 故障排查

### 1. 任务执行超时

- 检查手机连接是否正常
- 适当增加 timeout 参数
- 查看日志文件确认卡在哪一步

### 2. 未检测到粘贴板内容

- 确认任务是否完整执行到复制步骤
- 查看 `stdout_preview` 字段检查输出
- 检查日志文件中是否有错误信息

### 3. ADB 连接失败

- 确认 adb_path 路径正确
- 运行 `adb devices` 检查设备连接
- 重新连接手机并授权 USB 调试

## 性能优化建议

1. **使用进程池**：生产环境使用多个 worker 进程
2. **异步处理**：利用 FastAPI 的异步特性处理多个请求
3. **缓存结果**：对相同指令的结果可以考虑缓存
4. **队列管理**：使用消息队列管理任务，避免设备冲突

## 联系方式

如有问题，请查看项目文档或提交 Issue。

