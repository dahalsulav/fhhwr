from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Customer, Worker, HourlyRateApproval


class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = "customer"


class WorkerInline(admin.StackedInline):
    model = Worker
    can_delete = False
    verbose_name_plural = "worker"


class UserAdmin(BaseUserAdmin):
    inlines = (CustomerInline, WorkerInline)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_customer",
        "is_worker",
    )
    list_filter = ("is_customer", "is_worker", "is_active", "is_staff")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Account Type", {"fields": ("is_customer", "is_worker")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_customer",
                    "is_worker",
                ),
            },
        ),
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "customer__location",
        "worker__location",
        "worker__skills",
    )
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "email_verified")
    search_fields = ("user__email", "user__first_name", "user__last_name", "location")


class WorkerAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "location",
        "skills",
        "hourly_rate",
        "email_verified",
        "is_available",
    )
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "location",
        "skills",
    )


admin.site.register(User, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Worker, WorkerAdmin)


@admin.register(HourlyRateApproval)
class HourlyRateApprovalAdmin(admin.ModelAdmin):
    list_display = ("worker", "hourly_rate", "approved")
    actions = ["approve_workers"]

    def approve_workers(self, request, queryset):
        for hourly_rate_approval in queryset:
            if not hourly_rate_approval.approved:
                hourly_rate_approval.approved = True
                hourly_rate_approval.worker.user.is_active = True
                hourly_rate_approval.worker.hourly_rate = (
                    hourly_rate_approval.hourly_rate
                )
                hourly_rate_approval.worker.save()
                hourly_rate_approval.worker.user.save()
                hourly_rate_approval.save()
        self.message_user(request, "Selected workers have been approved.")

    approve_workers.short_description = "Approve workers and their hourly rates"
