from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, ListView

from account.forms import CustomUserCreationForm, LoginUserForm, ProfileUserForm, ParentsEditForm, DocumentEditForm, \
    AdmissionEditForm
from main.models import Applicant, Parent, Document, Admission, Department


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'account/authorization.html'
    context_object_name = 'login'

    def get_success_url(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return reverse_lazy('home')
        return reverse_lazy('account:profile', args=[self.request.user.id])


class UserCreation(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'account/authorization.html'
    context_object_name = 'registration'
    success_url = reverse_lazy('account:login')


class ProfileUser(TemplateView, LoginRequiredMixin):
    template_name = 'account/profile.html'

    def get_success_url(self):
        return reverse_lazy('account:profile', args=[self.request.user.id])

    def get_object(self, queryset=None):
        return self.request.user


class EditProfile(UpdateView, LoginRequiredMixin):
    model = Applicant
    template_name = 'account/profile_edit.html'
    form_class = ProfileUserForm

    def get_success_url(self):
        return reverse_lazy('account:profile', args=[self.request.user.id])


class ParentsProfileView(UpdateView, LoginRequiredMixin):
    model = Parent
    template_name = 'account/profile_edit.html'
    form_class = ParentsEditForm

    def get_success_url(self):
        return reverse_lazy('account:profile', args=[self.request.user.id])

    def get_object(self, queryset=None):
        return Parent.objects.get(student=self.request.user.student)


class DocumentsProfileView(UpdateView, LoginRequiredMixin):
    model = Document
    template_name = 'account/profile_edit.html'
    form_class = DocumentEditForm

    def get_success_url(self):
        return reverse_lazy('account:profile', args=[self.request.user.id])

    def get_object(self, queryset=None):
        return Document.objects.get(student=self.request.user.student)


class AdmissionProfileView(UpdateView, LoginRequiredMixin):
    model = Admission
    template_name = 'account/profile_edit.html'
    form_class = AdmissionEditForm

    def get_success_url(self):
        return reverse_lazy('account:profile', args=[self.request.user.id])

    def get_object(self, queryset=None):
        return Admission.objects.get(applicant=self.request.user.student)


class RankProfileView(LoginRequiredMixin, ListView):
    template_name = 'account/profile_rank.html'
    model = Admission

    def get_queryset(self):
        average_score = '4.0'
        user_departments = self.request.user.student.student.department.values_list('name', flat=True).distinct()
        user_admissions = Admission.objects.filter(applicant=self.request.user.student)

        department_admissions = []
        for departments in user_departments:
            department = Department.objects.get(name=departments)
            all_admissions = Admission.objects.filter(
                department=department,
                application_status__contains='accepted',
                average_score__gte=Decimal(average_score)
            ).order_by('-average_score', '-internal_exam')[:25]

            top_25_admissions = all_admissions[:25]

            # Добавляем пустые строки до 25
            while len(top_25_admissions) < 25:
                top_25_admissions = list(top_25_admissions) + [None]  # Добавляем None для пустых строк

            # Определяем текущий рейтинг пользователя в департаменте
            user_admission = user_admissions.filter(department=department).first()
            user_rank = list(all_admissions).index(user_admission) + 1 if user_admission in all_admissions else None
            is_on_budget = user_rank is not None and user_rank <= 25

            department_admissions.append((department, top_25_admissions, user_rank, is_on_budget))

        return department_admissions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['department_admissions'] = self.get_queryset()
        return context