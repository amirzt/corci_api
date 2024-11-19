from django.contrib import admin

from Users.models import CustomUser, Country, City, Connection, UserCategory, Category

# Register your models here.
admin.site.register(Country)
admin.site.register(City)
admin.site.register(CustomUser)
admin.site.register(Connection)
admin.site.register(UserCategory)
admin.site.register(Category)
