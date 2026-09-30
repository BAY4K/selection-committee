from django.urls import path, include

from . import views
from .views import export_to_excel

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('form/', views.TestFormView.as_view(), name='form'),
    path('download-table/', views.download_table, name='download-table'),
    path('download-document/', views.download_document, name='download_document'),
    path('update-schools/', views.update_schools, name='update-schools'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('admin/export/', views.export_data, name='export-csv'),
    path('generate_document/<int:person_id>/', views.generate_document, name='generate_document'),
    path('export/', export_to_excel, name='export_to_excel'),
]
