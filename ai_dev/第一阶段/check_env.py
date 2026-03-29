import sys
import langchain
import dotenv

# 1. 检查 Python 解释器路径（确保你在虚拟环境里）
print(f"✅ 当前 Python 路径: {sys.executable}")

# 2. 检查 LangChain 版本
print(f"✅ LangChain 版本: {langchain.__version__}")

# 3. 检查 dotenv
print(f"✅ python-dotenv 已安装")

print("🎉 环境配置成功！准备开始 AI 开发之旅！")