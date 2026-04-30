"""
Run: python manage.py seed_data
Seeds the database with sample menu items, courses, testimonials, gallery images.
"""
from django.core.management.base import BaseCommand
from restaurant.models import Category, MenuItem, CourseMenu, Testimonial, GalleryImage


CATEGORIES = [
    {'slug': 'sushi',   'name_ja': '寿司',   'name_en': 'Sushi',   'order': 1},
    {'slug': 'ramen',   'name_ja': 'ラーメン', 'name_en': 'Ramen',   'order': 2},
    {'slug': 'kaiseki', 'name_ja': '懐石',   'name_en': 'Kaiseki', 'order': 3},
    {'slug': 'drinks',  'name_ja': 'お飲み物', 'name_en': 'Drinks',  'order': 4},
    {'slug': 'dessert', 'name_ja': 'デザート', 'name_en': 'Dessert', 'order': 5},
]

MENU_ITEMS = [
    # SUSHI
    dict(category='sushi', name_ja='大トロ握り', name_en='Otoro Nigiri',
         description_ja='最高級本マグロの大トロ。口の中で溶ける脂の旨み。',
         description_en='Premium bluefin tuna belly. Melts on the tongue with sublime umami.',
         price=3200, badge='recommend',
         image_url='https://images.unsplash.com/photo-1617196034183-421b4040ed20?w=600&q=80', order=1),
    dict(category='sushi', name_ja='雲丹軍艦', name_en='Uni Gunkan',
         description_ja='北海道産バフンウニ。濃厚で甘みのある海の香り。',
         description_en='Hokkaido sea urchin. Rich, sweet ocean aroma in every bite.',
         price=2800, badge='',
         image_url='https://images.unsplash.com/photo-1553621042-f6e147245754?w=600&q=80', order=2),
    dict(category='sushi', name_ja='炙りサーモン', name_en='Aburi Salmon',
         description_ja='バーナーで炙ったノルウェー産サーモン。香ばしさと脂の調和。',
         description_en='Torched Norwegian salmon. Smoky fragrance meets silky richness.',
         price=1800, badge='seasonal',
         image_url='https://images.unsplash.com/photo-1611143669185-af224c5e3252?w=600&q=80', order=3),
    dict(category='sushi', name_ja='花膳特上盛', name_en='Hanzen Deluxe Set',
         description_ja='本日の特上ネタを10貫。板前がその日に厳選した逸品。',
         description_en='10 premium pieces curated by the chef from today\'s finest catch.',
         price=8500, badge='popular',
         image_url='https://images.unsplash.com/photo-1559410545-0bdcd187e0a6?w=600&q=80', order=4),
    # RAMEN
    dict(category='ramen', name_ja='黒醤油ラーメン', name_en='Black Soy Ramen',
         description_ja='72時間煮込んだ豚骨に黒醤油を合わせた深みのある一杯。',
         description_en='72-hour pork bone broth enriched with black soy for profound depth.',
         price=1480, badge='recommend',
         image_url='https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=600&q=80', order=1),
    dict(category='ramen', name_ja='鶏白湯らーめん', name_en='Tori Paitan',
         description_ja='国産地鶏を丸ごと炊き出した濃厚白湯スープ。',
         description_en='Whole Japanese free-range chicken simmered to creamy perfection.',
         price=1680, badge='new',
         image_url='https://images.unsplash.com/photo-1591814468924-caf88d1232e1?w=600&q=80', order=2),
    dict(category='ramen', name_ja='冷やし中華', name_en='Chilled Noodles',
         description_ja='爽やかな酢醤油タレに彩り豊かな具材を添えた夏の逸品。',
         description_en='Refreshing soy-vinegar tare with vibrant seasonal toppings.',
         price=1280, badge='limited',
         image_url='https://images.unsplash.com/photo-1565299543923-37dd37887442?w=600&q=80', order=3),
    # DRINKS
    dict(category='drinks', name_ja='獺祭 磨き二割三分', name_en='Dassai 23 Sake',
         description_ja='山口県旭酒造の最高峰。精米歩合23%の透明感ある一杯。',
         description_en='Asahi Shuzo finest. 23% polishing ratio yields crystal-clear elegance.',
         price=2200, badge='recommend',
         image_url='https://images.unsplash.com/photo-1620360289473-ba0e3daaa5c3?w=600&q=80', order=1),
    dict(category='drinks', name_ja='抹茶ラテ', name_en='Matcha Latte',
         description_ja='京都宇治産一番摘み抹茶。まろやかな甘みと深い香り。',
         description_en='First-harvest Uji matcha. Velvety sweetness with lingering depth.',
         price=980, badge='', is_vegetarian=True,
         image_url='https://images.unsplash.com/photo-1536256263959-770b48d82b0a?w=600&q=80', order=2),
    dict(category='drinks', name_ja='冷酒三種飲み比べ', name_en='Sake Tasting Flight',
         description_ja='全国の蔵元から厳選した3種の冷酒を飲み比べ。',
         description_en='Three curated cold sake from Japan\'s finest breweries.',
         price=3600, badge='recommend',
         image_url='https://images.unsplash.com/photo-1556742400-b5b7c512e6f8?w=600&q=80', order=3),
]

COURSES = [
    dict(tier='matsu',   name_ja='松コース',      name_en='Matsu — Pine Course',
         description_ja='全5品の気軽な懐石コース。四季折々の彩りを味わう。',
         description_en='5-course introduction to kaiseki. A journey through Japan\'s seasons.',
         price=12000, courses=5,
         image_url='https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=80'),
    dict(tier='chiku',   name_ja='竹コース',      name_en='Chiku — Bamboo Course',
         description_ja='全8品の本格懐石。旬の食材を職人の技で昇華した一夜。',
         description_en='8-course authentic kaiseki. A masterful celebration of seasonal ingredients.',
         price=22000, courses=8,
         image_url='https://images.unsplash.com/photo-1540648639573-8c848de23f0a?w=600&q=80'),
    dict(tier='ume',     name_ja='梅コース',      name_en='Ume — Plum Course',
         description_ja='全12品の特別懐石。花膳の全てを体験する至高のコース。',
         description_en='12-course premium kaiseki. The ultimate Hanzen experience.',
         price=38000, courses=12,
         image_url='https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=80'),
    dict(tier='omakase', name_ja='花膳おまかせ', name_en='Hanzen Omakase',
         description_ja='板前に全てをお任せ。その日最高の一皿を芸術として体験。',
         description_en='Leave everything to the chef. Experience each dish as living art.',
         price=60000, courses=15,
         image_url='https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80'),
]

TESTIMONIALS = [
    dict(author_name='山田 花子', author_location='Tokyo, Japan', rating=5,
         quote_ja='花膳での夕食は、私の人生で最も感動的な食体験でした。料理の一皿ごとが芸術品であり、スタッフの心遣いも完璧でした。',
         quote_en='"Dinner at Hanzen was the most moving culinary experience of my life. Each dish was a masterpiece, and the staff\'s warmth was impeccable."',
         order=1),
    dict(author_name='James Whitfield', author_location='London, UK', rating=5,
         quote_ja='おまかせコースを体験しましたが、何年経っても忘れられない一夜になりました。大トロと雲丹の組み合わせは衝撃的でした。',
         quote_en='"The omakase was an evening I will cherish for years. The otoro and uni pairing was nothing short of revelatory."',
         order=2),
    dict(author_name='Sophie Lefebvre', author_location='Paris, France', rating=5,
         quote_ja='接客から空間、料理まで全てが非の打ちどころがない。東京で一番おすすめしたいレストランです。',
         quote_en='"Flawless from service to atmosphere to cuisine. My top recommendation in Tokyo — I\'ve already booked for my next trip."',
         order=3),
]

GALLERY = [
    dict(title_en='Sushi Counter', title_ja='寿司カウンター', is_featured=True,
         image_url='https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=1200&q=80',
         thumb_url='https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=600&q=80', order=1),
    dict(title_en='Otoro Nigiri', title_ja='大トロ握り', is_featured=True,
         image_url='https://images.unsplash.com/photo-1617196034183-421b4040ed20?w=1200&q=90',
         thumb_url='https://images.unsplash.com/photo-1617196034183-421b4040ed20?w=600&q=80', order=2),
    dict(title_en='Uni Gunkan', title_ja='雲丹軍艦', is_featured=False,
         image_url='https://images.unsplash.com/photo-1553621042-f6e147245754?w=1200&q=90',
         thumb_url='https://images.unsplash.com/photo-1553621042-f6e147245754?w=600&q=80', order=3),
    dict(title_en='Private Dining', title_ja='個室', is_featured=True,
         image_url='https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1200&q=90',
         thumb_url='https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=600&q=80', order=4),
    dict(title_en='Kaiseki Presentation', title_ja='懐石盛り付け', is_featured=False,
         image_url='https://images.unsplash.com/photo-1540648639573-8c848de23f0a?w=1200&q=90',
         thumb_url='https://images.unsplash.com/photo-1540648639573-8c848de23f0a?w=600&q=80', order=5),
]


class Command(BaseCommand):
    help = 'Seed database with sample restaurant data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌸 Seeding 花膳 Hanzen database...')

        # Categories
        cat_map = {}
        for c in CATEGORIES:
            obj, _ = Category.objects.get_or_create(slug=c['slug'], defaults=c)
            cat_map[c['slug']] = obj
        self.stdout.write(f'  ✓ {len(CATEGORIES)} categories')

        # Menu Items
        for m in MENU_ITEMS:
            cat_slug = m.pop('category')
            m.setdefault('is_vegetarian', False)
            m.setdefault('is_gluten_free', False)
            MenuItem.objects.get_or_create(
                name_ja=m['name_ja'],
                defaults={**m, 'category': cat_map[cat_slug]}
            )
        self.stdout.write(f'  ✓ {len(MENU_ITEMS)} menu items')

        # Courses
        for c in COURSES:
            CourseMenu.objects.get_or_create(tier=c['tier'], defaults=c)
        self.stdout.write(f'  ✓ {len(COURSES)} courses')

        # Testimonials
        for t in TESTIMONIALS:
            Testimonial.objects.get_or_create(author_name=t['author_name'], defaults=t)
        self.stdout.write(f'  ✓ {len(TESTIMONIALS)} testimonials')

        # Gallery
        for g in GALLERY:
            GalleryImage.objects.get_or_create(image_url=g['image_url'], defaults=g)
        self.stdout.write(f'  ✓ {len(GALLERY)} gallery images')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully! 花膳 is ready.'))
