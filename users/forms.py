from django import forms
from .models import MyUser

class AdminUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name', 'role', 'school', 'phone_number', 'is_active', 'is_exam_manager', 'is_exam_officer', 'is_headteacher', 'profile_image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Include all roles
        self.fields['role'].choices = MyUser.ROLE_CHOICES
        
        # Make role required
        self.fields['role'].required = True
        
        # Make school optional by default, we'll enforce it in clean()
        self.fields['school'].required = False
        
        # Make phone number required
        self.fields['phone_number'].required = True
        
        # Make name fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
        # Add account status field
        self.fields['is_active'] = forms.BooleanField(
            label='Account Status',
            widget=forms.CheckboxInput,
            required=False,
            initial=True
        )
        
        # Add exam manager field
        self.fields['is_exam_manager'] = forms.BooleanField(
            label='Exam Manager',
            widget=forms.CheckboxInput,
            required=False,
            initial=False
        )
        
        # Add exam officer field
        self.fields['is_exam_officer'] = forms.BooleanField(
            label='Exam Officer',
            widget=forms.CheckboxInput,
            required=False,
            initial=False
        )

        # Add head teacher field
        self.fields['is_headteacher'] = forms.BooleanField(
            label='Head Teacher',
            widget=forms.CheckboxInput,
            required=False,
            initial=False
        )
        
        # Add client-side toggle logic or handle in clean() 
        # For now, let's keep it required unless we want to allow nulls generally
        # The user just asked to ALLOW Guardian role creation.
        
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        school = cleaned_data.get('school')
        
        if role == 'Guardian':
            # School is not strictly required for Guardians
            pass
        if role != 'Teacher':
            cleaned_data['is_exam_manager'] = False
            cleaned_data['is_exam_officer'] = False
            cleaned_data['is_headteacher'] = False
        elif not school:
            self.add_error('school', 'This field is required for the selected role.')
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep existing password"
    )

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name', 'role', 'school', 'phone_number', 'is_active', 'is_exam_manager', 'is_exam_officer', 'is_headteacher', 'profile_image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Include all roles
        self.fields['role'].choices = MyUser.ROLE_CHOICES
        
        # Make role required
        self.fields['role'].required = True
        
        # Make school optional by default, we'll enforce it in clean()
        self.fields['school'].required = False
        
        # Make phone number required
        self.fields['phone_number'].required = True
        
        # Make name fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
        # Add account status field
        self.fields['is_active'] = forms.BooleanField(
            label='Account Status',
            widget=forms.CheckboxInput,
            required=False
        )
        
        # Add exam manager field
        self.fields['is_exam_manager'] = forms.BooleanField(
            label='Exam Manager',
            widget=forms.CheckboxInput,
            required=False
        )
        
        # Add exam officer field
        self.fields['is_exam_officer'] = forms.BooleanField(
            label='Exam Officer',
            widget=forms.CheckboxInput,
            required=False
        )
        
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        school = cleaned_data.get('school')
        
        if role == 'Guardian':
            # School is not strictly required for Guardians
            pass
        if role != 'Teacher':
            cleaned_data['is_exam_manager'] = False
            cleaned_data['is_exam_officer'] = False
            cleaned_data['is_headteacher'] = False
        elif not school:
            self.add_error('school', 'This field is required for the selected role.')
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:  # Only update password if provided
            user.set_password(password)
        if commit:
            user.save()
        return user


class UserProfileUpdateForm(forms.ModelForm):
    """Form for users to update their own profile details, excluding roles and permissions."""
    password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep your current password"
    )

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'profile_image')

    def __init__(self, *args, **kwargs):
        # Extract the user who is performing the update
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['phone_number'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        # Restriction: Only Admins/Receptionists/Superusers can change non-password fields
        if current_user and not (current_user.is_superuser or current_user.role in ['Admin', 'Receptionist']):
            for field_name in ['email', 'first_name', 'last_name', 'phone_number', 'profile_image']:
                if field_name in self.fields:
                    self.fields[field_name].disabled = True
                    self.fields[field_name].help_text = "This field can only be changed by an administrator."

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
