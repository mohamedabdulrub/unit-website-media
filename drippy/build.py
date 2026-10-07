#!/usr/bin/env python3
"""Build Miss Drippy Squarespace code blocks + a local preview.

Outputs (drippy/squarespace/):
  home.html, menu.html, headford-street.html, centertainment.html, location.html
    -> paste each into ONE Code Block on that page (HTML only, no JS: Basic plan)
  custom.css (hand written) -> Design > Custom CSS
  preview/*.html -> standalone previews (CSS inlined) for review
Usage: python3 build.py <commit>
"""
import sys, html, pathlib, re

COMMIT = sys.argv[1] if len(sys.argv) > 1 else 'main'
CDN = f'https://cdn.jsdelivr.net/gh/mohamedabdulrub/unit-website-media@{COMMIT}/drippy'
IMG = f'{CDN}/img'
VID = f'{CDN}/video'
OUT = pathlib.Path(__file__).parent / 'squarespace'
PRE = OUT / 'preview'
PRE.mkdir(parents=True, exist_ok=True)
e = html.escape

# ---------------------------------------------------------------- facts
INSTA = 'https://www.instagram.com/missdrippy.uk/'
SITES = {
    'headford': dict(
        name='Headford Street', area='Sheffield city centre', pc='S3', short='Headford St',
        street='88 Headford Street', locality='Sheffield', postcode='S3 7WB',
        tel='+441144381532', tel_h='0114 438 1532',
        hours_h=[('Every day', '11am – 11pm')], hours_md='Mo-Su 11:00-23:00',
        uber='https://www.ubereats.com/gb/store/miss-drippy-desserts/J7Tpqdj2QfKeslBOl2nibg',
        roo='https://deliveroo.co.uk/menu/sheffield/sheffield-centre/miss-drippy-unit-headford',
        url='/headford-street', img='ferrero-bowl',
        blurb='Inside Unit on Headford Street, minutes from Division Street, West Street and Devonshire Green.',
        maps='https://www.google.com/maps/dir/?api=1&destination=88+Headford+Street%2C+Sheffield+S3+7WB',
        embed='https://maps.google.com/maps?q=88%20Headford%20Street%2C%20Sheffield%20S3%207WB&z=16&output=embed',
    ),
    'valley': dict(
        name='Centertainment', area='Valley Centertainment', pc='S9', short='Centertainment',
        street='Unit 4, Valley Centertainment, Broughton Lane', locality='Sheffield', postcode='S9 2EP',
        tel='+441143992513', tel_h='0114 399 2513',
        hours_h=[('Sun – Thu', '10am – 10pm'), ('Fri – Sat', '10am – 11pm')],
        hours_md=['Mo-Th 10:00-22:00', 'Su 10:00-22:00', 'Fr-Sa 10:00-23:00'],
        uber='https://www.ubereats.com/gb/store/miss-drippy-desserts-centertainment/oKgKSRmmXWGwNJozDxAnAg',
        roo='https://deliveroo.co.uk/menu/sheffield/rotherham-city-centre/miss-drippy',
        url='/centertainment', img='churros-bowl',
        blurb='Inside Unit at Valley Centertainment, next to Cineworld and Hollywood Bowl, on the same road as Utilita Arena. Delivering across east Sheffield and Rotherham.',
        maps='https://www.google.com/maps/dir/?api=1&destination=Unit+4%2C+Valley+Centertainment%2C+Broughton+Lane%2C+Sheffield+S9+2EP',
        embed='https://maps.google.com/maps?q=Valley%20Centertainment%2C%20Broughton%20Lane%2C%20Sheffield%20S9%202EP&z=16&output=embed',
    ),
}

# ---------------------------------------------------------------- menu (June 2026 in-store menu)
# star = marked as a favourite on the printed menu
MENU = [
    dict(id='waffle-bowls', name='Waffle Bowls', price='£8', img='brownie-bowl',
         alt='Brownie waffle bowl with ice cream, brownie chunks, chocolate drizzle and a cherry',
         blurb='A crispy waffle bowl stacked with ice cream, sauce and toppings. You eat the bowl too.',
         items=[('Brownie Bowl', 'Brownie chunks, chocolate and peanut drizzle, cherry on top.', True),
                ('Ferrero Bowl', 'Ferrero Rocher, chocolate and white drizzle, cherry on top.', False),
                ("Reese's Bowl", "Reese's chocolate and pieces with a peanut drizzle.", False),
                ('Churros Bowl', 'Churros, chocolate and caramel drizzle, cherry on top.', False),
                ('Salted Bowl', 'Salted caramel all the way down.', False),
                ('Pistachio Bowl', 'Pistachio sauce, ice cream, crunch.', False)]),
    dict(id='shakes', name='Shakes', price='£6.20', img='shakes-trio',
         alt='Three Miss Drippy milkshakes topped with whipped cream and Oreo',
         blurb='Thick shakes, sauce down the cup and toppings piled on.',
         items=[('Oreo Shake', 'Oreos blended in, chocolate sauce down the cup, Oreo dust on top.', True),
                ('Pistachio', 'Pistachio sauce in the shake, round the cup and on top.', True),
                ('Kinder Want', 'One for the Kinder fans.', True),
                ('Cheeseshake', 'Strawberry cheesecake vibes: strawberry and Lotus sauce, Lotus crumb.', True),
                ('Lustful Lotus', 'Lotus Biscoff blended in, Lotus sauce round the cup, Lotus crumb on top.', False),
                ('Salted Caramel', 'Salted caramel blended in and drizzled on top.', False),
                ('Nutella', 'Nutella in the shake and down the cup.', False),
                ("Reese's", 'Peanut butter meets chocolate.', False),
                ('Ferrero', 'Chocolate and hazelnut.', False),
                ('Strawberry', 'Strawberry sauce in, around and on top.', False),
                ('Miss Drippy', 'The house shake.', False),
                ('Crunch', '', False),
                ('Frappe', '', False),
                ('Vanilla', 'Classic vanilla ice cream, done properly.', False)]),
    dict(id='waffles', name='Waffles', price='£8.50', img='ferrero-waffle-2',
         alt='Michele Ferrero waffle loaded with Ferrero Rocher, chocolate, ice cream and a Miss Drippy wafer',
         blurb='Our waffles come stamped with the Miss Drippy logo. Then we load them up.',
         items=[('Michele Ferrero', 'Ferrero Rocher, chocolate chunks, ice cream and a double drizzle.', True),
                ('Frownie Berrero', 'Brownie meets Ferrero.', False),
                ("S'moreos", "S'mores meets Oreo.", False),
                ('Lo-Tus', 'Lotus Biscoff sauce, Lotus crumb and a tower of ice cream.', True),
                ("Reese's Peanut", 'Peanut butter and chocolate.', False),
                ('Pistachio', 'Pistachio sauce and crunch.', False)]),
    dict(id='cookie-dough', name='Cookie Dough', price='£8.50', img='ferrero-cookie-dough',
         alt='Ferrero cookie dough in a cast iron skillet with chocolate and a double drizzle',
         blurb='Cookie dough served in a skillet with all the extras.',
         items=[('Kinder Nice', 'Kinder chocolate on cookie dough.', True),
                ('Gimmeh S’mores', 'Marshmallows, chocolate and biscuit.', False),
                ('Get Lo-Tus', 'Lotus Biscoff sauce and crumb.', False),
                ("Reese's Peanut", 'Peanut butter and chocolate.', False),
                ('Chocolate Chip', 'The classic.', False),
                ('Pistachio', 'Warm cookie dough, pistachio drizzle and Lotus crumb.', False),
                ('Ferrero', 'Warm cookie dough, Ferrero Rocher and a double drizzle.', True)]),
    dict(id='sundaes', name='Sundaes', price='£5', img='churros-bowl-2',
         alt='Sundae with churros, ice cream, chocolate and caramel drizzle',
         blurb='Layered sundaes, sauce between every layer.',
         items=[("Reese's Salted", "Reese's and salted caramel.", True),
                ('Lotus Biscoff', 'Lotus sauce, Bueno sauce and Lotus crumb, layered with ice cream.', False),
                ('Pistachio', 'Pistachio sauce, Bueno sauce and Lotus crumb.', False),
                ('Cookies & Cream', 'Chocolate sauce and Oreo crumb, layered.', False),
                ('White Raspberry', 'Raspberry and Bueno sauce, layered with ice cream.', False),
                ('Miss Drippy', 'The house sundae.', False)]),
    dict(id='cakes', name='Cakes & Churros', price='from £5', img='crunch-cake',
         alt='Crunch cake slice with chocolate topping and crunchy crumb',
         blurb='Cake slices and filled churros for when you want something different.',
         items=[('Crunch Cake', 'Chocolate sponge under a thick chocolate topping and a crunchy crumb.', True, '£9'),
                ('Matilda Cake', 'Rich chocolate cake, drowned in warm chocolate sauce.', True, '£8.50'),
                ('Fudge Cake', '', False, '£7.50'),
                ('Caramel Filled Churros', '', False, '£8'),
                ('Choco Filled Churros', '', False, '£8'),
                ('To Embarrass A Friend', 'Ask the team. Trust us.', False, '£5'),
                ('Birthday Surprise', 'Ask in store.', False, '')]),
    dict(id='hot-drinks', name='Hot Drinks', price='£2.50', img=None, alt='',
         blurb='Something warm to go with it.',
         items=[('Coffee', '', False), ('Tea', '', False)]),
]
TOTAL_ITEMS = sum(len(c['items']) for c in MENU)

FAVES = [  # (name, desc, price, img, alt) - img "video:<name>" plays a loop from /video
    ('Ferrero Bowl', 'Waffle bowl, ice cream, Ferrero Rocher and a double drizzle.', '£8', 'ferrero-bowl', 'Ferrero waffle bowl with ice cream, Ferrero Rocher, chocolate drizzle and a cherry'),
    ('Brownie Bowl', 'Brownie chunks, chocolate and peanut drizzle, cherry on top.', '£8', 'brownie-bowl-2', 'Brownie waffle bowl with ice cream, brownie chunks, drizzle and a cherry'),
    ('Matilda Cake', 'Rich chocolate cake, drowned in warm chocolate sauce.', '£8.50', 'video:choc-pour', 'Warm chocolate sauce being poured over Matilda cake'),
    ('Lo-Tus Waffle', 'Lotus Biscoff sauce, Lotus crumb and a tower of ice cream.', '£8.50', 'lotus-waffle', 'Lotus Biscoff waffle with ice cream and caramel drizzle'),
    ('Crunch Cake', 'Chocolate sponge under a thick chocolate topping and a crunchy crumb.', '£9', 'crunch-cake', 'Crunch cake slice with chocolate topping and crumb on a green plate'),
    ('Ferrero Cookie Dough', 'Warm cookie dough, Ferrero Rocher and a double drizzle.', '£8.50', 'ferrero-cookie-dough-top', 'Ferrero cookie dough skillet seen from above'),
    ('Michele Ferrero Waffle', 'Loaded with Ferrero, chocolate chunks and ice cream.', '£8.50', 'ferrero-waffle-2', 'Michele Ferrero waffle with chocolate, Ferrero Rocher and ice cream'),
    ('Thick Shakes', 'Sauce down the cup, thick shake inside. 14 flavours.', '£6.20', 'video:shake-pour', 'Miss Drippy milkshake in a branded cup'),
    ('Pistachio Cookie Dough', 'Warm cookie dough, pistachio drizzle and Lotus crumb.', '£8.50', 'pistachio-cookie-dough', 'Pistachio cookie dough skillet with Lotus crumb and a Miss Drippy wafer'),
    ("Reese's Bowl", "Reese's everything with a peanut drizzle.", '£8', 'reeses-bowl', "Reese's waffle bowl with chocolate, Reese's pieces and peanut drizzle"),
]

DRIP = ('<svg class="md-drip" viewBox="0 0 1440 46" preserveAspectRatio="none" aria-hidden="true"><path d="M0 0h1440v10c-22 0-30 6-34 18-3 9-12 12-17 3-5-10-8-21-30-21-24 0-26 30-38 30s-12-30-40-30c-26 0-40 8-60 8s-24-8-54-8c-26 0-28 34-42 34s-14-34-40-34c-30 0-46 14-74 14s-30-14-64-14c-28 0-30 22-44 22s-16-22-46-22c-28 0-40 6-70 6s-34-6-62-6c-26 0-28 30-42 30s-14-30-42-30c-32 0-44 12-76 12S600 10 568 10c-24 0-26 24-40 24s-16-24-44-24c-30 0-44 8-74 8s-34-8-62-8c-28 0-30 32-44 32s-16-32-46-32c-28 0-40 10-68 10s-34-10-62-10c-24 0-26 20-38 20s-14-20-40-20C24 10 18 18 0 18z"/></svg>')


def img(name, alt, w=640, h=800, sm=True, cls='', eager=False):
    src = f'{IMG}/{name}-sm.webp' if sm else f'{IMG}/{name}.webp'
    srcset = f' srcset="{IMG}/{name}-sm.webp 640w, {IMG}/{name}.webp 1400w" sizes="(max-width:700px) 80vw, 33vw"'
    lazy = '' if eager else ' loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="{src}"{srcset} alt="{e(alt)}" width="{w}" height="{h}"{lazy}>'


def media(name, alt, w=640, h=800):
    if name.startswith('video:'):
        v = name[6:]
        return f'<video autoplay muted loop playsinline preload="none" poster="{VID}/{v}-poster.webp" aria-label="{e(alt)}"><source src="{VID}/{v}.mp4" type="video/mp4"></video>'
    return img(name, alt, w, h)


def order_btns(site, size=''):
    s = SITES[site]; sz = ' md-btn--sm' if size == 'sm' else ''
    out = [f'<a class="md-btn md-btn--uber{sz}" href="{s["uber"]}" target="_blank" rel="noopener">Uber Eats</a>']
    if s['roo']:
        out.append(f'<a class="md-btn md-btn--roo{sz}" href="{s["roo"]}" target="_blank" rel="noopener">Deliveroo</a>')
    return ''.join(out)


def nav(current=''):
    def a(href, label):
        cur = ' aria-current="page"' if href == current else ''
        return f'<a href="{href}"{cur}>{label}</a>'
    return f'''<header class="md-nav"><div class="md-wrap md-nav__in">
<a class="md-nav__logo" href="/" aria-label="Miss Drippy &amp; Co. home"><img src="{IMG}/logo-wordmark.webp" alt="Miss Drippy &amp; Co." width="687" height="339"></a>
<nav class="md-nav__links" aria-label="Main">{a('/menu','Menu')}{a('/headford-street','Headford St')}{a('/centertainment','Centertainment')}{a('/franchise','Franchise')}<a class="md-btn md-btn--ink md-btn--sm" href="{'/#order' if current else '#order'}">Order now</a></nav>
</div></header>'''


def bar(site=None):
    if site:
        s = SITES[site]
        btns = [f'<a class="md-btn md-btn--uber" href="{s["uber"]}" target="_blank" rel="noopener">Uber Eats<small>{s["pc"]} delivery</small></a>']
        if s['roo']:
            btns.append(f'<a class="md-btn md-btn--roo" href="{s["roo"]}" target="_blank" rel="noopener">Deliveroo<small>{s["pc"]} delivery</small></a>')
        else:
            btns.append(f'<a class="md-btn md-btn--pink" href="{s["maps"]}" target="_blank" rel="noopener">Directions<small>{s["postcode"]}</small></a>')
        label = f'Order from {s["name"]}'
    else:
        h, v = SITES['headford'], SITES['valley']
        btns = [f'<a class="md-btn md-btn--uber" href="{h["uber"]}" target="_blank" rel="noopener">Headford St<small>S3 · Uber Eats</small></a>',
                f'<a class="md-btn md-btn--uber" href="{v["uber"]}" target="_blank" rel="noopener">Centertainment<small>S9 · Uber Eats</small></a>']
        label = 'Order dessert to your door'
    return f'<div class="md-bar" role="region" aria-label="Order online"><p>{label}</p><div class="md-bar__btns">{"".join(btns)}</div></div>'


def footer():
    h, v = SITES['headford'], SITES['valley']
    return f'''<footer class="md-foot"><div class="md-wrap">
<div class="md-foot__in">
<div><img src="{IMG}/logo-duo.webp" alt="Miss Drippy &amp; Co." width="622" height="779" loading="lazy"><p>Desserts you crave. Waffle bowls, thick shakes, cookie dough and sundaes in Sheffield.</p></div>
<div><h4>Headford St · S3</h4><ul><li>{h['street']}, {h['postcode']}</li><li><a href="tel:{h['tel']}">{h['tel_h']}</a></li><li><a href="{h['uber']}" target="_blank" rel="noopener">Uber Eats</a> · <a href="{h['roo']}" target="_blank" rel="noopener">Deliveroo</a></li><li><a href="/headford-street">Store info</a></li></ul></div>
<div><h4>Centertainment · S9</h4><ul><li>Valley Centertainment, {v['postcode']}</li><li><a href="tel:{v['tel']}">{v['tel_h']}</a></li><li><a href="{v['uber']}" target="_blank" rel="noopener">Uber Eats</a> · <a href="{v['roo']}" target="_blank" rel="noopener">Deliveroo</a></li><li><a href="/centertainment">Store info · Rotherham delivery</a></li></ul></div>
<div><h4>More</h4><ul><li><a href="/menu">Full menu</a></li><li><a href="/franchise">Franchise with us</a></li><li><a href="{INSTA}" target="_blank" rel="noopener">Instagram @missdrippy.uk</a></li><li><a href="https://www.unitfood.co" target="_blank" rel="noopener">Unit Sheffield</a></li></ul></div>
</div>
<div class="md-foot__fine"><span>&copy; 2026 Miss Drippy &amp; Co. Sheffield.</span><span>Allergies? Ask our team before you order. Prices on delivery apps may differ.</span></div>
</div></footer>'''


def loc_card(key, heading='h3'):
    s = SITES[key]
    hours = ''.join(f'{d}: {t}<br>' for d, t in s['hours_h'])
    md_hours = s['hours_md'] if isinstance(s['hours_md'], list) else [s['hours_md']]
    hours_meta = ''.join(f'<meta itemprop="openingHours" content="{x}">' for x in md_hours)
    return f'''<article class="md-loc" itemscope itemtype="https://schema.org/IceCreamShop">
<meta itemprop="name" content="Miss Drippy {s['name']}"><meta itemprop="servesCuisine" content="Desserts"><meta itemprop="priceRange" content="£"><link itemprop="url" href="https://www.missdrippy.uk{s['url']}"><link itemprop="image" href="{IMG}/{s['img']}.webp"><link itemprop="hasMenu" href="https://www.missdrippy.uk/menu">{hours_meta}
<div class="md-loc__top"><span class="md-kicker">Sheffield {s['pc']}</span><{heading}>{s['name']}</{heading}></div>
<div class="md-loc__body">
<p style="margin:0">{s['blurb']}</p>
<dl class="md-loc__meta">
<div><dt>Address</dt><dd itemprop="address" itemscope itemtype="https://schema.org/PostalAddress"><span itemprop="streetAddress">{s['street']}</span>, <span itemprop="addressLocality">{s['locality']}</span> <span itemprop="postalCode">{s['postcode']}</span><meta itemprop="addressCountry" content="GB"></dd></div>
<div><dt>Open</dt><dd>{hours}<small>Delivery may finish a little earlier.</small></dd></div>
<div><dt>Call</dt><dd><a itemprop="telephone" href="tel:{s['tel']}">{s['tel_h']}</a></dd></div>
</dl>
<div class="md-loc__btns">{order_btns(key)}</div>
<div class="md-loc__links"><a href="{s['url']}">Store info &rarr;</a><a href="{s['maps']}" target="_blank" rel="noopener">Directions &rarr;</a></div>
</div></article>'''


def faq(items):
    out = ['<div class="md-faq" itemscope itemtype="https://schema.org/FAQPage">']
    for q, a in items:
        out.append(f'<details itemscope itemprop="mainEntity" itemtype="https://schema.org/Question"><summary itemprop="name">{q}</summary><div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer"><div itemprop="text"><p>{a}</p></div></div></details>')
    out.append('</div>')
    return ''.join(out)


def marquee(words):
    run = ''.join(f'<span>{w}<b>✦</b></span>' for w in words)
    return f'<div class="md-marquee" aria-hidden="true"><div class="md-marquee__track">{run}{run}</div></div>'


PAT = f' style="--pat:url({IMG}/pattern-tile.webp)"'


def wrap(body):
    return f'<div class="md-site">\n{body}\n</div>'

# ================================================================= HOME

def home():
    h, v = SITES['headford'], SITES['valley']
    cards = ''.join(f'''<a class="md-card" href="/menu" style="text-decoration:none">
<span class="md-card__price">{p}</span>{'<span class="md-card__badge">✦ fan fave</span>' if i < 4 else ''}
<div class="md-card__img">{media(im, alt)}</div>
<div class="md-card__body"><h3>{e(n)}</h3><p>{e(d)}</p></div></a>''' for i, (n, d, p, im, alt) in enumerate(FAVES))
    cats = ''.join(f'''<a class="md-cat" href="/menu#{c['id']}">{img(c['img'], c['alt'], 160, 160) if c['img'] else f'<img src="{IMG}/logo-cup.webp" alt="" width="160" height="160" loading="lazy" style="background:#fff;object-fit:contain;padding:6px">'}
<div><b>{c['name']}</b><span>{len(c['items'])} options · {c['price']}</span></div><i>&rarr;</i></a>''' for c in MENU)
    insta_imgs = ['lotus-bowl', 'oreo-smores-skillet', 'reeses-waffle', 'brownie-waffle', 'ferrero-cookie-dough-top-2', 'vanilla-shake']
    insta = ''.join(f'<a href="{INSTA}" target="_blank" rel="noopener" aria-label="See more on Instagram">{img(n, "Miss Drippy dessert on Instagram", 640, 640)}</a>' for n in insta_imgs)
    faqs = [
        ('Do you deliver desserts in Sheffield?', f'Yes. Order from our Headford Street kitchen (S3) on <a href="{h["uber"]}" target="_blank" rel="noopener">Uber Eats</a> or <a href="{h["roo"]}" target="_blank" rel="noopener">Deliveroo</a>, and from Valley Centertainment (S9) on <a href="{v["uber"]}" target="_blank" rel="noopener">Uber Eats</a> or <a href="{v["roo"]}" target="_blank" rel="noopener">Deliveroo</a>. The app shows which one delivers to you.'),
        ('Do you deliver to Rotherham?', f'Yes. Our Centertainment kitchen on Broughton Lane delivers to Rotherham on <a href="{v["roo"]}" target="_blank" rel="noopener">Deliveroo</a> and <a href="{v["uber"]}" target="_blank" rel="noopener">Uber Eats</a>. Pop your postcode in the app to check you\'re in range. We\'re also a short drive from Rotherham, just off the Parkway near Meadowhall.'),
        ('Where are you?', f'Two spots in Sheffield: <a href="/headford-street">88 Headford Street, S3 7WB</a> in the city centre, and <a href="/centertainment">Unit 4, Valley Centertainment, S9 2EP</a> on Broughton Lane. Both are inside Unit.'),
        ('How late are you open?', 'Headford Street is open 11am to 11pm every day. Centertainment is open 10am to 10pm Sunday to Thursday and until 11pm on Friday and Saturday.'),
        ("What's a waffle bowl?", 'A crispy waffle shaped into a bowl, filled with ice cream, sauce and toppings like Ferrero, brownie, churros or Reese\'s. You eat the bowl at the end.'),
        ('Do you have allergen info?', 'Yes. Please tell the team about any allergies before you order, or check the allergen notes in the Uber Eats or Deliveroo app.'),
    ]
    body = f'''{nav()}
<section class="md-hero"><div class="md-wrap md-hero__in">
<div>
<div class="md-hero__brand"><div class="md-hero__logo"><video autoplay muted loop playsinline preload="auto" poster="{VID}/logo-anim-poster.webp" aria-label="Miss Drippy &amp; Co. logo animation"><source src="{VID}/logo-anim.mp4" type="video/mp4"></video></div><span class="md-sticker">✦ Sheffield's dessert drop</span></div>
<h1>Desserts that <em>drip</em> different.</h1>
<p class="md-hero__lede">Waffle bowls, thick shakes, cookie dough and sundaes, loaded the way they should be. Get them delivered or come and find us in S3 and S9.</p>
<div class="md-hero__ctas"><a class="md-btn md-btn--ink" href="#order">Order now &darr;</a><a class="md-btn" href="/menu">See the menu</a></div>
<p class="md-hero__where">On <a href="#order">Uber Eats</a> &amp; <a href="#order">Deliveroo</a> · <a href="/headford-street">Headford St</a> · <a href="/centertainment">Centertainment</a></p>
</div>
<div class="md-hero__media">
<div class="md-hero__frame"><video autoplay muted loop playsinline preload="metadata" poster="{VID}/choc-pour-poster.webp" aria-label="Chocolate sauce pouring over a Miss Drippy dessert"><source src="{VID}/choc-pour.webm" type="video/webm"><source src="{VID}/choc-pour.mp4" type="video/mp4"></video></div>
<span class="md-sticker md-hero__tag">watch it drip ✦</span>
</div>
</div></section>
{marquee(['Waffle bowls', 'Thick shakes', 'Cookie dough', 'Sundaes', 'Filled churros', 'Stamped waffles'])}
<section class="md-sec md-sec--cream" id="faves"><div class="md-wrap">
<div class="md-head"><h2>Certified<br>bangers</h2><p>The stuff people come back for. Get them delivered on Uber Eats and Deliveroo.</p></div>
<div class="md-faves md-faves--10">{cards}</div>
</div></section>
<section class="md-sec md-sec--choc" style="border-bottom:0"><div class="md-wrap md-diff">
<div class="md-diff__photo">{img('wafer-sheets', 'Fresh Miss Drippy wafers stamped all over with the Miss Drippy logo', 640, 800)}<span class="md-sticker">yes, that's our name on it</span></div>
<div>
<h2>Not your average dessert spot.</h2>
<div class="md-points">
<div class="md-point"><span class="md-point__ico">1</span><div><h3>Our name's baked in</h3><p>Our wafers come off the iron stamped all over with the Miss Drippy logo. Little detail, big flex.</p></div></div>
<div class="md-point"><span class="md-point__ico">2</span><div><h3>Bowls you can eat</h3><p>Waffle bowls piled with ice cream, sauce and toppings. Nothing goes in the bin except the pot.</p></div></div>
<div class="md-point"><span class="md-point__ico">3</span><div><h3>{TOTAL_ITEMS//5*5}+ ways to go</h3><p>Shakes, sundaes, waffles, cookie dough, cakes and churros. Lotus, Ferrero, Reese's, Kinder, pistachio. Pick your fighter.</p></div></div>
</div></div>
</div></section>
<div style="background:var(--sky-soft)">{DRIP}</div>
<section class="md-sec md-sec--sky"><div class="md-wrap">
<div class="md-head"><h2>Pick your<br>menu</h2><p>Everything we make, with prices. <a href="/menu"><b>See the full menu &rarr;</b></a></p></div>
<div class="md-cats">{cats}</div>
</div></section>
<section class="md-sec md-pat" id="order"{PAT}><div class="md-wrap">
<div class="md-head"><h2>Order now</h2><p>Pick your closest spot. Delivery through Uber Eats and Deliveroo, or come in and grab a seat.</p></div>
<div class="md-locs">{loc_card('headford')}{loc_card('valley')}</div>
</div></section>
<section class="md-sec md-sec--cream"><div class="md-wrap md-insta">
<div>
<div class="md-insta__mascot"><video autoplay muted loop playsinline preload="none" poster="{VID}/mascot-shake-poster.webp" aria-label="Animated Miss Drippy milkshake character dancing"><source src="{VID}/mascot-shake.mp4" type="video/mp4"></video></div>
<h2>Post it or it didn't happen</h2>
<p>Tag <b>@missdrippy.uk</b> and we'll share our favourites.</p>
<a class="md-btn md-btn--pink" href="{INSTA}" target="_blank" rel="noopener">Follow @missdrippy.uk</a>
</div>
<div class="md-insta__grid">{insta}</div>
</div></section>
<section class="md-sec md-sec--sky"><div class="md-wrap">
<div class="md-head"><h2>Questions</h2></div>
{faq(faqs)}
</div></section>
{footer()}
{bar()}'''
    return wrap(body)

# ================================================================= MENU

def menu_page():
    chips = ''.join(f'<a href="#{c["id"]}">{c["name"]}</a>' for c in MENU)
    secs = []
    for c in MENU:
        items = []
        for it in c['items']:
            n, d, star = it[0], it[1], it[2]
            p = it[3] if len(it) > 3 else c['price']
            star_h = '<span class="md-star" title="Fan favourite" aria-label="fan favourite">✦</span>' if star else ''
            price_md = re.sub(r'[^0-9.]', '', p)
            offer = f'<span itemprop="offers" itemscope itemtype="https://schema.org/Offer"><meta itemprop="price" content="{price_md}"><meta itemprop="priceCurrency" content="GBP"></span>' if price_md else ''
            items.append(f'<li class="md-item" itemprop="hasMenuItem" itemscope itemtype="https://schema.org/MenuItem"><h3 itemprop="name">{e(n)}{star_h}</h3><span class="md-item__p">{e(p) if p else "Ask"}</span>{f"<p itemprop=description>{e(d)}</p>" if d else ""}{offer}</li>')
        pic = f'<div class="md-msec__img">{img(c["img"], c["alt"], 640, 800)}</div>' if c['img'] else ''
        secs.append(f'''<section class="md-msec" id="{c['id']}" itemprop="hasMenuSection" itemscope itemtype="https://schema.org/MenuSection"><div class="md-wrap md-msec__in">
<div class="md-msec__side"><h2 itemprop="name">{c['name']}</h2><span class="md-msec__price">{c['price']}</span><p>{c['blurb']}</p>{pic}</div>
<div><ul class="md-items">{''.join(items)}</ul>
<div class="md-msec__order"><a class="md-btn md-btn--uber md-btn--sm" href="{SITES['headford']['uber']}" target="_blank" rel="noopener">Uber Eats · S3</a><a class="md-btn md-btn--roo md-btn--sm" href="{SITES['headford']['roo']}" target="_blank" rel="noopener">Deliveroo · S3</a><a class="md-btn md-btn--uber md-btn--sm" href="{SITES['valley']['uber']}" target="_blank" rel="noopener">Uber Eats · S9</a><a class="md-btn md-btn--roo md-btn--sm" href="{SITES['valley']['roo']}" target="_blank" rel="noopener">Deliveroo · S9 &amp; Rotherham</a></div>
</div></div></section>''')
    body = f'''{nav('/menu')}
<section class="md-phero md-pat"{PAT}><div class="md-wrap md-phero__in">
<div class="md-phero__copy"><p class="md-crumbs"><a href="/">Home</a> / Menu</p>
<h1>The menu</h1>
<p>{TOTAL_ITEMS} desserts and drinks, from waffle bowls to Matilda cake. Look for the <span class="md-star">✦</span> for fan faves.</p>
<div class="md-hero__ctas"><a class="md-btn md-btn--ink" href="/#order">Order now</a></div></div>
<div class="md-phero__img">{img('ferrero-bowl-close', 'Close up of a Ferrero waffle bowl with chocolate drizzle', 640, 800, eager=True)}</div>
</div></section>
<nav class="md-chips" aria-label="Menu sections"><div class="md-wrap md-chips__in">{chips}</div></nav>
<div itemscope itemtype="https://schema.org/Menu"><meta itemprop="name" content="Miss Drippy dessert menu"><meta itemprop="inLanguage" content="en-GB">
{''.join(secs)}
</div>
<section class="md-sec md-sec--cream"><div class="md-wrap"><p class="md-note">In-store prices from our June 2026 menu. Prices and items on Uber Eats and Deliveroo can differ. Allergies? Please ask the team before ordering.</p></div></section>
{footer()}
{bar()}'''
    return wrap(body)

# ================================================================= LOCATION PAGES

LOC = {
    'headford': dict(
        h1='Miss Drippy<br>Headford Street',
        lede='Dessert in Sheffield city centre. Waffle bowls, shakes, cookie dough and sundaes at 88 Headford Street, S3, open until 11pm every day. Delivered across the centre on Uber Eats and Deliveroo.',
        hero='ferrero-bowl', hero_alt='Ferrero waffle bowl from Miss Drippy Headford Street', tone='md-phero--pink',
        near=[('Division Street', 'A few minutes away'), ('West Street', 'A few minutes away'), ('Devonshire Green', 'A few minutes away'),
              ('University of Sheffield', 'Close to campus'), ('Sheffield Hallam', 'Collegiate and City campuses'), ('Bramall Lane', 'Walking distance'),
              ('Parking', 'Pay & display outside, free after 8:30pm'), ('Postcode', 'S3 7WB')],
        intro=('Late-night dessert near the unis',
               'Headford Street sits between the University of Sheffield and Sheffield Hallam, a few minutes from Division Street and Devonshire Green. Come in after a night out, grab a shake between lectures, or get a waffle bowl delivered to your flat. Look for the blue building with the giant burger mural: we\'re inside Unit.'),
        faqs=[('Do you deliver from Headford Street?', 'Yes, on Uber Eats and Deliveroo. Open the app, search Miss Drippy, and pick the Headford Street store.'),
              ('What time does Miss Drippy Headford Street close?', 'We\'re open 11am to 11pm, seven days a week. Delivery can finish a little earlier.'),
              ('Can I eat in?', 'Yes. We\'re inside Unit at 88 Headford Street, so grab a seat and order at the counter.'),
              ('Is there parking?', 'There\'s pay and display parking right outside, free after 8:30pm.'),
              ('Do you have allergen info?', 'Yes. Please tell the team about any allergies before you order, or check the allergen notes in the delivery app.')]),
    'valley': dict(
        h1='Miss Drippy<br>Centertainment',
        lede='Dessert at Valley Centertainment, Sheffield S9. Waffle bowls, shakes, cookie dough and sundaes next to Cineworld and Hollywood Bowl, on the same road as Utilita Arena. Delivered across east Sheffield and Rotherham on Uber Eats and Deliveroo.',
        hero='churros-bowl', hero_alt='Churros waffle bowl from Miss Drippy Centertainment', tone='md-phero--sky',
        near=[('Utilita Arena', 'Steelers, gigs, a short walk'), ('Cineworld', 'Same complex'), ('Hollywood Bowl', 'Same complex'), ('Meadowhall', 'A few minutes away'),
              ('IKEA Sheffield', 'Just down the road'), ('iceSheffield', 'Close by'), ('Rotherham', 'A short drive, and we deliver'), ('Tram', 'Stop right outside')],
        intro=('Dessert before the film, after the game',
               'We\'re at Valley Centertainment on Broughton Lane, next to Cineworld and Hollywood Bowl and a short walk from Utilita Arena. Free parking and a tram stop outside make it the easy stop before a Steelers game or gig, after bowling, or after a day at Meadowhall. Find us inside Unit, Unit 4. We also deliver to Rotherham and around Meadowhall, so if you can\'t make it over, get it brought to you.'),
        faqs=[('Do you deliver from Centertainment?', 'Yes, on Uber Eats and Deliveroo. On Deliveroo we\'re listed as Miss Drippy – Rotherham City Centre, and on Uber Eats as Miss Drippy Desserts – Centertainment.'),
              ('Do you deliver to Rotherham?', 'Yes. Our Centertainment kitchen delivers dessert to Rotherham on Deliveroo and Uber Eats. Enter your postcode in the app to check you\'re in range.'),
              ('What are your opening times?', 'Sunday to Thursday 10am to 10pm, Friday and Saturday 10am to 11pm. Delivery can finish a little earlier.'),
              ('Is there parking?', 'Yes, Valley Centertainment has free parking, and the tram stops right outside.'),
              ('Are you near Utilita Arena?', 'Yes, we\'re on Broughton Lane, the same road as Utilita Arena. Grab dessert before or after the show.'),
              ('Do you have allergen info?', 'Yes. Please tell the team about any allergies before you order, or check the allergen notes in the delivery app.')]),
}


def location_page(key):
    s, L = SITES[key], LOC[key]
    other = 'valley' if key == 'headford' else 'headford'
    o = SITES[other]
    near = ''.join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in L['near'])
    faves = ''.join(f'''<a class="md-card" href="/menu" style="text-decoration:none"><span class="md-card__price">{p}</span>
<div class="md-card__img">{media(im, alt)}</div><div class="md-card__body"><h3>{e(n)}</h3><p>{e(d)}</p></div></a>''' for (n, d, p, im, alt) in FAVES[:4])
    hours = ''.join(f'<li><b>{d}</b> {t}</li>' for d, t in s['hours_h'])
    md_hours = s['hours_md'] if isinstance(s['hours_md'], list) else [s['hours_md']]
    hours_meta = ''.join(f'<meta itemprop="openingHours" content="{x}">' for x in md_hours)
    roo_line = f'<li><a href="{s["roo"]}" target="_blank" rel="noopener"><b>Deliveroo</b></a></li>' if s['roo'] else ''
    body = f'''{nav(s['url'])}
<section class="md-phero {L['tone']}"><div class="md-wrap md-phero__in">
<div><p class="md-crumbs"><a href="/">Home</a> / <a href="/location">Locations</a> / {s['name']}</p>
<h1>{L['h1']}</h1>
<p>{L['lede']}</p>
<div class="md-hero__ctas">{order_btns(key)}<a class="md-btn" href="{s['maps']}" target="_blank" rel="noopener">Directions</a></div></div>
<div class="md-phero__img">{img(L['hero'], L['hero_alt'], 640, 800, eager=True)}</div>
</div></section>
{marquee(['Waffle bowls', 'Thick shakes', 'Cookie dough', 'Sundaes', f'Sheffield {s["pc"]}'] + (['Rotherham delivery'] if key == 'valley' else []))}
<section class="md-sec md-sec--cream"><div class="md-wrap md-split" itemscope itemtype="https://schema.org/IceCreamShop">
<meta itemprop="name" content="Miss Drippy {s['name']}"><meta itemprop="servesCuisine" content="Desserts"><meta itemprop="priceRange" content="£"><link itemprop="url" href="https://www.missdrippy.uk{s['url']}"><link itemprop="image" href="{IMG}/{s['img']}.webp"><link itemprop="hasMenu" href="https://www.missdrippy.uk/menu">{hours_meta}
<div><h2 style="font-size:clamp(40px,5vw,68px);margin-bottom:18px">{L['intro'][0]}</h2><p style="font-size:18px">{L['intro'][1]}</p>
<div class="md-facts" style="grid-template-columns:1fr 1fr;margin-top:22px">
<div class="md-fact" style="grid-column:1/-1"><h3>Find us</h3><p itemprop="address" itemscope itemtype="https://schema.org/PostalAddress"><span itemprop="streetAddress">{s['street']}</span>, <span itemprop="addressLocality">{s['locality']}</span> <span itemprop="postalCode">{s['postcode']}</span><meta itemprop="addressCountry" content="GB"></p><p><a itemprop="telephone" href="tel:{s['tel']}">{s['tel_h']}</a> · <a href="{s['maps']}" target="_blank" rel="noopener"><b>Directions &rarr;</b></a></p></div>
<div class="md-fact"><h3>Opening hours</h3><ul>{hours}</ul><p style="font-size:14px;margin-top:6px">Delivery may finish a little earlier.</p></div>
<div class="md-fact"><h3>Order online</h3><div class="md-loc__btns md-loc__btns--col">{order_btns(key, 'sm')}</div></div>
</div></div>
<div class="md-map"><iframe src="{s['embed']}" title="Map showing Miss Drippy {s['name']}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
</div></section>
<section class="md-sec md-pat"{PAT}><div class="md-wrap">
<div class="md-head"><h2>What's nearby</h2></div>
<ul class="md-near">{near}</ul>
</div></section>
<section class="md-sec md-sec--cream"><div class="md-wrap">
<div class="md-head"><h2>Fan faves</h2><p><a href="/menu"><b>See the full menu &rarr;</b></a></p></div>
<div class="md-faves">{faves}</div>
</div></section>
<section class="md-sec md-sec--pink"><div class="md-wrap">
<div class="md-head"><h2>Questions</h2></div>
{faq(L['faqs'])}
<p style="margin-top:28px;font-weight:700">Closer to {o['area']}? <a href="{o['url']}">Visit Miss Drippy {o['name']} &rarr;</a></p>
</div></section>
{footer()}
{bar(key)}'''
    return wrap(body)


def location_hub():
    body = f'''{nav('/location')}
<section class="md-phero"><div class="md-wrap md-phero__in">
<div><p class="md-crumbs"><a href="/">Home</a> / Locations</p>
<h1>Find us in Sheffield</h1>
<p>Two spots, same drip. Headford Street in the city centre (S3) and Valley Centertainment near Utilita Arena and Meadowhall (S9), which also delivers to Rotherham.</p></div>
<div class="md-phero__img">{img('reeses-bowl', "Reese's waffle bowl", 640, 800, eager=True)}</div>
</div></section>
<section class="md-sec md-pat" id="order"{PAT}><div class="md-wrap">
<div class="md-locs">{loc_card('headford')}{loc_card('valley')}</div>
</div></section>
{footer()}
{bar()}'''
    return wrap(body)


FR_MAIL = 'mailto:info@unitfood.co?subject=Miss%20Drippy%20franchise%20enquiry'


def franchise_page():
    why = [('1', 'A brand people screenshot', 'Two cartoon characters, a swatch pattern, branded cups, boxes and wrap, and wafers stamped with our name. Miss Drippy is built to be posted.'),
           ('2', 'A menu made for delivery', 'Waffle bowls, cookie dough skillets, shakes and sundaes that travel well. We already trade on Uber Eats and Deliveroo from both Sheffield sites.'),
           ('3', 'Run by people who run sites', 'Miss Drippy is part of the Unit family in Sheffield, alongside Unit burger diners and WISL Cola. You get operators, not just a logo.')]
    why_h = ''.join(f'<div class="md-point"><span class="md-point__ico">{n}</span><div><h3>{h}</h3><p>{b}</p></div></div>' for n, h, b in why)
    formats = [('Dessert shop', 'A standalone Miss Drippy with seating, for high streets, student areas and city centres.', 'pink'),
               ('Shop-in-shop', 'A Miss Drippy counter inside a restaurant, leisure venue or food court. Like our two Sheffield sites inside Unit.', 'sky'),
               ('Delivery kitchen', 'A delivery-led setup for Uber Eats and Deliveroo, with branded packaging built for the trip.', 'mustard')]
    fmt_h = ''.join(f'<div class="md-fact" style="background:var(--{c if c!="mustard" else "mustard"});"><h3>{h}</h3><p>{b}</p></div>' for h, b, c in formats).replace('var(--pink)', 'var(--pink-soft)').replace('var(--sky)', 'var(--sky-soft)')
    support = [('Training', 'Recipes, builds and service, so every bowl looks like the photo.'),
               ('Brand & packaging', 'Cups, boxes, wraps, stickers, uniforms and shopfront artwork.'),
               ('Menu & suppliers', 'The full menu with specs, plus the suppliers we use.'),
               ('Delivery set-up', 'Getting you live and looking good on Uber Eats and Deliveroo.'),
               ('Launch marketing', 'Socials, content and noise for your opening.'),
               ('Ongoing support', 'New menu drops, campaigns and a team on the end of the phone.')]
    sup_h = ''.join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in support)
    steps = [('Enquire', 'Email us with a bit about you and where you\'d like to open.'),
             ('Chat', 'An intro call to talk formats, locations and what\'s involved.'),
             ('Visit', 'Come to Sheffield, try the menu and see how we run.'),
             ('Plan & open', 'Agree the site and the plan, then we help you launch.')]
    st_h = ''.join(f'<div class="md-point"><span class="md-point__ico">{i+1}</span><div><h3>{a}</h3><p>{b}</p></div></div>' for i, (a, b) in enumerate(steps))
    faqs = [('How much does a Miss Drippy franchise cost?', 'It depends on the format and the site. Get in touch and we\'ll talk you through the numbers for what you have in mind.'),
            ('Do I need food or hospitality experience?', 'It helps, but attitude and a real focus on customer service matter most. We train you and your team.'),
            ('Where can I open?', 'We\'re open to conversations about locations across the UK. Tell us where you\'re thinking.'),
            ('Is this the same company as Unit?', 'Miss Drippy is part of the Unit family in Sheffield. If you\'re interested in a burger diner too, see the <a href="https://www.unitfood.co/franchising" target="_blank" rel="noopener">Unit franchise page</a>.')]
    body = f'''{nav('/franchise')}
<section class="md-phero md-pat"{PAT}><div class="md-wrap md-phero__in">
<div class="md-phero__copy"><p class="md-crumbs"><a href="/">Home</a> / Franchise</p>
<span class="md-sticker" style="margin-top:6px">✦ Now taking enquiries</span>
<h1>Open a Miss Drippy</h1>
<p>Bring Sheffield's loudest dessert brand to your town. Waffle bowls, thick shakes and cookie dough, with the characters, packaging and playbook to go with them.</p>
<div class="md-hero__ctas"><a class="md-btn md-btn--ink" href="{FR_MAIL}">Start your enquiry</a><a class="md-btn" href="#formats">See the formats</a></div></div>
<div class="md-phero__img">{img('ferrero-waffle-2', 'Michele Ferrero waffle with a Miss Drippy wafer and WISL Cola', 640, 800, eager=True)}</div>
</div></section>
{marquee(['Franchise with us', 'Waffle bowls', 'Stamped wafers', 'Delivery ready', 'Made in Sheffield'])}
<section class="md-sec md-sec--choc" style="border-bottom:0"><div class="md-wrap md-diff">
<div class="md-diff__photo">{img('wafer-sheets', 'Miss Drippy wafers stamped with the Miss Drippy logo', 640, 800)}<span class="md-sticker">our name's on everything</span></div>
<div><h2>Why Miss Drippy?</h2><div class="md-points">{why_h}</div></div>
</div></section>
<div style="background:var(--cream)">{DRIP}</div>
<section class="md-sec md-sec--cream" id="formats"><div class="md-wrap">
<div class="md-head"><h2>Formats</h2><p>Three ways to bring Miss Drippy to your area. Investment depends on the format and site, so ask us for the details.</p></div>
<div class="md-facts">{fmt_h}</div>
</div></section>
<section class="md-sec md-pat"{PAT}><div class="md-wrap">
<div class="md-head"><h2>What you get</h2></div>
<ul class="md-near">{sup_h}</ul>
</div></section>
<section class="md-sec md-sec--sky"><div class="md-wrap md-split">
<div><h2 style="font-size:clamp(40px,5vw,68px);margin-bottom:18px">Who we're looking for</h2>
<p style="font-size:18px">People with a can-do attitude, a real focus on customer service, and the drive to build something in their area. Bonus points if you already know what Gen Z wants from a night out.</p>
<a class="md-btn md-btn--ink" href="{FR_MAIL}">Email info@unitfood.co</a></div>
<div><h2 style="font-size:clamp(34px,4vw,52px);margin-bottom:18px">How it works</h2><div class="md-points md-points--light">{st_h}</div></div>
</div></section>
<section class="md-sec md-sec--pink"><div class="md-wrap">
<div class="md-head"><h2>Questions</h2></div>
{faq(faqs)}
<div class="md-hero__ctas" style="margin-top:30px"><a class="md-btn md-btn--ink" href="{FR_MAIL}">Start your enquiry</a></div>
</div></section>
{footer()}'''
    return wrap(body)


PAGES = {
    'home': home(), 'menu': menu_page(), 'headford-street': location_page('headford'),
    'centertainment': location_page('valley'), 'location': location_hub(), 'franchise': franchise_page(),
}

css = (OUT / 'custom.css').read_text()
TITLES = {
    'home': 'Miss Drippy & Co. | Dessert Delivery in Sheffield',
    'menu': 'Menu | Miss Drippy & Co. Sheffield',
    'headford-street': 'Miss Drippy Headford Street | Desserts in Sheffield City Centre S3',
    'centertainment': 'Miss Drippy Centertainment | Dessert Delivery Sheffield S9 & Rotherham',
    'location': 'Locations | Miss Drippy & Co. Sheffield',
    'franchise': 'Franchise | Open a Miss Drippy Dessert Shop',
}
for k, v in PAGES.items():
    (OUT / f'{k}.html').write_text(f'<!-- Miss Drippy: paste into ONE Code Block on the {k} page. Built from build.py @ {COMMIT} -->\n{v}\n')
    # preview: rewrite internal links to preview files
    pv = v
    for slug in ['menu', 'headford-street', 'centertainment', 'location', 'franchise']:
        pv = pv.replace(f'href="/{slug}#', f'href="{slug}.html#').replace(f'href="/{slug}"', f'href="{slug}.html"')
    pv = pv.replace('href="/#order"', 'href="index.html#order"').replace('href="/"', 'href="index.html"')
    name = 'index' if k == 'home' else k
    (PRE / f'{name}.html').write_text(f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(TITLES[k])}</title><style>body{{margin:0;background:#FFF4E8}}{css}</style></head><body>{pv}</body></html>''')
print('built', list(PAGES), 'items', TOTAL_ITEMS)
