from django.contrib import admin

from Users.models import CustomUser, Country, City

# Register your models here.
admin.site.register(Country)
admin.site.register(City)
admin.site.register(CustomUser)
