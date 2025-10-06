from parler.admin import TranslatableAdmin

from django.contrib import admin

from .models import City, Country, Region


@admin.register(Country)
class CountryAdmin(TranslatableAdmin):
    list_display = ["name", "code"]
    search_fields = ["translations__name", "code"]
    ordering = ["code"]


@admin.register(Region)
class RegionAdmin(TranslatableAdmin):
    list_display = ["name", "country", "code"]
    list_filter = ["country"]
    search_fields = ["translations__name", "code"]
    autocomplete_fields = ["country"]


@admin.register(City)
class CityAdmin(TranslatableAdmin):
    list_display = ["name", "region", "postal_code"]
    list_filter = ["region__country", "region"]
    search_fields = ["translations__name", "postal_code"]
    autocomplete_fields = ["region"]