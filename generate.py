from svg_wheel import generate_svg_wheel
from utils import (
    annotate_wheels,
    get_top_packages,
    not_deprecated,
    remove_irrelevant_packages,
    save_to_file,
)


TO_CHART = 360


def main():
    active_packages = filter(not_deprecated, get_top_packages())
    packages = remove_irrelevant_packages(active_packages, TO_CHART)
    annotate_wheels(packages)
    save_to_file(packages, 'results.json')
    generate_svg_wheel(packages, TO_CHART)


if __name__ == '__main__':
    main()
