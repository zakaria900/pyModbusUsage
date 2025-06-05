from setuptools import setup, find_packages

setup(
    name='sdm_modbus_modified',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pymodbus',
    ],
)
