# -*- coding: utf-8 -*-
__author__ = 'My-Tien Nguyen'

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
            table = Table.objects.get(name=tableName)
        except Table.DoesNotExist:
            return None

        result = dict()
        result["name"] = table.name
        result.update(DatasetSerializer.serializeAll(tableName, user))

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

        for rights in RightListForColumn.objects.filter(user=user):
            allowedTables.add(rights.column.table)

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
    def serializeStructure(tableName):
        """
        return the table with its columns and the column's datatypes as well as ranges

        {
          "category": "categoryname"
          "columns": [
            {"name": "columnname0", "type": 0, "length": 100},
            {"name": "columnname1", "type": 1, "min": "a decimal", "max": "a decimal"},
            {"name": "columnname2", "type": 2, "min": "a date", "max": "a date"},
            {"name": "columnname3", "type": 3, "options": {"0": "opt1", "1": "opt2", "2": "opt3"},
            {"name": "columnname4", "type": 4, "table": "tablename", "shownColumn": "PSA"},
          ]
        }
        """
        table = Table.objects.get(name=tableName)
        if table is None:
            return None

        columns = table.getColumns()
        colStructs = []
        for col in columns:
            if col.deleted:
                continue
            comment = col.comment if col.comment is not None else ""
            type = col.type.type
            if type is Type.TEXT:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.TEXT, "length": col.type.getType().length, "comment": comment})
            elif type is Type.NUMERIC:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.NUMERIC, "min": col.type.getType().min, "max": col.type.getType().max, "comment": comment})
            elif type is Type.DATE:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.DATE, "min": col.type.getType().min, "max": col.type.getType().max, "comment": comment})

            elif type is Type.SELECTION:
                options = list()
                for value in col.type.getType().values():
                    options.append({"key": value.index, "value": value.content})
                colStructs.append({"id": col.id, "name": col.name, "type": Type.SELECTION, "options": options, "comment": comment})
            elif type is Type.BOOL:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.BOOL, "comment": comment})
            elif type is Type.TABLE:
                if col.type.getType().column is not None:
                    refCol = col.type.getType().column
                    colStructs.append({"id": col.id, "name": col.name, "type": Type.TABLE, "table": col.type.getType().table.name, "column": refCol.name, "refType": refCol.type.type, "comment": comment})
                else:
                    colStructs.append({"id": col.id, "name": col.name, "type": Type.TABLE, "table": col.type.getType().table.name, "comment": comment})
            else:
                return None

        #  add relation columns, that is, the columns, in which this table can be found in other tables
        typeTables = TypeTable.objects.filter(table=table)
        for typeTable in typeTables:
            typesColumn = Column.objects.get(type=typeTable.type)
            if typeTable.column is None:
                colStructs.append({"name": typesColumn.name + " in " + typesColumn.table.name, "type": Type.LINK, "table": typesColumn.table.name})

        result = dict()
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
            table = Table.objects.get(name=tableName)
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
            table = Table.objects.get(name=tableName)
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
    def serializeAllWithRights():
        result = dict()
        result["users"] = list()

        for user in DBUser.objects.all():
            result["users"].append(UserSerializer.serializeOne(user.username))

        return result


class GroupSerializer:
    @staticmethod
    def serializeOne(id):
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
            group = DBGroup.objects.get(name=id)
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
                    for link in DataTableToDataset.objects.filter(DataTable=item):
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
                    try:
                        dataObj["value"] = str(item.content)
                    except UnicodeEncodeError:
                        dataObj["value"] = unicode(item.content)

                result["data"].append(dataObj)

        return result

    @staticmethod
    def serializeAll(tableRef, user):
        try:
            datasets = Dataset.objects.filter(table=tableRef)
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
                    "column": "columnname", "table":"tablename","linkColumn":"columnname",
                    "child": {
                        "column": "columnInRelatedTable", "table":"tablename","linkColumn":"columnname",
                        "child": {
                            "column": "columnname2", "min": 12, "max": 20
                        }
                    }
                },
                {
                    "column": "columnname", "table":"tablename","linkColumn":"columnname",
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
            table = Table.objects.get(name=tableName)
        except Table.DoesNotExist:
            return None

        resultSet = table.getDatasets()
        for criterion in request["filter"]:
            resultSet = filter(resultSet, criterion, user)
            if not resultSet:
                return None

        result = dict()
        result["datasets"] = list()
        for dataset in resultSet.objects:
            result["datasets"].append(DatasetSerializer.serializeOne(dataset.datasetID, user))
        return result

    @staticmethod
    def filter(table, datasets, criterion, user):
        try:
            column = table.getColumns().filter(name=criterion["name"])
        except Column.DoesNotExist:
            return False

        if "child" not in criterion:  # filter only with criteria on this table
            if column.type.type == Type.TEXT:
                dataTexts = DataText.objects.filter(dataset__in=datasets, content__contains=criterion["substring"])
                datasetIDs = list()
                for dataText in dataTexts:
                    datasetIDs.append(dataText.dataset_id)
                return datasets.objects.filter(pk__in=datasetIDs)

            elif column.type.type == Type.NUERMIC:
                if "min" in criterion and "max" in criterion:
                    dataNumerics = DataNumeric.objects.filter(dataset__in=datasets, content__gte=criterion["min"], content__lte=criterion["max"])
                elif "min" in criterion:
                    dataNumerics = DataNumeric.objects.filter(dataset__in=datasets, content__gte=criterion["min"])
                else:  # "max" in criterion
                    dataNumerics = DataNumeric.objects.filter(dataset__in=datasets, content__lte=criterion["max"])
                datasetIDs = list()
                for dataNumeric in dataNumerics:
                    datasetIDs.append(dataNumeric.dataset_id)
                return datasets.objects.filter(pk__in=datasetIDs)

            elif column.type.type == Type.DATE:
                if "min" in criterion and "max" in criterion:
                    dataDates = DataDate.objects.filter(dataset__in=datasets, content__gte=criterion["min"], content__lte=criterion["max"])
                elif "min" in criterion:
                    dataDates = DataDate.objects.filter(dataset__in=datasets, content__gte=criterion["min"])
                else:  # "max" in criterion
                    dataDates = DataDate.objects.filter(dataset__in=datasets, content__lte=criterion["max"])
                datasetIDs = list()
                for dataDate in dataDates:
                    datasetIDs.append(dataDate.dataset_id)
                return datasets.objects.filter(pk__in=datasetIDs)

            elif column.type.type == Type.SELECTION:
                dataSelections = DataSelection.objects.filter(dataset__in=datasets, content=criterion["option"])
                datasetIDs = list()
                for dataSelection in dataSelections:
                    datasetIDs.append(dataSelection.dataset_id)
                return datasets.objects.filter(pk__in=datasetIDs)

            elif column.type.type == Type.BOOL:
                dataBools = DataBool.objects.filter(dataset__in=datasets, content=criterion["boolean"])
                datasetIDs = list()
                for dataBool in dataBools:
                    datasetIDs.append(dataBool.dataset_id)
                return datasets.objects.filter(pk__in=datasetIDs)

            elif column.type.type == Type.TABLE:
                typeTable = column.type.getType()
                # filter over column in another table. In principle it repeats the algorithm above on the referenced table's column
                if typeTable.column is None:
                    try:
                        nextTable = Table.objects.get(name=criterion["table"])
                    except Table.DoesNotExist:
                        return False
                    try:
                        refColumn = Column.objects.get(table=nextTable, name=criterion["linkColumn"])
                    except Column.DoesNotExist:
                        return False

                    """
                        First filter datasets of the next table with criteria specified in the criterion's child
                    """
                    filteredDatasets = DatasetSerializer.filter(nextTable, nextTable.getDatasets(), criterion["child"], user)

                    """
                        Now keep only those datasets, which have references to the "datasets" passed as argument
                    """
                    links = DataTableToDataset.objects.filter(dataset__in=datasets)
                    dataTableIDs = list()
                    for link in links:
                        dataTableIDs.append(link.DataTable_id)

                    # dataTables contained in datasets which fulfill child-criterion
                    dataTables = DataTable.objects.filter(dataset__in=filteredDatasets, column=refColumn, pk__in=dataTableIDs)
                    datasetIDs = list()
                    for dataTable in dataTables:
                        datasetIDs.append(dataTable.dataset_id)

                    filteredDatasets = filteredDatasets.objects.filter(pk__in=datasetIDs)  # all datasets which fulfill the criterion and have reference to passed 'datasets'

                    """
                        Finally, return a filtered version of 'datasets'.
                        That is, only those, which are referenced by datasets in filteredDatasets.
                    """

                    # dataTables contained in datasets which fulfill child-criterion and are in datasets with reference to passed 'datasets'
                    filteredDataTables = dataTables.filter(dataset__in=filteredDatasets)

                    filteredLinks = DataTableToDataset(DataTable__in=filteredDataTables)
                    finalDatasetIDs = list()
                    for filteredLink in filteredLinks:
                        finalDatasetIDs.append(filteredLink.dataset_id)

                    return datasets.objects.filter(pk__in=finalDatasetIDs)

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
                    links = DataTableToDataset.objects.filter(dataset__in=refDatasets)
                    dataTableIDs = list()
                    for link in links:
                        dataTableIDs.append(link.DataTable_id)
                    dataTables = DataTable.objects.filter(pk__in=dataTableIDs)
                    datasetIDs = list()
                    for dataTable in dataTables:
                        datasetIDs.append(dataTable.dataset_id)
                    return datasets.objects.filter(pk__in=datasetIDs)

            else:  # no matching column type
                return False

        else:  # filter with criteria on nested table
            try:
                nextTable = Table.objects.get(name=criterion["table"])
            except Table.DoesNotExist:
                return False
            try:
                refColumn = Column.objects.get(table=nextTable, name=criterion["linkColumn"])
            except Column.DoesNotExist:
                return False

            """
                First filter datasets of the next table with criteria specified in the criterion's child
            """
            filteredDatasets = DatasetSerializer.filter(nextTable, nextTable.getDatasets(), criterion["child"], user)

            """
                Now keep only those datasets, which have references to the "datasets" passed as argument
            """
            links = DataTableToDataset.objects.filter(dataset__in=datasets)
            dataTableIDs = list()
            for link in links:
                dataTableIDs.append(link.DataTable_id)

            # dataTables contained in datasets which fulfill child-criterion
            dataTables = DataTable.objects.filter(dataset__in=filteredDatasets, column=refColumn, pk__in=dataTableIDs)
            datasetIDs = list()
            for dataTable in dataTables:
                datasetIDs.append(dataTable.dataset_id)

            filteredDatasets = filteredDatasets.objects.filter(pk__in=datasetIDs)  # all datasets which fulfill the criterion and have reference to passed 'datasets'

            """
                Finally, return a filtered version of 'datasets'.
                That is, only those, which are referenced by datasets in filteredDatasets.
            """

            # dataTables contained in datasets which fulfill child-criterion and are in datasets with reference to passed 'datasets'
            filteredDataTables = dataTables.filter(dataset__in=filteredDatasets)

            filteredLinks = DataTableToDataset(DataTable__in=filteredDataTables)
            finalDatasetIDs = list()
            for filteredLink in filteredLinks:
                finalDatasetIDs.append(filteredLink.dataset_id)

            return datasets.objects.filter(pk__in=finalDatasetIDs)