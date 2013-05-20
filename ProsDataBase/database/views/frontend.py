from ..models import *
from django.shortcuts import render
def insertDataset(request, table_id=1, template='dataset.html'):
    """Render insert mask for dataset"""
    structure=Column.objects.filter(table=table_id)


    return render(request, template, {
        'strcuture': structure
    })