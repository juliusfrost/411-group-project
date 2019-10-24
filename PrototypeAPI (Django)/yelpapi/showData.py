import django_tables2 as tables

class DataTable(tables.Table):
    name = tables.Column()

def genTable(data):
    table = DataTable(data)
    return table.as_html()
