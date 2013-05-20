from ProsDataBase.database.models import Column *
def insertDataset(request, table_id, template='ProsDataBase/templates/dataset.html'):
    """Render insert mask for dataset"""
    structure=Column.objects.filter(tabele.id=table_id)


    return render(request, template, {
        'structure': strcuture,
    })