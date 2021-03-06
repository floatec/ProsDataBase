__author__ = 'tieni'

import json
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from models import *
from forms import *
from response import Error
import historyfactory


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


def modifyUserRights(request):
    jsonRequest = json.loads(request.raw_post_data)

    messages = list()  # message for writing into history
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

            message = _("User ").__unicode__() + userObj["name"] + ": "
            if activeChanged:
                if user.is_active:
                    message += _("has been activated, ").__unicode__()
                else:
                    message += _("has been deactivated, ").__unicode__()
            if tableCreatorChanged:
                if user.tableCreator:
                    message += _("can create tables now, ").__unicode__()
                else:
                    message += _("cannot create tables anymore, ").__unicode__()
            if userManagerChanged:
                if user.userManager:
                    message += _("has become user manager.").__unicode__()
                else:
                    message += _("is no user manager anymore.").__unicode__()
            if message[-2:] == ", ":
                message = message[:-2]
            messages.append(message)

    history = None
    for message in messages:
        history = historyfactory.writeAuthHistory(history, request.user, HistoryAuth.USER_MODIFIED, message)
    return HttpResponse(json.dumps({"success": _("Successfully modified user rights.").__unicode__()}), content_type="application/json")


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

    msgs = historyfactory.printGroup(jsonRequest["name"])
    history = None
    for msg in msgs:
        history = historyfactory.writeAuthHistory(history, request.user, HistoryAuth.GROUP_CREATED, msg)
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
    message = _("Group: ").__unicode__() + jsonRequest["name"] + "."
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

    historyfactory.writeAuthHistory(None, request.user, HistoryAuth.GROUP_DELETED, name)
    return HttpResponse(json.dumps({"success": _("Successfully deleted group ").__unicode__() + name + "."}), content_type="application/json")


def checkMyPassword(request):
    jsonRequest = json.loads(request.body)

    if request.user.check_password(jsonRequest["password"]):
        return HttpResponse(json.dumps({"success": _("Successfully changed password").__unicode__()}), content_type="application/json")
    return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Wrong password.").__unicode__()}]}), content_type="application/json")


def changeMyPassword(request):
    jsonRequest = json.loads(request.raw_post_data)
    request.user.set_password(jsonRequest["password"])
    request.user.save()
    return HttpResponse(json.dumps({"success" : _("Saved password successfully.")}),content_type="application/jon")