__author__ = 'tieni'

from datetime import datetime
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from forms import *
from serializers import *


def writeAuthHistory(history, user, type, message=""):
    """
    write messages to the user management history.

    If history is None, a new history object is created and messages are added to it.
    type can be:
    GROUP_CREATED
    GROUP_MEMBER_ADDED
    GROUP_MEMBER_REMOVED
    GROUP_MODIFIED
    GROUP_DELETED
    USER_REGISTERED
    USER_MODIFIED
    """
    if history is None:  # create a new history entry
        historyF = HistoryAuthForm({"date": datetime.utcnow().replace(tzinfo=utc), "type": type})
        if historyF.is_valid():
            history = historyF.save(commit=False)
            history.user = user
            history.save()

    if len(message) > 0:
        messageF = MessageAuthForm({"content": message})
        message = messageF.save(commit=False)
        message.history = history
        message.save()
    return history


def writeTableHistory(history, table, user, type, message=""):
    """
    write messages to a table's history.

    If history is None, a new history object is created and messages are added to it.
    type can be:
    TABLE_CREATED
    TABLE_DELETED
    TABLE_MODIFIED
    DATASET_INSERTED
    DATASET_DELETED
    DATASET_MODIFIED
    EXPORT
    """
    if history is None:  # create a new history entry
        historyF = HistoryTableForm({"date": datetime.utcnow().replace(tzinfo=utc), "type": type})
        if historyF.is_valid():
            history = historyF.save(commit=False)
            history.table = table
            history.user = user
            history.save()

    if len(message) > 0:
        messageF = MessageTableForm({"content": message})
        message = messageF.save(commit=False)
        message.history = history
        message.save()
    return history


def printGroup(groupName):
    """
    returns a human readable string of the group, its users and rights.
    """
    serial = GroupSerializer.serializeOne(groupName)

    result = "Name: " + groupName + "."
    if serial["tableCreator"]:
        result += "\n Can create tables."
    result += "\n Users: "

    for userName in serial["users"]:
        result += userName + ", "

    result = result[:-2]  # cut off trailing comma

    if len(serial["users"]) == 0:
        result += "no users yet."

    return result


def printRightsFor(tableName):
    """
    returns a human readable string for a table and all access rights on it.
    """
    serial = TableSerializer.serializeRightsFor(tableName)
    if serial is None:
        return None
    result = list()
    for actor in serial["actors"]:
        message = ""
        #  check if user or group
        try:
            DBUser.objects.get(username=actor["name"])
            user = True
        except DBUser.DoesNotExist:
            DBGroup.objects.get(name=actor["name"])
            user = False
        if user:
            message += _("User ").__unicode__() + actor["name"] + _(" may ").__unicode__()
        else:
            message += _("Group ").__unicode__() + actor["name"] + _(" may ").__unicode__()

        # table rights
        if actor["tableRights"]["viewLog"]:
            message += _("view the table log, ").__unicode__()
        if actor["tableRights"]["rightsAdmin"]:
            message += _("modify the table, ").__unicode__()
        if actor["tableRights"]["insert"]:
            message += _("insert datasets, ").__unicode__()
        if actor["tableRights"]["delete"]:
            if message[-2:] == ", ":
                message = message[:-2] + _(" and delete datasets").__unicode__()
            else:
                message += _("delete datasets").__unicode__()
        if message[-2:] == ", ":  # cut off trailing comma
            message = message[:-2]

        # column rights
        if len(actor["columnRights"]) > 0:
            message += _(". Column rights:").__unicode__()
            for column in actor["columnRights"]:
                if not column["rights"]["read"] and not column["rights"]["modify"]:
                    continue
                message += "\n" + column["name"] + ": "
                if column["rights"]["read"]:
                    message += _("read, ").__unicode__()
                if column["rights"]["modify"]:
                    if message[-2:] == ", ":
                        message = message[:-2] + _(" and modify").__unicode__()
                    else:
                        message += _("modify").__unicode__()
                if message[-2:] == ", ":  # cut off trailing comma
                    message = message[:-2]

        if message[-1] != "\n":  # new line for next actor
            message += ". \n"
        result.append(message)

    return result


def printDataset(datasetID, user):
    """
    returns a human readable string of the dataset and its content.
    """
    serial = DatasetSerializer.serializeOne(datasetID, user)

    result = "System ID: " + str(serial["id"]) + "\n"

    for data in serial["data"]:
        result += _("In column ").__unicode__() + unicode(data["column"]) + ": " + unicode(data["value"]) + "\n"

    if result[-1] == "\n":
        result = result[:-1]

    return result