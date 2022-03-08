from setuptools import setup

setup(
    name='fifemon-condor-probe',
    version='1.0',
    packages=['fifemon','fifemon.condor'],
    include_package_data=True,
    install_requires=[
        'htcondor',
        'prometheus-client==0.10.1',
        'elasticsearch',
        'influxdb',
    ],
    entry_points='''
        [console_scripts]
        fifemon=fifemon.condor_probe:main
    ''',
)
