from django.contrib import admin

from testproject.db.models import *


admin.site.register(JSONModel)
admin.site.register(MonthModel)
admin.site.register(PickleModel)
admin.site.register(TimeDeltaModel)
