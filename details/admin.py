from django.contrib import admin
from .models import User, Organisation

class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['name', 'orgId']
# Register your models here.
admin.site.register(User)
admin.site.register(Organisation, OrganisationAdmin)
