#!/bin/bash
# Stellar AI Treasury 启动脚本

echo "🚀 启动 Stellar AI Treasury Dashboard"
echo "======================================"

# 进入项目目录
cd "$(dirname "$0")"

# 显示Python信息
echo "📍 项目目录: $(pwd)"
echo "🐍 Python路径: $(which python)"
echo "📦 Python版本: $(python --version)"
echo ""

# 检查stellar_sdk
echo "🔍 检查依赖..."
if python -c "import stellar_sdk" 2>/dev/null; then
    echo "✅ stellar_sdk 已安装"
else
    echo "❌ stellar_sdk 未安装"
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

# 启动dashboard
echo ""
echo "🌐 启动Web界面..."
echo "浏览器将自动打开 http://localhost:8501"
echo ""
echo "💡 提示: 按 Ctrl+C 停止服务器"
echo "======================================"
echo ""

# 使用完整路径启动streamlit
export PYTHONPATH="$(pwd):$PYTHONPATH"
python -m streamlit run app/dashboard.py \
    --server.port 8501 \
    --server.address localhost \
    --theme.primaryColor "#667eea" \
    --theme.backgroundColor "#ffffff"
