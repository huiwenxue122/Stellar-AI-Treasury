#!/usr/bin/env python3
"""
诊断脚本 - 检查前端启动问题
"""

import sys
import os

print("🔍 诊断前端启动问题")
print("=" * 60)

# 1. 检查Python版本和路径
print("1. Python环境信息:")
print(f"   Python版本: {sys.version}")
print(f"   Python路径: {sys.executable}")
print(f"   当前工作目录: {os.getcwd()}")
print()

# 2. 检查关键模块
print("2. 检查关键模块:")
modules_to_check = [
    'stellar_sdk',
    'streamlit',
    'plotly',
    'pandas',
    'aiohttp',
    'yaml',
    'dotenv'
]

missing_modules = []
installed_modules = []

for module in modules_to_check:
    try:
        if module == 'yaml':
            __import__('pyyaml')
            module_name = 'pyyaml'
        elif module == 'dotenv':
            __import__('python_dotenv')
            module_name = 'python-dotenv'
        else:
            __import__(module)
            module_name = module
        
        # Get version if possible
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            print(f"   ✅ {module_name}: v{version}")
            installed_modules.append(module_name)
        except:
            print(f"   ✅ {module_name}: installed")
            installed_modules.append(module_name)
    except ImportError as e:
        print(f"   ❌ {module}: 未安装")
        missing_modules.append(module)

print()

# 3. 检查项目结构
print("3. 检查项目文件:")
files_to_check = [
    'app/orchestrator.py',
    'app/dashboard.py',
    'app/ui_dashboard.py',
    'cli_dashboard.py',
    'requirements.txt',
    '.env'
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} (不存在)")

print()

# 4. 尝试导入orchestrator
print("4. 测试导入Orchestrator:")
try:
    sys.path.insert(0, os.getcwd())
    from app.orchestrator import ORCHESTRATOR
    print("   ✅ Orchestrator导入成功")
except Exception as e:
    print(f"   ❌ Orchestrator导入失败: {e}")

print()

# 5. 提供解决方案
print("=" * 60)
if missing_modules:
    print("⚠️  发现问题: 缺少以下模块")
    print()
    print("解决方案:")
    print(f"pip install {' '.join(missing_modules)}")
    print()
    print("或者重新安装所有依赖:")
    print("pip install -r requirements.txt")
else:
    print("✅ 所有模块都已安装")
    print()
    print("如果仍然遇到问题，请尝试:")
    print()
    print("方法1 - 使用完整路径启动:")
    print(f"{sys.executable} run_enhanced_dashboard.py")
    print()
    print("方法2 - 使用streamlit命令:")
    print(f"{sys.executable} -m streamlit run app/dashboard.py")
    print()
    print("方法3 - 检查是否使用了不同的Python环境:")
    print("which python  # 查看Python路径")
    print("python --version  # 查看Python版本")

print()
print("=" * 60)
print("💡 提示: 如果你使用虚拟环境，请确保已激活正确的环境")
