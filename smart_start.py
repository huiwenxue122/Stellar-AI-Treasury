#!/usr/bin/env python3
"""
智能启动脚本 - 自动解决所有常见问题
"""

import subprocess
import sys
import os
import time
import socket

def find_free_port(start_port=8501, max_tries=10):
    """找到一个可用的端口"""
    for port in range(start_port, start_port + max_tries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    return None

def kill_old_streamlit():
    """关闭旧的streamlit进程"""
    try:
        if sys.platform == 'darwin' or sys.platform == 'linux':
            subprocess.run(['pkill', '-9', 'streamlit'], 
                         stderr=subprocess.DEVNULL, 
                         stdout=subprocess.DEVNULL)
            time.sleep(1)
            print("✅ 已清理旧的streamlit进程")
    except:
        pass

def check_dependencies():
    """检查并安装依赖"""
    print("🔍 检查依赖...")
    
    required = {
        'stellar_sdk': 'stellar-sdk>=11.0.0',
        'streamlit': 'streamlit>=1.28.0',
        'plotly': 'plotly>=5.0.0',
        'pandas': 'pandas>=1.4.0'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module.replace('_', '-'))
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            print(f"   ✅ {module}: v{version}")
        except ImportError:
            print(f"   ❌ {module}: 未安装")
            missing.append(package)
    
    if missing:
        print(f"\n📦 安装缺失的依赖: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing,
                                stdout=subprocess.DEVNULL)
            print("✅ 依赖安装完成")
        except:
            print("⚠️  依赖安装失败，但我们继续尝试...")
    
    return len(missing) == 0

def main():
    """主函数"""
    print("🚀 Stellar AI Treasury - 智能启动器")
    print("=" * 60)
    
    # 设置项目目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    print(f"📍 项目目录: {project_root}")
    print(f"🐍 Python路径: {sys.executable}")
    print(f"📦 Python版本: {sys.version.split()[0]}")
    print()
    
    # 检查依赖
    check_dependencies()
    print()
    
    # 清理旧进程
    print("🧹 清理旧的streamlit进程...")
    kill_old_streamlit()
    print()
    
    # 找可用端口
    print("🔍 寻找可用端口...")
    port = find_free_port(8501)
    
    if port is None:
        print("❌ 无法找到可用端口 (8501-8510)")
        print("\n💡 尝试使用命令行界面:")
        print(f"   {sys.executable} cli_dashboard.py")
        return
    
    print(f"✅ 使用端口: {port}")
    print()
    
    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
    
    # 启动streamlit
    print("🌐 启动Web界面...")
    print(f"浏览器将自动打开 http://localhost:{port}")
    print()
    print("💡 提示: 按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            os.path.join(project_root, "app", "dashboard.py"),
            "--server.port", str(port),
            "--server.address", "localhost",
            "--theme.primaryColor", "#667eea",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6"
        ], env=env, cwd=project_root)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard已停止")
    except FileNotFoundError:
        print("\n❌ Streamlit未安装")
        print("正在安装...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'streamlit>=1.28.0'])
        print("请重新运行此脚本")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n💡 备选方案:")
        print(f"   1. 使用命令行界面: {sys.executable} cli_dashboard.py")
        print(f"   2. 手动启动: {sys.executable} -m streamlit run app/dashboard.py --server.port {port}")

if __name__ == "__main__":
    main()
