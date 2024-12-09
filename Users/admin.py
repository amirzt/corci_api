from django.contrib import admin

from Users.models import CustomUser, Country, City, Connection, UserCategory, Category, Banner, HomeMessage, Version, \
    UserFCMToken, OTP

# Register your models here.
admin.site.register(Country)
admin.site.register(City)
admin.site.register(CustomUser)
admin.site.register(Connection)
admin.site.register(UserCategory)
admin.site.register(Category)
admin.site.register(Banner)
admin.site.register(HomeMessage)
admin.site.register(Version)
admin.site.register(UserFCMToken)
admin.site.register(OTP)

