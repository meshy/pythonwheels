import datetime
import json
import pytz
import requests


BASE_URL = 'https://pypi.org/pypi'

DEPRECATED_PACKAGES = {
    'BeautifulSoup',
    'distribute',
    'django-social-auth',
    'nose',
    'pep8',
    'pycrypto',
    'sklearn',
}

SESSION = requests.Session()


def get_json_url(package_name):
    return BASE_URL + '/' + package_name + '/json'


wheel_icon = dict()
wheel_icon['manylinux1_py3'] = ''
wheel_icon['manylinux1_py2'] = ''
wheel_icon['win32_py3'] = ''
wheel_icon['win32_py2'] = ''
wheel_icon['win_amd64_py3'] = ''
wheel_icon['win_amd64_py2'] = ''


def annotate_wheels(packages):
    print('Getting wheel data...')
    num_packages = len(packages)
    for index, package in enumerate(packages):
        print(index + 1, num_packages, package['name'])
        has_wheel = False
        has_manylinux_py3 = False
        has_manylinux_py2 = False
        has_win32_py3 = False
        has_win32_py2 = False
        has_win_amd64_py3 = False
        has_win_amd64_py2 = False
        url = get_json_url(package['name'])
        response = SESSION.get(url)
        if response.status_code != 200:
            print(' ! Skipping ' + package['name'])
            continue
        data = response.json()
        for download in data['urls']:
            if download['packagetype'] == 'bdist_wheel':
                has_wheel = True
                if download['python_version'].startswith("cp3") \
                        and 'manylinux1' in download['filename']:
                    has_manylinux_py3 = True
                if download['python_version'].startswith("cp2") \
                        and 'manylinux1' in download['filename']:
                    has_manylinux_py2 = True
                if download['python_version'].startswith("cp3") \
                        and 'win32' in download['filename']:
                    has_win32_py3 = True
                if download['python_version'].startswith("cp2") \
                        and 'win32' in download['filename']:
                    has_win32_py2 = True
                if download['python_version'].startswith("cp3") \
                        and 'win_amd64' in download['filename']:
                    has_win32_py3 = True
                if download['python_version'].startswith("cp2") \
                        and 'win_amd64' in download['filename']:
                    has_win32_py2 = True

        package['wheel'] = has_wheel
        package['manylinux1_py3'] = has_manylinux_py3
        package['manylinux1_py2'] = has_manylinux_py2
        package['win32_py3'] = has_win32_py3
        package['win32_py2'] = has_win32_py2
        package['win_amd64_py3'] = has_win_amd64_py3
        package['win_amd64_py2'] = has_win_amd64_py2

        # Display logic. I know, I'm sorry.
        package['value'] = 1
        if has_wheel:
            package['css_class'] = 'success'
            package['icon'] = u'\u2713'  # Check mark
            package['title'] = 'This package provides a wheel.'
        else:
            package['css_class'] = 'default'
            package['icon'] = u'\u2717'  # Ballot X
            package['title'] = ('This package has no wheel archives uploaded '
                                '(yet!).')

        available_types = []
        for wheel_type in ['manylinux1_py3', 'manylinux1_py2',
                           'win32_py3', 'win32_py2',
                           'win_amd64_py3', 'win_amd64_py2']:
            if package[wheel_type]:
                available_types.append(wheel_type)

        package['title'] += ' [{}]'.format(", ".join(available_types))


def get_top_packages():
    print('Getting packages...')

    with open('top-pypi-packages.json') as data_file:
        packages = json.load(data_file)['rows']

    # Rename keys
    for package in packages:
        package['downloads'] = package.pop('download_count')
        package['name'] = package.pop('project')

    return packages


def not_deprecated(package):
    return package['name'] not in DEPRECATED_PACKAGES


def remove_irrelevant_packages(packages, limit):
    print('Removing cruft...')
    active_packages = list(filter(not_deprecated, packages))
    return active_packages[:limit]


def save_to_file(packages, file_name):
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    with open(file_name, 'w') as f:
        f.write(json.dumps({
            'data': packages,
            'last_update': now.strftime('%A, %d %B %Y, %X %Z'),
        }, indent=1))
