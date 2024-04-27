from pprint import pformat

from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.timezone import now

from .models import Session


class IsValidFilter(admin.SimpleListFilter):
    title = "validity"
    parameter_name = "active"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> tuple[tuple[bool, str], tuple[bool, str]]:
        return ((True, "active"), (False, "expired"))

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value() is True:
            return queryset.filter(expire_date__gt=now())
        elif self.value() is False:
            return queryset.filter(expire_date__lte=now())
        else:
            return queryset


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    search_fields = ()
    list_display = (
        "session_key",
        "user",
        "ip",
        "device",
        "location",
        "is_valid",
        "created_at",
        "expire_date",
    )
    sortable_by = (
        "user",
        "ip",
        "device",
        "location",
        "is_valid",
        "created_at",
        "expire_date",
    )
    list_filter = (
        IsValidFilter,
        AutocompleteFilterFactory("user", "user"),
        "created_at",
        "expire_date",
    )
    fields = (
        "session_key",
        "user_id",
        "user",
        "ip",
        "device",
        "location",
        "is_valid",
        "session_data_decoded",
        "created_at",
        "expire_date",
    )
    readonly_fields = (
        "session_key",
        "user_id",
        "user",
        "ip",
        "device",
        "location",
        "is_valid",
        "session_data_decoded",
        "created_at",
        "expire_date",
    )

    @admin.display(boolean=True, description="Is valid")
    def is_valid(self, obj: Session) -> bool:
        return obj.expire_date > now()

    @admin.display(description="Session data (decoded)")
    def session_data_decoded(self, obj: Session) -> str:
        return format_html(
            '<pre style="white-space: pre-wrap; max-width: 800px; display: inline-block; direction: ltr;">{}</pre>',
            pformat(obj.get_decoded()),
        )
