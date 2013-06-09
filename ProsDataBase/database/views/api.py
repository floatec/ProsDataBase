# Create your views here.
# -*- coding: UTF-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
import json
from datetime import datetime
from django.contrib import auth

from ..serializers import *
from ..forms import *
from .. import tablefactory


def session(request):
    if request.method == 'POST':
        return register(request)
    elif request.method == 'PUT':
        return login(request)
    elif request.method == 'DELETE':
        return logoff(request)


def users(request):
    if request.method == 'GET':
        return showAllUsers()


def user(request, name):
    if request.method == 'GET':
        return showOneUser(name)


def userRights(request):
    if request.method == 'GET':
        return showUserRights(request)


def groups(request):
    if request.method == 'GET':
        return showAllGroups()
    elif request.method == 'POST':
        return addGroup(request)


def group(request, name):
    if request.method == 'GET':
        return showOneGroup(name)
    if request.method == 'PUT':
        return modifyGroup(request, name)
    if request.method == 'DELETE':
        return deleteGroup(request, name)


def myself(request):
    if request.method == 'GET':
        return showMyUser(request.user.username)


def myPassword(request):
    if request.method == 'POST':
        return checkMyPassword(request)
    if request.method == 'PUT':
        return changeMyPassword(request)


def categories(request):
    if request.method == 'GET':
        return showCategories()
    if request.method == 'PUT':
        return modifyCategories(request)


def category(request, name):
    if request.method == 'DELETE':
        return deleteCategory(name)


def tables(request):
    if request.method == 'GET':
        return showAllTables(request.user)
    if request.method == 'POST':
        return tablefactory.createTable(request)


def table(request, name):
    if request.method == 'GET':
        return showTable(name, request.user)
    if request.method == 'POST':
        return insertData(request, name)
    if request.method == 'PUT':
        return tablefactory.modifyTable(request, name)
    if request.method == "DELETE":
        return deleteTable(name, request.user)


def tableRights(request, tableName):
    if request.method == 'GET':
        return showTableRights(tableName)


def column(request, tableName, columnName):
    if request.method == 'DELETE':
        answer = tablefactory.deleteColumn(tableName, columnName, request.user)
        if answer != 'OK':
            return answer
        else:
            return HttpResponse("Successfully deleted column " + columnName + " from table " + tableName + ".", status=200)


def datasets(request, tableName):
    if request.method == 'POST':
        if request.user.mayReadTable(tableName):
            return showDatasets(request, tableName, request.user)
        else:
            return HttpResponse("Permission denied", status=403)
    if request.method == 'DELETE':
        if request.user.mayDeleteTable(tableName):
            return deleteDatasets(request, tableName)
        else:
            return HttpResponse("Permission denied", status=403)


def filterDatasets(request, tableName):
    if request.method == 'POST':
        datasets = DatasetSerializer.serializeBy(json.loads(request.raw_post_data), tableName, request.user)
        return HttpResponse(json.dumps(datasets), content_type="application/json")


def dataset(request, tableName, datasetID):
    if request.method == 'GET':
        return showDataset(tableName, datasetID)
    elif request.method == 'PUT':
        return modifyData(request, tableName, datasetID)
    elif request.method == 'DELETE':
        return deleteDataset(tableName, datasetID, request.user)


def register(request):
    jsonRequest = json.loads(request.raw_post_data)
    try:
        DBUser.objects.get(username=jsonRequest["username"])
        return HttpResponse("user with name " + jsonRequest["username"] + " already exists.", status=400)
    except DBUser.DoesNotExist:
        user = DBUser.objects.create_user(username=jsonRequest["username"], email=jsonRequest["email"], password=jsonRequest["password"])
        user.is_active = True
        user.save()
        return HttpResponseRedirect("/login/")


def login(request):
    jsonRequest = json.loads(request.raw_post_data)
    user = auth.authenticate(username=jsonRequest["username"], password=jsonRequest["password"])
    if user is not None and user.is_active:
        auth.login(request, user)
        #return HttpResponseRedirect("table/")
        return HttpResponse('{"status":"ok"}')
    else:
        if user is None:
            return HttpResponse('{"status":"not_ok"}')
        if not user.is_active:
        #return HttpResponseRedirect("invalid/")
            return HttpResponse('{"status":"not_ok"}')


def logoff(request):
    auth.logout(request)
    #return HttpResponseRedirect("loggedoff/")
    return HttpResponse("logged off")


def showAllUsers():
    users = UserSerializer.serializeAll()
    return HttpResponse(json.dumps(users), content_type="application/json")


def showOneUser(name):
    user = UserSerializer.serializeOne(name)
    if user is None:
        return HttpResponse("User does not exist", status=400)
    else:
        return HttpResponse(json.dumps(user), content_type="application/json")


def showUserRights(request):
    rights = UserSerializer.serializeAllWithRights()
    return HttpResponse(json.dumps(rights), content_type="application/json")


def showAllGroups():
    groups = GroupSerializer.serializeAll()
    return HttpResponse(json.dumps(groups), content_type="application/json")


def showOneGroup(name):
    group = GroupSerializer.serializeOne(name)
    return HttpResponse(json.dumps(group), content_type="application/json")


def addGroup(request):
    request = json.loads(request.raw_post_data)

    groupNames = list()
    for name in DBGroup.objects.all():
        groupNames.append(name)

    if request["name"] in groupNames:
        HttpResponse(content="Group with name " + request["name"] + " already exists.", status=400)

    groupF = DBGroupForm({"name": request["name"]})
    if groupF.is_valid():
        newGroup = groupF.save(commit=False)
        newGroup.tableCreator = request["tableCreator"]
        newGroup.groupCreator = request["groupCreator"]
        newGroup.userManager = request["userManager"]
        newGroup.save()

        failed = list() # list of users whose names could not be found in the database
        for adminName in set(request["admins"]):
            try:
                admin = DBUser.objects.get(username=adminName)
            except DBUser.DoesNotExist:
                if len(adminName) > 0:
                    failed.append(adminName)
                continue
            membership = Membership(group=newGroup, user=admin)
            membership.isAdmin = True
            membership.save()

        for userName in set(request["users"]) - set(request["admins"]):
            try:
                user = DBUser.objects.get(username=userName)
            except DBUser.DoesNotExist:
                if len(userName) > 0:
                    failed.append(userName)
                continue
            membership = Membership(group=newGroup, user=user)
            membership.save()

    if len(failed) > 0:
        return HttpResponse({"error": "following users could not be added to the group: " + str(failed) + ". Have you misspelled them?"}, content_type="application/json")
    return HttpResponse("Successfully saved group " + request["name"] + ".", status=200)


def modifyGroup(request, name):
    """
    {
        "name": "group1",
        "users": ["John Doe","Alex Anonymus"],
        "admins": ["admin1", "admin2"],
        "tableCreator": true,
        "groupCreator": false
    }
    """
    try:
        group = DBGroup.objects.get(name=name)
    except DBGroup.DoesNotExist:
        return HttpResponse(content="Could not find group with name " + name + ".", status=400)

    request = json.loads(request.raw_post_data)
    if request["name"] != group.name:
        try:
            DBGroup.objects.get(name=request["name"])
            return HttpResponse(content="A group with name " + request["name"] + " already exists.", status=400)
        except DBGroup.DoesNotExist:
            group.name = request["name"]

    group.tableCreator = request["tableCreator"]
    group.groupCreator = request["groupCreator"]
    group.userManager = request["userManager"]
    group.save()

    usernames = list()
    adminnames = list()
    for m in Membership.objects.filter(group=group):
        if m.isAdmin:
            adminnames.append(m.user.username)
        else:
            usernames.append(m.user.username)

    sendUsers = set(request["users"]) - set(request["admins"])

    for user in set(sendUsers) - set(usernames):  # new users were added to the group
        if len(user) > 0:  # workaround. frontend always sends one empty string
            membershipF = MembershipForm({"isAdmin": False})
            if membershipF.is_valid():
                membership = membershipF.save(commit=False)
                membership.user = DBUser.objects.get(username=user)
                membership.group = group
                membership.save()

    for user in set(usernames) - set(sendUsers):  # users were deleted from the group
        theUser = DBUser.objects.get(username=user)
        membership = Membership.objects.get(user=theUser)
        membership.delete()

    for admin in set(request["admins"]) - set(adminnames):  # new admins were added to the group
        if len(admin) > 0:
            membershipF = MembershipForm({"isAdmin": True})
            if membershipF.is_valid():
                membership = membershipF.save(commit=False)
                membership.user = DBUser.objects.get(username=admin)
                membership.group = group
                membership.save()

    for admin in set(adminnames) - set(request["admins"]):  # users were deleted from the group
        theUser = DBUser.objects.get(username=admin)
        membership = Membership.objects.get(user=theUser)
        membership.delete()

    return HttpResponse("Successfully modifed group " + name + ".", status=200)


def deleteGroup(request, name):
    try:
        group = DBGroup.objects.get(name=name)
    except DBGroup.DoesNotExist:
        return HttpResponse(content="Could not find group with name " + name + ".", status=400)

    Membership.objects.filter(group=group).delete()
    group.delete()

    return HttpResponse(content="Successfully deleted group " + name + ".", status=200)


def showMyUser(user):
    myself = UserSerializer.serializeOne(user)
    return HttpResponse(json.dumps(myself), content_type="application/json")


def checkMyPassword(request):
    jsonRequest = json.loads(request.raw_post_data)

    response = dict()
    response["valid"] = request.user.check_password(jsonRequest["password"])

    return HttpResponse(json.dumps(response), content_type="application/json")


def changeMyPassword(request):
    jsonRequest = json.loads(request.raw_post_data)
    request.user.set_password(jsonRequest["password"])
    request.user.save()
    return HttpResponse("Saved password successfully.", status=200)


def showCategories():
    categories = TableSerializer.serializeCategories()
    return HttpResponse(json.dumps(categories), content_type="application/json")


def modifyCategories(request):
    """
    {
        "categories": [{"old": "name", "new": "newname"}, {"old": "name", "new": "newname"}, {"old": "name", "new": "newname"}]
    }
    """
    request = json.loads(request.raw_post_data)

    oldNotFound = list()
    newExists = list()
    for cat in request["categories"]:
        if "old" in cat:
            try:
                catForChange = Category.objects.get(name=cat["old"])
            except Category.DoesNotExist:
                oldNotFound.append(cat["old"])

            try:  # check if category with name already exists. Only save new name, if not existent yet
                Category.objects.get(name=cat["new"])
                newExists.append(cat["new"])
            except Category.DoesNotExist:
                catForChange.name = cat["new"]
                catForChange.save()

        else:
            try:  # check if category with name already exists. Only save new name, if not existent yet
                Category.objects.get(name=cat["new"])
                newExists.append(cat["new"])
            except Category.DoesNotExist:
                newCatF = CategoryForm({"name": cat["new"]})
                if newCatF.is_valid():
                    newCat = newCatF.save()
                    newCat.save()

    if len(oldNotFound) > 0:
        if len(newExists) > 0:
            return HttpResponse({"notFound": oldNotFound, "newExists": newExists}, content_type="application/json")
        return HttpResponse({"notFound": oldNotFound}, content_type="application/json")

    return HttpResponse(content="Saved changes successfully.", status=200)


def deleteCategory(name):
    try:
        category = Category.objects.get(name=name)
        try:
            Table.objects.filter(category=category)
            return HttpResponse(content="Please put the tables of this group into another category first.")
        except Table.DoesNotExist:
            category.delete()
    except Category.DoesNotExist:
        return HttpResponse(content="Category with name " + name + " does not exist.")

    return HttpResponse(content="Deleted category " + name + ".", status=400)


def showTableRights(name):
    rights = TableSerializer.serializeRightsFor(name)
    return HttpResponse(json.dumps(rights), content_type="application/json")


def tableStructure(request, name):
    if request.method == 'GET':
        structure = TableSerializer.serializeStructure(name)
        return HttpResponse(json.dumps(structure), content_type="application/json")


def showDatasets(request, tableName):
    try:
        Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="Could not find table with name " + tableName + ".", status=400)

    jsonRequest = json.loads(request.raw_post_data)
    result = dict()
    result["datasets"] = list()
    for obj in jsonRequest["datasets"]:
        result["datasets"].append(DatasetSerializer.serializeOne(obj["id"], request.user))

    return HttpResponse(json.dumps(result), content_type="application/json")


def showDataset(tableName, datasetID, user):
    try:
        table = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="Table with name " + tableName + " could not be found.", status=400)
    try:
        dataset = Dataset.objects.get(datasetID=datasetID, table=table)
    except Dataset.DoesNotExist:
        return HttpResponse(content="dataset with id " + datasetID + " could not be found in table " + tableName + ".", status=400)

    if dataset.deleted:
        return HttpResponse("The requested dataset does not exist.", status=400)
    else:
        dataset = DatasetSerializer.serializeOne(datasetID, user)
        return HttpResponse(json.dumps(dataset), content_type="application/json")


def deleteDatasets(request, tableName):
    try:
        Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="Could not find table " + tableName + " to delete from.", status=400)

    jsonRequest = json.loads(request.raw_post_data)
    deleted = list()
    for id in jsonRequest:
        try:
            dataset = Dataset.objects.get(datasetID=id)
        except Dataset.DoesNotExist:
            continue
        if dataset.deleted:
            continue
        dataset.deleted = True
        dataset.modifed = datetime.now()
        dataset.modifier = request.user
        dataset.save()
        deleted.append(id)

    return HttpResponse(json.dumps({"deleted": deleted}), content_type="application/json")


def deleteDataset(tableName, datasetID, user):
    try:
        table = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="Could not find table " + tableName + " to delete from.", status=400)
    try:
        dataset = Dataset.objects.get(datasetID=datasetID, table=table)
    except Dataset.DoesNotExist:
        return HttpResponse(content="Could not find dataset with id " + datasetID + " in table " + tableName + ".", status=400)

    if dataset.deleted:
        return HttpResponse(content="Dataset with id " + datasetID + " does not exist.", status=400)
    dataset.deleted = True
    dataset.modified = datetime.now()
    dataset.modifier = user
    dataset.save()
    return HttpResponse("Successfully deleted dataset with id " + datasetID + " from table " + tableName + ".", status=200)


def insertData(request, tableName):
    """
    Insert a dataset into a table.

    Receives data in json format:
    {
        "columns": [
            {"name": "colname1", "value": "val1"},
            {"name": "colname2", "value": ["3.2013_44_T", "3.2013_43_Q", "3.2013_45_L"], "table": "referencedTableName"} // for TypeTable columns
        ]
    }
    """
    jsonRequest = json.loads(request.raw_post_data)
    try:
        theTable = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="table with name " + tableName + " not found.", status=400)

    datasetF = DatasetForm({"created": datetime.now()})
    if not datasetF.is_valid():
        return HttpResponse(content="Error creating a new dataset.", status=500)

    newDataset = datasetF.save(commit=False)
    newDataset.table = theTable
    newDataset.creator = request.user
    newDataset.save()
    newDataset.datasetID = theTable.generateDatasetID(newDataset)
    newDataset.save()

    for col in jsonRequest["columns"]:
        try:
            column = Column.objects.get(name=col["name"], table=theTable)
        except Column.DoesNotExist:
            HttpResponse(content="Could not find a column with name " + col["name"] + "in table " + tableName + ".", status=400)
            continue
        print "col " + col["name"]
        if not column.type.getType().isValid(col["value"]):
            return HttpResponse(content="input " + unicode(col["value"]) + " for column " + column.name + " is not valid.", status=400)

        if column.type.type == Type.TEXT:
            textF = DataTextForm({"created": datetime.now(), "content": col["value"]})
            if textF.is_valid():
                newData = textF.save(commit=False)

        elif column.type.type == Type.NUMERIC:
            numF = DataNumericForm({"created": datetime.now(), "content": col["value"]})
            if numF.is_valid():
                newData = numF.save(commit=False)

        elif column.type.type == Type.DATE:
            dateF = DataDateForm({"created": datetime.now(), "content": col["value"]})
            if dateF.is_valid():
                newData = dateF.save(commit=False)

        elif column.type.type == Type.SELECTION:
            selF = DataSelectionForm({"created": datetime.now(), "content": col["value"]})
            if selF.is_valid():
                newData = selF.save(commit=False)

        elif column.type.type == Type.BOOL:
            boolF = DataBoolForm({"created": datetime.now(), "content": col["value"]})
            if boolF.is_valid():
                newData = boolF.save(commit=False)

        elif column.type.type == Type.TABLE:
            dataTblF = DataTableForm({"created": datetime.now()})
            if dataTblF.is_valid():
                newData = dataTblF.save(commit=False)

        if newData is None:
            return HttpResponse(content="Could not add data for column + " + col["name"] + ". The content type was not valid.", status=400)

        else:
            newData.creator = request.user
            newData.column = column
            newData.dataset = newDataset
            newData.save()

        if column.type.type == Type.TABLE and newData is not None:
            for index in col["value"]:  # find all datasets for this
                try:
                    dataset = Dataset.objects.get(datasetID=index)
                except Dataset.DoesNotExist:
                    return HttpResponse(content="dataset with id " + index + " could not be found in table " + column.type.getType().table.name + ".", status=400)
                else:
                    link = DataTableToDataset()
                    link.DataTable = newData
                    link.dataset = dataset
                    link.save()

    return HttpResponse(json.dumps({"id": newDataset.datasetID}), content_type="application/json", status=200)


def modifyData(request, tableName, datasetID):
    """
    Modify a table's dataset.

    Receives data in json format:
    {
        "columns": [
            {"column": "column1", "value": 0},
            {"column": "column2", "value": "2013-12-07 22:07:00"},
            {"column": "column3", "value": ["3.2013_44_T", "3.2013_43_Q", "3.2013_45_L"]}
        ]
    }
    """
    jsonRequest = json.loads(request.raw_post_data)
    try:
        theTable = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="table with name" + tableName + " not found.", status=400)
    try:
        dataset = Dataset.objects.get(datasetID=datasetID)
    except Dataset.DoesNotExist:
        return HttpResponse(content="Could not find dataset with id " + datasetID + " in table " + tableName + ".", status=400)

    dataCreatedNewly = False  # is set to True if a data element was not modified but created newly
    newData = None
    for col in jsonRequest["columns"]:
        try:
            column = Column.objects.get(name=col["name"], table=theTable)
        except Column.DoesNotExist:
            return HttpResponse("Could not find column with name " + col["name"] + ".", status=400)
            continue

        if not column.type.getType().isValid(col["value"]):
            return HttpResponse(content="input " + unicode(col["value"]) + " for column " + column.name + " is not valid.", status=400)

        if column.type.type == Type.TEXT:
            try:
                text = dataset.datatext.get(column=column)
                text.modified = datetime.now()
                text.modifier = request.user
                text.content = col["value"]
                text.save()
            except DataText.DoesNotExist:
                dataCreatedNewly = True
                textF = DataTextForm({"created": datetime.now(), "content": col["value"]})
                if textF.is_valid():
                    newData = textF.save(commit=False)

        elif column.type.type == Type.NUMERIC:
            try:
                num = dataset.datanumeric.get(column=column)
                num.modified = datetime.now()
                num.modifier = request.user
                num.content = col["value"]
                num.save()
            except DataNumeric.DoesNotExist:
                dataCreatedNewly = True
                numF = DataNumericForm({"created": datetime.now(), "content": col["value"]})
                if numF.is_valid():
                    newData = numF.save(commit=False)

        elif column.type.type == Type.DATE:
            try:
                date = dataset.datadate.get(column=column)
                date.modified = datetime.now()
                date.modifier = request.user
                date.content = col["value"]
                date.save()
            except DataDate.DoesNotExist:
                dataCreatedNewly = True
                dateF = DataDateForm({"created": datetime.now(), "content": col["value"]})
                if dateF.is_valid():
                    newData = dateF.save(commit=False)

        elif column.type.type == Type.SELECTION:
            try:
                sel = dataset.dataselection.get(column=column)
                sel.modified = datetime.now()
                sel.modifier = request.user
                sel.content = col["value"]
                sel.save()
            except DataSelection.DoesNotExist:
                dataCreatedNewly = True
                selF = DataSelectionForm({"created": datetime.now(), "content": col["value"]})
                if selF.is_valid():
                    newData = selF.save(commit=False)

        elif column.type.type == Type.BOOL:
            try:
                bool = dataset.databool.get(column=column)
                bool.modified = datetime.now()
                bool.modifier = request.user
                bool.content = col["value"]
                bool.save()
            except DataBool.DoesNotExist:
                dataCreatedNewly = True
                boolF = DataBoolForm({"created": datetime.now(), "content": col["value"]})
                if boolF.is_valid():
                    newData = boolF.save(commit=False)

        elif column.type.type == Type.TABLE:
            try:
                dataTbl = dataset.datatable.get(column=column)
                links = DataTableToDataset.objects.filter(DataTable=dataTbl)
                setIDs = list()
                #  remove all links between dataTable and datasets which are not listed in col["value"]
                for link in links:
                    setIDs.append(link.dataset_id)
                    if link.dataset_id not in col["value"]:
                        link.delete()

                #  now add any link that does not exist yet
                for id in [index for index in col["value"] if index not in setIDs]:  # this list comprehension returns the difference col["value"] - setIDs
                    try:
                        newDataset = Dataset.objects.get(datasetID=id)
                        newLink = DataTableToDataset()
                        newLink.DataTable = dataTbl
                        newLink.dataset = newDataset
                        newLink.save()
                    except Dataset.DoesNotExist:
                        return HttpResponse(content="Could not find dataset with id " + id + ".", status=400)

            except DataTable.DoesNotExist:
                dataCreatedNewly = True
                dataTblF = DataTableForm({"created": datetime.now()})
                if dataTblF.is_valid():
                    newData = dataTblF.save(commit=False)

        if dataCreatedNewly:
            if newData is None:
                return HttpResponse(content="Could not add data to column " + col["name"] + ". The content type was invalid.", status=400)

            else:
                newData.creator = request.user
                newData.column = column
                newData.dataset = Dataset.objects.get(datasetID=datasetID)
                newData.save()

            # this must be performed at the end, because DatatableToDataset receives newData, which has to be saved first
            if column.type.type == Type.TABLE and newData is not None:
                for index in col["value"]:  # find all datasets for this
                    try:
                        dataset = Dataset.objects.get(pk=index)
                        link = DataTableToDataset()
                        link.DataTable = newData
                        link.dataset = dataset
                        link.save()
                    except Dataset.DoesNotExist:
                        return HttpResponse(content="Could not find dataset with id " + index + ".", status=400)

    return HttpResponse(json.dumps({"id": dataset.datasetID}), status=200)


def showAllTables(user):
    tables = TableSerializer.serializeAll(user)
    return HttpResponse(json.dumps(tables), content_type="application/json") if tables is not None \
        else HttpResponse(status=500)


def showTable(name, user):
    table = TableSerializer.serializeOne(name, user)
    return HttpResponse(json.dumps(table), content_type="application/json")


def deleteTable(name, user):
    try:
        table = Table.objects.get(name=name)
    except Table.DoesNotExist:
        HttpResponse(content="Could not find table with name " + name + ".", status=400)

    if table.deleted:
        HttpResponse(content="Table with name " + name + " does not exist.", status=400)

    datasets = list()
    for dataset in table.datasets.all():
        datasets.append(dataset)
        dataset.deleted = True
        dataset.modified = datetime.now()
        dataset.modifier = user
        dataset.save()

    columns = list()
    for column in table.columns.all():
        answer = tablefactory.deleteColumn(table.name, column.name, user)
        if answer != 'OK':
            return answer

    table.deleted = True
    table.modified = datetime.now()
    table.modifier = user
    table.name = table.name + "_DELETED_" + str(datetime.now())
    table.save()

    for col in columns:
        col.table = table
        col.save()

    for dataset in datasets:
        dataset.table = table
        dataset.save()

    return HttpResponse(json.dumps({"deleted": table.name}), status=200)