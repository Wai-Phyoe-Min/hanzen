from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    # Pages
    path('',                              views.home,                   name='home'),
    path('menu/',                         views.menu,                   name='menu'),
    path('gallery/',                      views.gallery,                name='gallery'),
    path('about/',                        views.about,                  name='about'),
    path('hours/',                        views.hours,                  name='hours'),
    path('contact/',                      views.contact,                name='contact'),
    path('reservation/',                  views.reservation,            name='reservation'),
    path('reservation/success/<int:pk>/', views.reservation_success,    name='reservation_success'),
    path('reservation/<int:pk>/cancel/',  views.cancel_reservation,     name='cancel_reservation'),
    path('cart/',                         views.cart_view,              name='cart'),
    path('order/',                        views.order,                  name='order'),
    path('order/success/<int:pk>/',      views.order_success,          name='order_success'),

    # Cart AJAX
    path('cart/add/',    views.cart_add,    name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/clear/',  views.cart_clear,  name='cart_clear'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # User Dashboard
    path('dashboard/',              views.dashboard,               name='dashboard'),
    path('dashboard/profile/',      views.dashboard_profile,       name='dashboard_profile'),
    path('dashboard/reservations/', views.dashboard_reservations,  name='dashboard_reservations'),
    path('dashboard/orders/',       views.dashboard_orders,        name='dashboard_orders'),

    # Admin Dashboard
    path('hanzen-admin/',                          views.admin_dashboard,          name='admin_dashboard'),
    path('hanzen-admin/reservations/',             views.admin_reservations,       name='admin_reservations'),
    path('hanzen-admin/reservations/<int:pk>/update/', views.admin_reservation_update, name='admin_reservation_update'),
    path('hanzen-admin/menu/',                     views.admin_menu,               name='admin_menu'),
    path('hanzen-admin/menu/<int:pk>/toggle/',     views.admin_menu_toggle,        name='admin_menu_toggle'),
    path('hanzen-admin/users/',                    views.admin_users,              name='admin_users'),
    path('hanzen-admin/gallery/',                  views.admin_gallery,            name='admin_gallery'),
    path('hanzen-admin/gallery/add/',              views.admin_gallery_add,        name='admin_gallery_add'),
    path('hanzen-admin/gallery/<int:pk>/delete/',  views.admin_gallery_delete,     name='admin_gallery_delete'),
    path('hanzen-admin/profile/',                  views.admin_profile,            name='admin_profile'),
    path('hanzen-admin/change-password/',          views.admin_change_password,    name='admin_change_password'),
    # Admin: Course Management
    path('hanzen-admin/courses/',                  views.admin_courses,            name='admin_courses'),
    path('hanzen-admin/courses/add/',              views.admin_course_add,         name='admin_course_add'),
    path('hanzen-admin/courses/<int:pk>/edit/',    views.admin_course_edit,        name='admin_course_edit'),
    path('hanzen-admin/courses/<int:pk>/delete/',  views.admin_course_delete,      name='admin_course_delete'),
    path('hanzen-admin/courses/<int:pk>/toggle/',  views.admin_course_toggle,      name='admin_course_toggle'),
    # Admin: Newsletter Management
    path('hanzen-admin/newsletter/',               views.admin_newsletter,         name='admin_newsletter'),
    path('hanzen-admin/newsletter/<int:pk>/toggle/', views.admin_newsletter_toggle, name='admin_newsletter_toggle'),
    path('hanzen-admin/newsletter/<int:pk>/delete/', views.admin_newsletter_delete, name='admin_newsletter_delete'),

    # Legal pages
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/',   views.terms_view,   name='terms'),

    # Newsletter & APIs
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('api/menu/',             views.api_menu,             name='api_menu'),
    path('api/availability/',     views.api_availability,     name='api_availability'),
    path('api/time-slots/',       views.api_time_slots,       name='api_time_slots'),

    # Admin CRUD
    path('hanzen-admin/menu/add/',              views.admin_menu_add,            name='admin_menu_add'),
    path('hanzen-admin/menu/<int:pk>/edit/',    views.admin_menu_edit,           name='admin_menu_edit'),
    path('hanzen-admin/menu/<int:pk>/delete/',  views.admin_menu_delete,         name='admin_menu_delete'),
    path('hanzen-admin/users/<int:pk>/delete/', views.admin_user_delete,         name='admin_user_delete'),
    path('hanzen-admin/users/<int:pk>/toggle-staff/', views.admin_user_toggle_staff, name='admin_user_toggle_staff'),
    path('hanzen-admin/business-hours/',        views.admin_business_hours,      name='admin_business_hours'),
    path('hanzen-admin/business-hours/save/',   views.admin_business_hours_save, name='admin_business_hours_save'),
    path('hanzen-admin/gallery/<int:pk>/edit/', views.admin_gallery_edit,        name='admin_gallery_edit'),
    path('hanzen-admin/orders/',                   views.admin_orders,             name='admin_orders'),
    path('hanzen-admin/orders/<int:pk>/status/',   views.admin_order_status_update, name='admin_order_status_update'),
    path('hanzen-admin/orders/<int:pk>/details/',  views.admin_order_details,      name='admin_order_details'),
    path('hanzen-admin/contact/',                  views.admin_contact,            name='admin_contact'),
    path('hanzen-admin/contact/<int:pk>/mark-read/', views.admin_contact_mark_read, name='admin_contact_mark_read'),
    path('hanzen-admin/contact/<int:pk>/details/', views.admin_contact_details,    name='admin_contact_details'),
    path('hanzen-admin/settings/',              views.admin_settings,            name='admin_settings'),

    # User: change password
    path('dashboard/change-password/', views.change_password, name='change_password'),

    # API
    path('api/categories/', views.api_categories, name='api_categories'),

]
