from setuptools import setup

setup(
    name='pg-deps-analyzer',
    version='0.1',
    packages=['pg_deps_parser'],
    url='',
    license='MIT',
    author='Paulius Danenas',
    author_email='danpaulius@gmail.com',
    description='Dependency visualizer and reference generator for PostgreSQL databases',
    install_requires=['pygraphviz', 'psycopg2', 'pyvis', 'fpdf'],
    entry_points={
        'console_scripts': [
            'pg_deps_graph=pg_deps_parser.visualize_deps:main',
            'pg_deps_reference=pg_deps_parser.reference:main'
        ],
    },
)
