"""
Simple venn diagrams.
"""

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

setup(
    name='svplot',
    version='0.0.1',
    description='Plotting helper functions',
    long_description=readme,
    author='Matthew Stone',
    author_email='matthew(dot)stone12(at)gmail.com',
    url='https://github.com/msto/svplot',
    license='MIT',
    packages=find_packages(exclude=['demo']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    keywords='matplotlib annotation',
    install_requires=['numpy', 'matplotlib'],
)
