from argparse import ArgumentParser
import sys
import psycopg2
from .pdf import UnicodeFPDF
from .pg_connect import PgConnect

DOC_FONT = "Arial"

class PgReference(PgConnect):

    def _function_info(self, schema = None):
        sql = """
        SELECT quote_ident(n.nspname), p.proname, pg_get_function_arguments(p.oid), pg_get_function_result(p.oid), d.description
        FROM pg_proc p JOIN pg_namespace n on n.oid = p.pronamespace
        JOIN pg_description d on p.oid = d.objoid {}
        """.format("WHERE n.nspname = '{}'".format(schema) if schema else "")
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except (psycopg2.OperationalError, psycopg2.ProgrammingError)  as e:
            print("Error connecting to database: " + e.pgerror)
            return None

    def _type_info(self, schema = None):
        sql = """
        SELECT t.typname, a.attname, at_.typname as att_type, a.attnotnull, a.attndims
        FROM pg_type t
        JOIN pg_namespace n on n.oid = t.typnamespace
        JOIN pg_attribute a ON a.attrelid = t.typrelid
        JOIN pg_type at_ ON at_.oid = a.atttypid
        WHERE t.typtype = 'c' AND t.typarray > 0 AND pg_catalog.pg_type_is_visible(t.oid )
        AND (t.typrelid = 0 OR ( SELECT c.relkind = 'c' FROM pg_catalog.pg_class c WHERE c.oid = t.typrelid)){}
        """.format("AND n.nspname = '{}'".format(schema) if schema else "")
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except (psycopg2.OperationalError, psycopg2.ProgrammingError)  as e:
            print("Error connecting to database: " + e.pgerror)
            return None


    def open_pdf(self):
        self.pdf = UnicodeFPDF()
        self.pdf.add_page()
        self.pdf.compress = False

    def save_pdf(self, filename):
        if self.pdf:
            self.pdf.output(filename)

    def create_info(self, schema):
        data = self._function_info(schema)
        if data is None:
            return None

        self.pdf.set_font(DOC_FONT, size=14, style='B')
        self.pdf.write(8, "Functions")
        self.pdf.ln(5)
        self.pdf.set_font(DOC_FONT, size=12)

        left_cell = self.pdf.w / 4.5
        right_cell = self.pdf.w - self.pdf.r_margin - left_cell - 25
        col_width = [left_cell, right_cell]
        row_height = self.pdf.font_size
        spacing = 2

        def simple_table(data):
            for row in data:
                for ind, item in enumerate(row):
                    self.pdf.cell(col_width[ind], row_height * spacing, txt=item, border=1)
                self.pdf.ln(row_height * spacing)

        for row in data:
            schema, name, args, output, description = row
            tbl_data = [['Input', arg] for arg in args.split(',')]
            self.pdf.ln(10)
            self.pdf.set_font(DOC_FONT, size=12, style='B')
            self.pdf.write(8, name)
            self.pdf.set_font(DOC_FONT, size=12)
            if description is not None:
                self.pdf.ln(10)
                self.pdf.multi_cell(self.pdf.w - self.pdf.r_margin - 35, 6, description, align='L')
            if len(args) > 0:
                self.pdf.ln(5)
                simple_table(tbl_data)
            else:
                self.pdf.ln(5)
            self.pdf.ln(5)
            self.pdf.set_font(DOC_FONT, size=12, style='B')
            self.pdf.write(8, 'Output: ')
            self.pdf.set_font(DOC_FONT, size=12)
            self.pdf.write(8, output)
            self.pdf.ln(5)


    def create_types(self, schema):
        data = self._type_info(schema)
        if data is None:
            return None
        types_data = {}
        for row in data:
            typename, attname, att_type, attnotnull, dim = row
            if types_data.get(typename) is None:
                types_data[typename] = []
            types_data[typename].append("{} {}{} {}".format(attname, att_type, "[]" if dim == 1 else "",
                                                            "NOT NULL" if attnotnull is True else ""))
        self.pdf.set_font(DOC_FONT, size=14, style='B')
        self.pdf.ln(12)
        self.pdf.write(8, "Types")
        self.pdf.ln(8)
        self.pdf.set_font(DOC_FONT, size=12)
        for typename, value in types_data.items():
            self.pdf.l_margin += 5
            self.pdf.write(8, "CREATE TYPE {}.{} {{".format(schema, typename))
            self.pdf.ln(5)
            for row in value:
                self.pdf.write(8, row)
                self.pdf.ln(5)
            self.pdf.l_margin -= 5
            self.pdf.ln(0)
            self.pdf.write(8, "}")
            self.pdf.ln(15)


def main(argv=None):
    parser = ArgumentParser()
    group = parser.add_argument_group("Database Options")
    group.add_argument("--dbname", action="store", dest="dbname", help="Database name", required=True)
    group.add_argument("--dbhost", action="store", dest="dbhost", default="localhost",  help="Database host")
    group.add_argument("--dbuser", action="store", dest="dbuser", help="Database username")
    group.add_argument("--dbpass", action="store", dest="dbpass", help="Database password")
    group.add_argument("--dbschema", action="store", dest="dbschema", help="Database schema")
    group = parser.add_argument_group("Output options")
    group.add_argument("--output-function-info", action="store_true", dest="output_functions", help="Output function information")
    group.add_argument("--output-types", action="store_true", dest="output_types", help="Output composite type information")
    group.add_argument("--filename", action="store", dest="filename", help="PDF file name")
    parser.set_defaults(output_functions=True)
    parser.set_defaults(output_types=True)
    options = parser.parse_args()
    dbschema = options.dbschema or None
    filename = options.filename or 'reference.pdf'
    ref_obj = PgReference(options.dbhost, options.dbname, options.dbuser, options.dbpass)
    with ref_obj:
        if ref_obj.connect() is None:
            print("Use --help for more info.")
            sys.exit(1)
        ref_obj.open_pdf()
        if options.output_functions:
            ref_obj.create_info(dbschema)
        if options.output_types:
            ref_obj.create_types(dbschema)
        ref_obj.save_pdf(filename)
        sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
