"""Convenience script to execute full project workflow."""

from main_etl import run_etl
from run_analysis import run_analysis


def main() -> None:
    run_etl()
    run_analysis()


if __name__ == "__main__":
    main()

