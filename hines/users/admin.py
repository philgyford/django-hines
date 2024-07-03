from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra fields", {"fields": ["mastodon_account"]}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra fields", {"fields": ["mastodon_account"]}),
    )
