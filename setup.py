from setuptools import setup

setup(
    name='sugarstore-generator',
    version='0.1.alpha',
    packages=['saasbuild', 'saasbuild.lib', 'saasbuild.lib.progressbar', 'saasbuild.bundle', 'saasbuild.platform'],
    url='https://github.com/sugarlabs-appstore/sugarappstore',
    license='AGPLv3+',
    author='srevinsaju',
    package_data={
        'saasbuild': ['data/flatpak.json', 'assets/activity-helloworld.svg']
    },
    author_email='srevinsaju@sugarlabs.org',
    description='A python package to build sugar app store',
    include_package_data=True,
    install_requires=['python_utils'],
    entry_points={'console_scripts': ['saasbuild = saasbuild.__main__:main']},  # noqa: E501
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
