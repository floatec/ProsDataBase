# Create your views here.
# -*- coding: UTF-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
import json
from django.contrib import auth

from ..response import *
from ..serializers import *
from ..forms import *
from .. import tablefactory
from .. import historyfactory
from django.utils.translation import ugettext_lazy as _


def session(request):
    """
    api calls for registering, logging on and logging off.

    url: /api/session/
    POST: register. This action will be logged.
    PUT: login
    DELETE: logoff
    """
    if request.method == 'POST':
        return register(request)
    elif request.method == 'PUT':
        return login(request)
    elif request.method == 'DELETE':
        return logoff(request)


def users(request):
    """
    api for getting a list of all usernames

    url: /api/user/
    GET: get a list of all usernames
    """
    if request.method == 'GET':
        return showAllUsers()


def user(request, name):
    """
    api for getting one user and his permissions

    url: /api/user/[username]/
    GET: get one user and his permissions
    possible permissions are: admin, tablecreator and usermanager
    """
    if request.method == 'GET':
        return showOneUser(name)


def userRights(request):
    """
    api for managing user permissions

    url: /api/user/rights/
    GET: get all users and their permissions
    POST: set permissions for a list of users. This action will be logged.
    possible permissions are: admin, tablecreator and usermanager
    You must have user manager or admin status to make this request.
    """
    if request.user.userManager or request.user.admin:
        if request.method == 'GET':
            return showUserRights(request)
        if request.method == 'POST':
            return modifyUserRights(request)
    else:
        return HttpResponse(json.dumps({"errors": [{"message": _("You have no permissions to perform this opperation.").__unicode__()}]}), content_type="application/json")


def groups(request):
    """
    api for managing groups

    url: /api/group/
    GET: get a list of all groups
    POST: create a new group. You must have user manager or admin status to make a POST request.
    The POST request will be logged.
    """
    if request.method == 'GET':
        return showAllGroups()
    elif request.method == 'POST':
        if request.user.userManager or request.user.admin:
            return addGroup(request)
        else:
            return HttpResponse(json.dumps({"errors": [{"message": _("You have no permissions to perform this opperation.").__unicode__()}]}), content_type="application/json")


def group(request, name):
    """
    api for managing one group

    url: /api/group/[name]/
    GET: get one group with its members
    PUT: edit the group's members and its table creator status
    DELETE: delete the group
    You need user manager or admin status to make this request.
    PUT and DELETE requests will be logged.
    """
    try:
        DBGroup.objects.get(name=name)
    except DBGroup.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.GROUP_NOTFOUND, "message": _("This page does not exist!").__unicode__()}]}), content_type="application/json")
    if request.method == 'GET':
        return showOneGroup(name)
    if request.user.userManager or request.user.admin:
        if request.method == 'PUT':
            return modifyGroup(request, name)
        if request.method == 'DELETE':
            return deleteGroup(request, name)
    else:
        return HttpResponse(json.dumps({"errors": [{"message": _("You have no permissions to perform this opperation.").__unicode__()}]}), content_type="application/json")


def myself(request):
    """
    api for getting the permissions of the logged-in user

    url: /api/myself/
    GET: get your own permissions
    possible permissions are table creator, user manager or admin
    """
    if request.method == 'GET':
        return showMyUser(request.user.username)


def myPassword(request):
    """
    api for password management

    url: /api/myself/password/
    POST: check your password
    PUT: change your password
    """
    if request.method == 'POST':
        return checkMyPassword(request)
    if request.method == 'PUT':
        return changeMyPassword(request)


def categories(request):
    """
    api for managing table categories

    url: /api/category/
    GET: get a list of all categories
    PUT: add new categories or change the name of existing ones. You need to be admin to make PUT requests.
    """
    if request.method == 'GET':
        return showCategories()
    if request.user.admin:
        if request.method == 'PUT':
            return tablefactory.modifyCategories(json.loads(request.body))
    else:
        return HttpResponse(json.dumps({"errors": [{"message": _("You have not the rights to do this opperation").__unicode__()}]}), content_type="application/json")


def category(request, name):
    """
    api for deleting a category

    url: /api/category/[name]/
    DELETE: delete this category. You need to be admin to make this request.
    """
    if request.user.admin:
        if request.method == 'DELETE':
            return tablefactory.deleteCategory(name)
    else:
        return HttpResponse(json.dumps({"errors":[{"message": _("You have not the rights to do this opperation").__unicode__()}]}), content_type="application/json")


def tables(request):
    """
    api for showing or creating tables

    url: /api/table/
    GET: get all tables with their columns for which you have access rights
    POST: create a new table. You need to be a table creator or admin to perform this task. This request will be logged.
    """
    if request.method == 'GET':
        return showAllTables(request.user)
    if request.method == 'POST':
        if request.user.admin or request.user.tableCreator:
            return tablefactory.createTable(json.loads(request.body), request.user)


def table(request, name):
    """
    api for managing one table

    url: /api/table/[name]/
    GET: get the table and all its datasets. You need to have access rights to at least one column to see datasets
    POST: insert a new dataset to the table. Requires permission to insert data
    PUT: edit the table's structure, name and category. You need admin rights on this table to do this.
    DELETE: remove this table. It will be hidden but not deleted entirely. You need table admin rights on this table to do this.
    All requests except the GET request will be logged.
    """
    try:
        Table.objects.get(name=name, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("This page does not exist!").__unicode__()}]}), content_type="application/json")
    if request.method == 'GET':
        return showTable(name, request.user)
    if request.method == 'POST':
        return tablefactory.insertData(request, name)
    if request.method == 'PUT':
        return tablefactory.modifyTable(request, name)
    if request.method == "DELETE":
        return tablefactory.deleteTable(name, request.user)


def tableRights(request, tableName):
    """
    api for editing access rights on a table

    url: /api/table/[name]/rights
    PUT: edit access rights for users and groups. This action will be logged.
    GET: show all users and groups and their permissions on this table.
    possible permission are: administration (that is the permission to modify the table structure and access rights for other users),
    log viewing, inserting data, deleting data, reading data and modifying existing data.
    """
    try:
        Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("This page does not exist!").__unicode__()}]}), content_type="application/json")
    if request.method == 'PUT':
        return tablefactory.modifyTableRights(json.loads(request.raw_post_data), tableName, request.user)
    if request.method == 'GET':
        return showTableRights(tableName)


def column(request, tableName, columnName):
    """
    api for deleting one column

    url: /api/table/[tablename]/column/[columnname]/
    DELETE: delete the column. You need admin rights on this table to perform this task.
    The column will only be hidden but not deleted from the database entirely.
    This action will be logged.
    """
    if request.method == 'DELETE':
        answer = tablefactory.deleteColumn(tableName, columnName, request.user)
        if not answer:
            return HttpResponse(json.dumps({"errors": [answer]}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"success": _("Successfully deleted column ").__unicode__() + columnName + _(" from table ").__unicode__() + tableName + "."}), content_type="application/json")


def export(request, tableName):
    """
    api for exporting a table's datasets to CSV

    url: /api/table/[name]/export/
    POST: export a specified list of datasetes from this table to CSV.
    You can only export data from columns for which you have read permission.
    """
    if request.method == 'POST':
        return tablefactory.exportTable(json.loads(request.raw_post_data), tableName)


def tableHistory(request, tableName):
    """
    api for reading a table's log.

    url: /api/table/[name]/history/
    GET: read the table's history. You need to have log viewing permission to perform this task.
    Logged actions are: the table creation, table structure modifications, table deletion, access rights modifications,
    dataset insertion, dataset modification and dataset deletion.
    """
    if request.method == 'GET':
        response = TableSerializer.serializeHistory(tableName)
        if not response:
            return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table with name ").__unicode__() + tableName + "."}]}), content_type="application/json")
        return HttpResponse(json.dumps(response), content_type="application/json")


def history(request):
    """
    api for reading the general history log.

    url: /api/history/
    GET: get all logs, that is from all tables and from the user management.
    You need admin rights to perform this task.
    Logged actions for tables: the table creation, table structure modifications, table deletion, access rights modifications,
    dataset insertion, dataset modification and dataset deletion.
    Logged actions for user management: user registration, user rights modification, group creation, group modification, group deletion
    """
    if not request.user.admin:
        return HttpResponse(json.dumps({"errors": [{"code": Error.RIGHTS_NO_ADMIN, "message": _("You have no right to view the log.").__unicode__()}]}))
    return HttpResponse(json.dumps(HistorySerializer.serializeHistory()), content_type="application/json")


def datasets(request, tableName):
    """
    api for reading or deleting a tables datasets

    url: /api/table/[name]/dataset/
    POST: show the requested datasets. You need read permission on at least one of the table's columns
    DELETE: delete a list of specified datasets. You need data deletion rights to do this.
    """
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
            return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_NOTFOUND, "message": _("No matching datasets.").__unicode__()}]}), content_type="application/json")
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
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("user with name ").__unicode__() + jsonRequest["username"] + _(" already exists.").__unicode__()}]}),content_type="application/json")
    except DBUser.DoesNotExist:
        user = DBUser.objects.create_user(username=jsonRequest["username"], password=jsonRequest["password"])
        user.save()
        historyfactory.writeAuthHistory(None, request.user, HistoryAuth.USER_REGISTERED, user.username)
        return HttpResponse(json.dumps({"success": _("Created account successfully.").__unicode__()}), content_type="application/json")


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
    return HttpResponse(_("logged off"))


def showAllUsers():
    users = UserSerializer.serializeAll()
    return HttpResponse(json.dumps(users), content_type="application/json")


def showOneUser(name):
    user = UserSerializer.serializeOne(name)
    if user is None:
        return HttpResponse(json.dumps({"errors": [{"code": -1, "message": _("User does not exist").__unicode__()}]}), content_type="application/json")
    else:
        return HttpResponse(json.dumps(user), content_type="application/json")


def showUserRights(request):
    rights = UserSerializer.serializeAllWithRights(request.user)
    return HttpResponse(json.dumps(rights), content_type="application/json")


def modifyUserRights(request):
    jsonRequest = json.loads(request.raw_post_data)

    message = ""  # message for writing into history
    for userObj in jsonRequest["users"]:
        try:
            user = DBUser.objects.get(username=userObj["name"])
            if user is request.user:
                continue
        except DBUser.DoesNotExist:
            HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Could not find user with name ").__unicode__() + userObj["name"] + "."}]}), content_type="application/json")

        # for tracking changes made
        tableCreatorChanged = False
        userManagerChanged = False
        activeChanged = False
        modified = False

        if userObj["tableCreator"] != user.tableCreator:
            modified = True
            tableCreatorChanged = True
        if userObj["userManager"] != user.userManager:
            modified = True
            userManagerChanged = True
        if userObj["active"] != user.is_active:
            modified = True
            activeChanged = True

        user.tableCreator = userObj["tableCreator"]
        user.userManager = userObj["userManager"]
        user.is_active = userObj["active"]
        if modified:
            user.save()

            message += "User " + userObj["name"] + ": "
            if activeChanged:
                if user.is_active:
                    message += "has been activated, "
                else:
                    message += "has been deactivated, "
            if tableCreatorChanged:
                if user.tableCreator:
                    message += "can create tables now, "
                else:
                    message += "cannot create tables anymore, "
            if userManagerChanged:
                if user.userManager:
                    message += "has become user manager."
                else:
                    message += "is no user manager anymore."
            message += "\n"  # cut off trailing comma

    historyfactory.writeAuthHistory(None, request.user, HistoryAuth.USER_MODIFIED, message)
    return HttpResponse(json.dumps({"success": _("Successfully modified user rights.").__unicode__()}), content_type="application/json")


def showAllGroups():
    groups = GroupSerializer.serializeAll()
    return HttpResponse(json.dumps(groups), content_type="application/json")


def showOneGroup(name):
    group = GroupSerializer.serializeOne(name)
    return HttpResponse(json.dumps(group), content_type="application/json")


def addGroup(request):
    jsonRequest = json.loads(request.raw_post_data)

    groupNames = list()
    for name in DBGroup.objects.all():
        groupNames.append(name)

    if jsonRequest["name"] in groupNames:
        HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Group with name ").__unicode__() + jsonRequest["name"] + _(" already exists.").__unicode__()}]}), content_type="application/json")

    groupF = DBGroupForm({"name": jsonRequest["name"]})
    if groupF.is_valid():
        newGroup = groupF.save(commit=False)
        newGroup.tableCreator = jsonRequest["tableCreator"]
        newGroup.save()

        failed = list()  # list of users whose names could not be found in the database

        for userName in set(jsonRequest["users"]):
            try:
                user = DBUser.objects.get(username=userName)
            except DBUser.DoesNotExist:
                if len(userName) > 0:
                    failed.append(userName)
                continue
            membership = Membership(group=newGroup, user=user)
            membership.save()

    if len(failed) > 0:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("following users could not be added to the group: ") + str(failed) + _(". Have you misspelled them?")}]}), content_type="application/json")

    message = historyfactory.printGroup(jsonRequest["name"])
    historyfactory.writeAuthHistory(None, request.user, HistoryAuth.GROUP_CREATED, message)
    return HttpResponse(json.dumps({"success": _("Successfully saved group ").__unicode__() + jsonRequest["name"] + "."}), content_type="application/json")


def modifyGroup(request, name):
    """
    {
        "name": "group1",
        "users": ["John Doe","Alex Anonymus"],
        "admins": ["admin1", "admin2"],
        "tableCreator": true,
    }
    """
    try:
        group = DBGroup.objects.get(name=name)
    except DBGroup.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Could not find group with name ").__unicode__() + name + "."}]}), content_type="application/json")

    # will hold content for history entry
    oldName = None
    tableCreatorChanged = False
    userRemoved = list()
    userAdded = list()

    jsonRequest = json.loads(request.raw_post_data)
    if jsonRequest["name"] != group.name:
        try:
            DBGroup.objects.get(name=jsonRequest["name"])
            return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("A group with name ").__unicode__() + jsonRequest["name"] + _(" already exists.").__unicode__()}]}), content_type="application/json")
        except DBGroup.DoesNotExist:
            oldName = group.name
            group.name = jsonRequest["name"]

    if jsonRequest["tableCreator"] != group.tableCreator:
        tableCreatorChanged = True
        group.tableCreator = jsonRequest["tableCreator"]
    group.save()

    usernames = list()
    for m in Membership.objects.filter(group=group):
        usernames.append(m.user.username)

    sendUsers = set(jsonRequest["users"])

    for user in set(sendUsers) - set(usernames):  # new users were added to the group
        if len(user) > 0:  # workaround. frontend always sends one empty string
            membershipF = MembershipForm({"isAdmin": False})
            if membershipF.is_valid():
                membership = membershipF.save(commit=False)
                membership.user = DBUser.objects.get(username=user)
                membership.group = group
                membership.save()
            userAdded.append(user)

    for user in set(usernames) - set(sendUsers):  # users were deleted from the group
        theUser = DBUser.objects.get(username=user)
        membership = Membership.objects.get(user=theUser, group=group)
        membership.delete()
        userRemoved.append(user)

    # write modification to history
    message = "Group " + jsonRequest["name"] + ":"
    history = historyfactory.writeAuthHistory(None, request.user, HistoryAuth.GROUP_MODIFIED, message)
    if oldName is not None:
        message = _("Changed name from '").__unicode__() + oldName + _("' to '").__unicode__() + jsonRequest["name"] + "'."
        historyfactory.writeAuthHistory(history, request.user, HistoryAuth.GROUP_MODIFIED, message)
    if tableCreatorChanged:
        if group.tableCreator:
            message = "Can now create tables."
        else:
            message = "Cannot create tables anymore."
        historyfactory.writeAuthHistory(history, request.user, HistoryAuth.GROUP_MODIFIED, message)
    if len(userAdded) > 0:
        message = "New users: "
        for user in userAdded:
            message += user + ", "
        message = message[:-2]  # cut off trailing comma
        historyfactory.writeAuthHistory(history, request.user, HistoryAuth.GROUP_MODIFIED, message)
    if len(userRemoved) > 0:
        message = "Removed users: "
        for user in userRemoved:
            message += user + ", "
        message = message[:-2] + "\n"  # cut off trailing comma
        historyfactory.writeAuthHistory(history, request.user, HistoryAuth.GROUP_MODIFIED, message)

    return HttpResponse(json.dumps({"success": _("Successfully modifed group ").__unicode__() + name + "."}), content_type="applciation/json")


def deleteGroup(request, name):
    try:
        group = DBGroup.objects.get(name=name)
    except DBGroup.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Could not find group with name ").__unicode__() + name + "."}]}), content_type="application/json")

    Membership.objects.filter(group=group).delete()
    group.delete()

    historyfactory.writeAuthHistory(None, request.user, HistoryAuth.GROUP_DELETED)
    return HttpResponse(json.dumps({"success": _("Successfully deleted group ").__unicode__() + name + "."}), content_type="application/json")


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
    #TODO JSON
    return HttpResponse(json.dumps({"success" : _("Saved password successfully.")}),content_type="application/jon")


def showCategories():
    categories = TableSerializer.serializeCategories()
    return HttpResponse(json.dumps(categories), content_type="application/json")


def showTableRights(name):
    rights = TableSerializer.serializeRightsFor(name)
    return HttpResponse(json.dumps(rights), content_type="application/json")


def tableStructure(request, name):
    try:
        Table.objects.get(name=name, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("This page does not exist!").__unicode__()}]}), content_type="application/json")
    if request.method == 'GET':
        structure = TableSerializer.serializeStructure(name, request.user)
        return HttpResponse(json.dumps(structure), content_type="application/json")


def showDatasets(request, tableName):
    try:
        Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Could not find table with name ").__unicode__() + tableName + "."}]}), content_type="application/json")

    jsonRequest = json.loads(request.raw_post_data)
    result = dict()
    result["datasets"] = list()
    for obj in jsonRequest["datasets"]:
        result["datasets"].append(DatasetSerializer.serializeOne(obj["id"], request.user))

    return HttpResponse(json.dumps(result), content_type="application/json")


def showDataset(tableName, datasetID, user):
    try:
        table = Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Table with name ").__unicode__() + tableName + _(" could not be found.").__unicode__()}]}), content_type="application/json")
    try:
        dataset = Dataset.objects.get(datasetID=datasetID, table=table)
    except Dataset.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("dataset with id ").__unicode__() + datasetID + _(" could not be found in table ").__unicode__() + tableName + "."}]}), content_type="application/json")

    if dataset.deleted:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("The requested dataset does not exist.").__unicode__()}]}),content_type="application/json")
    else:
        dataset = DatasetSerializer.serializeOne(datasetID, user)
        return HttpResponse(json.dumps(dataset), content_type="application/json")


def showAllTables(user):
    tables = TableSerializer.serializeAll(user)
    return HttpResponse(json.dumps(tables), content_type="application/json") if tables is not None \
        else HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Table could not be found").__unicode__()}]}),content_type="application/json")


def showTable(name, user):
    table = TableSerializer.serializeOne(name, user)
    return HttpResponse(json.dumps(table), content_type="application/json")