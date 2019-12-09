import django_tables2 as tables

class DataTable(tables.Table):
    name = tables.Column(verbose_name="Name", orderable=False)
    rating = tables.Column(verbose_name="Rating", orderable=False)
    price = tables.Column(verbose_name="Price Range", orderable=False)

def genTable(request, data):
    table = DataTable(data)
    return table.as_html(request)
