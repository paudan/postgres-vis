from setuptools import setup

setup(
    name='visualize-pg',
    version='0.1',
    packages=['pg_vis'],
    url='',
    license='MIT',
    author='Paulius Danenas',
    author_email='danpaulius@gmail.com',
    description='Dependency visualizer for PostgreSQL',
    install_requires=['pygraphviz', 'psycopg2'],
    entry_points={
        'console_scripts': [
            'show_pg_deps=visualize_deps:main',
        ],
    },
)
