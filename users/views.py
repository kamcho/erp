from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import SetPasswordForm
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import MyUser
from .forms import AdminUserCreationForm, UserUpdateForm, UserProfileUpdateForm

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MyUser
    form_class = AdminUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:create-user')

    def test_func(self):
        # Only Admins, Superusers or Receptionists can create users here
        return self.request.user.role in ['Admin', 'Receptionist'] or self.request.user.is_superuser

    def form_valid(self, form):
        if self.request.user.school:
            form.instance.school = self.request.user.school
        messages.success(self.request, f"User {form.cleaned_data.get('email')} created successfully.")
        return super().form_valid(form)


class UserProfileView(LoginRequiredMixin, DetailView):
    model = MyUser
    template_name = 'users/user_profile.html'
    context_object_name = 'user_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = (
            self.request.user.is_superuser or 
            self.request.user.role in ['Admin', 'Receptionist'] or 
            (self.request.user == self.object and self.request.user.role == 'Admin')
        )
        context['can_reset_password'] = (
            self.request.user.is_superuser or 
            self.request.user.role in ['Admin', 'Receptionist']
        )
        return context


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MyUser
    form_class = UserProfileUpdateForm
    template_name = 'users/user_update.html'
    context_object_name = 'user_profile'
    
    def get_success_url(self):
        from django.urls import reverse
        return reverse('users:user-profile', kwargs={'pk': self.object.pk})

    def test_func(self):
        # Allow users to update their own profile OR Admins, Superusers and Receptionists to update any
        obj = self.get_object()
        return self.request.user == obj or self.request.user.role in ['Admin', 'Receptionist'] or self.request.user.is_superuser

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f"User {form.cleaned_data.get('email')} updated successfully.")
        return super().form_valid(form)

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def quick_update_user_role(request):
    """Allows superusers to quickly switch their own identity for testing purposes."""
    user = request.user
    role = request.POST.get('role')
    flag = request.POST.get('flag')
    
    school_id = request.POST.get('school_id')
    
    if role:
        user.role = role
        messages.success(request, f"Role switched to {role}")
    
    if school_id:
        from core.models import School
        if school_id == 'none':
            user.school = None
            messages.success(request, "Switched to Global View (No School linked)")
        else:
            try:
                school = School.objects.get(id=school_id)
                user.school = school
                messages.success(request, f"Switched to {school.name}")
            except School.DoesNotExist:
                messages.error(request, "Invalid school selected")
    
    if flag:
        if flag == 'is_headteacher':
            user.is_headteacher = not user.is_headteacher
            messages.success(request, f"Headteacher status: {user.is_headteacher}")
        elif flag == 'is_exam_manager':
            user.is_exam_manager = not user.is_exam_manager
            messages.success(request, f"Exam Manager status: {user.is_exam_manager}")
        elif flag == 'is_exam_officer':
            user.is_exam_officer = not user.is_exam_officer
            messages.success(request, f"Exam Officer status: {user.is_exam_officer}")
        elif flag == 'is_staff':
            user.is_staff = not user.is_staff
            messages.success(request, f"Staff status: {user.is_staff}")
            
    user.save()
    return redirect(request.META.get('HTTP_REFERER', 'core:dashboard'))

@login_required
def receptionist_reset_password(request, user_id):
    """Allows receptionists, admins, or superusers to reset a user's password."""
    if not (request.user.role in ['Admin', 'Receptionist'] or request.user.is_superuser):
        messages.error(request, "You do not have permission to reset passwords.")
        return redirect('core:dashboard')
    
    target_user = get_object_or_404(MyUser, id=user_id)
    
    if request.method == 'POST':
        form = SetPasswordForm(target_user, request.POST)
        if form.is_valid():
            form.save()
            
            # Log the action
            from core.models import ActivityLog
            ActivityLog.objects.create(
                user=request.user,
                action='Reset Password',
                category='User',
                description=f"Manually reset password for user {target_user.get_full_name()} ({target_user.email})",
                target_model='MyUser',
                target_id=target_user.id,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f"Password for {target_user.email} has been reset successfully.")
            return redirect('users:user-profile', pk=user_id)
    else:
        form = SetPasswordForm(target_user)
        
    return render(request, 'users/receptionist_reset_password.html', {
        'form': form,
        'target_user': target_user
    })

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = MyUser
    template_name = 'users/user_list.html'
    context_object_name = 'users_list'
    paginate_by = 20

    def test_func(self):
        # Only Admins, Superusers or Receptionists can view the user list
        return self.request.user.role in ['Admin', 'Receptionist'] or self.request.user.is_superuser

    def get_queryset(self):
        queryset = MyUser.objects.all().order_by('-date_joined')
        
        q = self.request.GET.get('q')
        role = self.request.GET.get('role')
        
        if q:
            queryset = queryset.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q) |
                Q(phone_number__icontains=q)
            )
            
        if role:
            queryset = queryset.filter(role=role)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Stats for the top cards
        context['total_users'] = MyUser.objects.count()
        context['active_users'] = MyUser.objects.filter(is_active=True).count()
        context['staff_users'] = MyUser.objects.filter(is_staff=True).count()
        context['admin_users'] = MyUser.objects.filter(role='Admin').count()
        
        # Roles for filter dropdown
        context['roles'] = MyUser.ROLE_CHOICES
        
        # Current filters to persist in pagination and UI
        context['q'] = self.request.GET.get('q', '')
        context['selected_role'] = self.request.GET.get('role', '')
        
        return context
