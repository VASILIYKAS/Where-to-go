from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase
from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import Place, PlaceImage


class PlaceImageInline(SortableInlineAdminMixin, admin.StackedInline):
    model = PlaceImage
    extra = 3
    fields = ('image', 'get_preview', 'position')
    readonly_fields = ('get_preview',)
    ordering = ['position']

    def get_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '''
                <div>
                  <img src="{}" style="max-height: 200px;"/>
                </div>
                ''',
                obj.image.url,
                )
        return "Нет файла"


class PlaceAdminForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = '__all__'
        widgets = {
            'description_long': forms.Textarea(attrs={'cols': 80, 'rows': 30}),
        }


@admin.register(Place)
class PlaceAdmin(SortableAdminBase, admin.ModelAdmin):
    form = PlaceAdminForm
    inlines = [PlaceImageInline]
    list_display = ('title',)
    search_fields = ('title',)