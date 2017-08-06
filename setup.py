"""Setup file for souliss package."""
import os
from setuptools import setup, find_packages

if os.path.exists('README.rst'):
    README = open('README.rst').read()
else:
    README = ''

setup(
    name='pysouliss',
    version='0.0.3',
    description='Python API for talking to a Souliss gateway gateway',
    long_description=README,
    url='https://github.com/maoterodapena/pysouliss',
    author='Miguel Otero',
    author_email='maoterodapena@gmail.com',
    license='MIT License',
    install_requires=['paho-mqtt'],
    packages=find_packages(exclude=['tests', 'tests.*']),
    keywords=['sensor', 'actuator', 'IoT', 'DYI'],
    zip_safe=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Home Automation',
    ])
