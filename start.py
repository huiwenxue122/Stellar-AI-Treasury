#!/usr/bin/env python3
"""
可靠的启动脚本 - 解决模块导入问题
"""

import subprocess
import sys
import os

# 设置项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

print("🚀 启动 Stellar AI Treasury Dashboard")
print("=" * 60)
print(f"📍 项目目录: {project_root}")
print(f"🐍 Python路径: {sys.executable}")
print(f"📦 Python版本: {sys.version.split()[0]}")
print()

# 检查依赖
print("🔍 检查依赖...")
try:
    import stellar_sdk
    print(f"✅ stellar_sdk {stellar_sdk.__version__} 已安装")
except ImportError:
    print("❌ stellar_sdk 未安装，正在安装...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "stellar-sdk>=11.0.0"])

try:
    import streamlit
    print(f"✅ streamlit {streamlit.__version__} 已安装")
except ImportError:
    print("❌ streamlit 未安装，正在安装...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit>=1.28.0"])

print()
print("🌐 启动Web界面...")
print("浏览器将自动打开 http://localhost:8501")
print()
print("💡 提示: 按 Ctrl+C 停止服务器")
print("=" * 60)
print()

# 设置环境变量
env = os.environ.copy()
env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')

# 启动streamlit
try:
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        os.path.join(project_root, "app", "dashboard.py"),
        "--server.port", "8501",
        "--server.address", "localhost",
        "--theme.primaryColor", "#667eea",
        "--theme.backgroundColor", "#ffffff"
    ], env=env, cwd=project_root)
except KeyboardInterrupt:
    print("\n\n👋 Dashboard已停止")
except Exception as e:
    print(f"\n❌ 启动失败: {e}")
    print("\n尝试使用备选方式:")
    print(f"  {sys.executable} -m streamlit run app/dashboard.py")
