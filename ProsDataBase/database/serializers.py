# -*- coding: utf-8 -*-
__author__ = 'My-Tien Nguyen'

from django.utils.translation import ugettext_lazy as _
from models import *


class TableSerializer:
    @staticmethod
    def serializeOne(tableName, user):
        """
        return the table with specified name, along with its columns and datasets.

        {
            "name": "example",
            "datasets": [
                {"id": 38, "data": [ {"column": "id", "type": 1, "value": 0}, "column": "columnname", "type": 0, "value": "aString"}, {"column": "anothercolumn", "type": 5, "value": [1, 2], "table": "aTableName"} ]},  //row 1
                {"id": 18, "data": [ {"column": "id", "type": 1, "value": 17}, "column": "columnname", "type": 0, "value": "aString"}, {"column": "anothercolumn", "type": 5, "value": [13, 14], "table": "aTableName"} ]}   //row 2
            ]
        }
        """
        try:
            table = Table.objects.get(name=tableName, deleted=False)
        except Table.DoesNotExist:
            return None

        result = dict()
        result["name"] = table.name
        result.update(DatasetSerializer.serializeAll(table, user))

        return result

    @staticmethod
    def serializeAll(user):
        """
        return all tables with their columns

        {
            "tables": [
                {"name": "example", "columns": ["columname","anothercolum"]},
                {"name": "2nd", "columns": ["columname","anothercolum"]}
            ]
        }
        """
        user = user
        allowedTables = set()
        memberships = Membership.objects.filter(user=user)
        groupNames = list()
        for membership in memberships:
            groupNames.append(membership.group.name)
        groups = DBGroup.objects.filter(name__in=groupNames)
        for rights in RightListForColumn.objects.filter(user=user):
            allowedTables.add(rights.table)
        for rights in RightListForColumn.objects.filter(group__in=groups, table__deleted=False):
            allowedTables.add(rights.table)
        for rights in RightListForTable.objects.filter(user=user, table__deleted=False):
            allowedTables.add(rights.table)
        for rights in RightListForTable.objects.filter(group__in=groups, table__deleted=False):
            allowedTables.add(rights.table)

        result = dict()
        result["tables"] = list()

        # first find all tables with no group
        tables = Table.objects.filter(name__in=allowedTables)
        for table in tables:
            if table.deleted:
                continue
            columns = table.getColumns()
            columnNames = []
            for col in columns:
                if col.deleted:
                    continue
                columnNames.append(col.name)

            result["tables"].append({"name": table.name, "columns": columnNames, "category": table.category.name})

        return result

    @staticmethod
    def serializeStructure(tableName, user):
        """
        return the table with its columns and the column's datatypes as well as ranges

        {
          "admin": true
          "rightsAdmin": true,
          "category": "categoryname"
          "columns": [
            {"name": "columnname0", "type": 0, "length": 100, "modify": false},
            {"name": "columnname1", "type": 1, "min": "a decimal", "max": "a decimal", "modify": false},
            {"name": "columnname2", "type": 2, "min": "a date", "max": "a date", "modify": false},
            {"name": "columnname3", "type": 3, "options": {"0": "opt1", "1": "opt2", "2": "opt3", "modify": false},
            {"name": "columnname4", "type": 4, "table": "tablename", "shownColumn": "PSA", "modify": false},
          ]
        }
        """
        table = Table.objects.get(name=tableName, deleted=False)
        if table is None:
            return None

        columns = table.getColumns()
        colStructs = []
        for col in columns:
            if col.deleted:
                continue
            comment = col.comment if col.comment is not None else ""

            try:
                rightList = RightListForColumn.objects.get(column=col, user=user)
                modify = rightList.modify
            except RightListForColumn.DoesNotExist:
                modify = True

            type = col.type.type
            if type == Type.TEXT:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.TEXT, "length": col.type.getType().length, "comment": comment, "modify": modify})
            elif type == Type.NUMERIC:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.NUMERIC, "min": col.type.getType().min, "max": col.type.getType().max, "comment": comment, "modify": modify})
            elif type == Type.DATE:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.DATE, "min": col.type.getType().min, "max": col.type.getType().max, "comment": comment, "modify": modify})

            elif type == Type.SELECTION:
                options = list()
                for value in col.type.getType().values():
                    options.append({"key": value.index, "value": value.content})
                colStructs.append({"id": col.id, "name": col.name, "type": Type.SELECTION, "options": options, "comment": comment, "modify": modify})
            elif type == Type.BOOL:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.BOOL, "comment": comment, "modify": modify})
            elif type == Type.TABLE:
                if col.type.getType().column is not None:
                    refCol = col.type.getType().column
                    colStructs.append({"id": col.id, "name": col.name, "type": Type.TABLE, "table": col.type.getType().table.name, "column": refCol.name, "refType": refCol.type.type, "comment": comment, "modify": modify})
                else:
                    colStructs.append({"id": col.id, "name": col.name, "type": Type.TABLE, "table": col.type.getType().table.name, "comment": comment, "modify": modify})
            else:
                return None

        #  add relation columns, that is, the columns, in which this table can be found in other tables
        typeTables = TypeTable.objects.filter(table=table)
        for typeTable in typeTables:
            typesColumn = Column.objects.get(type=typeTable.type)
            if typeTable.column is None:
                linkCol = Column.objects.get(type=typeTable.type)
                colStructs.append({"name": typesColumn.name + " in " + typesColumn.table.name, "type": Type.LINK, "table": typesColumn.table.name, "link": linkCol.name})

        rightsAdmin = False
        viewLog = False
        delete = False
        insert = False
        try:
            tableRights = RightListForTable.objects.get(user=user, table=table)
            rightsAdmin = tableRights.rightsAdmin
            viewLog = tableRights.viewLog
            delete = tableRights.delete
            insert = tableRights.insert
        except RightListForTable.DoesNotExist:
            pass

        groupNames = list()
        for membership in Membership.objects.filter(user=user):
            groupNames.append(membership.group.name)

        groups = DBGroup.objects.filter(name__in=groupNames)
        rightsFromGroup = RightListForTable.objects.filter(group__in=groups)
        for right in rightsFromGroup:
            rightsAdmin = right.rightsAdmin if not rightsAdmin else True
            viewLog = right.viewLog if not viewLog else True
            delete = right.delete if not delete else True
            insert = right.insert if not insert else True

        result = dict()
        result["admin"] = user.admin
        result["rightsAdmin"] = rightsAdmin
        result["viewLog"] = viewLog
        result["delete"] = delete
        result["insert"] = insert
        result["category"] = table.category.name
        result["columns"] = colStructs

        return result

    @staticmethod
    def serializeCategories():
        """
        {
            "categories": ["cat1", "cat2", "cat3"]
        }
        """
        result = dict()
        result["categories"] = list()
        for cat in Category.objects.all():
            result["categories"].append(cat.name)
        return result


    @staticmethod
    def serializeRightsFor(tableName):
        """
        {
            "actors": [
                {
                    "name": "actor1",
                    "tableRights": {"insert": false, "delete": false, "viewLog": true, "rightsAdmin": true},
                    "columnRights": [
                        {"name": "col1", "rights": {"modify": true, "read": true}},
                        {"name": "col2", "rights": {"modify": false, "read": true}},
                        {"name": "col3", "rights": {"modify": false, "read": true}},
                        {"name": "col4", "rights": {"modify": false, "read": true}}
                    ]
                },
                {
                    "name": "actor2",
                    "tableRights": {"viewLog": false, "rightsAdmin": false, "delete": true, "insert": true},
                    "columnRights": []
                }
            ]
        }
        """
        try:
            table = Table.objects.get(name=tableName, deleted=False)
        except Table.DoesNotExist:
            return None

        result = dict()

        result["actors"] = list()
        users = table.getUsersWithRights()
        for user in users:
            userObj = dict()
            userObj["name"] = user.username
            rights = TableSerializer.serializeRightsForActor(user.username, table.name)
            userObj["tableRights"] = rights["tableRights"]
            userObj["columnRights"] = rights["columnRights"]

            result["actors"].append(userObj)
        print result
        groups = table.getGroupsWithRights()
        for group in groups:
            groupObj = dict()
            groupObj["name"] = group.name
            rights = TableSerializer.serializeRightsForActor(group.name, table.name)
            groupObj["tableRights"] = rights["tableRights"]
            groupObj["columnRights"] = rights["columnRights"]

            result["actors"].append(groupObj)

        return result

    @staticmethod
    def serializeRightsForActor(name, tableName):
        """
        {
            "name": "actor1",
            "tableRights": {"insert": false, "delete": false, "viewLog": true, "rightsAdmin": true},
            "columnRights": [
                {"name": "col1", "rights": {"modify": true, "read": true}},
                {"name": "col2", "rights": {"modify": false, "read": true}}
            ]
        }
        """
        try:
            table = Table.objects.get(name=tableName, deleted=False)
        except Table.DoesNotExist:
            return None
        # either a user or a group name was passed
        try:
            actor = DBUser.objects.get(username=name)
            user = True
        except DBUser.DoesNotExist:
            actor = DBGroup.objects.get(name=name)
            user = False

        if user:
            try:
                tableRights = RightListForTable.objects.get(user=actor, table=table)
            except RightListForTable. DoesNotExist:
                tableRights = None
        else:  # a group was passed
            try:
                tableRights = RightListForTable.objects.get(group=actor, table=table)
            except RightListForTable. DoesNotExist:
                tableRights = None

        result = dict()
        result["tableRights"] = dict()
        result["tableRights"]["rightsAdmin"] = tableRights.rightsAdmin if tableRights else False
        result["tableRights"]["viewLog"] = tableRights.viewLog if tableRights else False
        result["tableRights"]["insert"] = tableRights.insert if tableRights else False
        result["tableRights"]["delete"] = tableRights.delete if tableRights else False

        result["columnRights"] = list()
        columns = table.getColumns()

        for column in columns:
            if column.deleted:
                continue
            if user:
                try:
                    columnRights = RightListForColumn.objects.get(column=column, user=actor)
                except RightListForColumn.DoesNotExist:
                    columnRights = None
            else:
                try:
                    columnRights = RightListForColumn.objects.get(column=column, group=actor)
                except RightListForColumn.DoesNotExist:
                    columnRights = None

            colObj = dict()
            colObj["name"] = column.name
            colObj["rights"] = dict()
            colObj["rights"]["read"] = columnRights.read if columnRights else False
            colObj["rights"]["modify"] = columnRights.modify if columnRights else False

            result["columnRights"].append(colObj)
        print result
        return result

    @staticmethod
    def serializeHistory(tableName):
        """
        {
            "history": [
                {
                    "type": TABLE:CREATED,
                    "user": username,
                    "messages": ["created rights for ...", "created columns..."]
                }
            ]
        }
        """
        try:
            table = Table.objects.get(name=tableName, deleted=False)
        except Table.DoesNotExist:
            return False

        result = dict()
        result["history"] = list()
        histories = HistoryTable.objects.filter(table=table)
        for history in histories:
            historyObj = dict()
            if history.type == HistoryTable.TABLE_CREATED:
                historyObj["type"] = _("TABLE CREATED").__unicode__()
            if history.type == HistoryTable.TABLE_MODIFIED:
                historyObj["type"] = _("TABLE MODIFIED").__unicode__()
            if history.type == HistoryTable.TABLE_DELETED:
                historyObj["type"] = _("TABLE DELETED").__unicode__()
            if history.type == HistoryTable.DATASET_INSERTED:
                historyObj["type"] = _("DATASET INSERTED").__unicode__()
            if history.type == HistoryTable.DATASET_MODIFIED:
                historyObj["type"] = _("DATASET MODIFIED").__unicode__()
            if history.type == HistoryTable.DATASET_DELETED:
                historyObj["type"] = _("DATASET DELETED").__unicode__()
            historyObj["user"] = history.user.username
            historyObj["date"] = str(history.date.strftime('%Y.%M.%d, %H:%M'))
            historyObj["messages"] = list()
            for msg in history.messages.all():
                historyObj["messages"].append(msg.content)
            result["history"].append(historyObj)

        return result


class HistorySerializer:
    @staticmethod
    def serializeHistory():
        """
        {
            "tableHistory": [
                {
                    "table": "table 1",
                    "type": "TABLE_CREATED",
                    "user": "user 1",
                    "messages": ["created rights for ...", "created columns..."]
                }
            ],
            "authHistory": [
                {
                    "user": "user 1",
                    "type": "GROUP MODIFIED",
                    "messages": ["Added group member ...", "can now create tables..."]
                }
            ]

        }
        """
        result = dict()
        result["tableHistory"] = list()
        for table in Table.objects.all():
            tableHist = TableSerializer.serializeHistory(table.name)
            if tableHist and tableHist is not None:
                result["tableHistory"] = tableHist["history"]

        result["authHistory"] = list()
        for history in HistoryAuth.objects.all():
            historyObj = dict()
            historyObj["user"] = history.user.username
            historyObj["date"] = str(history.date.strftime('%Y.%M.%d, %H:%M'))
            if history.type == HistoryAuth.GROUP_CREATED:
                historyObj["type"] = _("GROUP CREATED").__unicode__()
            if history.type == HistoryAuth.GROUP_MODIFIED:
                historyObj["type"] = _("GROUP MODIFIED").__unicode__()
            if history.type == HistoryAuth.GROUP_DELETED:
                historyObj["type"] = _("GROUP DELETED").__unicode__()
            if history.type == HistoryAuth.USER_REGISTERED:
                historyObj["type"] = _("USER REGISTERED").__unicode__()
            if history.type == HistoryAuth.USER_MODIFIED:
                historyObj["type"] = _("USER MODIFIED").__unicode__()
            historyObj["messages"] = list()
            for message in history.messages.all():
                historyObj["messages"].append(message.content)

            result["authHistory"].append(historyObj)
        print result
        return result


class UserSerializer:
    @staticmethod
    def serializeOne(username):
        """
        {
            "name": "myname",
            "tableCreator": false,
            "userManager": true,
            "admin": false
        }
        """
        try:
            user = DBUser.objects.get(username=username)
        except DBUser.DoesNotExist:
            return None

        result = dict()
        result["name"] = username
        result["groups"] = list()
        for m in Membership.objects.filter(user=user):
            groupObj = dict()
            groupObj["name"] = m.group.name
            groupObj["tableCreator"] = m.group.tableCreator
            result["groups"].append(groupObj)

        result["tableCreator"] = user.tableCreator
        result["userManager"] = user.userManager
        result["active"] = user.is_active
        result["admin"] = user.admin

        return result

    @staticmethod
    def serializeAll():
        """
        return all tables with their columns

        {
            "users": [
                {"id":"1","name": "example"},
                {"id":"2","name": "example2"}]}
            ]
        }
        """
        users = DBUser.objects.all()
        result = dict()
        result["users"] = []

        for user in users:
            if user.is_active:
                result["users"].append(user.username)

        return result

    @staticmethod
    def serializeAllWithRights(callingUser):
        result = dict()
        result["users"] = list()

        for user in DBUser.objects.all():
            if user is callingUser:
                continue
            result["users"].append(UserSerializer.serializeOne(user.username))

        return result


class GroupSerializer:
    @staticmethod
    def serializeOne(name):
        """
        {
            "name": "group1",
            "users": [
                {"name": "John Doe"},
                {"name": "Alex Anonymus"}
            ]
        }
        """
        try:
            group = DBGroup.objects.get(name=name)
        except DBGroup.DoesNotExist:
            return False

        theGroup = dict()
        theGroup["name"] = group.name
        theGroup["tableCreator"] = group.tableCreator
        theGroup["admins"] = list()
        theGroup["users"] = list()

        for m in Membership.objects.filter(group=group, isAdmin=True):
            theGroup["admins"].append(m.user.username)

        for m in Membership.objects.filter(group=group, isAdmin=False):
            theGroup["users"].append(m.user.username)

        return theGroup

    @staticmethod
    def serializeAll():
        """
        return all groups

        """
        groups = DBGroup.objects.all()
        result = dict()
        result["groups"] = []

        for group in groups:
            result["groups"].append(GroupSerializer.serializeOne(group.name))

        return result


class DatasetSerializer:

    @staticmethod
    def serializeOne(id, user):
        """
        {
            "id": "2.2013_192_B",
            "data": [
                {"column": "columnname1", "type": 0, "value": "aText"},
                {"column": "columnname2", "type": 1, "value": 392.03},
                {"column": "columnname3", "type": 2, "value": "2013-08-22 10:55:00"},
                {"column": "columnname4", "type": 3, "value": "aSelectionOption"},
                {"column": "columnname5", "type": 4, "value": true},
                {"column": "columnname6", "type": 5, "value": ["5.2013_3_B", "5.2013_4_K"], "table": "aTableName"}
            ]
        }
        """
        try:
            dataset = Dataset.objects.get(datasetID=id)
        except Dataset.DoesNotExist:
            return None

        result = dict()
        result["id"] = dataset.datasetID
        result["data"] = list()

        datalist = dataset.getData()
        for data in datalist:
            for item in data:
                if item.deleted:
                    continue
                dataObj = dict()
                dataObj["column"] = item.column.name
                dataObj["type"] = item.column.type.type

                if dataObj["type"] == Type.TABLE:
                    dataObj["value"] = list()
                    for link in TableLink.objects.filter(dataTable=item):
                        valObj = dict()
                        valObj["id"] = link.dataset.datasetID
                        typeTable = item.column.type.getType()
                        columnForDisplay = typeTable.column if typeTable.column else None
                        if columnForDisplay:
                            refDataList = link.dataset.getData()
                            for refData in refDataList:
                                for refItem in refData:
                                    if refItem.column == columnForDisplay:
                                        valObj["value"] = refItem.content

                        dataObj["value"].append(valObj)

                else:
                    if item.column.type.type == Type.DATE:
                        dataObj["value"] = str(item.content.strftime('%Y.%M.%d, %H:%M'))
                    else:
                        dataObj["value"] = unicode(item.content)

                result["data"].append(dataObj)

        return result

    @staticmethod
    def serializeOneWithLinks(datasetID, tables, user):
        # first serialize data from all ordinary columns
        try:
            dataset = Dataset.objects.get(datasetID=datasetID)
        except Dataset.DoesNotExist:
            return None
        result = DatasetSerializer.serializeOne(datasetID, user)

        # now add datasets from the filter which reference this dataset
        links = TableLink.objects.filter(dataset=dataset)
        dataTableIDs = list()
        for link in links:
            dataTableIDs.append(link.dataTable_id)

        for tableName in tables:
            try:
                table = Table.objects.get(name=tableName, deleted=False)
            except Table.DoesNotExist:
                continue
            refDataTables = DataTable.objects.filter(pk__in=dataTableIDs, dataset__in=table.getDatasets())
            refDatasetIDs = list()
            for refDataTable in refDataTables:
                refDatasetIDs.append({"id": refDataTable.dataset.datasetID})

            # get the name of the column, in which this dataset is referenced in the other table
            columns = table.getColumns()
            for col in columns:
                if col.type.getType().table == dataset.table:
                    columnName = col.name
                    break
            dataObj = dict()
            dataObj["column"] = columnName + " in " + table.name
            dataObj["type"] = Type.LINK
            dataObj["value"] = refDatasetIDs

            result["data"].append(dataObj)

        return result

    @staticmethod
    def serializeAll(table, user):
        try:
            datasets = Dataset.objects.filter(table=table)
        except Dataset.DoesNotExist:
            pass

        result = dict()
        result["datasets"] = list()
        for dataset in datasets:
            if dataset.deleted:
                continue
            result["datasets"].append(DatasetSerializer.serializeOne(dataset.datasetID, user))

        return result

    @staticmethod
    def serializeBy(request, tableName, user):
        """
        {
            "filter":[
                {
                    "column": "columnname", "table":"tablename","link":"columnname",
                    "child": {
                        "column": "columnInRelatedTable", "table":"tablename","linkColumn":"columnname",
                        "child": {
                            "column": "columnname2", "min": 12, "max": 20
                        }
                    }
                },
                {
                    "column": "columnname", "table":"tablename","link":"columnname",
                    "child": {
                        "column": "columnInRelatedTable", "table":"tablename","linkColumn":"columnname",
                        "child": {
                            "column": "columnname2", "min": 12, "max": 20
                        }
                    }
                }
            ]
        }
        """
        try:
            table = Table.objects.get(name=tableName, deleted=False)
        except Table.DoesNotExist:
            return None

        if len(request["filter"]) == 0:
            return DatasetSerializer.serializeAll(table, user)
        linkedTables = list()
        resultSet = table.getDatasets()
        for criterion in request["filter"]:
            if "column" not in criterion:  # the user has deselected a column
                continue
            if "link" in criterion:  # the user wants to filter over referencing tables
                linkedTables.append(criterion["table"])  # remember the referencing tables, to display columns for them
            resultSet = DatasetSerializer.filter(table, resultSet, criterion, user)

            if not resultSet:
                return None

        result = dict()
        result["datasets"] = list()
        for dataset in resultSet:
            if len(linkedTables) > 0:
                result["datasets"].append(DatasetSerializer.serializeOneWithLinks(dataset.datasetID, linkedTables, user))
            else:
                result["datasets"].append(DatasetSerializer.serializeOne(dataset.datasetID, user))

        return result

    @staticmethod
    def filter(table, datasets, criterion, user):
        if "link" not in criterion:  # filter only with criteria on this table
            #  check if the user filters over a specific dataset id. As this is not a column, it must be handled differently
            if "datasetID" in criterion:
                return datasets.filter(datasetID=criterion["datasetID"])
            try:
                column = table.getColumns().get(name=criterion["column"], deleted=False)
            except Column.DoesNotExist:
                return False
            if column.type.type == Type.TEXT:
                dataTexts = DataText.objects.filter(dataset__in=datasets, content__contains=criterion["substring"])
                datasetIDs = list()
                for dataText in dataTexts:
                    datasetIDs.append(dataText.dataset_id)
                return datasets.filter(pk__in=datasetIDs, deleted=False)

            elif column.type.type == Type.NUMERIC:
                if "min" in criterion and "max" in criterion:
                    dataNumerics = DataNumeric.objects.filter(dataset__in=datasets, content__gte=criterion["min"], content__lte=criterion["max"])
                elif "min" in criterion:
                    dataNumerics = DataNumeric.objects.filter(dataset__in=datasets, content__gte=criterion["min"])
                elif "max" in criterion:
                    dataNumerics = DataNumeric.objects.filter(dataset__in=datasets, content__lte=criterion["max"])
                else:  # no filtering
                    return datasets
                datasetIDs = list()
                for dataNumeric in dataNumerics:
                    datasetIDs.append(dataNumeric.dataset_id)
                return datasets.filter(pk__in=datasetIDs, deleted=False)

            elif column.type.type == Type.DATE:
                if "min" in criterion and "max" in criterion:
                    dataDates = DataDate.objects.filter(dataset__in=datasets, content__gte=criterion["min"], content__lte=criterion["max"])
                elif "min" in criterion:
                    dataDates = DataDate.objects.filter(dataset__in=datasets, content__gte=criterion["min"])
                elif "max" in criterion:
                    dataDates = DataDate.objects.filter(dataset__in=datasets, content__lte=criterion["max"])
                else:  # no filtering
                    return datasets
                datasetIDs = list()
                for dataDate in dataDates:
                    datasetIDs.append(dataDate.dataset_id)
                return datasets.filter(pk__in=datasetIDs, deleted=False)

            elif column.type.type == Type.SELECTION:
                dataSelections = DataSelection.objects.filter(dataset__in=datasets, content=criterion["option"])
                datasetIDs = list()
                for dataSelection in dataSelections:
                    datasetIDs.append(dataSelection.dataset_id)
                return datasets.filter(pk__in=datasetIDs, deleted=False)

            elif column.type.type == Type.BOOL:
                dataBools = DataBool.objects.filter(dataset__in=datasets, content=criterion["boolean"])
                datasetIDs = list()
                for dataBool in dataBools:
                    datasetIDs.append(dataBool.dataset_id)
                return datasets.filter(pk__in=datasetIDs, deleted=False)

            elif column.type.type == Type.TABLE:
                typeTable = column.type.getType()
                # filter over column in another table. In principle it repeats the algorithm above on the referenced table's column
                if typeTable.column is None:
                    try:
                        nextTable = Table.objects.get(name=criterion["table"], deleted=False)
                    except Table.DoesNotExist:
                        return False
                    try:
                        refColumn = Column.objects.get(table=nextTable, name=criterion["child"]["column"], deleted=False)
                    except Column.DoesNotExist:
                        return False

                    # First filter datasets of the next table with criteria specified in the criterion's child
                    filteredDatasets = DatasetSerializer.filter(nextTable, nextTable.getDatasets(), criterion["child"], user)

                    # Now keep only those datasets, which have references to the "datasets" passed as argument
                    links = TableLink.objects.filter(dataset__in=filteredDatasets)
                    dataTableIDs = list()
                    for link in links:
                        dataTableIDs.append(link.dataTable_id)

                    # dataTables contained in datasets which fulfill child-criterion
                    dataTables = DataTable.objects.filter(dataset__in=datasets, pk__in=dataTableIDs)

                    datasetIDs = list()
                    for dataTable in dataTables:
                        datasetIDs.append(dataTable.dataset_id)

                    datasets = datasets.filter(pk__in=datasetIDs, deleted=False)  # all datasets which fulfill the criterion and have reference to passed 'datasets'

                    return datasets
                else:  # filter over column in table
                    refTable = typeTable.table

                    if typeTable.column.type.type == Type.TEXT:
                        refDataTexts = DataText.objects.filter(dataset__in=refTable.getDatasets(), content__contains=criterion["substring"])
                        refDatasetIDs = list()
                        for refDataText in refDataTexts:
                            refDatasetIDs.append(refDataText.dataset_id)

                    elif typeTable.column.type.type == Type.NUMERIC:
                        if "min" in criterion and "max" in criterion:
                            refDataNumerics = DataNumeric.objects.filter(dataset__in=refTable.getDatasets(), content__gte=criterion["min"], content_lte=criterion["max"])
                        elif "min" in criterion:
                            refDataNumerics = DataNumeric.objects.filter(dataset__in=refTable.getDatasets(), content__gte=criterion["min"])
                        else:  # "max" in criterion
                            refDataNumerics = DataNumeric.objects.filter(dataset__in=refTable.getDatasets(), content_lte=criterion["max"])
                        refDatasetIDs = list()
                        for refDataNumeric in refDataNumerics:
                            refDatasetIDs.append(refDataNumeric.dataset_id)

                    elif typeTable.column.type.type == Type.DATE:
                        if "min" in criterion and "max" in criterion:
                            refDataDates = DataDate.objects.filter(dataset__in=refTable.getDatasets(), content__gte=criterion["min"], content_lte=criterion["max"])
                        elif "min" in criterion:
                            refDataDates = DataDate.objects.filter(dataset__in=refTable.getDatasets(), content__gte=criterion["min"])
                        else:  # "max" in criterion
                            refDataDates = DataDate.objects.filter(dataset__in=refTable.getDatasets(), content_lte=criterion["max"])
                        refDatasetIDs = list()
                        for refDataDate in refDataDates:
                            refDatasetIDs.append(refDataDate.dataset_id)

                    elif typeTable.column.type.type == Type.SELECTION:
                        refDataSelections = DataSelection.objects.filter(dataset__in=refTable.getDatasets(), content=criterion["option"])
                        refDatasetIDs = list()
                        for refDataSelection in refDataSelections:
                            refDatasetIDs.append(refDataSelection.dataset_id)

                    elif typeTable.column.type.type == Type.BOOL:
                        refDataBools = DataBool.objects.filter(dataset__in=refTable.getDatasets(), content__contains=criterion["boolean"])
                        refDatasetIDs = list()
                        for refDataBool in refDataBools:
                            refDatasetIDs.append(refDataBool.dataset_id)

                    refDatasets = Dataset.objects.filter(pk__in=refDatasetIDs)
                    links = TableLink.objects.filter(dataset__in=refDatasets)
                    dataTableIDs = list()
                    for link in links:
                        dataTableIDs.append(link.dataTable_id)
                    dataTables = DataTable.objects.filter(pk__in=dataTableIDs)
                    datasetIDs = list()
                    for dataTable in dataTables:
                        datasetIDs.append(dataTable.dataset_id)
                    return datasets.filter(pk__in=datasetIDs, deleted=False)

            else:  # no matching column type
                return False

        else:  # filter with criteria on nested table
            try:
                nextTable = Table.objects.get(name=criterion["table"], deleted=False)
            except Table.DoesNotExist:
                return False
            try:
                refColumn = Column.objects.get(table=nextTable, name=criterion["link"], deleted=False)
            except Column.DoesNotExist:
                return False

            """
                First filter datasets of the next table with criteria specified in the criterion's child
            """
            filteredDatasets = DatasetSerializer.filter(nextTable, nextTable.getDatasets(), criterion["child"], user)
            """
                Now keep only those datasets, which have references to the "datasets" passed as argument
            """
            links = TableLink.objects.filter(dataset__in=datasets)
            dataTableIDs = list()
            for link in links:
                dataTableIDs.append(link.dataTable_id)

            # dataTables contained in datasets which fulfill child-criterion
            dataTables = DataTable.objects.filter(dataset__in=filteredDatasets, column=refColumn, pk__in=dataTableIDs)
            datasetIDs = list()
            for dataTable in dataTables:
                datasetIDs.append(dataTable.dataset_id)

            filteredDatasets = filteredDatasets.filter(pk__in=datasetIDs)  # all datasets which fulfill the criterion and have reference to passed 'datasets'

            """
                Finally, return a filtered version of 'datasets'.
                That is, only those, which are referenced by datasets in filteredDatasets.
            """

            # dataTables contained in datasets which fulfill child-criterion and are in datasets with reference to passed 'datasets'
            filteredDataTables = dataTables.filter(dataset__in=filteredDatasets)

            filteredLinks = TableLink.objects.filter(dataTable__in=filteredDataTables)
            finalDatasetIDs = list()
            for filteredLink in filteredLinks:
                finalDatasetIDs.append(filteredLink.dataset_id)

            return datasets.filter(pk__in=finalDatasetIDs, deleted=False)