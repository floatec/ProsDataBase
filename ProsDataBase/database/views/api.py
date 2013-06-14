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
    if request.method == 'POST':
        return modifyUserRights(request)


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
        return tablefactory.modifyCategories(request)


def category(request, name):
    if request.method == 'DELETE':
        return tablefactory.deleteCategory(name)


def tables(request):
    if request.method == 'GET':
        return showAllTables(request.user)
    if request.method == 'POST':
        return tablefactory.createTable(request)


def table(request, name):
    if request.method == 'GET':
        return showTable(name, request.user)
    if request.method == 'POST':
        return tablefactory.insertData(request, name)
    if request.method == 'PUT':
        return tablefactory.modifyTable(request, name)
    if request.method == "DELETE":
        return tablefactory.deleteTable(name, request.user)


def tableRights(request, tableName):
    if request.method == 'GET':
        return showTableRights(tableName)


def column(request, tableName, columnName):
    if request.method == 'DELETE':
        answer = tablefactory.deleteColumn(tableName, columnName, request.user)
        if not answer:
            return HttpResponse(json.dumps({"errors": [answer]}), content_type="application/json")
        else:
            return HttpResponse("Successfully deleted column " + columnName + " from table " + tableName + ".", status=200)


def export(request, tableName):
    if request.method == 'POST':
        return tablefactory.exportTable(json.loads(request), tableName, request.user)


def datasets(request, tableName):
    if request.method == 'POST':
        #if request.user.mayReadTable(tableName):
        return showDatasets(request, tableName)  # request.user)
        #else:
        #    return HttpResponse("Permission denied", status=403)
    if request.method == 'DELETE':
        #if request.user.mayDeleteTable(tableName):
        return tablefactory.deleteDatasets(request, tableName)
       # else:
       #     return HttpResponse("Permission denied", status=403)


def filterDatasets(request, tableName):
    if request.method == 'POST':
        datasets = DatasetSerializer.serializeBy(json.loads(request.raw_post_data), tableName, request.user)
        if datasets is None:
            return HttpResponse(content="An error occured", status=500)
        return HttpResponse(json.dumps(datasets), content_type="application/json")


def dataset(request, tableName, datasetID):
    if request.method == 'GET':
        return showDataset(tableName, datasetID, user)
    elif request.method == 'PUT':
        return tablefactory.modifyData(request, tableName, datasetID)


def register(request):
    jsonRequest = json.loads(request.raw_post_data)
    try:
        DBUser.objects.get(username=jsonRequest["username"])
        return HttpResponse("user with name " + jsonRequest["username"] + " already exists.", status=400)
    except DBUser.DoesNotExist:
        user = DBUser.objects.create_user(username=jsonRequest["username"], password=jsonRequest["password"])
        user.save()
        return HttpResponseRedirect("/login/")


def login(request):
    jsonRequest = json.loads(request.raw_post_data)
    user = auth.authenticate(username=jsonRequest["username"], password=jsonRequest["password"])
    if user is not None and user.is_active:
        auth.login(request, user)
        return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"status": "not_ok"}), content_type="application/json")


def logoff(request):
    auth.logout(request)
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


def modifyUserRights(request):
    jsonRequest = json.loads(request.raw_post_data)

    for userObj in jsonRequest["users"]:
        modified = False
        try:
            user = DBUser.objects.get(username=userObj["name"])
        except DBUser.DoesNotExist:
            HttpResponse("Could not find user with name " + userObj["name"] + ".", status=400)

        if userObj["tableCreator"] != user.tableCreator\
                or userObj["userManager"] != user.userManager\
                or userObj["active"] != user.is_active:
            modified = True

        user.tableCreator = userObj["tableCreator"]
        user.userManager = userObj["userManager"]
        user.is_active = userObj["active"]
        if modified:
            user.save()

    return HttpResponse("Successfully modified user rights.", status=200)


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


def showTableRights(name):
    rights = TableSerializer.serializeRightsFor(name)
    return HttpResponse(json.dumps(rights), content_type="application/json")


def tableStructure(request, name):
    if request.method == 'GET':
        structure = TableSerializer.serializeStructure(name, request.user)
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


def showAllTables(user):
    tables = TableSerializer.serializeAll(user)
    return HttpResponse(json.dumps(tables), content_type="application/json") if tables is not None \
        else HttpResponse(status=500)


def showTable(name, user):
    table = TableSerializer.serializeOne(name, user)
    return HttpResponse(json.dumps(table), content_type="application/json")