from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.utils.html import format_html

from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from .models import Place, PlaceImage


class MoveImagesForm(forms.Form):
    target_place = forms.ModelChoiceField(
        queryset=Place.objects.all(),
        label='Перенести в место'
    )


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
                  <img src='{}' style='max-width: 300px; max-height: 200px;'/>
                </div>
                ''',
                obj.image.url,
            )
        return 'Нет файла'


class PlaceAdminForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = '__all__'
        widgets = {
            'long_description': forms.Textarea(attrs={'cols': 80, 'rows': 30}),
        }


@admin.register(Place)
class PlaceAdmin(SortableAdminBase, admin.ModelAdmin):
    form = PlaceAdminForm
    inlines = [PlaceImageInline]
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(PlaceImage)
class PlaceImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'fetch_preview', 'place_title', 'position')
    list_filter = ('place',)
    raw_id_fields = ('place',)
    actions = ['move_images']

    def place_title(self, obj):
        return obj.place.title if obj.place else '-'

    place_title.short_description = 'Название места'
    place_title.admin_order_field = 'place__title'

    def fetch_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '''
                <div>
                  <img src='{}' style='max-width: 300px; max-height: 200px;'/>
                </div>
                ''',
                obj.image.url,
            )
        return 'Нет файла'

    fetch_preview.short_description = 'Превью'

    def move_images(self, request, queryset):
        if 'apply' in request.POST:
            form = MoveImagesForm(request.POST)
            if form.is_valid():
                target_place = form.cleaned_data['target_place']
                count = queryset.count()
                queryset.update(place=target_place)
                self.message_user(
                    request,
                    f'Успешно перенесено {count} изображений в место '{target_place.title}'',
                    messages.SUCCESS
                )
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = MoveImagesForm(initial={
                '_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)
            })

        return render(
            request,
            'reassign_place.html',
            context={
                'images': queryset,
                'form': form,
                'title': 'Перенос изображений'
            }
        )

    move_images.short_description = 'Перенести выбранные изображения'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'move-images/',
                self.admin_site.admin_view(self.move_images),
                name='move_images'
            ),
        ]
        return custom_urls + urls