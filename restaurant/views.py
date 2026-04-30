import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, F, Count, Q
from django.views.decorators.csrf import csrf_exempt
import datetime

from .models import (Category, MenuItem, CourseMenu, Reservation,
                     Testimonial, GalleryImage, Order, OrderLine, UserProfile, SiteSettings, ContactSubmission, BusinessHours)
from .forms import (ReservationForm, ContactForm, NewsletterForm,
                    RegisterForm, LoginForm, UserProfileForm)

def is_staff(user): return user.is_authenticated and (user.is_staff or user.is_superuser)

# ── helpers ──────────────────────────────────────
def get_cart(request):
    return request.session.get('cart', {})

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def cart_count(request):
    return sum(get_cart(request).values())

def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile

# ── HOME ─────────────────────────────────────────
def home(request):
    try:
        categories = Category.objects.prefetch_related('items').all()
        courses = CourseMenu.objects.filter(is_active=True)
        testimonials = Testimonial.objects.filter(is_active=True)
        gallery = GalleryImage.objects.all()[:6]
    except Exception:
        categories = []
        courses = []
        testimonials = []
        gallery = []
    
    return render(request, 'restaurant/home.html', {
        'categories': categories,
        'courses': courses,
        'testimonials': testimonials,
        'gallery': gallery,
        'cart_count': cart_count(request),
        'page': 'home',
    })

# ── MENU ─────────────────────────────────────────
def menu(request):
    cat_slug   = request.GET.get('cat','')
    categories = Category.objects.prefetch_related('items').all()
    active_cat = None
    items = MenuItem.objects.filter(is_available=True)
    if cat_slug:
        active_cat = get_object_or_404(Category, slug=cat_slug)
        items = items.filter(category=active_cat)
    return render(request, 'restaurant/menu.html', {
        'categories': categories, 'active_cat': active_cat,
        'items': items, 'cart_count': cart_count(request), 'page':'menu'})

# ── ABOUT ────────────────────────────────────────
def about(request):
    return render(request, 'restaurant/about.html', {'cart_count':cart_count(request),'page':'about'})

# ── HOURS ────────────────────────────────────────
def hours(request):
    from .models import BusinessHours
    today_index = timezone.localtime(timezone.now()).weekday()
    return render(request, 'restaurant/hours.html', {
        'hours': BusinessHours.objects.order_by('day').all(),
        'today_index': today_index,
        'cart_count': cart_count(request),
        'page': 'hours',
    })

# ── GALLERY ──────────────────────────────────────
def gallery(request):
    return render(request, 'restaurant/gallery.html', {
        'images': GalleryImage.objects.all(), 'cart_count':cart_count(request),'page':'gallery'})

# ── CONTACT ──────────────────────────────────────
def contact(request):
    initial = {}
    if request.user.is_authenticated:
        initial = {
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    
    form = ContactForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        # Save to database
        ContactSubmission.objects.create(
            name=d['name'],
            email=d['email'],
            subject=d['subject'],
            message=d['message']
        )
        # Get the display value for subject
        subject_display = dict(ContactForm.SUBJECT_CHOICES).get(d['subject'], d['subject'])
        send_mail(
            f'[花膳] {subject_display}', 
            f'From: {d["name"]} <{d["email"]}>\n\nSubject: {subject_display}\n\n{d["message"]}',
            settings.RESTAURANT_EMAIL, 
            [settings.RESTAURANT_EMAIL], 
            fail_silently=True
        )
        messages.success(request, 'お問い合わせを受け付けました / Message sent!')
        return redirect('restaurant:contact')
    
    settings_obj, _ = SiteSettings.objects.get_or_create(pk=1)
    return render(request, 'restaurant/contact.html', {
        'form': form,
        'settings': settings_obj,
        'cart_count': cart_count(request),
        'page': 'contact'
    })

# ── RESERVATION ──────────────────────────────────
def reservation(request):
    initial = {}
    if request.user.is_authenticated:
        initial = {'name': request.user.get_full_name() or request.user.username,
                   'email': request.user.email}
    
    # Pre-select course if provided in URL
    selected_course = request.GET.get('course', '')
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            res = form.save(commit=False)
            if request.user.is_authenticated: res.user = request.user
            res.save()
            send_mail(f'[花膳] ご予約確認 #{res.pk}',
                f'{res.name} 様\nご予約を承りました。\n日時: {res.date} {res.time}\n人数: {res.party_size}名',
                settings.RESTAURANT_EMAIL, [res.email], fail_silently=True)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok':True,'id':res.pk})
            messages.success(request, 'ご予約を承りました！')
            return redirect('restaurant:reservation_success', pk=res.pk)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok':False,'errors':form.errors}, status=400)
    else:
        # Set initial course if provided
        if selected_course:
            try:
                course = CourseMenu.objects.get(tier=selected_course, is_active=True)
                initial['course'] = course.pk
            except CourseMenu.DoesNotExist:
                pass
        
        form = ReservationForm(initial=initial)
    
    today_hours = BusinessHours.objects.filter(day=timezone.localtime(timezone.now()).weekday()).first()
    site_settings_obj, _ = SiteSettings.objects.get_or_create(pk=1)
    
    return render(request, 'restaurant/reservation.html', {
        'form': form,
        'today_hours': today_hours,
        'settings': site_settings_obj,
        'cart_count': cart_count(request),
        'page': 'reservation'
    })

def reservation_success(request, pk):
    res = get_object_or_404(Reservation, pk=pk)
    return render(request, 'restaurant/reservation_success.html', {
        'reservation': res,
        'cart_count': cart_count(request),
        'page': 'reservation_success',
    })

# ── CART ─────────────────────────────────────────
def cart_view(request):
    cart  = get_cart(request)
    items_data = []
    total = 0
    for item_id, qty in cart.items():
        try:
            item = MenuItem.objects.get(pk=int(item_id))
            sub  = item.price * qty
            items_data.append({'item':item,'qty':qty,'subtotal':sub})
            total += sub
        except MenuItem.DoesNotExist:
            pass
    return render(request, 'restaurant/cart.html', {
        'cart_items': items_data, 'total': total,
        'cart_count': cart_count(request), 'page':'cart'})


def order(request):
    cart  = get_cart(request)
    items_data = []
    total = 0
    for item_id, qty in cart.items():
        try:
            item = MenuItem.objects.get(pk=int(item_id))
            sub  = item.price * qty
            items_data.append({'item':item,'qty':qty,'subtotal':sub})
            total += sub
        except MenuItem.DoesNotExist:
            pass

    if not items_data:
        messages.info(request, 'カートに商品がありません / Your cart is empty.')
        return redirect('restaurant:cart')

    if request.method == 'POST':
        if not request.session.session_key:
            request.session.save()

        order_obj = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            status='submitted'
        )
        for row in items_data:
            OrderLine.objects.create(
                order=order_obj,
                menu_item=row['item'],
                quantity=row['qty'],
                unit_price=row['item'].price
            )

        save_cart(request, {})
        messages.success(request, 'ご注文を承りました / Order placed successfully.')
        return redirect('restaurant:order_success', pk=order_obj.pk)

    return render(request, 'restaurant/order.html', {
        'cart_items': items_data,
        'total': total,
        'cart_count': cart_count(request),
        'page': 'order'
    })


def order_success(request, pk):
    order_obj = get_object_or_404(Order, pk=pk)
    return render(request, 'restaurant/order_success.html', {
        'order': order_obj,
        'cart_count': cart_count(request),
        'page': 'order'
    })


@require_POST
def cart_add(request):
    data    = json.loads(request.body)
    item_id = str(data.get('item_id'))
    qty     = int(data.get('qty', 1))
    cart    = get_cart(request)
    cart[item_id] = cart.get(item_id, 0) + qty
    save_cart(request, cart)
    return JsonResponse({'ok':True,'cart_count':sum(cart.values())})

@require_POST
def cart_update(request):
    """Set exact quantity for an item."""
    data    = json.loads(request.body)
    item_id = str(data.get('item_id'))
    qty     = int(data.get('qty', 1))
    cart    = get_cart(request)
    if qty <= 0:
        cart.pop(item_id, None)
    else:
        cart[item_id] = qty
    save_cart(request, cart)
    # Recalculate subtotal
    subtotal = 0
    try:
        item = MenuItem.objects.get(pk=int(item_id))
        subtotal = item.price * qty
    except MenuItem.DoesNotExist:
        pass
    total = sum(MenuItem.objects.get(pk=int(k)).price * v
                for k,v in cart.items()
                if MenuItem.objects.filter(pk=int(k)).exists())
    return JsonResponse({'ok':True,'cart_count':sum(cart.values()),'subtotal':subtotal,'total':total,'qty':qty})

@require_POST
def cart_remove(request):
    data    = json.loads(request.body)
    item_id = str(data.get('item_id'))
    cart    = get_cart(request)
    cart.pop(item_id, None)
    save_cart(request, cart)
    total = sum(MenuItem.objects.get(pk=int(k)).price * v
                for k,v in cart.items()
                if MenuItem.objects.filter(pk=int(k)).exists())
    return JsonResponse({'ok':True,'cart_count':sum(cart.values()),'total':total})

@require_POST
def cart_clear(request):
    save_cart(request, {})
    return JsonResponse({'ok':True})

# ── NEWSLETTER ────────────────────────────────────
@require_POST
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        # Save to database if not already subscribed
        from .models import NewsletterSubscriber
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        if not created and not subscriber.is_active:
            # Re-activate if previously unsubscribed
            subscriber.is_active = True
            subscriber.save()
        
        return JsonResponse({'ok': True, 'email': email})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


# ── ADMIN NEWSLETTER ─────────────────────────────
@user_passes_test(is_staff, login_url='/login/')
def admin_newsletter(request):
    from .models import NewsletterSubscriber
    search_q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    subscribers = NewsletterSubscriber.objects.all()
    if search_q:
        subscribers = subscribers.filter(email__icontains=search_q)
    if status_filter == 'active':
        subscribers = subscribers.filter(is_active=True)
    elif status_filter == 'inactive':
        subscribers = subscribers.filter(is_active=False)
    return render(request, 'restaurant/admin_dashboard/newsletter.html', {
        'subscribers': subscribers,
        'cart_count': cart_count(request),
        'page': 'admin_dashboard'
    })


@require_POST
@user_passes_test(is_staff, login_url='/login/')
def admin_newsletter_toggle(request, pk):
    from .models import NewsletterSubscriber
    subscriber = get_object_or_404(NewsletterSubscriber, pk=pk)
    subscriber.is_active = not subscriber.is_active
    subscriber.save()
    return JsonResponse({'ok': True, 'is_active': subscriber.is_active})


@require_POST
@user_passes_test(is_staff, login_url='/login/')
def admin_newsletter_delete(request, pk):
    from .models import NewsletterSubscriber
    subscriber = get_object_or_404(NewsletterSubscriber, pk=pk)
    subscriber.delete()
    return JsonResponse({'ok': True})


# ── AUTH ─────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('restaurant:admin_dashboard')
        return redirect('restaurant:dashboard')
    
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        get_or_create_profile(user)
        login(request, user)
        messages.success(request, f'ようこそ、{user.first_name or user.username} 様！')
        return redirect('restaurant:dashboard')  # New users always go to user dashboard
    
    return render(request, 'registration/register.html', {
        'form': form,
        'cart_count': cart_count(request)
    })

def login_view(request):
    if request.user.is_authenticated:
        # If already logged in, redirect based on role
        if request.user.is_staff or request.user.is_superuser:
            return redirect('restaurant:admin_dashboard')
        return redirect('restaurant:dashboard')
    
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        get_or_create_profile(user)
        messages.success(request, f'お帰りなさい、{user.first_name or user.username} 様！')
        
        # Redirect based on user role
        if user.is_staff or user.is_superuser:
            return redirect('restaurant:admin_dashboard')
        return redirect(request.GET.get('next', 'restaurant:dashboard'))
    
    return render(request, 'registration/login.html', {
        'form': form,
        'cart_count': cart_count(request)
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'ログアウトしました / Logged out successfully.')
    return redirect('restaurant:home')

# ── USER DASHBOARD ────────────────────────────────
@login_required(login_url='/login/')
def dashboard(request):
    profile = get_or_create_profile(request.user)
    upcoming = request.user.reservations.filter(
        date__gte=timezone.now().date(), status__in=['pending','confirmed']).order_by('date','time')
    past     = request.user.reservations.filter(
        Q(date__lt=timezone.now().date()) | Q(status='completed')).order_by('-date')[:5]
    orders   = request.user.orders.exclude(status='open').order_by('-created_at')[:5]
    return render(request, 'restaurant/dashboard/index.html', {
        'profile': profile, 'upcoming': upcoming, 'past': past,
        'orders': orders, 'cart_count': cart_count(request), 'page':'dashboard'})

@login_required(login_url='/login/')
def dashboard_profile(request):
    profile = get_or_create_profile(request.user)
    form = UserProfileForm(request.POST or None, instance=profile, user=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'プロフィールを更新しました / Profile updated!')
        return redirect('restaurant:dashboard_profile')
    return render(request, 'restaurant/dashboard/profile.html', {
        'profile':profile,'form':form,'cart_count':cart_count(request),'page':'dashboard'})

@login_required(login_url='/login/')
def dashboard_reservations(request):
    profile = get_or_create_profile(request.user)
    all_res = request.user.reservations.all().order_by('-date','-time')
    return render(request, 'restaurant/dashboard/reservations.html', {
        'profile':profile,'reservations':all_res,'cart_count':cart_count(request),'page':'dashboard'})

@login_required(login_url='/login/')
def dashboard_orders(request):
    profile = get_or_create_profile(request.user)
    orders  = request.user.orders.exclude(status='open').order_by('-created_at')
    return render(request, 'restaurant/dashboard/orders.html', {
        'profile':profile,'orders':orders,'cart_count':cart_count(request),'page':'dashboard'})

@login_required(login_url='/login/')
def cancel_reservation(request, pk):
    res = get_object_or_404(Reservation, pk=pk, user=request.user)
    if res.status in ['pending','confirmed']:
        res.status = 'cancelled'
        res.save()
        messages.success(request, 'ご予約をキャンセルしました。')
    return redirect('restaurant:dashboard_reservations')

# ── ADMIN DASHBOARD ───────────────────────────────
@user_passes_test(is_staff, login_url='/login/')
def admin_dashboard(request):
    today = timezone.now().date()
    ctx = {
        'total_reservations':  Reservation.objects.count(),
        'today_reservations':  Reservation.objects.filter(date=today).count(),
        'pending_reservations':Reservation.objects.filter(status='pending').count(),
        'total_users':         User.objects.count(),
        'total_menu_items':    MenuItem.objects.count(),
        'total_orders':        Order.objects.count(),
        'total_revenue':       OrderLine.objects.aggregate(total=Sum(F('unit_price') * F('quantity')))['total'] or 0,
        'recent_reservations': Reservation.objects.order_by('-created_at')[:8],
        'recent_users':        User.objects.order_by('-date_joined')[:6],
        'status_counts': {
            'pending':   Reservation.objects.filter(status='pending').count(),
            'confirmed': Reservation.objects.filter(status='confirmed').count(),
            'completed': Reservation.objects.filter(status='completed').count(),
            'cancelled': Reservation.objects.filter(status='cancelled').count(),
        },
        'monthly_res': _monthly_reservations(),
        'popular_items': MenuItem.objects.annotate(order_count=Count('orderline')).order_by('-order_count')[:5],
        'cart_count': cart_count(request), 'page':'admin_dashboard',
    }
    return render(request, 'restaurant/admin_dashboard/index.html', ctx)

def _monthly_reservations():
    today = timezone.now().date()
    data  = []
    for i in range(5,-1,-1):
        month = today.replace(day=1) - datetime.timedelta(days=i*28)
        count = Reservation.objects.filter(date__year=month.year, date__month=month.month).count()
        data.append({'month': month.strftime('%b'), 'count': count})
    return data

@user_passes_test(is_staff, login_url='/login/')
def admin_reservations(request):
    status = request.GET.get('status','')
    qs     = Reservation.objects.select_related('user','course').order_by('-date','-time')
    if status: qs = qs.filter(status=status)
    return render(request, 'restaurant/admin_dashboard/reservations.html', {
        'reservations':qs,'status_filter':status,'cart_count':cart_count(request),'page':'admin_dashboard'})

@user_passes_test(is_staff, login_url='/login/')
@require_POST
def admin_reservation_update(request, pk):
    res = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        res.status = request.POST.get('status', res.status)
        res.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok':True,'status':res.status,'status_display':res.get_status_display()})
        messages.success(request, 'ステータスを更新しました。')
        return redirect('restaurant:admin_reservations')
    return JsonResponse({'ok':False}, status=400)

@user_passes_test(is_staff, login_url='/login/')
def admin_menu(request):
    cat_slug = request.GET.get('cat', '')
    search_q = request.GET.get('q', '').strip()
    items = MenuItem.objects.select_related('category').all()
    if cat_slug:
        items = items.filter(category__slug=cat_slug)
    if search_q:
        items = items.filter(
            Q(name_ja__icontains=search_q) | 
            Q(name_en__icontains=search_q) |
            Q(description_ja__icontains=search_q) |
            Q(description_en__icontains=search_q)
        )
    cats  = Category.objects.all()
    return render(request, 'restaurant/admin_dashboard/menu.html', {
        'items': items,
        'categories': cats,
        'cart_count': cart_count(request),
        'page': 'admin_dashboard'
    })

@csrf_exempt
@user_passes_test(is_staff, login_url='/login/')
def admin_menu_toggle(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        item.is_available = not item.is_available
        item.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'is_available': item.is_available})
        return redirect('restaurant:admin_menu')
    return JsonResponse({'ok': False}, status=400)

@user_passes_test(is_staff, login_url='/login/')
def admin_users(request):
    search_q = request.GET.get('q', '').strip()
    users = User.objects.select_related('profile').order_by('-date_joined')
    if search_q:
        users = users.filter(
            Q(username__icontains=search_q) | 
            Q(email__icontains=search_q) |
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q)
        )
    return render(request, 'restaurant/admin_dashboard/users.html', {
        'users':users,'cart_count':cart_count(request),'page':'admin_dashboard'})

@user_passes_test(is_staff, login_url='/login/')
def admin_gallery(request):
    images = GalleryImage.objects.all()
    return render(request, 'restaurant/admin_dashboard/gallery.html', {
        'images':images,'cart_count':cart_count(request),'page':'admin_dashboard'})

@user_passes_test(is_staff, login_url='/login/')
def admin_gallery_add(request):
    if request.method == 'POST':
        image_url = request.POST.get('image_url', '').strip()
        if request.FILES.get('image_file'):
            from django.core.files.storage import default_storage
            image_file = request.FILES['image_file']
            file_path = default_storage.save(f'gallery_images/{image_file.name}', image_file)
            image_url = default_storage.url(file_path)

        if not image_url:
            messages.error(request, '画像ファイルまたは画像URLが必要です。 / An image file or image URL is required.')
            return redirect('restaurant:admin_gallery')

        GalleryImage.objects.create(
            title_ja=request.POST.get('title_ja',''),
            title_en=request.POST.get('title_en',''),
            image_url=image_url,
            thumb_url=request.POST.get('thumb_url',''),
            is_featured=request.POST.get('is_featured')=='on',
            order=int(request.POST.get('order',0)),
        )
        messages.success(request, '画像を追加しました / Image added successfully.')
    return redirect('restaurant:admin_gallery')

@user_passes_test(is_staff, login_url='/login/')
def admin_gallery_delete(request, pk):
    from django.core.files.storage import default_storage
    
    img = get_object_or_404(GalleryImage, pk=pk)
    
    # Delete the image file if it's a local file
    if img.image_url and img.image_url.startswith('/media/'):
        try:
            old_file_path = img.image_url.replace('/media/', '')
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)
        except Exception:
            pass
    
    img.delete()
    return JsonResponse({'ok': True})

# ── ADMIN PROFILE ────────────────────────────────
@user_passes_test(is_staff, login_url='/login/')
def admin_profile(request):
    profile = get_or_create_profile(request.user)
    form = UserProfileForm(request.POST or None, instance=profile, user=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'プロフィールを更新しました / Profile updated!')
        return redirect('restaurant:admin_profile')
    return render(request, 'restaurant/admin_dashboard/profile.html', {
        'profile': profile,
        'form': form,
        'cart_count': cart_count(request),
        'page': 'admin_dashboard'
    })


@user_passes_test(is_staff, login_url='/login/')
def admin_change_password(request):
    from django.contrib.auth import update_session_auth_hash
    from .forms import BilingualPasswordChangeForm
    
    if request.method == 'POST':
        form = BilingualPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': True})
            messages.success(request, 'パスワードを変更しました / Password changed successfully.')
            return redirect('restaurant:admin_profile')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Format errors for AJAX response
                errors = {}
                for field, field_errors in form.errors.items():
                    errors[field] = [str(e) for e in field_errors]
                return JsonResponse({'ok': False, 'errors': errors}, status=400)
    else:
        form = BilingualPasswordChangeForm(request.user)
    
    return render(request, 'restaurant/admin_dashboard/change_password.html', {
        'form': form,
        'cart_count': cart_count(request),
        'page': 'admin_dashboard'
    })

# ── LEGAL PAGES ──────────────────────────────────
def privacy_view(request):
    return render(request, 'restaurant/privacy.html', {'cart_count':cart_count(request),'page':'privacy'})

def terms_view(request):
    return render(request, 'restaurant/terms.html', {'cart_count':cart_count(request),'page':'terms'})

# ── APIS ─────────────────────────────────────────
def api_menu(request):
    cat_slug = request.GET.get('cat','')
    qs = MenuItem.objects.filter(is_available=True)
    if cat_slug: qs = qs.filter(category__slug=cat_slug)
    data = [{'id':i.pk,'name_ja':i.name_ja,'name_en':i.name_en,'desc_ja':i.description_ja,
             'desc_en':i.description_en,'price':i.price,'price_fmt':i.price_formatted,
             'image':i.image_url,'badge':i.badge,'vegetarian':i.is_vegetarian,'gluten_free':i.is_gluten_free} for i in qs]
    return JsonResponse({'items':data})

def api_availability(request):
    date = request.GET.get('date','')
    time = request.GET.get('time','')
    if not date or not time: 
        return JsonResponse({'available':False,'message':'Invalid'})
    
    # Get max slots from settings (default to 8)
    from .models import SiteSettings
    try:
        settings_obj = SiteSettings.objects.get(pk=1)
        max_slots = settings_obj.slots_per_timeslot
    except SiteSettings.DoesNotExist:
        max_slots = 8
    
    count = Reservation.objects.filter(
        date=date, time=time, 
        status__in=['pending','confirmed']
    ).count()
    
    avail = count < max_slots
    remaining = max(0, max_slots - count)
    
    return JsonResponse({
        'available': avail,
        'remaining': remaining,
        'message': '空席あり / Available' if avail else '満席 / Fully booked'
    })


def api_time_slots(request):
    """Return available time slots for a given date based on business hours"""
    date_str = request.GET.get('date', '')
    if not date_str:
        return JsonResponse({'time_slots': []})
    
    try:
        # Parse the date
        year, month, day = map(int, date_str.split('-'))
        selected_date = datetime.date(year, month, day)
        day_of_week = selected_date.weekday()  # 0=Monday, 6=Sunday
        
        # Get business hours for that day
        try:
            hours = BusinessHours.objects.get(day=day_of_week)
        except BusinessHours.DoesNotExist:
            return JsonResponse({'time_slots': list(Reservation.TIME_SLOTS)})
        
        if hours.is_closed:
            return JsonResponse({'time_slots': [], 'is_closed': True, 'message': '定休日です / Closed on this day'})
        
        # Filter time slots based on business hours
        available_slots = []
        for time_value, time_label in Reservation.TIME_SLOTS:
            hour, minute = map(int, time_value.split(':'))
            slot_time = datetime.time(hour, minute)
            
            # Check if time falls within lunch or dinner hours
            is_lunch = (hours.lunch_open and hours.lunch_close and 
                       hours.lunch_open <= slot_time < hours.lunch_close)
            is_dinner = (hours.dinner_open and hours.dinner_close and 
                        hours.dinner_open <= slot_time < hours.dinner_close)
            
            if is_lunch or is_dinner:
                available_slots.append([time_value, time_label])
        
        return JsonResponse({
            'time_slots': available_slots,
            'is_closed': False,
            'day_info': {
                'is_closed': hours.is_closed,
                'lunch_open': hours.lunch_open.strftime('%H:%M') if hours.lunch_open else None,
                'lunch_close': hours.lunch_close.strftime('%H:%M') if hours.lunch_close else None,
                'dinner_open': hours.dinner_open.strftime('%H:%M') if hours.dinner_open else None,
                'dinner_close': hours.dinner_close.strftime('%H:%M') if hours.dinner_close else None,
            }
        })
    except (ValueError, TypeError):
        return JsonResponse({'time_slots': list(Reservation.TIME_SLOTS)})

# ── ADMIN: FULL CRUD ─────────────────────────────

@user_passes_test(is_staff, login_url='/login/')
def admin_menu_add(request):
    from .forms import MenuItemForm
    import os
    from django.core.files.storage import default_storage
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            
            # Handle file upload
            if request.FILES.get('image_file'):
                image_file = request.FILES['image_file']
                # Save to media/menu_images/
                file_path = default_storage.save(f'menu_images/{image_file.name}', image_file)
                item.image_url = default_storage.url(file_path)
            
            item.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': True})
            messages.success(request, 'メニューを追加しました / Menu item added.')
            return redirect('restaurant:admin_menu')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
    return redirect('restaurant:admin_menu')


@user_passes_test(is_staff, login_url='/login/')
def admin_menu_edit(request, pk):
    from .forms import MenuItemForm
    import os
    from django.core.files.storage import default_storage
    
    item = get_object_or_404(MenuItem, pk=pk)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            
            # Handle file upload
            if request.FILES.get('image_file'):
                # Delete old image if it's a local file (starts with /media/)
                old_image_url = item.image_url
                if old_image_url and old_image_url.startswith('/media/'):
                    try:
                        # Convert URL to file path
                        old_file_path = old_image_url.replace('/media/', '')
                        if default_storage.exists(old_file_path):
                            default_storage.delete(old_file_path)
                            print(f"Deleted old image: {old_file_path}")
                    except Exception as e:
                        print(f"Could not delete old image: {e}")
                
                # Save new image
                image_file = request.FILES['image_file']
                file_path = default_storage.save(f'menu_images/{image_file.name}', image_file)
                item.image_url = default_storage.url(file_path)
            
            item.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': True})
            messages.success(request, 'メニューを更新しました / Menu item updated.')
            return redirect('restaurant:admin_menu')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
    
    # GET request - return item data as JSON
    item_data = {
        'id': item.pk, 
        'name_ja': item.name_ja, 
        'name_en': item.name_en,
        'description_ja': item.description_ja, 
        'description_en': item.description_en,
        'price': item.price, 
        'image_url': item.image_url or '', 
        'badge': item.badge or '',
        'category': item.category_id, 
        'is_available': item.is_available,
        'is_vegetarian': item.is_vegetarian, 
        'is_gluten_free': item.is_gluten_free,
        'order': item.order,
    }
    return JsonResponse(item_data)


@user_passes_test(is_staff, login_url='/login/')
def admin_menu_delete(request, pk):
    from django.core.files.storage import default_storage
    
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        # Delete the image file if it's a local file
        if item.image_url and item.image_url.startswith('/media/'):
            try:
                old_file_path = item.image_url.replace('/media/', '')
                if default_storage.exists(old_file_path):
                    default_storage.delete(old_file_path)
                    print(f"Deleted image: {old_file_path}")
            except Exception as e:
                print(f"Could not delete image: {e}")
        
        item.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        messages.success(request, 'メニューを削除しました / Menu item deleted.')
        return redirect('restaurant:admin_menu')
    return JsonResponse({'ok': False}, status=400)


@user_passes_test(is_staff, login_url='/login/')
def admin_user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user_obj == request.user:
            return JsonResponse({'ok': False, 'error': '自分自身は削除できません / Cannot delete yourself'}, status=400)
        if user_obj.is_superuser:
            return JsonResponse({'ok': False, 'error': 'スーパーユーザーは削除できません / Cannot delete superuser'}, status=400)
        user_obj.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        messages.success(request, 'ユーザーを削除しました / User deleted.')
        return redirect('restaurant:admin_users')
    return JsonResponse({'ok': False}, status=400)


@user_passes_test(is_staff, login_url='/login/')
def admin_user_toggle_staff(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user_obj.is_superuser:
            return JsonResponse({'ok': False, 'error': 'Cannot modify superuser'}, status=400)
        user_obj.is_staff = not user_obj.is_staff
        user_obj.save()
        return JsonResponse({'ok': True, 'is_staff': user_obj.is_staff})
    return JsonResponse({'ok': False}, status=400)


@user_passes_test(is_staff, login_url='/login/')
def admin_business_hours(request):
    from .models import BusinessHours
    hours = BusinessHours.objects.all()
    # Auto-create all 7 days if not exist
    if hours.count() < 7:
        for day in range(7):
            BusinessHours.objects.get_or_create(
                day=day,
                defaults={
                    'is_closed': day == 1,
                    'lunch_open':  datetime.time(11, 30) if day != 1 else None,
                    'lunch_close': datetime.time(14, 0)  if day != 1 else None,
                    'dinner_open': datetime.time(18, 0)  if day != 1 else None,
                    'dinner_close':datetime.time(22, 30) if day != 1 else None,
                }
            )
        hours = BusinessHours.objects.all()
    return render(request, 'restaurant/admin_dashboard/business_hours.html', {
        'hours': hours, 'cart_count': cart_count(request), 'page': 'admin_dashboard'
    })


@require_POST
@user_passes_test(is_staff, login_url='/login/')
def admin_business_hours_save(request):
    from .models import BusinessHours
    try:
        data = json.loads(request.body)
        for row in data:
            bh = BusinessHours.objects.get(pk=row['id'])
            bh.is_closed     = row.get('is_closed', False)
            bh.lunch_open    = row.get('lunch_open')  or None
            bh.lunch_close   = row.get('lunch_close') or None
            bh.dinner_open   = row.get('dinner_open') or None
            bh.dinner_close  = row.get('dinner_close') or None
            bh.note_ja       = row.get('note_ja', '')
            bh.note_en       = row.get('note_en', '')
            bh.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@user_passes_test(is_staff, login_url='/login/')
def admin_gallery_edit(request, pk):
    from django.core.files.storage import default_storage
    
    img = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        img.title_ja    = request.POST.get('title_ja', img.title_ja)
        img.title_en    = request.POST.get('title_en', img.title_en)
        
        # Handle file upload
        if request.FILES.get('image_file'):
            # Delete old image if it's a local file
            old_image_url = img.image_url
            if old_image_url and old_image_url.startswith('/media/'):
                try:
                    old_file_path = old_image_url.replace('/media/', '')
                    if default_storage.exists(old_file_path):
                        default_storage.delete(old_file_path)
                except Exception:
                    pass
            
            # Save new image
            image_file = request.FILES['image_file']
            file_path = default_storage.save(f'gallery_images/{image_file.name}', image_file)
            img.image_url = default_storage.url(file_path)
        else:
            # Use URL if provided
            image_url = request.POST.get('image_url', '').strip()
            if image_url:
                img.image_url = image_url
        
        img.thumb_url   = request.POST.get('thumb_url', img.thumb_url)
        img.is_featured = request.POST.get('is_featured') == 'on'
        img.order       = int(request.POST.get('order', img.order))
        img.save()
        return JsonResponse({'ok': True})
    
    return JsonResponse({
        'id': img.pk, 'title_ja': img.title_ja, 'title_en': img.title_en,
        'image_url': img.image_url, 'thumb_url': img.thumb_url,
        'is_featured': img.is_featured, 'order': img.order,
    })

# ── ADMIN ORDERS ────────────────────────────────
@user_passes_test(is_staff, login_url='/login/')
def admin_orders(request):
    search_q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').prefetch_related('lines__menu_item').all()
    if search_q:
        orders = orders.filter(
            Q(user__username__icontains=search_q) | 
            Q(user__email__icontains=search_q) |
            Q(user__first_name__icontains=search_q) |
            Q(user__last_name__icontains=search_q) |
            Q(pk__icontains=search_q)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'restaurant/admin_dashboard/orders.html', {
        'orders': orders,
        'cart_count': cart_count(request),
        'page': 'admin_dashboard'
    })


@require_POST
@user_passes_test(is_staff, login_url='/login/')
def admin_order_status_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Order.STATUS):
        order.status = new_status
        order.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'error': 'Invalid status'}, status=400)


# ── ADMIN CONTACT ────────────────────────────────
@user_passes_test(is_staff, login_url='/login/')
def admin_contact(request):
    search_q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')  # 'read' or 'unread'
    contacts = ContactSubmission.objects.all()
    if search_q:
        contacts = contacts.filter(
            Q(name__icontains=search_q) | 
            Q(email__icontains=search_q) |
            Q(message__icontains=search_q)
        )
    if status_filter == 'read':
        contacts = contacts.filter(is_read=True)
    elif status_filter == 'unread':
        contacts = contacts.filter(is_read=False)
    return render(request, 'restaurant/admin_dashboard/contact.html', {
        'contacts': contacts,
        'cart_count': cart_count(request),
        'page': 'admin_dashboard'
    })


@require_POST
@user_passes_test(is_staff, login_url='/login/')
def admin_contact_mark_read(request, pk):
    contact = get_object_or_404(ContactSubmission, pk=pk)
    contact.is_read = True
    contact.save()
    return JsonResponse({'ok': True})


@user_passes_test(is_staff, login_url='/login/')
def admin_order_details(request, pk):
    order = get_object_or_404(Order.objects.select_related('user').prefetch_related('lines__menu_item'), pk=pk)
    return JsonResponse({
        'customer': order.user.get_full_name() if order.user else 'ゲスト / Guest',
        'email': order.user.email if order.user else '',
        'status': order.get_status_display(),
        'created_at': order.created_at.strftime('%Y/%m/%d %H:%M'),
        'total': order.total(),
        'note': order.note,
        'items': [{
            'name_ja': line.menu_item.name_ja,
            'name_en': line.menu_item.name_en,
            'image_url': line.menu_item.image_url,
            'quantity': line.quantity,
            'unit_price': line.unit_price,
            'subtotal': line.subtotal()
        } for line in order.lines.all()]
    })


@user_passes_test(is_staff, login_url='/login/')
def admin_contact_details(request, pk):
    contact = get_object_or_404(ContactSubmission, pk=pk)
    return JsonResponse({
        'name': contact.name,
        'email': contact.email,
        'subject_display': contact.get_subject_display(),
        'message': contact.message,
        'is_read': contact.is_read,
        'created_at': contact.created_at.strftime('%Y/%m/%d %H:%M')
    })


# ── SITE SETTINGS ────────────────────────────────
@user_passes_test(is_staff, login_url='/login/')
def admin_settings(request):
    from .models import SiteSettings
    settings_obj, _ = SiteSettings.objects.get_or_create(pk=1)
    if request.method == 'POST':
        settings_obj.seasonal_banner_text_ja = request.POST.get('banner_ja', '')
        settings_obj.seasonal_banner_text_en = request.POST.get('banner_en', '')
        settings_obj.banner_active           = request.POST.get('banner_active') == 'on'
        settings_obj.announcement_ja         = request.POST.get('announcement_ja', '')
        settings_obj.announcement_en         = request.POST.get('announcement_en', '')
        settings_obj.contact_phone           = request.POST.get('contact_phone', '03-1234-5678')
        settings_obj.contact_hours_ja        = request.POST.get('contact_hours_ja', '月〜土 10:00〜20:00')
        settings_obj.contact_hours_en        = request.POST.get('contact_hours_en', 'Mon–Sat 10:00–20:00')
        settings_obj.contact_note_ja         = request.POST.get('contact_note_ja', '日曜・祝日は除く')
        settings_obj.contact_note_en         = request.POST.get('contact_note_en', '(Closed Sundays & holidays)')
        settings_obj.slots_per_timeslot      = int(request.POST.get('slots_per_timeslot', 8))
        settings_obj.save()
        messages.success(request, '設定を保存しました / Settings saved.')
        return redirect('restaurant:admin_settings')
    return render(request, 'restaurant/admin_dashboard/settings.html', {
        'settings': settings_obj, 'cart_count': cart_count(request), 'page': 'admin_dashboard'
    })


# ── CHANGE PASSWORD (user) ────────────────────────
@login_required(login_url='/login/')
def change_password(request):
    from django.contrib.auth import update_session_auth_hash
    from .forms import BilingualPasswordChangeForm
    
    form = BilingualPasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': True})
            messages.success(request, 'パスワードを変更しました / Password changed successfully.')
            return redirect('restaurant:dashboard_profile')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(e) for e in field_errors]
            return JsonResponse({'ok': False, 'errors': errors}, status=400)
    
    return render(request, 'restaurant/dashboard/change_password.html', {
        'form': form,
        'cart_count': cart_count(request),
        'page': 'dashboard'
    })


# ── API: categories list ──────────────────────────
def api_categories(request):
    cats = [{'id': c.pk, 'slug': c.slug, 'name_ja': c.name_ja, 'name_en': c.name_en} for c in Category.objects.all()]
    return JsonResponse({'categories': cats})

# ── ADMIN COURSE MANAGEMENT ─────────────────────
@user_passes_test(is_staff, login_url='/login/')
def admin_courses(request):
    courses = CourseMenu.objects.all()
    return render(request, 'restaurant/admin_dashboard/courses.html', {
        'courses': courses,
        'cart_count': cart_count(request),
        'page': 'admin_dashboard'
    })


@user_passes_test(is_staff, login_url='/login/')
def admin_course_add(request):
    from django.core.files.storage import default_storage
    
    if request.method == 'POST':
        image_url = request.POST.get('image_url', '').strip()
        
        # Handle file upload
        if request.FILES.get('image_file'):
            image_file = request.FILES['image_file']
            file_path = default_storage.save(f'course_images/{image_file.name}', image_file)
            image_url = default_storage.url(file_path)
        
        course = CourseMenu.objects.create(
            tier=request.POST.get('tier', 'omakase'),
            name_ja=request.POST.get('name_ja', ''),
            name_en=request.POST.get('name_en', ''),
            description_ja=request.POST.get('description_ja', ''),
            description_en=request.POST.get('description_en', ''),
            price=int(request.POST.get('price', 0)),
            courses=int(request.POST.get('courses', 5)),
            image_url=image_url,
            is_active=request.POST.get('is_active') == 'on',
        )
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        
        messages.success(request, 'コースを追加しました / Course added successfully.')
        return redirect('restaurant:admin_courses')
    
    return redirect('restaurant:admin_courses')


@user_passes_test(is_staff, login_url='/login/')
def admin_course_edit(request, pk):
    from django.core.files.storage import default_storage
    
    course = get_object_or_404(CourseMenu, pk=pk)
    if request.method == 'POST':
        course.tier = request.POST.get('tier', course.tier)
        course.name_ja = request.POST.get('name_ja', course.name_ja)
        course.name_en = request.POST.get('name_en', course.name_en)
        course.description_ja = request.POST.get('description_ja', course.description_ja)
        course.description_en = request.POST.get('description_en', course.description_en)
        course.price = int(request.POST.get('price', course.price))
        course.courses = int(request.POST.get('courses', course.courses))
        
        # Handle file upload
        if request.FILES.get('image_file'):
            # Delete old image if local
            old_image_url = course.image_url
            if old_image_url and old_image_url.startswith('/media/'):
                try:
                    old_file_path = old_image_url.replace('/media/', '')
                    if default_storage.exists(old_file_path):
                        default_storage.delete(old_file_path)
                except Exception:
                    pass
            
            image_file = request.FILES['image_file']
            file_path = default_storage.save(f'course_images/{image_file.name}', image_file)
            course.image_url = default_storage.url(file_path)
        else:
            image_url = request.POST.get('image_url', '').strip()
            if image_url:
                course.image_url = image_url
        
        course.is_active = request.POST.get('is_active') == 'on'
        course.save()
        
        # Return JSON for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        
        messages.success(request, 'コースを更新しました / Course updated.')
        return redirect('restaurant:admin_courses')
    
    # GET request - return data as JSON
    return JsonResponse({
        'id': course.pk,
        'tier': course.tier,
        'name_ja': course.name_ja,
        'name_en': course.name_en,
        'description_ja': course.description_ja,
        'description_en': course.description_en,
        'price': course.price,
        'courses': course.courses,
        'image_url': course.image_url or '',
        'is_active': course.is_active,
    })


@user_passes_test(is_staff, login_url='/login/')
def admin_course_delete(request, pk):
    course = get_object_or_404(CourseMenu, pk=pk)
    if request.method == 'POST':
        course.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        messages.success(request, 'コースを削除しました / Course deleted.')
        return redirect('restaurant:admin_courses')
    return JsonResponse({'ok': False}, status=400)


@csrf_exempt
@user_passes_test(is_staff, login_url='/login/')
def admin_course_toggle(request, pk):
    course = get_object_or_404(CourseMenu, pk=pk)
    if request.method == 'POST':
        course.is_active = not course.is_active
        course.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'is_active': course.is_active})
        return redirect('restaurant:admin_courses')
    return JsonResponse({'ok': False}, status=400)