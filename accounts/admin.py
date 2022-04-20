from django.contrib import admin
from .models import Account, UserProfile
from django.utils.html import format_html

# Register your models here.
class AccountAdmin(admin.ModelAdmin):
    # https://docs.djangoproject.com/zh-hans/3.2/ref/contrib/admin/
    list_display = ('email', 'first_name', 'last_name', 'username')# Register your models here.
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_join')
    ordering = ('-date_join',)
    fieldsets = ()  # 'password' readonly


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        if object.profile_picture:
            pic_url = object.profile_picture.url
        else:
            pic_url = 'https://www.w3schools.com/howto/img_avatar.png'
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(pic_url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'zipcode')

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
