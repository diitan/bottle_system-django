from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('', include('orders.urls')),

    path('login/', accounts_views.login_view, name='login'),
    path('admin-panel/logout/', core_views.admin_logout, name='admin_logout'),
    path('admin-panel/', core_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/export-excel/', core_views.admin_export_excel, name='admin_export_excel'),
    path("delete-order/<int:order_id>/", core_views.delete_order, name="delete_order"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")


