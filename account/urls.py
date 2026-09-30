from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordChangeDoneView, PasswordChangeView
from django.urls import path, reverse_lazy

from . import views
from .views import RankProfileView

app_name = "account"

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.UserCreation.as_view(), name='registration'),

    path('profile/<int:pk>/', views.ProfileUser.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', views.EditProfile.as_view(), name='profile-edit'),
    path('profile/parents/<int:pk>/', views.ParentsProfileView.as_view(), name='parents-edit'),
    path('profile/documents/<int:pk>/', views.DocumentsProfileView.as_view(), name='documents-edit'),
    path('profile/admission/<int:pk>', views.AdmissionProfileView.as_view(), name='admission-create'),
    path('profile/rank/', RankProfileView.as_view(), name='rank-profile'),

    path('profile/rank', views.RankProfileView.as_view(), name='rank-profile'),

    path('password-change/', PasswordChangeView.as_view(), name='password_change_done'),
    path('password-change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password-reset/', PasswordResetView.as_view(
        template_name='account/password_reset_form.html',
        email_template_name='account/password_reset_email.html',
        success_url=reverse_lazy('account:password_reset_done')),
         name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='account/password_reset_confirm.html',
        success_url=reverse_lazy('account:password_reset_complete')
    ), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # path('change_password/', ),
]

