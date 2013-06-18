from ..models import *
from django.shortcuts import render
def insertDataset(request, tableName, template='dataset.html'):
    """Render insert mask for dataset"""
    table = Table.objects.get(name=tableName, deleted=False)
    structure = Column.objects.filter(table=table)


    return render(request, template, {
        'strcuture': structure
    })