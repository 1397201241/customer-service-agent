"""Command-line interface for the customer service agent."""

import argparse
import os
import sys
import uuid

from dotenv import load_dotenv

from customer_service_agent.agent import chat_sync


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="电商售后客服 Agent - 命令行交互",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--session-id",
        "-s",
        type=str,
        default=None,
        help="会话ID（默认自动生成UUID）",
    )
    parser.add_argument(
        "--phone",
        "-p",
        type=str,
        default=None,
        help="用户手机号",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI模型名称（默认: gpt-4o-mini）",
    )
    return parser.parse_args()


def run_cli(session_id: str, phone: str | None, model: str) -> None:
    """Run the interactive CLI loop.

    Args:
        session_id: Conversation session identifier.
        phone: Optional customer phone number.
        model: OpenAI model name.
    """
    print("=" * 50)
    print("  欢迎使用电商售后客服 Agent")
    print("  输入 'quit' 或 'exit' 退出")
    print("=" * 50)
    print(f"会话ID: {session_id}")
    if phone:
        print(f"手机号: {phone}")
    print("-" * 50)

    while True:
        try:
            user_input = input("\n用户: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit", "q", "退出"}:
            print("再见！")
            break

        try:
            result = chat_sync(
                session_id=session_id,
                message=user_input,
                model_name=model,
            )
            response = result.get("output", "抱歉，处理请求时出现问题，请稍后重试。")
            print(f"\n客服: {response}")
        except Exception as e:
            print(f"\n错误: {e}")


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    load_dotenv()

    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "错误: 未设置 OPENAI_API_KEY 环境变量。\n"
            "请先设置环境变量或创建 .env 文件。",
            file=sys.stderr,
        )
        return 1

    args = parse_args()
    session_id = args.session_id or str(uuid.uuid4())
    run_cli(session_id, args.phone, args.model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
