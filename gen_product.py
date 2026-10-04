"""Restyle Squarespace product pages (/shop/p/...) to match the new design.

Output: out/product-header-injection.html -> paste into the Store page ("Shop", /shop)
Page Settings > Advanced > Page Header Code Injection. Squarespace applies a collection
page's header injection to all of its item pages too.

Usage: python3 gen_product.py   (live URLs)
"""
import json, os, re, runpy, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
sys.argv = [sys.argv[0], 'live']
g = runpy.run_path(os.path.join(HERE, 'gen_shop.py'))
CATS, products, style, footer = g['CATS'], g['products'], g['style'], g['footer']
MERCH = '/merch'
HS, CT = g['HS'], g['CT']

header = g['header'].replace('href="#', 'href="%s#' % MERCH)

# page CSS shared with the other new pages (hides template header/footer, mobile header rules)
head_main = open(os.path.join(OUT, 'main-header-injection.html')).read()
page_css = head_main.split('<script type="application/ld+json">')[0]
page_css = page_css.replace('<meta name="robots" content="noindex, nofollow">\n', '')
shop_head = open(os.path.join(OUT, 'shop-header-injection.html')).read()
shop_css = re.search(r'<style>\n@media \(max-width: 767px\)\{\n\.unit-site \.u-shop-grid.*?</style>', shop_head, re.S).group(0)

# product data keyed by URL path
data = {}
for cid, title, intro, colour, items in CATS:
    for pid, name, sub, blurb, tags in items:
        p = products[pid]
        data[p['u']] = {'id': pid, 'n': html.unescape(name), 's': sub, 'b': blurb, 't': tags, 'c': cid,
                        'i': p['img'], 'p': min(p['p']), 'm': len(set(p['p'])) > 1, 'o': p['stock'] == 0}
cat_names = {c[0]: html.unescape(c[1]) for c in CATS}

pdp_css = '''<style>
/* Unit redesign: product pages */
body{background:#FFFAF0!important}
.product-detail-section, .product-reviews-section, .related-products-section{background:#FFFAF0!important}
.product-detail-section .section-background, .product-reviews-section .section-background, .related-products-section .section-background{background:#FFFAF0!important}
.related-products-section{display:none!important}
.product-detail-section .content-wrapper{max-width:1280px!important;margin:0 auto!important;padding:36px 24px 56px!important}
.product-detail .pdp-gallery-images, .product-detail .pdp-gallery-slides, .product-detail .pdp-gallery img{border-radius:22px}
.product-detail .pdp-gallery-images{border:3px solid #2D2926;overflow:hidden;background:#FFFFFF}
.product-detail .pdp-gallery-thumbnails img, .product-detail [class*=thumbnail] img{border:2.5px solid #2D2926;border-radius:12px}
.product-detail .pdp-carousel-controls button{background:#FFFAF0!important;border:2.5px solid #2D2926!important;border-radius:999px!important;color:#2D2926!important}
.product-detail .pdp-gallery-slide-indicator{font-family:'American Typewriter','Courier Prime',serif;color:#2D2926;background:#FFFAF0;border:2px solid #2D2926;border-radius:999px;padding:2px 10px}
.product-detail, .product-detail p, .product-detail div, .product-detail span, .product-detail label, .product-detail legend{font-family:'American Typewriter','Courier Prime','Courier New',serif;color:#2D2926;letter-spacing:normal}
.product-detail .product-nav{font-size:13px!important;font-weight:700;text-transform:uppercase;letter-spacing:.5px!important;margin-bottom:14px}
.product-detail .product-nav a{color:#9E6950!important;font-family:'American Typewriter','Courier Prime',serif!important;text-decoration:none;border-bottom:2px solid transparent}
.product-detail .product-nav a:hover{border-bottom-color:#9E6950}
.product-detail .product-nav span{color:#9E6950!important}
.product-detail .product-title{font-family:'Motter Corpus ITC TT','Motter Corpus',MOTTCI,Corben,Georgia,serif!important;font-weight:700!important;color:#9E6950!important;font-size:clamp(36px,4.6vw,60px)!important;line-height:1.02!important;text-transform:none!important;letter-spacing:normal!important;margin:0 0 10px!important;white-space:normal!important}
.product-detail .product-price, .product-detail .product-price-value{font-size:24px!important;font-weight:700!important;color:#2D2926!important}
.product-detail .product-price{margin:4px 0 12px!important}
.product-detail .product-description, .product-detail .product-description p{font-size:18px!important;line-height:1.55!important}
.product-detail .product-description{margin:0 0 18px!important}
.product-detail .variant-option-title{font-size:13px!important;font-weight:700!important;text-transform:uppercase;letter-spacing:.5px!important;margin-bottom:6px}
.product-detail .variant-select{font-family:'American Typewriter','Courier Prime',serif!important;font-size:16px!important;color:#2D2926!important;background:#FFFFFF!important;border:2.5px solid #2D2926!important;border-radius:14px!important;min-height:50px;padding:0 44px 0 16px!important}
.product-detail .variant-select-wrapper .form-input-effects{display:none!important}
.product-detail .variant-select-icon, .product-detail .variant-select-icon svg{color:#2D2926!important;fill:#2D2926!important;stroke:#2D2926!important}
.product-detail .product-quantity-input{background:#FFFFFF!important;border:2.5px solid #2D2926!important;border-radius:999px!important;min-height:52px;overflow:hidden}
.product-detail .product-quantity-input input{font-family:'American Typewriter','Courier Prime',serif!important;font-size:17px!important;font-weight:700;color:#2D2926!important;background:transparent!important}
.product-detail .product-quantity-input button span{background-color:#2D2926!important;border-color:#2D2926!important}
.product-detail .product-quantity-input-wrapper .form-input-effects{display:none!important}
.product-detail .sqs-add-to-cart-button{background:#F99814!important;color:#2D2926!important;border:2.5px solid #2D2926!important;border-radius:999px!important;min-height:52px!important;font-family:'American Typewriter','Courier Prime',serif!important;font-weight:700!important;font-size:16px!important;text-transform:uppercase!important;letter-spacing:.5px!important;box-shadow:0 4px 0 #2D2926;transition:transform .12s ease, box-shadow .12s ease, background .12s ease}
.product-detail .sqs-add-to-cart-button *{color:inherit!important;font-family:inherit!important}
.product-detail .sqs-add-to-cart-button:hover{background:#FCE053!important;transform:translateY(-2px);box-shadow:0 6px 0 #2D2926}
.product-detail .sqs-add-to-cart-button:active{transform:translateY(2px);box-shadow:0 2px 0 #2D2926}
.product-detail .sqs-add-to-cart-button[disabled], .product-detail .sqs-add-to-cart-button.cart-sold-out{background:#E8E1D5!important;box-shadow:none!important;cursor:not-allowed}
.product-detail .product-mark{font-family:'American Typewriter','Courier Prime',serif;background:#D1555A!important;color:#FFFAF0!important;border:2px solid #2D2926;border-radius:999px;padding:3px 10px}
/* injected extras */
.u-pdp-tags{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px}
.u-pdp-tags span{background:#2D2926;color:#FFFAF0!important;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
.u-pdp-sub{margin:0 0 6px!important;font-size:14px!important;font-weight:700;text-transform:uppercase;letter-spacing:.5px!important;color:#9E6950!important}
.u-pdp-info{margin-top:24px;border:3px solid #2D2926;border-radius:22px;background:#FFFFFF;padding:18px 20px;display:flex;flex-direction:column;gap:10px}
.u-pdp-info h2{margin:0;font-family:'Motter Corpus ITC TT','Motter Corpus',MOTTCI,Corben,Georgia,serif;font-weight:700;font-size:20px;color:#2D2926;text-transform:none;letter-spacing:normal}
.u-pdp-info p{margin:0!important;font-size:15px!important;line-height:1.45!important}
.u-pdp-info .u-row{display:flex;flex-wrap:wrap;gap:8px}
.u-pdp-info a{display:inline-flex;align-items:center;min-height:42px;padding:0 16px;border-radius:999px;border:2.5px solid #2D2926;font-family:'American Typewriter','Courier Prime',serif;font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:.5px;text-decoration:none;color:#2D2926!important;background:#FFFAF0}
.u-pdp-info a.u-hot{background:#F99814}
.u-pdp-info a:hover{background:#FCE053}
.u-added{display:none;margin-top:12px;font-weight:700}
.u-added a{color:#2D2926!important;border-bottom:2px solid #2D2926;text-decoration:none}
@media (max-width: 767px){
.product-detail-section .content-wrapper{padding:20px 16px 40px!important}
.product-detail .product-title{font-size:36px!important}
.product-detail .product-description, .product-detail .product-description p{font-size:16px!important}
}
</style>'''

pdp_js = r'''<script>
(function(){
  var path=location.pathname.replace(/\/+$/,'');
  if(path==='/shop'){location.replace('/merch'+location.hash);return;}
  var D=__DATA__, CATN=__CATN__, HEADER=__HEADER__, FOOTER=__FOOTER__, HS='__HS__', CT='__CT__';
  function money(v){return v>=1?'£'+v.toFixed(2):Math.round(v*100)+'p';}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function wrap(inner){var d=document.createElement('div');d.className='unit-site';d.innerHTML='<div class="u-tw" style="color: #2D2926; background: #FFFAF0; width: 100%; line-height: 1.55; font-size: 17px; overflow-x: hidden">'+inner+'</div>';return d;}
  function card(u,p){
    var tags=p.t.map(function(t){return '<span style="background: #2D2926; color: #FFFAF0; border-radius: 999px; padding: 2px 9px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px">'+esc(t)+'</span>';}).join('');
    var img=p.i+(p.i.indexOf('?')>-1?'&':'?')+'format=600w';
    return '<a class="u-shop-card" data-id="'+p.id+'" href="'+u+'" style="text-decoration: none; color: #2D2926; background: #FFFAF0; border: 3px solid #2D2926; border-radius: 22px; overflow: hidden; display: flex; flex-direction: column">'+
      '<div style="position: relative; aspect-ratio: 1 / 1; background: #FFFFFF; border-bottom: 3px solid #2D2926"><img src="'+img+'" alt="'+esc(p.n)+'" loading="lazy" style="display: block; width: 100%; height: 100%; object-fit: cover">'+
      '<span class="u-sold" style="position: absolute; left: 10px; top: 10px; background: #D1555A; color: #FFFAF0; border: 2px solid #2D2926; border-radius: 999px; padding: 3px 10px; font-size: 12px; font-weight: 700; text-transform: uppercase;'+(p.o?'':' display: none')+'">Sold out</span></div>'+
      '<div style="padding: 16px 16px 18px; display: flex; flex-direction: column; gap: 6px; flex-grow: 1"><div style="display: flex; flex-wrap: wrap; gap: 6px">'+tags+'</div>'+
      '<h3 class="u-disp" style="margin: 0; font-size: 22px; line-height: 1.1">'+esc(p.n)+'</h3>'+
      '<p style="margin: 0; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; color: #9E6950">'+esc(p.s)+'</p>'+
      '<p style="margin: 0; font-size: 15px; line-height: 1.45">'+esc(p.b)+'</p>'+
      '<div style="margin-top: auto; padding-top: 8px; display: flex; align-items: center; justify-content: space-between; gap: 8px"><strong class="u-price" style="font-size: 18px">'+(p.m?'From ':'')+money(p.p)+'</strong>'+
      '<span class="u-cta" style="font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; border-bottom: 2px solid #2D2926">'+(p.o?'View':'Buy now')+' →</span></div></div></a>';
  }
  function run(){
    if(document.documentElement.__unitPdp)return; document.documentElement.__unitPdp=true;
    var site=document.getElementById('siteWrapper')||document.body, page=document.getElementById('page');
    var h=wrap(HEADER); site.insertBefore(h,site.firstChild);
    var p=D[path], detail=document.querySelector('.product-detail');
    // breadcrumb back to the new shop page
    document.querySelectorAll('.product-nav-breadcrumb-link').forEach(function(a,i){ if(i===0){a.href='/merch'+(p?'#'+p.c:'');a.textContent='Shop';} });
    if(p&&detail){
      var meta=detail.querySelector('.product-meta'), title=meta&&meta.querySelector('.product-title');
      if(title){
        var tg=document.createElement('div');tg.className='u-pdp-tags';tg.innerHTML=p.t.map(function(t){return '<span>'+esc(t)+'</span>';}).join('');
        if(p.t.length)title.parentNode.insertBefore(tg,title);
        var sub=document.createElement('p');sub.className='u-pdp-sub';sub.textContent=CATN[p.c]+' · '+p.s;title.parentNode.insertBefore(sub,title);
      }
      detail.querySelectorAll('.product-description').forEach(function(d){
        var txt=(d.textContent||'').replace(/\s+/g,' ').trim();
        // replace blank or placeholder descriptions with our copy; keep longer hand-written ones underneath
        d.innerHTML='<p class="u-pdp-lead" style="margin: 0 0 10px">'+esc(p.b)+'</p>';
        d.style.opacity='1';
      });
    }
    var atc=detail&&detail.querySelector('.product-add-to-cart');
    if(atc){
      var added=document.createElement('p');added.className='u-added';added.innerHTML='Added to your basket. <a href="/cart">View basket →</a>';
      atc.appendChild(added);
      var btn=atc.querySelector('.sqs-add-to-cart-button');
      if(btn)btn.addEventListener('click',function(){setTimeout(function(){added.style.display='block';},900);});
      var info=document.createElement('div');info.className='u-pdp-info';
      info.innerHTML='<h2>Hungry now?</h2><p>Order food online and collect it from your nearest Unit.</p><div class="u-row"><a class="u-hot" href="'+HS+'">Collect from Headford St</a><a class="u-hot" href="'+CT+'">Collect from Centertainment</a></div>';
      atc.parentNode.insertBefore(info,atc.nextSibling);
    }
    // more from the shop
    var others=Object.keys(D).filter(function(u){return u!==path;});
    var same=others.filter(function(u){return p&&D[u].c===p.c;}), rest=others.filter(function(u){return !p||D[u].c!==p.c;});
    var pickU=same.concat(rest).filter(function(u){return !D[u].o;}).slice(0,4);
    var more='<section style="max-width: 1280px; margin: 0 auto; padding: 8px 24px 64px; display: flex; flex-direction: column; gap: 22px">'+
      '<div style="display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 12px"><h2 class="u-disp" style="margin: 0; font-size: clamp(30px, 4vw, 46px); line-height: 1.02; color: #9E6950">More from the shop</h2>'+
      '<a class="u-btn" href="/merch" style="background: #FFFAF0; color: #2D2926">See everything</a></div>'+
      '<div class="u-shop-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 250px), 1fr)); gap: 20px">'+pickU.map(function(u){return card(u,D[u]);}).join('')+'</div></section>';
    var m=wrap(more+FOOTER);
    if(page&&page.parentNode)page.parentNode.insertBefore(m,page.nextSibling);else site.appendChild(m);
    // live prices / stock for the cards
    fetch('/shop?format=json',{credentials:'same-origin'}).then(function(r){return r.json();}).then(function(j){
      (j.items||[]).forEach(function(it){
        var c=m.querySelector('.u-shop-card[data-id="'+it.id+'"]'); if(!c)return;
        var vs=(it.structuredContent&&it.structuredContent.variants)||[]; if(!vs.length)return;
        var pr=vs.map(function(v){return v.onSale?(v.salePriceMoney?+v.salePriceMoney.value:v.salePrice/100):(v.priceMoney?+v.priceMoney.value:v.price/100);});
        var mn=Math.min.apply(null,pr), multi=pr.some(function(x){return x!==pr[0];}), stock=vs.some(function(v){return v.unlimited||v.qtyInStock>0;});
        var pe=c.querySelector('.u-price'); if(pe)pe.textContent=(multi?'From ':'')+money(mn);
        var so=c.querySelector('.u-sold'); if(so)so.style.display=stock?'none':'';
      });
    }).catch(function(){});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run);else run();
})();
</script>'''

pdp_js = (pdp_js.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
          .replace('__CATN__', json.dumps(cat_names, ensure_ascii=False))
          .replace('__HEADER__', json.dumps(header, ensure_ascii=False))
          .replace('__FOOTER__', json.dumps(footer, ensure_ascii=False))
          .replace('__HS__', HS).replace('__CT__', CT))
# keep "</" out of the inline script strings
pdp_js_body = pdp_js[len('<script>'):-len('</script>')].replace('</', '<\\/')
pdp_js = '<script>' + pdp_js_body + '</script>'

head = page_css + style + '\n' + shop_css + '\n' + pdp_css + '\n' + pdp_js
open(os.path.join(OUT, 'product-header-injection.html'), 'w').write(head)
print('product-header-injection.html', len(head))
