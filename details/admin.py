from django.contrib import admin
from .models import User, Organization

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
# Register your models here.
admin.site.register(User)
admin.site.register(Organization, OrganizationAdmin)
