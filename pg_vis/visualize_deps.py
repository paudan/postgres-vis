from argparse import ArgumentParser
import psycopg2
import pygraphviz as pgv
import sys


def table_deps(cursor, schema):
    G = pgv.AGraph(directed=True)
    sql = """
    SELECT
        tc.constraint_name, tc.table_name, kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM
        information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu ON
        tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu ON 
        ccu.constraint_name = tc.constraint_name
    WHERE constraint_type = 'FOREIGN KEY'{}
    """.format("AND tc.table_schema = '{}'".format(schema) if schema else "")
    try:
        cursor.execute(sql)
    except (psycopg2.OperationalError, psycopg2.ProgrammingError)  as e:
        print("Error connecting to database: " + e.pgerror)
        return G
    for row in cursor.fetchall():
        constraint, table, column, foreign_table, foreign_column = row
        G.add_nodes_from([table, foreign_table])
        G.add_edge(table, foreign_table, label=constraint)
    return G

def view_deps(cursor, schema):
    G = pgv.AGraph(directed=True)
    sql = """
    SELECT DISTINCT dependent_ns.nspname as dependent_schema, dependent_view.relname as dependent_view, 
    source_ns.nspname as source_schema, source_table.relname as source_table
    FROM pg_depend 
    JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid 
    JOIN pg_class as dependent_view ON pg_rewrite.ev_class = dependent_view.oid 
    JOIN pg_class as source_table ON pg_depend.refobjid = source_table.oid 
    JOIN pg_attribute ON pg_depend.refobjid = pg_attribute.attrelid 
        AND pg_depend.refobjsubid = pg_attribute.attnum 
    JOIN pg_namespace dependent_ns ON dependent_ns.oid = dependent_view.relnamespace
    JOIN pg_namespace source_ns ON source_ns.oid = source_table.relnamespace
    WHERE source_ns.nspname NOT IN ('information_schema', 'pg_catalog')
    {}""".format("AND source_ns.nspname = '{}'".format(schema) if schema else "")
    try:
        cursor.execute(sql)
    except (psycopg2.OperationalError, psycopg2.ProgrammingError)  as e:
        print("Error connecting to database: " + e.pgerror)
        return G
    for row in cursor.fetchall():
        dependent_schema, dependent_view, source_schema, source_table = row
        G.add_nodes_from([dependent_view, source_table])
        G.add_edge(dependent_view, source_table)
    return G


def main(argv=None):
    parser = ArgumentParser()
    group = parser.add_argument_group("Database Options")
    group.add_argument("--dbname", action="store", dest="dbname", help="Database name", required=True)
    group.add_argument("--dbhost", action="store", dest="dbhost", default="localhost",  help="Database host")
    group.add_argument("--dbuser", action="store", dest="dbuser", help="Database username")
    group.add_argument("--dbpass", action="store", dest="dbpass", help="Database password")
    group.add_argument("--dbschema", action="store", dest="schema", help="Database schema")
    group = parser.add_argument_group("Output options")
    group.add_argument("--output-table-deps", action="store_true", dest="output_tables", help="Output tables deps")
    group.add_argument("--file-table-deps", action="store", dest="filename_table", help="Filename for tables deps output")
    group.add_argument("--output-view-deps", action="store_true", dest="output_views", help="Output view deps")
    group.add_argument("--file-view-deps", action="store", dest="filename_views", help="Filename for view deps output")
    group.add_argument("--layout", action="store", dest="layout", help="Layout of displayed deps, as supported by GraphViz",
                       choices=['neato','dot','twopi','circo','fdp'])
    parser.set_defaults(output_tables=True)
    parser.set_defaults(output_views=True)
    options = parser.parse_args()
    try:
        conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'"
            % (options.dbname, options.dbuser, options.dbhost, options.dbpass))
    except psycopg2.OperationalError as e:
        print("Error connecting to database: " + e.pgerror)
        print("Use --help for more info.")
        sys.exit(1)
    layout = options.layout or 'dot'
    if options.output_tables:
        filename = options.filename_table or 'file_tables.png'
        G = table_deps(conn.cursor(), options.schema)
        G.layout(prog=layout)
        G.draw(filename)
    if options.output_views:
        filename = options.filename_table or 'file_views.png'
        G = view_deps(conn.cursor(), options.schema)
        G.layout(prog=layout)
        G.draw(filename)
    if conn:
        conn.close()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])