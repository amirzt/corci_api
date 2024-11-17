from django.contrib import admin

from Users.models import CustomUser, Country, City, Connection

# Register your models here.
admin.site.register(Country)
admin.site.register(City)
admin.site.register(CustomUser)
admin.site.register(Connection)
