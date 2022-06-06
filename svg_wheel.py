import math
import os
import xml.etree.ElementTree as et

HEADERS = b"""<?xml version=\"1.0\" standalone=\"no\"?>
<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\"
\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">
"""

STYLES = """
.success { stroke: #4CAE4C; stroke-width: 1; fill: #5CB85C; }
.default { stroke: #cccccc; stroke-width: 1; fill: #ffffff; }
"""

PATH_TEMPLATE = """
M {start_outer_x},{start_outer_y}
A{outer_radius},{outer_radius} 0 0 1 {end_outer_x},{end_outer_y}
L {start_inner_x},{start_inner_y}
A{inner_radius},{inner_radius} 0 0 0 {end_inner_x},{end_inner_y}
Z
"""

FRACTION_LINE = 80
OFFSET = 20
PADDING = 10
OUTER_RADIUS = 180
INNER_RADIUS = OUTER_RADIUS / 2
CENTER = PADDING + OUTER_RADIUS
TAU = 2 * math.pi  # The angle, in radians, of a full circle.


def annular_sector_path(start, stop):
    cos_stop = math.cos(stop)
    cos_start = math.cos(start)
    sin_stop = math.sin(stop)
    sin_start = math.sin(start)

    points = {
        "inner_radius": INNER_RADIUS,
        "outer_radius": OUTER_RADIUS,
        "start_outer_x": CENTER + OUTER_RADIUS * cos_start,
        "start_outer_y": CENTER + OUTER_RADIUS * sin_start,
        "end_outer_x": CENTER + OUTER_RADIUS * cos_stop,
        "end_outer_y": CENTER + OUTER_RADIUS * sin_stop,
        "start_inner_x": CENTER + INNER_RADIUS * cos_stop,
        "start_inner_y": CENTER + INNER_RADIUS * sin_stop,
        "end_inner_x": CENTER + INNER_RADIUS * cos_start,
        "end_inner_y": CENTER + INNER_RADIUS * sin_start,
    }
    return PATH_TEMPLATE.format(**points)


def add_annular_sectors(wheel, packages, total):
    for index, result in enumerate(packages):
        sector = et.SubElement(
            wheel,
            "path",
            d=annular_sector_path(*angles(index, total)),
            attrib={"class": result["css_class"]},
        )
        title = et.SubElement(sector, "title")
        title.text = "{0} {1}".format(result["name"], result["icon"])


def angles(index, total):
    # Angle, in radians, of one wedge of the wheel.
    angle_per_wedge = TAU / total
    # Used to turn the start of the wheel from east to north.
    quarter_circle = TAU / 4

    # Angle of the beginning of the wedge.
    start = (index * angle_per_wedge) - quarter_circle
    # Angle of the end of the wedge.
    stop = start + angle_per_wedge

    return start, stop


def add_fraction(wheel, packages, total):
    text_attributes = {
        "text-anchor": "middle",
        "dominant-baseline": "central",
        "font-size": str(2 * OFFSET),
        "font-family": '"Helvetica Neue",Helvetica,Arial,sans-serif',
        "fill": "#333333",
    }

    # Packages with some sort of wheel
    wheel_packages = sum(package["wheel"] for package in packages)

    packages_with_wheels = et.SubElement(
        wheel,
        "text",
        x=str(CENTER),
        y=str(CENTER - OFFSET),
        attrib=text_attributes,
    )
    packages_with_wheels.text = "{0}".format(wheel_packages)

    title = et.SubElement(packages_with_wheels, "title")
    percentage = "{:.0%}".format(wheel_packages / total)
    title.text = percentage

    # Dividing line
    et.SubElement(
        wheel,
        "line",
        x1=str(CENTER - FRACTION_LINE // 2),
        y1=str(CENTER),
        x2=str(CENTER + FRACTION_LINE // 2),
        y2=str(CENTER),
        attrib={"stroke": "#333333", "stroke-width": "2"},
    )

    # Total packages
    total_packages = et.SubElement(
        wheel,
        "text",
        x=str(CENTER),
        y=str(CENTER + OFFSET),
        attrib=text_attributes,
    )
    total_packages.text = "{0}".format(total)

    title = et.SubElement(total_packages, "title")
    title.text = percentage


def generate_svg_wheel(packages, total):
    wheel = et.Element(
        "svg",
        viewBox="0 0 {0} {0}".format(2 * CENTER),
        version="1.1",
        xmlns="http://www.w3.org/2000/svg",
    )
    style = et.SubElement(wheel, "style", attrib={"type": "text/css"})
    style.text = STYLES

    add_annular_sectors(wheel, packages, total)

    add_fraction(wheel, packages, total)

    with open("wheel.svg", "wb") as svg:
        svg.write(HEADERS)
        svg.write(et.tostring(wheel))
