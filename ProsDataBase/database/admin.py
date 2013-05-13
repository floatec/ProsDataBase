__author__ = 'My-Tien Nguyen'


from django.contrib import admin
from models import *

admin.site.register(Table)
admin.site.register(DataDescr)
admin.site.register(Dataset)

admin.site.register(TextData)
admin.site.register(NumericData)
admin.site.register(SelectionData)
admin.site.register(SelectionValue)
admin.site.register(DateData)
admin.site.register(BoolData)

admin.site.register(Datatype)
admin.site.register(TextType)
admin.site.register(NumericType)
admin.site.register(SelectionType)
admin.site.register(DateType)

admin.site.register(DBUser)
admin.site.register(DBGroup)
admin.site.register(RelUserGroup)
admin.site.register(RightList)
admin.site.register(RelRightsDataDescr)


#class TableAdmin(admin.ModelAdmin):
#    list_display = ('name', 'dataDescrs')