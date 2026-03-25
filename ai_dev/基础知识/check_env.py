# check_env.py
import sys
import os


def get_version(package_name, module_attr="__version__"):
    """通用版本获取函数，处理异常"""
    try:
        module = __import__(package_name)
        # 尝试直接获取 __version__
        if hasattr(module, module_attr):
            return getattr(module, module_attr)

        # 特殊处理：llama-index 的版本在 core 子模块中
        if package_name == "llama_index":
            try:
                from llama_index.core import __version__ as core_version
                return core_version
            except ImportError:
                return "Installed (core version unknown)"

        return "Installed (version attribute not found)"
    except ImportError:
        return "❌ NOT INSTALLED"


def check_environment():
    print(f"🐍 Python 版本: {sys.version}")
    print(f"📂 当前环境路径: {sys.prefix}")

    # 检查是否在 ai_dev 环境中
    if "ai_dev" in sys.prefix:
        print("✅ 确认：正在 'ai_dev' 虚拟环境中运行")
    else:
        print("⚠️ 警告：似乎未在 'ai_dev' 环境中运行，请检查 conda activate")

    print("\n📦 核心库版本检查:")
    print("-" * 40)

    libs = [
        ("langchain", "langchain"),
        ("llama-index", "llama_index"),
        ("openai", "openai"),
        ("pydantic", "pydantic"),
        ("python-dotenv", "dotenv"),  # 注意：包名是 dotenv
    ]

    all_good = True
    for display_name, import_name in libs:
        version = get_version(import_name)
        if "❌" in version:
            print(f"{display_name}: {version}")
            all_good = False
        else:
            print(f"✅ {display_name}: {version}")

    print("-" * 40)

    if all_good:
        print("\n🎉 环境准备就绪！所有核心库已正确安装。")

        # 额外测试：实例化一个 Pydantic 模型，确保核心功能正常
        try:
            from pydantic import BaseModel
            class TestModel(BaseModel):
                status: str

            t = TestModel(status="ok")
            print(f"✅ Pydantic 功能测试通过: {t.status}")
        except Exception as e:
            print(f"⚠️ Pydantic 功能测试失败: {e}")
    else:
        print("\n❌ 部分库缺失，请检查安装日志。")


if __name__ == "__main__":
    check_environment()