from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Category(models.Model):
    slug     = models.SlugField(unique=True)
    name_ja  = models.CharField(max_length=60)
    name_en  = models.CharField(max_length=60)
    order    = models.PositiveIntegerField(default=0)
    class Meta: ordering = ['order']
    def __str__(self): return f'{self.name_ja} / {self.name_en}'


class MenuItem(models.Model):
    BADGE_CHOICES = [('','—'),('recommend','おすすめ'),('seasonal','季節'),('popular','人気'),('new','NEW'),('limited','限定')]
    category       = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name_ja        = models.CharField(max_length=100)
    name_en        = models.CharField(max_length=100)
    description_ja = models.TextField()
    description_en = models.TextField()
    price          = models.PositiveIntegerField()
    image_url      = models.CharField(max_length=500, blank=True)
    badge          = models.CharField(max_length=20, choices=BADGE_CHOICES, blank=True)
    is_available   = models.BooleanField(default=True)
    is_vegetarian  = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    order          = models.PositiveIntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['order','name_ja']
    def __str__(self): return f'{self.name_ja} — ¥{self.price:,}'
    @property
    def price_formatted(self): return f'¥{self.price:,}'
    @property
    def badge_label_en(self):
        return {
            'recommend': 'RECOMMEND',
            'seasonal': 'SEASONAL',
            'popular': 'POPULAR',
            'new': 'NEW',
            'limited': 'LIMITED'
        }.get(self.badge, '')


class CourseMenu(models.Model):
    COURSE_TIER = [('matsu','松 Matsu'),('chiku','竹 Chiku'),('ume','梅 Ume'),('omakase','おまかせ')]
    tier           = models.CharField(max_length=20, choices=COURSE_TIER, unique=True)
    name_ja        = models.CharField(max_length=60)
    name_en        = models.CharField(max_length=60)
    description_ja = models.TextField()
    description_en = models.TextField()
    price          = models.PositiveIntegerField()
    courses        = models.PositiveIntegerField()
    image_url = models.CharField(max_length=500, blank=True)
    is_active      = models.BooleanField(default=True)
    class Meta: ordering = ['price']
    def __str__(self): return f'{self.name_ja} ¥{self.price:,}'


class Reservation(models.Model):
    PARTY_CHOICES = [(i,f'{i}名') for i in range(1,9)] + [(9,'9名以上')]
    TIME_SLOTS = [('11:30','11:30'),('12:00','12:00'),('12:30','12:30'),
                  ('18:00','18:00'),('18:30','18:30'),('19:00','19:00'),
                  ('19:30','19:30'),('20:00','20:00'),('20:30','20:30')]
    STATUS = [('pending','確認待ち'),('confirmed','確認済み'),('cancelled','キャンセル'),('completed','来店済み')]
    user           = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reservations')
    name           = models.CharField(max_length=100)
    email          = models.EmailField()
    phone          = models.CharField(max_length=20)
    date           = models.DateField()
    time           = models.CharField(max_length=5, choices=TIME_SLOTS)
    party_size     = models.PositiveIntegerField(choices=PARTY_CHOICES)
    course         = models.ForeignKey(CourseMenu, null=True, blank=True, on_delete=models.SET_NULL)
    special_request= models.TextField(blank=True)
    status         = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at     = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-date','time']
    def __str__(self): return f'{self.name} — {self.date} {self.time}'


class Testimonial(models.Model):
    author_name     = models.CharField(max_length=100)
    author_location = models.CharField(max_length=100, blank=True)
    quote_ja        = models.TextField()
    quote_en        = models.TextField()
    rating          = models.PositiveSmallIntegerField(default=5)
    is_active       = models.BooleanField(default=True)
    order           = models.PositiveIntegerField(default=0)
    class Meta: ordering = ['order']
    def __str__(self): return f'{self.author_name} ({self.rating}★)'


class GalleryImage(models.Model):
    title_ja    = models.CharField(max_length=100, blank=True)
    title_en    = models.CharField(max_length=100, blank=True)
    image_url   = models.URLField()
    thumb_url   = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    order       = models.PositiveIntegerField(default=0)
    class Meta: ordering = ['order']
    def __str__(self): return self.title_en or self.image_url[:60]


class Order(models.Model):
    STATUS = [('open','Open'),('submitted','Submitted'),('kitchen','In Kitchen'),('ready','Ready'),('done','Done'),('cancelled','Cancelled')]
    user        = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    session_key = models.CharField(max_length=40, blank=True)
    status      = models.CharField(max_length=20, choices=STATUS, default='open')
    note        = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    def total(self): return sum(item.subtotal() for item in self.lines.all())
    def total_items(self): return sum(item.quantity for item in self.lines.all())
    def __str__(self): return f'Order #{self.pk} [{self.status}]'


class OrderLine(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    menu_item  = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity   = models.PositiveIntegerField(default=1)
    unit_price = models.PositiveIntegerField()
    def subtotal(self): return self.quantity * self.unit_price
    def __str__(self): return f'{self.menu_item.name_ja} x{self.quantity}'


class UserProfile(models.Model):
    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone        = models.CharField(max_length=20, blank=True)
    birthday     = models.DateField(null=True, blank=True)
    avatar_url   = models.URLField(blank=True)
    preferred_lang = models.CharField(max_length=4, choices=[('ja','Japanese'),('en','English')], default='ja')
    dietary_notes  = models.TextField(blank=True)
    newsletter     = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.user.username} profile'
    @property
    def total_reservations(self): return self.user.reservations.count()
    @property
    def upcoming_reservations(self): return self.user.reservations.filter(date__gte=timezone.now().date(), status__in=['pending','confirmed'])


class SiteSettings(models.Model):
    """Singleton model for admin-editable site settings."""
    seasonal_banner_text_ja = models.CharField(max_length=200, default='春の特別メニュー 開始')
    seasonal_banner_text_en = models.CharField(max_length=200, default='Spring Special Menu Now Available')
    banner_active            = models.BooleanField(default=True)
    announcement_ja          = models.TextField(blank=True)
    announcement_en          = models.TextField(blank=True)
    contact_phone            = models.CharField(max_length=30, default='03-1234-5678')
    contact_hours_ja         = models.CharField(max_length=120, default='月〜土 10:00〜20:00')
    contact_hours_en         = models.CharField(max_length=120, default='Mon–Sat 10:00–20:00')
    contact_note_ja          = models.CharField(max_length=120, default='日曜・祝日は除く')
    contact_note_en          = models.CharField(max_length=120, default='(Closed Sundays & holidays)')
    max_party_size           = models.PositiveIntegerField(default=8)
    slots_per_timeslot       = models.PositiveIntegerField(default=8)
    class Meta: verbose_name = 'Site Settings'
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    def __str__(self): return 'Site Settings'


# ── Signal: auto-create UserProfile on user creation ──
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


class BusinessHours(models.Model):
    DAYS = [
        (0,'月曜日 / Monday'),(1,'火曜日 / Tuesday'),(2,'水曜日 / Wednesday'),
        (3,'木曜日 / Thursday'),(4,'金曜日 / Friday'),(5,'土曜日 / Saturday'),(6,'日曜日 / Sunday'),
    ]
    day          = models.IntegerField(choices=DAYS, unique=True)
    is_closed    = models.BooleanField(default=False)
    lunch_open   = models.TimeField(null=True, blank=True)
    lunch_close  = models.TimeField(null=True, blank=True)
    dinner_open  = models.TimeField(null=True, blank=True)
    dinner_close = models.TimeField(null=True, blank=True)
    note_ja      = models.CharField(max_length=200, blank=True)
    note_en      = models.CharField(max_length=200, blank=True)
    class Meta: ordering = ['day']
    def __str__(self): return self.get_day_display()

    @property
    def day_label_ja(self):
        return self.get_day_display().split(' / ')[0]

    @property
    def day_label_en(self):
        return self.get_day_display().split(' / ')[1]


class ContactSubmission(models.Model):
    SUBJECT_CHOICES = [
        ('reservation', 'ご予約について / About Reservations'),
        ('menu', 'メニューについて / About Menu'),
        ('course', 'コース料理について / About Course Meals'),
        ('private', '個室・貸切について / Private Rooms & Events'),
        ('allergy', 'アレルギー・食事制限について / Allergies & Dietary Restrictions'),
        ('career', '採用について / Careers'),
        ('press', '取材・メディアについて / Press & Media'),
        ('other', 'その他 / Other'),
    ]
    
    name      = models.CharField(max_length=100)
    email     = models.EmailField()
    subject   = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message   = models.TextField()
    is_read   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta: ordering = ['-created_at']
    def __str__(self): return f'{self.name} - {self.get_subject_display()}'


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
    
    def __str__(self):
        return self.email