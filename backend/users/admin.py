from django.contrib import admin

from users.models import Follow, User

admin.site.unregister(User)


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = (
        'username',
        'email'
    )
    list_filter = (
        'first_name',
        'last_name'
    )


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
