#!/bin/bash
# Tools 真实验证执行脚本
# 使用方法：
# 1. 确保 .env 已配置（从 .env.example 复制并填入真实值）
# 2. chmod +x run-tools-verification.sh
# 3. ./run-tools-verification.sh

set -e

echo "=== Tools 真实验证 ==="
echo ""

# 检查 .env 是否存在
if [ ! -f .env ]; then
    echo "ERROR: .env 文件不存在"
    echo "请先运行: cp .env.example .env 并填入真实配置"
    exit 1
fi

# 检查必要的变量
source .env
if [ -z "$LC_API_KEY" ] || [ "$LC_API_KEY" = "your-api-key-here" ]; then
    echo "ERROR: LC_API_KEY 未配置或仍为默认值"
    exit 1
fi

if [ -z "$LC_BASE_URL" ] || [ "$LC_BASE_URL" = "https://api.example.com/v1" ]; then
    echo "ERROR: LC_BASE_URL 未配置或仍为默认值"
    exit 1
fi

if [ -z "$LC_MODEL" ] || [ "$LC_MODEL" = "gpt-3.5-turbo" ]; then
    echo "WARNING: LC_MODEL 使用默认值 gpt-3.5-turbo"
fi

echo "配置检查通过"
echo "Base URL: $LC_BASE_URL"
echo "Model: $LC_MODEL"
echo ""

# 激活虚拟环境
if [ ! -d ".venv" ]; then
    echo "ERROR: .venv 不存在，请先运行: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source .venv/bin/activate

# 测试 1: 默认问题（产品查询）
echo "=== 测试 1: 默认问题 ==="
echo "发送: P001 的价格是多少？"
echo ""

OUTPUT_FILE="tools-real-run-$(date +%Y%m%d-%H%M%S).json"
.venv/bin/python agent.py --output "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "✓ 测试 1 成功"
    echo "输出已保存: $OUTPUT_FILE"
    echo ""
    
    # 运行独立验证器
    echo "运行独立验证器..."
    .venv/bin/python verify_run.py "$OUTPUT_FILE"
    echo ""
else
    echo "✗ 测试 1 失败"
    exit 1
fi

# 测试 2: 近邻迁移（不同产品）
echo "=== 测试 2: 近邻迁移 ==="
echo "发送: P005 是什么产品？"
echo ""

OUTPUT_FILE_2="tools-real-transfer-$(date +%Y%m%d-%H%M%S).json"
.venv/bin/python agent.py --message "P005 是什么产品？" --output "$OUTPUT_FILE_2"

if [ $? -eq 0 ]; then
    echo "✓ 测试 2 成功"
    echo "输出已保存: $OUTPUT_FILE_2"
    echo ""
    
    echo "运行独立验证器..."
    .venv/bin/python verify_run.py "$OUTPUT_FILE_2"
    echo ""
else
    echo "✗ 测试 2 失败"
    exit 1
fi

# 测试 3: 诊断迁移（错误处理）
echo "=== 测试 3: 诊断迁移（错误处理） ==="
echo "发送: P999 的价格是多少？"
echo ""

OUTPUT_FILE_3="tools-real-diagnostic-$(date +%Y%m%d-%H%M%S).json"
.venv/bin/python agent.py --message "P999 的价格是多少？" --output "$OUTPUT_FILE_3"

if [ $? -eq 0 ]; then
    echo "✓ 测试 3 成功"
    echo "输出已保存: $OUTPUT_FILE_3"
    echo ""
    
    echo "运行独立验证器..."
    .venv/bin/python verify_run.py "$OUTPUT_FILE_3"
    echo ""
    
    # 检查是否正确处理错误
    if grep -q "Product not found" "$OUTPUT_FILE_3"; then
        echo "✓ 错误处理正确：工具返回 Product not found"
    else
        echo "⚠ 警告：未找到预期的错误信息"
    fi
    echo ""
else
    echo "✗ 测试 3 失败"
    exit 1
fi

# 测试 4: 组合迁移（多次调用）
echo "=== 测试 4: 组合迁移（多次调用） ==="
echo "发送: 所有教程的价格是多少？"
echo ""

OUTPUT_FILE_4="tools-real-combo-$(date +%Y%m%d-%H%M%S).json"
.venv/bin/python agent.py --message "所有教程的价格是多少？" --output "$OUTPUT_FILE_4"

if [ $? -eq 0 ]; then
    echo "✓ 测试 4 成功"
    echo "输出已保存: $OUTPUT_FILE_4"
    echo ""
    
    echo "运行独立验证器..."
    .venv/bin/python verify_run.py "$OUTPUT_FILE_4"
    echo ""
else
    echo "✗ 测试 4 失败"
    exit 1
fi

echo "=== 验证完成 ==="
echo ""
echo "已生成文件："
echo "  - $OUTPUT_FILE (默认问题)"
echo "  - $OUTPUT_FILE_2 (近邻迁移)"
echo "  - $OUTPUT_FILE_3 (诊断迁移)"
echo "  - $OUTPUT_FILE_4 (组合迁移)"
echo ""
echo "下一步："
echo "1. 检查输出文件中的 answer 字段，人工判断语义正确性"
echo "2. 验证工具调用是否正确（检查 tool_calls 和 tool 消息）"
echo "3. 将文件移动到 docs/validation/ 目录"
echo "4. 更新验证记录文档"
