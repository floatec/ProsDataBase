from database.models import *
from database.forms import *

def create_table(**kwargs):
    """ creates a table"""

    table = dict()
    table["name"] = "Test"
    table["created"] = datetime.now()
    tabF = TableForm(table)
    if tabF.is_valid():
        newTable = tabF.save()

    column = dict()
    column["name"] = "A"
    column["required"] = True
    column["created"] = datetime.now()
    colF = ColumnForm(column)
    if colF.is_valid():
        newColumn = colF.save()

    newColumn.table = newTable

    data = Data.objects.create()
