#!/usr/bin/env python3
"""
自动创建Stellar Testnet账户并更新.env文件
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_testnet_account():
    """创建testnet账户"""
    print("🌟 Stellar Testnet 账户创建器")
    print("=" * 60)
    
    try:
        from stellar_sdk import Keypair
        import requests
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("正在安装...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'stellar-sdk', 'requests'])
        from stellar_sdk import Keypair
        import requests
    
    # 生成新密钥对
    print("\n🔑 生成新的密钥对...")
    kp = Keypair.random()
    
    print(f"✅ Public Key:  {kp.public_key}")
    print(f"✅ Secret Key:  {kp.secret}")
    
    # 使用friendbot获取测试币
    print("\n💰 正在从friendbot获取测试币...")
    try:
        response = requests.get(
            f'https://friendbot.stellar.org',
            params={'addr': kp.public_key},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ 成功！账户已创建并获得10,000 XLM测试币")
            account_created = True
        else:
            print(f"⚠️  Friendbot返回状态码: {response.status_code}")
            print("账户已生成，但需要手动获取测试币")
            account_created = False
    except Exception as e:
        print(f"⚠️  无法连接到friendbot: {e}")
        print("账户已生成，但需要手动获取测试币")
        account_created = False
    
    # 更新.env文件
    print("\n📝 更新.env文件...")
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    env_content = f"""# Stellar Testnet Configuration
STELLAR_SECRET={kp.secret}
STELLAR_PUBLIC={kp.public_key}

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key_here
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ .env文件已更新: {env_path}")
    except Exception as e:
        print(f"⚠️  无法更新.env文件: {e}")
        print("\n请手动创建.env文件，内容如下:")
        print(env_content)
    
    # 验证账户
    if account_created:
        print("\n🔍 验证账户...")
        try:
            verify_response = requests.get(
                f'https://horizon-testnet.stellar.org/accounts/{kp.public_key}',
                timeout=10
            )
            if verify_response.status_code == 200:
                account_data = verify_response.json()
                print("✅ 账户验证成功！")
                print(f"   账户ID: {account_data['account_id']}")
                
                # 显示余额
                for balance in account_data.get('balances', []):
                    if balance.get('asset_type') == 'native':
                        print(f"   XLM余额: {float(balance['balance']):.2f}")
            else:
                print("⚠️  无法验证账户")
        except Exception as e:
            print(f"⚠️  验证失败: {e}")
    
    # 显示后续步骤
    print("\n" + "=" * 60)
    print("🎉 完成！接下来的步骤:")
    print()
    print("1. 重启dashboard:")
    print("   python smart_start.py")
    print()
    print("2. 在浏览器中刷新页面")
    print()
    print("3. 点击侧边栏的 '🚀 Initialize System' 按钮")
    print()
    print("4. 你现在应该能看到真实的账户余额了！")
    print()
    
    if not account_created:
        print("⚠️  手动获取测试币:")
        print(f"   访问: https://laboratory.stellar.org/#account-creator?network=test")
        print(f"   或访问: https://friendbot.stellar.org/?addr={kp.public_key}")
        print()
    
    print("🌐 查看你的账户:")
    print(f"   https://stellar.expert/explorer/testnet/account/{kp.public_key}")
    print()
    print("=" * 60)
    
    return kp.public_key, kp.secret

if __name__ == "__main__":
    try:
        create_testnet_account()
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("\n请尝试手动创建账户:")
        print("1. 访问 https://laboratory.stellar.org/#account-creator?network=test")
        print("2. 点击 'Generate keypair'")
        print("3. 点击 'Fund account with friendbot'")
        print("4. 将密钥复制到 .env 文件")
