from django.contrib import admin
from .models import Place, PlaceImage
from django.utils.html import format_html


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 1
    fields = ('image', 'get_preview', 'position')
    readonly_fields = ('get_preview',)

    def get_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '''
                <div>
                  <img src="{}" style="max-height: 200px;"/>
                </div>
                ''',
                obj.image.url,
                obj.image.name.split('/')[-1]
                )
        return "Нет файла"


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    inlines = [PlaceImageInline]
    list_display = ('title',)