#!/bin/bash
# Basic 真实验证执行脚本
# 使用方法：
# 1. 确保 .env 已配置（从 .env.example 复制并填入真实值）
# 2. chmod +x run-basic-verification.sh
# 3. ./run-basic-verification.sh

set -e

echo "=== Basic 真实验证 ==="
echo ""

# 检查 .env 是否存在
if [ ! -f .env ]; then
    echo "ERROR: .env 文件不存在"
    echo "请先运行: cp .env.example .env 并填入真实配置"
    exit 1
fi

# 检查必要的变量（用 grep 检查，不 source，因为值可能有空格）
if ! grep -q '^LC_API_KEY=' .env; then
    echo "ERROR: LC_API_KEY 未在 .env 中配置"
    exit 1
fi

if ! grep -q '^LC_BASE_URL=' .env; then
    echo "ERROR: LC_BASE_URL 未在 .env 中配置"
    exit 1
fi

if ! grep -q '^LC_MODEL=' .env; then
    echo "WARNING: LC_MODEL 未在 .env 中配置"
fi

LC_BASE_URL=$(grep '^LC_BASE_URL=' .env | head -1 | cut -d= -f2-)
LC_MODEL=$(grep '^LC_MODEL=' .env | head -1 | cut -d= -f2-)

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

# 测试 1: 默认问题
echo "=== 测试 1: 默认问题 ==="
echo "发送: What is the capital of France?"
echo ""

OUTPUT_FILE="basic-real-run-$(date +%Y%m%d-%H%M%S).json"
.venv/bin/python agent.py --output "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "✓ 测试 1 成功"
    echo "输出已保存: $OUTPUT_FILE"
    echo ""
    
    # 运行独立验证器
    echo "运行独立验证器..."
    .venv/bin/python inspect_result.py "$OUTPUT_FILE"
    echo ""
else
    echo "✗ 测试 1 失败"
    exit 1
fi

# 测试 2: 近邻迁移
echo "=== 测试 2: 近邻迁移 ==="
echo "发送: Explain quantum computing in one sentence."
echo ""

OUTPUT_FILE_2="basic-real-transfer-$(date +%Y%m%d-%H%M%S).json"
.venv/bin/python agent.py --message "Explain quantum computing in one sentence." --output "$OUTPUT_FILE_2"

if [ $? -eq 0 ]; then
    echo "✓ 测试 2 成功"
    echo "输出已保存: $OUTPUT_FILE_2"
    echo ""
    
    # 运行独立验证器
    echo "运行独立验证器..."
    .venv/bin/python inspect_result.py "$OUTPUT_FILE_2"
    echo ""
else
    echo "✗ 测试 2 失败"
    exit 1
fi

echo "=== 验证完成 ==="
echo ""
echo "已生成文件："
echo "  - $OUTPUT_FILE"
echo "  - $OUTPUT_FILE_2"
echo ""
echo "下一步："
echo "1. 检查输出文件中的 answer 字段，人工判断语义正确性"
echo "2. 将文件移动到 docs/validation/ 目录"
echo "3. 更新验证记录文档"
