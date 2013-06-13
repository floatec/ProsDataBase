__author__ = 'tieni'


class Error():
    # table errors
    CATEGORY_NOTFOUND = 0
    CATEGORY_CREATE = 1
    CATEGORY_DELETE = 2
    TABLE_NOTFOUND = 3
    TABLE_REFERENCED = 4
    TABLE_CREATE = 5

    # column errors
    COLUMN_NOTFOUND = 6
    COLUMN_CREATE = 7
    COLUMN_REF = 8

    # dataset errors
    DATASET_CREATE = 9
    DATASET_NOTFOUND = 10
    DATASET_REF = 11

    # data field errors
    DATAFIELD_NOTFOUND = 12
    DATAFIELD_CREATE = 13

    # data type errors
    TYPE_CREATE = 14
    TYPE_INVALID = 15
    TYPE_NOTYPE = 16

    # auth errors
    USER_NOTFOUND = 17
    GROUP_NOTFOUND = 18

    # rights
    RIGHTS_TABLE_CREATE = 19
    RIGHTS_COLUMN_CREATE = 20
    RIGHTS_TABLE_DELETE = 21
    RIGHTS_COLUMN_DELETE = 22