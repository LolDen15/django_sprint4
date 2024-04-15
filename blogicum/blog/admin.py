from django.contrib import admin

from .models import Post, Category, Location


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'is_published'
    )
    list_editable = ('is_published', 'category')
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display_links = ('title',)


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'is_published'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display_links = ('title',)


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
