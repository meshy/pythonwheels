from svg_wheel import generate_svg_wheel
from utils import (
    annotate_wheels,
    get_top_packages,
    remove_irrelevant_packages,
    save_to_file,
)

TO_CHART = 360


def main(to_chart: int = TO_CHART) -> None:
    packages = remove_irrelevant_packages(get_top_packages(), to_chart)
    annotate_wheels(packages)
    save_to_file(packages, "results.json")
    generate_svg_wheel(packages, to_chart)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-n", "--number", type=int, default=TO_CHART, help="number of packages to chart"
    )
    args = parser.parse_args()

    main(args.number)
