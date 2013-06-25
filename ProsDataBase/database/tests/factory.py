from ..models import *
from ..forms import *
from ..serializers import *
from string import ascii_lowercase, digits
from random import choice


class LiteralFactory:
    usedStrings = list()
    usedNumbers = list()

    @staticmethod
    def genRandString(length=5, chars=ascii_lowercase):
        """
        generate a random lowercase string with the length of 5 characters
        """
        while True:
            newString = ''.join([choice(chars) for i in xrange(length)])
            if newString not in LiteralFactory.usedStrings:
                LiteralFactory.usedStrings.append(newString)
                return newString

    @staticmethod
    def genRandNumber(length=5, chars=digits):
        """
        generate a random number with 5 digits
        """
        while True:
            number = ''.join([choice(chars) for k in xrange(length)])
            if number not in LiteralFactory.usedNumbers:
                LiteralFactory.usedNumbers.append(number)
                return number


class StructureFactory:

    @staticmethod
    def createTable(user):
        # ============================================================
        # creates a simple table with two columns and
        # two datasets filed with 3 values
        # ============================================================
        category = dict()
        category["name"] = "Allgemein"
        categoryF = CategoryForm(category)
        if categoryF.is_valid():
            newCategory = categoryF.save(commit=False)
            newCategory.save()

        table = dict()
        table["name"] = LiteralFactory.genRandString()
        table["created"] = datetime.utcnow().replace(tzinfo=utc)

        tabF = TableForm(table)
        if tabF.is_valid():
            newTable = tabF.save(commit=False)
            newTable.creator = user
            newTable.category = newCategory
            newTable.save()

        StructureFactory.createColumns(newTable, user)

        return newTable

    @staticmethod
    def createColumns(table, user):
        # ============================================================
        # - create a texttype
        # ============================================================
        texttype = Type(name="Text", type=0)
        texttype.save()
        typetext = TypeText(length=30, type=texttype)
        typetext.save()

        # ============================================================
        # - creates a numerictype
        # ============================================================
        numerictype = Type(name="Numeric", type=1)
        numerictype.save()
        numericCond = TypeNumeric(type=numerictype, min=2, max=10)
        numericCond.save()

        # ============================================================
        # - creates a datetype
        # ============================================================
        datetype = Type(name="Type", type=2)
        datetype.save()
        typedate = TypeDate(type=datetype)
        typedate.save()

        # ============================================================
        # - creates a selectiontype
        # ============================================================
        selectiontype = Type(name="Selection", type=3)
        selectiontype.save()

        typeSelection = dict()
        typeSelection["count"] = 2
        typeSelectionF = TypeSelectionForm(typeSelection)
        if typeSelectionF.is_valid():
            newTypeSelection = typeSelectionF.save(commit=False)
            newTypeSelection.type = selectiontype
            newTypeSelection.save()

        selection1 = dict()
        selection1["index"] = 0
        selection1["content"] = "ja"
        selection1F = SelectionValueForm(selection1)
        if selection1F.is_valid():
            newSelection1 = selection1F.save(commit=False)
            newSelection1.typeSelection = newTypeSelection
            newSelection1.save()

        selection2 = dict()
        selection2["index"] = 1
        selection2["content"] = "nein"
        selection2F = SelectionValueForm(selection2)
        if selection2F.is_valid():
            newSelection2 = selection2F.save(commit=False)
            newSelection2.typeSelection = newTypeSelection
            newSelection2.save()

        # ============================================================
        # - creates a booleantype
        # ============================================================
        booleantype = Type(name="Boolean", type=4)
        booleantype.save()
        typeBoolean = TypeBool(type=booleantype)
        typeBoolean.save()

        tabletype = Type(name="Table", type=5)
        tabletype.save()

        columns = dict()
        columns["name"] = "TEXT" + table.name
        columns["created"] = datetime.utcnow().replace(tzinfo=utc)
        columnsF = ColumnForm(columns)
        if columnsF.is_valid():
            textColumns = columnsF.save(commit=False)
            textColumns.table = table
            textColumns.type = texttype
            textColumns.creator = user
            textColumns.save()

        columns = dict()
        columns["name"] = "NUMERIC" + table.name
        columns["created"] = datetime.utcnow().replace(tzinfo=utc)
        columnsF = ColumnForm(columns)
        if columnsF.is_valid():
            numericColumns = columnsF.save(commit=False)
            numericColumns.table = table
            numericColumns.type = numerictype
            numericColumns.creator = user
            numericColumns.save()

        columns = dict()
        columns["name"] = "DATE" + table.name
        columns["created"] = datetime.utcnow().replace(tzinfo=utc)
        columnsF = ColumnForm(columns)
        if columnsF.is_valid():
            dateColumns = columnsF.save(commit=False)
            dateColumns.table = table
            dateColumns.type = datetype
            dateColumns.creator = user
            dateColumns.save()

        columns = dict()
        columns["name"] = "SELECTION" + table.name
        columns["created"] = datetime.utcnow().replace(tzinfo=utc)
        columnsF = ColumnForm(columns)
        if columnsF.is_valid():
            selectionColumns = columnsF.save(commit=False)
            selectionColumns.table = table
            selectionColumns.type = selectiontype
            selectionColumns.creator = user
            selectionColumns.save()

        columns = dict()
        columns["name"] = "BOOLEAN" + table.name
        columns["created"] = datetime.utcnow().replace(tzinfo=utc)
        columnsF = ColumnForm(columns)
        if columnsF.is_valid():
            boolColumns = columnsF.save(commit=False)
            boolColumns.table = table
            boolColumns.type = booleantype
            boolColumns.creator = user
            boolColumns.save()


class DataFactory:
    @staticmethod
    def genRandDatasets(table, user, n=100):
        for i in range(0, n):

            dataset = dict()
            dataset["created"] = datetime.utcnow().replace(tzinfo=utc)
            datasetF = DatasetForm(dataset)
            if datasetF.is_valid():
                newDataset = datasetF.save(commit=False)
                newDataset.creator = user
                newDataset.table = table
                newDataset.save()
                newDataset.datasetID = table.generateDatasetID(newDataset)
                newDataset.save()

            for column in table.getColumns():
                if column.type.type == Type.TEXT:
                    # ============================================================
                    # - the 1st column have a text data type
                    # ============================================================
                    dataText = dict()
                    dataText["created"] = datetime.utcnow().replace(tzinfo=utc)
                    dataText["content"] = LiteralFactory.genRandString()
                    dataTextF = DataTextForm(dataText)
                    if dataTextF.is_valid():
                        newDataText = dataTextF.save(commit=False)
                        newDataText.column = column
                        newDataText.dataset = newDataset
                        newDataText.creator = user
                        newDataText.save()

                if column.type.type == Type.NUMERIC:
                    # ============================================================
                    # - the 2nd column have a numeric data type
                    # ============================================================
                    dataNumeric = dict()
                    dataNumeric["created"] = datetime.utcnow().replace(tzinfo=utc)
                    dataNumeric["content"] = LiteralFactory.genRandNumber()
                    dataNumericF = DataNumericForm(dataNumeric)
                    if dataNumericF.is_valid():
                        newDataNummeric = dataNumericF.save(commit=False)
                        newDataNummeric.column = column
                        newDataNummeric.dataset = newDataset
                        newDataNummeric.creator = user
                        newDataNummeric.save()

                if column.type.type == Type.DATE:
                    # ============================================================
                    # -- the 3rd column have a date data type
                    # ============================================================
                    dataDate = dict()
                    dataDate["created"] = datetime.utcnow().replace(tzinfo=utc)
                    dataDate["content"] = datetime.utcnow().replace(tzinfo=utc)
                    dataDateF = DataDateForm(dataDate)
                    if dataDateF.is_valid():
                        newDataDate = dataDateF.save(commit=False)
                        newDataDate.column = column
                        newDataDate.dataset = newDataset
                        newDataDate.creator = user
                        newDataDate.save()

                if column.type.type == Type.SELECTION:
                    # ============================================================
                    # -- the 4th column have a Selection data type
                    # ============================================================
                    dataSelection = dict()
                    dataSelection["created"] = datetime.utcnow().replace(tzinfo=utc)
                    dataSelection["content"] = "ja"
                    dataSelectionF = DataSelectionForm(dataSelection)
                    if dataSelectionF.is_valid():
                        newDataSelection = dataSelectionF.save(commit=False)
                        newDataSelection.column = column
                        newDataSelection.dataset = newDataset
                        newDataSelection.creator = user
                        newDataSelection.save()

                if column.type.type == Type.BOOL:
                    # ============================================================
                    # -- the 5th column have a boolean data type
                    # ============================================================

                    dataBoolean = dict()
                    dataBoolean["created"] = datetime.utcnow().replace(tzinfo=utc)
                    dataBoolean["content"] = "True"
                    dataBooleanF = DataBoolForm(dataBoolean)
                    if dataBooleanF.is_valid():
                        newDataBoolean = dataBooleanF.save(commit=False)
                        newDataBoolean.column = column
                        newDataBoolean.dataset = newDataset
                        newDataBoolean.creator = user
                        newDataBoolean.save()


class UserFactory:
    @staticmethod
    def createGroup(numMembers=10):
        # ============================================================
        # creates a group with 1000 members
        # ============================================================
        groupA = dict()
        groupA["name"] = (LiteralFactory.genRandString())
        groupF = DBGroupForm(groupA)
        if groupF.is_valid():
            newDBGroup = groupF.save()
            newDBGroup.save()
        for i in range(0, numMembers):
            user = DBUser.objects.create_user(username=LiteralFactory.genRandString())
            user.save()
            m = dict()
            m["isAdmin"] = False
            mF = MembershipForm(m)
            if mF.is_valid():
                newm = mF.save(commit=False)
                newm.user = user
                newm.group = newDBGroup
                newm.save()

        GroupSerializer.serializeOne(groupA["name"])
        return newDBGroup

    @staticmethod
    def createUserWithName(name, password):
        user = DBUser.objects.create_user(username=name, password=password)
        user.save()
        return user

    @staticmethod
    def createRandomUser(password):
        user = DBUser.objects.create_user(username=LiteralFactory.genRandString(), tableCreator=True, password=password)
        user.is_active = True
        user.admin = True
        user.save()
        return user

    @staticmethod
    def createTableRights(user, table):
        # ============================================================
        # creates a User with rights
        # ============================================================
        rights = dict()
        rights['viewLog'] = True
        rights['rightsAdmin'] = True
        rights['insert'] = True
        rights['delete'] = True
        rightsF = RightListForTableForm(rights)
        if rightsF.is_valid():
            newRights = rightsF.save(commit=False)
            newRights.user = user
            newRights.table = table
            newRights.save()
            return newRights

    @staticmethod
    def createColRights(user, column):
        # ============================================================
        # creates a User with rights
        # ============================================================
        rights = dict()
        rights['modify'] = True
        rights['read'] = True
        rightsF = RightListForColumnForm(rights)
        if rightsF.is_valid():
            newRights = rightsF.save(commit=False)
            newRights.user = user
            newRights.table = column.table
            newRights.column = column
            newRights.save()
            return newRights