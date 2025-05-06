from django.contrib import admin
from .models import Place, PlaceImage


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 1
    fields = ('image', 'position')
    readonly_fields = ('image_info',)

    def image_info(self, obj):
        if obj.pk and obj.image:
            return obj.image.name.split('/')[-1]
        return "Нет файла"


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    inlines = [PlaceImageInline]
    list_display = ('title',)