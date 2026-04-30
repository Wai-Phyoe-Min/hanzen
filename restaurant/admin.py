from django.contrib import admin
from .models import (
    Category, MenuItem, CourseMenu, Reservation,
    Testimonial, GalleryImage, Order, OrderLine,
    UserProfile, SiteSettings, BusinessHours, ContactSubmission, NewsletterSubscriber
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ja', 'name_en', 'slug', 'order')
    prepopulated_fields = {'slug': ('name_en',)}
    ordering = ('order',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display  = ('name_ja', 'name_en', 'category', 'price', 'badge', 'is_available', 'is_vegetarian')
    list_filter   = ('category', 'is_available', 'badge', 'is_vegetarian')
    search_fields = ('name_ja', 'name_en')
    list_editable = ('is_available', 'price')
    ordering      = ('category', 'order')


@admin.register(CourseMenu)
class CourseMenuAdmin(admin.ModelAdmin):
    list_display  = ('name_ja', 'name_en', 'courses', 'price', 'is_active')
    list_editable = ('is_active',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display    = ('name', 'date', 'time', 'party_size', 'status', 'created_at')
    list_filter     = ('status', 'date')
    search_fields   = ('name', 'email', 'phone')
    list_editable   = ('status',)
    date_hierarchy  = 'date'
    readonly_fields = ('created_at',)
    raw_id_fields   = ('user',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ('author_name', 'author_location', 'rating', 'is_active', 'order')
    list_editable = ('is_active', 'order')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display  = ('title_en', 'is_featured', 'order')
    list_editable = ('is_featured', 'order')


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0
    readonly_fields = ('unit_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ('pk', 'session_key', 'status', 'created_at')
    list_filter     = ('status',)
    inlines         = [OrderLineInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display    = ('user', 'phone', 'preferred_lang', 'newsletter', 'created_at')
    list_filter     = ('preferred_lang', 'newsletter')
    search_fields   = ('user__username', 'user__email', 'phone')
    readonly_fields = ('created_at',)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display  = ('get_day_display', 'is_closed', 'lunch_open', 'lunch_close', 'dinner_open', 'dinner_close')
    list_editable = ('is_closed',)
    ordering      = ('day',)


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter   = ('subject', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
    ordering      = ('-created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    list_editable = ('is_active',)
    ordering = ('-subscribed_at',)