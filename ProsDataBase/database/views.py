# Create your views here.

from django.http import HttpResponse

from serializers import *
from forms import *
from datetime import datetime


def showAllTables(request):
    if request.method == 'GET':
        tables = TableSerializer.serializeAll()
        return HttpResponse(tables)


#{
#  "name": "example",
#  "admin": [4, 23, 10003],  //group ids have an offset of say 10000, to distinguish from user ids
#  "dataDescr": [
#	  {"name": "columname", "type": 1, "options": ["0": "yes", "1": "no", "2": "maybe"]},
#    {"name": "anothercolum", "type": 1, "options": ["0": "yes", "1": "no", "2": "maybe"]}
#	],
#	"rights": [
#    {"name":"columname", "read": [17, 8, 10001], "write": [22], "modify": [], "delete": []}
#  ]
#}


def AddTable(request):
    '''


    '''

    if request.method == 'POST':
        tableData = dict()
        tableData["name"] = request["name"]
        tableData["creator"] = request.user.name
        tableData["created"] = datetime.now()
        newTable(tableData)


def newTable(data):
    t = TableForm(data)
    if t.is_valid():
        t.save()

    return HttpResponse(status=200)