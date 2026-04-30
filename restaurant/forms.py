from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .models import Reservation, CourseMenu, UserProfile, MenuItem, Category
import datetime


class ReservationForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type':'date','min':datetime.date.today().isoformat()}),
        label=_('ご来店日 / Date'))
    
    class Meta:
        model  = Reservation
        fields = ['name','email','phone','date','time','party_size','course','special_request']
        labels = {'name':_('お名前 / Name'),'email':_('メール / Email'),'phone':_('電話 / Phone'),
                  'time':_('時間 / Time'),'party_size':_('人数 / Guests'),'course':_('コース / Course'),'special_request':_('ご要望 / Requests')}
        widgets = {'name':forms.TextInput(attrs={'placeholder':'田中 太郎'}),'email':forms.EmailInput(attrs={'placeholder':'taro@example.com'}),
                   'phone':forms.TextInput(attrs={'placeholder':'03-XXXX-XXXX'}),'special_request':forms.Textarea(attrs={'rows':3})}
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['course'].queryset = CourseMenu.objects.filter(is_active=True)
        self.fields['course'].empty_label = '未定 / Undecided'
        self.fields['course'].required = False
        for f in self.fields.values(): 
            f.widget.attrs.setdefault('class','form-control')


class ContactForm(forms.Form):
    SUBJECT_CHOICES = [
        ('', '選択してください / Select a subject'),
        ('reservation', 'ご予約について / About Reservations'),
        ('menu', 'メニューについて / About Menu'),
        ('course', 'コース料理について / About Course Meals'),
        ('private', '個室・貸切について / Private Rooms & Events'),
        ('allergy', 'アレルギー・食事制限について / Allergies & Dietary Restrictions'),
        ('career', '採用について / Careers'),
        ('press', '取材・メディアについて / Press & Media'),
        ('other', 'その他 / Other'),
    ]
    
    name    = forms.CharField(max_length=100, label=_('お名前 / Name'))
    email   = forms.EmailField(label=_('メール / Email'))
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, label=_('件名 / Subject'))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows':5}), label=_('メッセージ / Message'))
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for f in self.fields.values(): 
            f.widget.attrs['class'] = 'form-control'
        # Add specific class for select
        self.fields['subject'].widget.attrs['class'] = 'form-select'


class NewsletterForm(forms.Form):
    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'placeholder':'email@example.com','class':'newsletter-input'}))


class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True, label=_('メールアドレス / Email'))
    first_name = forms.CharField(max_length=50, label=_('名前 / First Name'))
    last_name  = forms.CharField(max_length=50, label=_('苗字 / Last Name'))
    class Meta:
        model  = User
        fields = ['username','first_name','last_name','email','password1','password2']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for f in self.fields.values(): f.widget.attrs['class'] = 'form-control'


class LoginForm(AuthenticationForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for f in self.fields.values(): f.widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, label=_('名前'))
    last_name  = forms.CharField(max_length=50, label=_('苗字'))
    email      = forms.EmailField(label=_('メール'))
    class Meta:
        model  = UserProfile
        fields = ['phone','birthday','preferred_lang','dietary_notes','newsletter']
        labels = {'phone':_('電話番号'),'birthday':_('誕生日'),'preferred_lang':_('言語'),'dietary_notes':_('食事制限・アレルギー'),'newsletter':_('メルマガ登録')}
        widgets = {'birthday':forms.DateInput(attrs={'type':'date'}),'dietary_notes':forms.Textarea(attrs={'rows':3})}
    def __init__(self,*args,**kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args,**kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial  = self.user.last_name
            self.fields['email'].initial      = self.user.email
        for f in self.fields.values():
            if hasattr(f.widget,'attrs'): f.widget.attrs.setdefault('class','form-control')
    def save(self,commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name  = self.cleaned_data['last_name']
            self.user.email      = self.cleaned_data['email']
            if commit: self.user.save()
        if commit: profile.save()
        return profile
    
class BilingualPasswordChangeForm(DjangoPasswordChangeForm):
    """Custom password change form with bilingual error messages"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update labels
        self.fields['old_password'].label = _('現在のパスワード / Current Password')
        self.fields['new_password1'].label = _('新しいパスワード / New Password')
        self.fields['new_password2'].label = _('新しいパスワード（確認） / Confirm New Password')
        
        # Update help texts
        self.fields['new_password1'].help_text = _(
            '8文字以上必要です。数字のみやよく使われるパスワードは使用できません。 / '
            'At least 8 characters. Cannot be entirely numeric or too common.'
        )
        
        # Add styling
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'form-control')
    
    def clean_old_password(self):
        """
        Validate that the old password is correct.
        Override to provide bilingual error message.
        """
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                _('元のパスワードが間違っています。もう一度入力してください。 / Your old password was entered incorrectly. Please enter it again.'),
                code='password_incorrect',
            )
        return old_password
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            # Re-use Django's validation but capture errors for translation
            from django.contrib.auth.password_validation import validate_password
            from django.core.exceptions import ValidationError
            try:
                validate_password(password, self.user)
            except ValidationError as e:
                # Translate Django's default messages
                translated_errors = []
                for msg in e.messages:
                    translated_errors.append(self._translate_error(msg))
                raise ValidationError(translated_errors)
        return password
    
    def _translate_error(self, msg):
        """Translate Django's built-in password validation messages to bilingual"""
        translations = {
            'This password is too short. It must contain at least 8 characters.':
                'パスワードが短すぎます。最低 8 文字以上必要です。 / Password is too short. It must contain at least 8 characters.',
            'This password is too common.':
                'このパスワードはよく使われています。別のパスワードを選んでください。 / This password is too common. Please choose a different one.',
            'This password is entirely numeric.':
                '数字だけのパスワードは使用できません。文字も含めてください。 / This password is entirely numeric. Please include letters.',
            'The password is too similar to the username.':
                'パスワードがユーザー名に似すぎています。 / The password is too similar to the username.',
            'The password is too similar to the email address.':
                'パスワードがメールアドレスに似すぎています。 / The password is too similar to the email address.',
            'The password is too similar to the first name.':
                'パスワードが名前に似すぎています。 / The password is too similar to the first name.',
            'The password is too similar to the last name.':
                'パスワードが姓に似すぎています。 / The password is too similar to the last name.',
        }
        
        # Check exact and partial matches
        for eng_key, bilingual_msg in translations.items():
            if eng_key == msg or eng_key in msg:
                return bilingual_msg
        
        # Handle old password error (which may come in different formats)
        if 'old password' in msg.lower() and ('incorrect' in msg.lower() or 'wrong' in msg.lower()):
            return '元のパスワードが間違っています。もう一度入力してください。 / Your old password was entered incorrectly. Please enter it again.'
        
        # If message contains "too similar" but with dynamic content
        if 'too similar to' in msg:
            return 'パスワードが他の個人情報に似すぎています。 / The password is too similar to your other personal information.'
        
        # Fallback: return bilingual format with original message
        return f'パスワードエラー / Password Error: {msg}'


class MenuItemForm(forms.ModelForm):
    class Meta:
        model  = MenuItem
        fields = ['category','name_ja','name_en','description_ja','description_en',
                  'price','image_url','badge','is_available','is_vegetarian','is_gluten_free','order']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description_ja': forms.Textarea(attrs={'rows':3, 'class': 'form-control'}),
            'description_en': forms.Textarea(attrs={'rows':3, 'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'form-control')
        # Ensure category uses form-select
        self.fields['category'].widget.attrs['class'] = 'form-select'
