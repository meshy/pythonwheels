from svg_wheel import generate_svg_wheel
from utils import (annotate_wheels, get_top_packages,
                   remove_irrelevant_packages, save_to_file)

TO_CHART = 360


def main():
    packages = remove_irrelevant_packages(get_top_packages(), TO_CHART)
    annotate_wheels(packages)
    save_to_file(packages, 'results.json')
    generate_svg_wheel(packages, TO_CHART)

    # TODO:
    # to think if I need those, since hard to tell which package
    # is a compiled one, maybe base on trove classifiers.

    # wheel_types = ['manylinux1_py3', 'manylinux1_py2',
    #                'win32_py3', 'win32_py2',
    #                'win_amd64_py3', 'win_amd64_py2']
    # for t in wheel_types:
    #    generate_svg(t, packages, TO_CHART)


if __name__ == '__main__':
    main()
