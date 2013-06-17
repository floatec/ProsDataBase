__author__ = 'My-Tien Nguyen'


from django.contrib import admin
from models import *

admin.site.register(Category)
admin.site.register(Table)
admin.site.register(Column)
admin.site.register(Dataset)

admin.site.register(DataText)
admin.site.register(DataNumeric)
admin.site.register(DataDate)
admin.site.register(DataSelection)
admin.site.register(SelectionValue)
admin.site.register(DataBool)
admin.site.register(DataTable)
admin.site.register(TableLink)

admin.site.register(Type)
admin.site.register(TypeText)
admin.site.register(TypeNumeric)
admin.site.register(TypeDate)
admin.site.register(TypeSelection)
admin.site.register(TypeBool)
admin.site.register(TypeTable)

admin.site.register(HistoryTable)
admin.site.register(MessageTable)

admin.site.register(DBUser)
admin.site.register(DBGroup)
admin.site.register(Membership)
admin.site.register(RightListForTable)
admin.site.register(RightListForColumn)


#class TableAdmin(admin.ModelAdmin):
#    list_display = ('name', 'column')