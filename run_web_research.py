#!/usr/bin/env python3
"""
Web Research Agent Runner

Usage:
    python run_web_research.py "your research question"
    python run_web_research.py --help

Options:
    --agent, -a      Agent type: 'research' (default)
    --num-urls, -n   Number of URLs to visit (default: 5, max: 10)
    --no-synthesis   Disable AI synthesis of findings
    --verbose, -v    Enable verbose logging
"""

import argparse
import asyncio
import sys

from app.agent.web_research import WebResearchAgent
from app.logger import logger
from app.tool.enhanced_web_research import EnhancedWebResearchTool


async def main():
    parser = argparse.ArgumentParser(
        description="Run WebResearch agent for comprehensive web research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_web_research.py "What are the latest AI trends in 2025?"
    python run_web_research.py "Compare Python vs JavaScript for backend development" --num-urls 10
    python run_web_research.py "Best practices for API design" --no-synthesis
        """,
    )

    parser.add_argument(
        "query",
        type=str,
        nargs="?",
        help="Research question or topic to investigate",
    )
    parser.add_argument(
        "--agent",
        "-a",
        type=str,
        default="research",
        choices=["research"],
        help="Agent to use (default: research)",
    )
    parser.add_argument(
        "--num-urls",
        "-n",
        type=int,
        default=5,
        help="Number of URLs to visit (1-10, default: 5)",
    )
    parser.add_argument(
        "--no-synthesis",
        action="store_true",
        help="Disable AI synthesis of findings",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        print("\nError: Please provide a research query")
        print("Example: python run_web_research.py 'Latest AI developments'")
        sys.exit(1)

    if args.verbose:
        import logging

        logging.getLogger("app").setLevel(logging.DEBUG)

    print("=" * 60)
    print("🌐 Web Research Agent")
    print("=" * 60)
    print(f"Query: {args.query}")
    print(f"URLs to visit: {args.num_urls}")
    print(f"Synthesis: {'Enabled' if not args.no_synthesis else 'Disabled'}")
    print("=" * 60)

    agent = WebResearchAgent()

    try:
        tool = EnhancedWebResearchTool()

        result = await tool.execute(
            query=args.query,
            num_urls=args.num_urls,
            synthesis=not args.no_synthesis,
        )

        print("\n" + "=" * 60)
        print("📊 RESEARCH RESULTS")
        print("=" * 60)
        print(f"\nQuery: {result.query}")
        print(f"Total sources found: {result.total_sources_found}")
        print(f"Sources visited: {result.total_sources_visited}")
        print()

        for source in result.sources:
            status = "✅" if not source.error else "❌"
            print(f"{status} [{source.position}] {source.title}")
            print(f"   URL: {source.url}")

            if source.error:
                print(f"   Error: {source.error}")
            else:
                if source.extracted_content:
                    print(
                        f"   Content extracted: {len(str(source.extracted_content))} chars"
                    )
                    if source.relevance_score > 0:
                        print(f"   Relevance: {source.relevance_score:.2%}")
            print()

        if result.synthesis:
            print("=" * 60)
            print("📝 SYNTHESIS")
            print("=" * 60)
            print(result.synthesis)

        import re
        match = re.search(r"Research report saved to: (.+\.md)", str(result.output))
        if match:
            md_path = match.group(1)
            print("\n" + "=" * 60)
            print(f"📄 Full report: {md_path}")
            print("=" * 60)

        print("\n" + "=" * 60)
        print("✅ Research completed!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n⚠️ Research interrupted by user")
    except Exception as e:
        logger.error(f"Research failed: {e}")
        print(f"\n❌ Error: {e}")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
