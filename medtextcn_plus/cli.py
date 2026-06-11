"""MedTextCN-Plus 命令行接口"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="medtext",
        description="MedTextCN-Plus: 中文医疗文本智能分析引擎 Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="综合分析医疗文本")
    analyze_parser.add_argument("-i", "--input", required=True, help="输入文件路径")
    analyze_parser.add_argument("-o", "--output", help="输出文件路径（默认stdout）")
    analyze_parser.add_argument("--ner", action="store_true", help="NER实体识别")
    analyze_parser.add_argument("--pii", action="store_true", help="PII脱敏")
    analyze_parser.add_argument("--summary", action="store_true", help="文本摘要")
    analyze_parser.add_argument("--relations", action="store_true", help="关系抽取")
    analyze_parser.add_argument("--drugs", action="store_true", help="药物交互检测")
    analyze_parser.add_argument("--all", action="store_true", help="全部分析")

    # sanitize 命令
    sanitize_parser = subparsers.add_parser("sanitize", help="PII隐私脱敏")
    sanitize_parser.add_argument("-i", "--input", required=True, help="输入文件路径")
    sanitize_parser.add_argument("-o", "--output", help="输出文件路径")
    sanitize_parser.add_argument("--full", action="store_true", help="输出完整脱敏报告")

    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量处理文件")
    batch_parser.add_argument("-d", "--dir", required=True, help="输入目录")
    batch_parser.add_argument("-o", "--output", required=True, help="输出目录")
    batch_parser.add_argument("--ext", default=".txt", help="文件扩展名（默认.txt）")
    batch_parser.add_argument("--recursive", action="store_true", help="递归处理子目录")

    # serve 命令
    serve_parser = subparsers.add_parser("serve", help="启动REST API服务")
    serve_parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    serve_parser.add_argument("--port", type=int, default=8080, help="监听端口")
    serve_parser.add_argument("--debug", action="store_true", help="调试模式")

    # tui 命令
    subparsers.add_parser("tui", help="启动交互式TUI界面")

    # version
    parser.add_argument("-v", "--version", action="version", version="MedTextCN-Plus v1.2.0")

    return parser


def cmd_analyze(args: argparse.Namespace) -> int:
    """执行分析命令"""
    from medtextcn_plus.core.engine import MedTextAnalyzer

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：文件不存在 - {args.input}", file=sys.stderr)
        return 1

    text = input_path.read_text(encoding="utf-8")
    analyzer = MedTextAnalyzer()

    # 构建分析选项
    options = {}
    if args.all:
        options = {k: True for k in [
            "ner", "pii", "summary", "relations",
            "drug_interaction", "keywords", "sentiment", "classification"
        ]}
    else:
        options = {
            "ner": args.ner,
            "pii": args.pii,
            "summary": args.summary,
            "relations": args.relations,
            "drug_interaction": args.drugs,
        }
        # 如果没有指定任何选项，默认全部开启
        if not any(options.values()):
            options = {k: True for k in options}

    result = analyzer.analyze(text, options)
    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"分析结果已保存到 {args.output}")
    else:
        print(output)

    return 0


def cmd_sanitize(args: argparse.Namespace) -> int:
    """执行脱敏命令"""
    from medtextcn_plus.core.engine import MedTextAnalyzer

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：文件不存在 - {args.input}", file=sys.stderr)
        return 1

    text = input_path.read_text(encoding="utf-8")
    analyzer = MedTextAnalyzer()

    if args.full:
        result = analyzer.sanitize_pii_full(text)
        output = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    else:
        output = analyzer.sanitize_pii(text)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"脱敏结果已保存到 {args.output}")
    else:
        print(output)

    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    """执行批量处理命令"""
    from medtextcn_plus.core.engine import MedTextAnalyzer

    input_dir = Path(args.dir)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_dir.exists():
        print(f"错误：目录不存在 - {args.dir}", file=sys.stderr)
        return 1

    pattern = f"**/*{args.ext}" if args.recursive else f"*{args.ext}"
    files = list(input_dir.glob(pattern))

    if not files:
        print(f"未找到匹配 {args.ext} 的文件")
        return 0

    analyzer = MedTextAnalyzer()
    print(f"开始批量处理 {len(files)} 个文件...")

    for i, file_path in enumerate(files, 1):
        try:
            text = file_path.read_text(encoding="utf-8")
            result = analyzer.analyze(text)
            out_path = output_dir / f"{file_path.stem}_result.json"
            out_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  [{i}/{len(files)}] {file_path.name} -> {out_path.name}")
        except Exception as e:
            print(f"  [{i}/{len(files)}] {file_path.name} - 错误: {e}", file=sys.stderr)

    print(f"批量处理完成，共处理 {len(files)} 个文件")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    """启动API服务"""
    try:
        from medtextcn_plus.api.server import create_app
    except ImportError as e:
        print(f"错误：{e}", file=sys.stderr)
        print("请安装Flask: pip install medtextcn-plus[server]", file=sys.stderr)
        return 1

    app = create_app()
    print(f"MedTextCN-Plus API 服务启动于 http://{args.host}:{args.port}")
    print("按 Ctrl+C 停止服务")
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


def cmd_tui(args: argparse.Namespace) -> int:
    """启动TUI界面"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.prompt import Prompt
    except ImportError:
        print("错误：需要安装rich库", file=sys.stderr)
        print("请运行: pip install medtextcn-plus[tui]", file=sys.stderr)
        return 1

    from medtextcn_plus.core.engine import MedTextAnalyzer

    console = Console()
    analyzer = MedTextAnalyzer()

    console.print(Panel(
        "[bold cyan]MedTextCN-Plus 中文医疗文本智能分析引擎[/bold cyan]\n"
        "输入医疗文本进行分析，输入 'quit' 退出",
        title="🩺 MedTextCN-Plus TUI",
        border_style="cyan",
    ))

    while True:
        console.print()
        text = Prompt.ask("[bold green]请输入医疗文本[/bold green]")

        if text.lower() in ("quit", "exit", "q"):
            console.print("[yellow]再见！[/yellow]")
            break

        if not text.strip():
            continue

        with console.status("[cyan]分析中..."):
            result = analyzer.analyze(text)

        # 显示实体
        entities = result.get("analyses", {}).get("entities", [])
        if entities:
            table = Table(title="🩺 医疗实体识别结果")
            table.add_column("实体", style="cyan")
            table.add_column("类型", style="green")
            table.add_column("置信度", style="yellow")
            for ent in entities:
                table.add_row(ent["text"], ent["type"], f"{ent['confidence']:.2f}")
            console.print(table)

        # 显示摘要
        summary = result.get("analyses", {}).get("summary", "")
        if summary:
            console.print(Panel(summary, title="📝 摘要", border_style="green"))

        # 显示PII
        pii = result.get("analyses", {}).get("pii", {})
        if pii and pii.get("pii_count", 0) > 0:
            console.print(Panel(
                pii.get("sanitized_text", ""),
                title=f"🔒 PII脱敏 (发现{pii['pii_count']}处)",
                border_style="red",
            ))

        # 显示药物交互
        interactions = result.get("analyses", {}).get("drug_interactions", [])
        if interactions:
            table = Table(title="💊 药物交互检测")
            table.add_column("药物A", style="cyan")
            table.add_column("药物B", style="cyan")
            table.add_column("严重程度", style="red")
            table.add_column("描述", style="white")
            for inter in interactions:
                table.add_row(
                    inter["drug_a"], inter["drug_b"],
                    inter["severity"], inter["description"]
                )
            console.print(table)

    return 0


def main(argv: Optional[list] = None) -> int:
    """CLI入口"""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    cmd_map = {
        "analyze": cmd_analyze,
        "sanitize": cmd_sanitize,
        "batch": cmd_batch,
        "serve": cmd_serve,
        "tui": cmd_tui,
    }

    handler = cmd_map.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
