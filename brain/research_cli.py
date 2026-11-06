"""Command-line entry point for ASTA_AI live web research."""
import argparse

from web_research import ResearchError, format_sources, search_web


def main() -> int:
    parser = argparse.ArgumentParser(description="Search the web with ASTA_AI.")
    parser.add_argument("query", help="What ASTA_AI should research")
    parser.add_argument("--results", type=int, default=5, help="Number of sources (1-10)")
    args = parser.parse_args()

    try:
        results = search_web(args.query, max_results=args.results)
    except (ResearchError, ValueError) as exc:
        parser.error(str(exc))
    print(format_sources(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
