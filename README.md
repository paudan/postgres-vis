## PostgreSQL visualizer and reference generator

A simple command-line tool written to visualize internal table/view dependencies as dependency graphs using ``pyvis`` or ``graphviz``. 
It also provides command-line functionality to generate documentation for PostgreSQL functions and types in PDF format.

The tool can be installed using ``pip`` command.

### Usage

The dependency graph visualizer can be run with ``pg_deps_graph`` as follows:
```
usage: pg_deps_graph [-h] --dbname DBNAME [--dbhost DBHOST] [--dbuser DBUSER]
                     [--dbpass DBPASS] [--dbschema DBSCHEMA]
                     [--output-table-deps] [--file-table-deps FILENAME_TABLE]
                     [--output-view-deps] [--file-view-deps FILENAME_VIEWS]
                     [--output-format {png,html}]
                     [--layout {neato,dot,twopi,circo,fdp}]

optional arguments:
  -h, --help            show this help message and exit

Database Options:
  --dbname DBNAME       Database name
  --dbhost DBHOST       Database host
  --dbuser DBUSER       Database username
  --dbpass DBPASS       Database password
  --dbschema DBSCHEMA   Database schema

Output options:
  --output-table-deps   Output tables deps
  --file-table-deps FILENAME_TABLE
                        Filename for tables deps output
  --output-view-deps    Output view deps
  --file-view-deps FILENAME_VIEWS
                        Filename for view deps output
  --output-format {png,html}
                        Output format
  --layout {neato,dot,twopi,circo,fdp}
                        Layout of displayed deps, if image output is selected,
                        as supported by GraphViz
```

The output will be either HTML file (with dynamic Javacsript based graph which layout can be customized) or PNG file (with ``graphviz`` as the rendering engine)

The reference can be generated using ``pg_deps_reference`` command:

```
usage: pg_deps_reference [-h] --dbname DBNAME [--dbhost DBHOST]
                         [--dbuser DBUSER] [--dbpass DBPASS]
                         [--dbschema DBSCHEMA] [--output-function-info]
                         [--output-types] [--filename FILENAME]

optional arguments:
  -h, --help            show this help message and exit

Database Options:
  --dbname DBNAME       Database name
  --dbhost DBHOST       Database host
  --dbuser DBUSER       Database username
  --dbpass DBPASS       Database password
  --dbschema DBSCHEMA   Database schema

Output options:
  --output-function-info
                        Output function information
  --output-types        Output composite type information
  --filename FILENAME   PDF file name
```

The output will be PDF file with information extracted from PostgreSQL metadata 