from flask_table import Table, Col, create_table

class DataTable():

  def __init__(self, data):
    columns = create_table()
    columns.add_column("Name", Col("Name"))
    columns.add_column("Rating", Col("Rating"))
    self.table = columns(data)
    
  def getHTML(self):
    return self.table.__html__()