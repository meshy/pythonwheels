import math
import os
import xml.etree.ElementTree as et

HEADERS = b'''<?xml version=\"1.0\" standalone=\"no\"?>
<?xml-stylesheet href="wheel.css" type="text/css"?>
<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\"
\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">
'''

PATH_TEMPLATE = '''
M {start_outer_x},{start_outer_y}
A{outer_radius},{outer_radius} 0 0 1 {end_outer_x},{end_outer_y}
L {start_inner_x},{start_inner_y}
A{inner_radius},{inner_radius} 0 0 0 {end_inner_x},{end_inner_y}
Z
'''

FRACTION_LINE = 80
OFFSET = 20
PADDING = 10
RADIUS = 180
CENTER = PADDING + RADIUS
TAU = 2 * math.pi


def annular_sector_path(start, stop):
    inner_radius = RADIUS // 2
    outer_radius = RADIUS
    cos_stop = math.cos(stop)
    cos_start = math.cos(start)
    sin_stop = math.sin(stop)
    sin_start = math.sin(start)

    points = {
        'inner_radius': inner_radius,
        'outer_radius': outer_radius,
        'start_outer_x': CENTER + outer_radius * cos_start,
        'start_outer_y': CENTER + outer_radius * sin_start,
        'end_outer_x': CENTER + outer_radius * cos_stop,
        'end_outer_y': CENTER + outer_radius * sin_stop,
        'start_inner_x': CENTER + inner_radius * cos_stop,
        'start_inner_y': CENTER + inner_radius * sin_stop,
        'end_inner_x': CENTER + inner_radius * cos_start,
        'end_inner_y': CENTER + inner_radius * sin_start,
    }
    return PATH_TEMPLATE.format(**points)


def add_annular_sector(wheel, start, stop, style_class):
    return et.SubElement(
        wheel, 'path',
        d=annular_sector_path(start=start, stop=stop),
        attrib={'class': style_class},
    )


def angles(index, total):
    start = index * TAU / total
    stop = (index + 1) * TAU / total

    return (start - TAU / 4, stop - TAU / 4)


def add_fraction(wheel, packages, total):
    text_attributes = {
        'text-anchor': 'middle',
        'dominant-baseline': 'central',
        'font-size': str(2 * OFFSET),
        'font-family': '"Helvetica Neue",Helvetica,Arial,sans-serif',
        'fill': '#333333',
    }

    # Packages with some sort of wheel
    wheel_packages = sum(package['wheel'] for package in packages)

    packages_with_wheels = et.SubElement(
        wheel, 'text',
        x=str(CENTER), y=str(CENTER - OFFSET),
        attrib=text_attributes,
    )
    packages_with_wheels.text = '{0}'.format(wheel_packages)

    # Dividing line
    et.SubElement(
        wheel, 'line',
        x1=str(CENTER - FRACTION_LINE // 2), y1=str(CENTER),
        x2=str(CENTER + FRACTION_LINE // 2), y2=str(CENTER),
        attrib={'stroke': '#333333', 'stroke-width': '2'},
    )

    # Total packages
    total_packages = et.SubElement(
        wheel, 'text',
        x=str(CENTER), y=str(CENTER + OFFSET),
        attrib=text_attributes,
    )
    total_packages.text = '{0}'.format(total)


def generate_svg_wheel(packages, total):
    wheel = et.Element(
        'svg',
        viewBox='0 0 {0} {0}'.format(2 * CENTER),
        version='1.1',
        xmlns='http://www.w3.org/2000/svg',
    )

    for index, result in enumerate(packages):
        start, stop = angles(index, total)
        sector = add_annular_sector(
            wheel,
            start=start, stop=stop,
            style_class=result['css_class'],
        )
        title = et.SubElement(sector, 'title')
        title.text = u'{0} {1}'.format(result['name'], result['icon'])

    add_fraction(wheel, packages, total)

    with open('wheel.svg', 'wb') as svg:
        svg.write(HEADERS)
        svg.write(et.tostring(wheel))

    # Install with: npm install svgexport -g
    os.system('svgexport wheel.svg wheel.png 32:32')
