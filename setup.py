from setuptools import setup

setup(
    name='aslo4',
    version='0.2',
    packages=['aslo4', 'aslo4.lib', 'aslo4.lib.progressbar', 'aslo4.bundle', 'aslo4.platform', 'aslo4.rdf'],
    url='https://github.com/sugarlabs/aslo-v4',
    download_url="https://pypi.python.org/pypi/aslo4",
    license='AGPLv3+',
    author='srevinsaju',
    package_data={
        'aslo4': ['data/flatpak.json', 'assets/activity-helloworld.svg']
    },
    author_email='srevinsaju@sugarlabs.org',
    description='A python package to build sugar app store',
    include_package_data=True,
    install_requires=['python_utils', 'jinja2', 'colorama'],
    entry_points={
        'console_scripts': [
            'aslo4-gen = aslo4.__main__:main',
            'aslo4 = aslo4.__main__:main'
        ]
    },  # noqa: E501
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
    ],
)

