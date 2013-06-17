__author__ = 'tieni'

from datetime import datetime
from django.utils.translation import ugettext_lazy as _

from forms import *
from serializers import *


def writeTableHistory(history, table, user, type, message=""):
    if history is None:  # create a new history entry
        historyF = HistoryTableForm({"date": datetime.now(), "type": type})
        if historyF.is_valid():
            history = historyF.save(commit=False)
            history.table = table
            history.user = user
            history.save()

    messageF = MessageTableForm({"content": message})
    message = messageF.save(commit=False)
    message.history = history
    message.save()
    return history


def printRightsFor(tableName):
    serial = TableSerializer.serializeRightsFor(tableName)

    result = ""
    for actor in serial["actors"]:
        #  check if user or group
        try:
            DBUser.objects.get(username=actor["name"])
            user = True
        except DBUser.doesNotExist:
            DBGroup.objects.get(name=actor["name"])
            user = False
        if user:
            result += _("User ").__unicode__() + actor["name"] + _(" may ").__unicode__()
        else:
            result += _("Group ").__unicode__() + actor["name"] + _(" may ").__unicode__()

        # table rights
        if actor["tableRights"]["viewLog"]:
            result += "view the table log, "
        if actor["tableRights"]["rightsAdmin"]:
            result += "modify the table, "
        if actor["tableRights"]["insert"]:
            result += "insert datasets, "
        if actor["tableRights"]["delete"]:
            if result[-2:] == ", ":
                result = result[:-2] + " and delete datasets"
            else:
                result += "delete datasets"
        if result[-2:] == ", ":  # cut off trailing comma
            result = result[:-2]

        # column rights
        if len(actor["columnRights"]) > 0:
            result += ". Column rights:"
            for column in actor["columnRights"]:
                result += "\n" + column["name"] + ": "
                if column["rights"]["read"]:
                    result += "read, "
                if column["rights"]["modify"]:
                    if result[-2:] == ", ":
                        result = result[:-2] + " and modify"
                    else:
                        result += "modify"
                if result[-2:] == ", ":  # cut off trailing comma
                    result = result[:-2]

        if result[-1] != "\n":  # new line for next actor
            result += "\n"

    if result[-1] == "\n":  # cut off trailing new line
        result = result[:-1]

    return result