# 花膳 HANZEN — Restaurant Website
## Full-Stack Django + Bootstrap 5 Project

---

## 📁 Project Structure

```
hanzen/
├── manage.py
├── requirements.txt
├── README.md
│
├── hanzen/ # Django project config
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── restaurant/                 # Main Django app
│ ├── models.py                 # 11 models (see below)
│ ├── views.py                  # 60+ views + API endpoints
│ ├── urls.py                   # URL routing
│ ├── forms.py                  # Django forms (7 forms)
│ ├── admin.py                  # Admin panel config (11 models)
│ ├── context_processors.py     # Global context (site settings, hours)
│ ├── migrations/
│ └── templates/restaurant/
│ ├── base.html                 # Master layout
│ ├── home.html                 # Landing page
│ ├── menu.html                 # Full menu with filters
│ ├── reservation.html          # Booking with dynamic time slots
│ ├── cart.html                 # Session-based cart
│ ├── order.html                # Checkout
│ ├── about.html                # Story & timeline
│ ├── gallery.html              # Full gallery + lightbox
│ ├── contact.html              # Contact form
│ ├── hours.html                # Business hours
│ ├── registration/             # Login & Register
│ ├── dashboard/                # User dashboard
│ └── admin_dashboard/          # Admin panel (11 pages)
│ ├── index.html                # KPI dashboard
│ ├── menu.html                 # Menu CRUD
│ ├── courses.html              # Course CRUD
│ ├── gallery.html              # Gallery CRUD
│ ├── reservations.html         # Reservation management
│ ├── orders.html               # Order management
│ ├── users.html                # User management
│ ├── contact.html              # Contact inquiries
│ ├── newsletter.html           # Newsletter subscribers
│ ├── business_hours.html       # Business hours editor
│ ├── settings.html             # Site settings
│ ├── profile.html              # Admin profile
│ └── change_password.html      # Admin password change
│
├── static/restaurant/
│ ├── css/main.css              # Full custom stylesheet
│ └── js/main.js                # Frontend logic
│
└── media/                      # Uploaded images
├── site_images/
├── menu_images/
├── gallery_images/
└── course_images/
```

---

## 🚀 Quick Start

### 1. Create virtual environment & install
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py makemigrations restaurant
python manage.py migrate
```

### 3. Create admin user
```bash
python manage.py createsuperuser
```

### 4. Start development server
```bash
python manage.py runserver
```

Open: http://127.0.0.1:8000

User Dashboard: http://127.0.0.1:8000/dashboard/

Admin Dashboard: http://127.0.0.1:8000/hanzen-admin/

Django Admin: http://127.0.0.1:8000/admin/

---

## ✨ Features

### Frontend
| Feature | Details |
|---|---|
| **Bilingual JP/EN** | Language toggle with localStorage persistence |
| **Custom cursor** | Gold dot + ring, hover effects |
| **Sakura petals** | CSS-animated falling petals on hero |
| **Parallax hero** | Background pan + zoom animation |
| **Dynamic menu** | AJAX category switching, dietary filters |
| **Session cart** | Add/remove/update quantities via AJAX |
| **Reservation form** | Dynamic time slots based on business hours, real-time availability check |
| **Course pre-selection** | Selecting a course on homepage pre-fills reservation form |
| **Announcements** | Admin-editable announcement banner on homepage |
| **Seasonal banner** | Admin-editable dismissable top banner |
| **Contact form** | Subject dropdown, CSRF protection, DB storage + email |
| **Newsletter** | Footer subscription with DB storage |
| **Business hours** | Dynamic display on homepage, reservation page, and hours page |
| **Gallery lightbox** | Full-screen with keyboard close |
| **Testimonial slider** | Auto-rotating with dot navigation |
| **Scroll animations** | IntersectionObserver fade-in |
| **Counter animation** | Animated stat numbers |
| **Ripple effects** | Click ripple on all buttons |
| **Toast notifications** | Animated success/error messages |
| **Responsive design** | Mobile-first, Bootstrap 5 |

### Admin Dashboard (/hanzen-admin/)
| Feature | Details |
|---|---|
| **KPI Dashboard** | Total reservations, revenue, users, menu items, monthly chart |
| **Reservation Management** | Status updates, filtering, search |
| **Menu Management** | Full CRUD, image upload, category filter, search, availability toggle |
| **Course Management** | Full CRUD, image upload, tier management, availability toggle |
| **User Management** | List, delete, staff toggle, search |
| **Gallery Management** | Full CRUD, image upload, edit modal, featured toggle |
| **Order Management** | Status workflow, search, detail view |
| **Contact Management** | Read/unread filtering, mark as read, detail view |
| **Newsletter Management** | Subscriber list, active/inactive toggle, delete, search |
| **Business Hours** | Per-day open/close, lunch/dinner times, closed day toggle |
| **Site Settings** | Banner text, announcements, phone numbers, slot limits |
| **Admin Profile** | Edit own profile, change password |

### API Endpoints
| Endpoint | Method | Description |
|---|---|---|
| **/api/menu/?cat=** | GET | Filter menu items by category |
| **/api/availability/?date=&time=** | GET | Real-time reservation slot check |
| **/api/time-slots/?date=** | GET | Dynamic time slots based on business hours |
| **/api/categories/** | GET | All categories list |

### Models (11 total)
Category, MenuItem, CourseMenu, Reservation, Testimonial, GalleryImage, Order, OrderLine, UserProfile, SiteSettings, BusinessHours, ContactSubmission, NewsletterSubscriber

---

## 🎨 Design System

```css
--aka:        #8b1c1c   /* Primary red */
--aka-dark:   #5c0f0f   /* Dark red (buttons) */
--aka-light:  #b84444   /* Light red (accents) */
--sumi:       #1c1410   /* Ink black */
--shiro:      #fdfaf5   /* Washi white */
--shiro-warm: #f5ede0   /* Warm paper */
--ki:         #c8903a   /* Gold accent */
--matcha:     #5a6e3a   /* Green (vegetarian/confirmed) */
--tsuchi:     #9e8870   /* Earth tone */
--smoke:      #8a7a6a   /* Muted text */

Fonts:
  Noto Serif JP      — Japanese headings
  Cormorant Garamond  — English elegance
  Noto Sans JP       — UI / body
```

---

## 🔧 Production Checklist

- [ ] Set `SECRET_KEY` from environment variable
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure real email backend (SMTP / SendGrid)
- [ ] Run `python manage.py collectstatic`
- [ ] Serve with gunicorn + nginx
- [ ] Set up media file serving (nginx / S3)

---

## 📦 Tech Stack

- **Backend**: Django 4.2, SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Bootstrap 5.3, Font Awesome 6, Google Fonts
- **CSS**: Custom properties, CSS Grid, Flexbox, Animations (~2500 lines)
- **JS**: Vanilla ES6+, IntersectionObserver, Fetch API, localStorage
- **i18n**: Django i18n + custom JS toggle with persistence
- **Storage**: Django file storage for image uploads

---

### 📝 Key Customizations from Base Django

- **Custom admin dashboard** — Complete separation from Django admin, built with same design system

- **Session-based cart** — Works for both authenticated and anonymous users

- **Dynamic time slots** — Reservation times filtered by actual business hours per day

- **Image management** — File upload with preview, old file cleanup on edit/delete

- **Bilingual architecture** — All text stored with [data-ja] and [data-en] attributes

- **Real-time validation** — Client-side form validation with bilingual error messages

- **Disabled submit buttons** — Forms require all fields before enabling submission

---

## 👨‍💻 About the Developer

**Wai Phyoe Min**

This full-stack restaurant website was built from scratch as a comprehensive Django project. It features:

- Complete bilingual (Japanese/English) architecture
- Custom admin dashboard with full CRUD operations
- Session-based cart system
- Dynamic reservation system with business hours integration
- Responsive design with traditional Japanese aesthetics

---

*花膳 Hanzen — 東京・銀座 · Fine Japanese Cuisine Since 1987*
*Built by Wai Phyoe Min © 2026*