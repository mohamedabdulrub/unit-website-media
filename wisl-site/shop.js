/* Wisl shop skin: adds the Wisl top bar, footer, shop heading and product perks on /shop, /shop/p/* and /cart. */
(function(){
  var A='https://cdn.jsdelivr.net/gh/mohamedabdulrub/unit-website-media@03aed2413993b6d486103edfa9f81c4d3cad9ba1/wisl-site/';
  var path=location.pathname, isCart=/^\/cart/.test(path), isItem=/^\/shop\/p\//.test(path), isList=/^\/shop\/?$/.test(path);
  function el(html){var d=document.createElement('div');d.innerHTML=html.trim();return d.firstChild;}
  function cartCount(){
    var n=document.querySelector('.header-actions .cart-quantity, .header-actions [class*="cart-quantity"], .sqs-cart-quantity');
    var v=n?parseInt(n.textContent,10):0; return isNaN(v)?0:v;
  }
  function run(){
    if(document.querySelector('.wisl-bar')) return;
    var bar=el('<header class="wisl-bar"><a href="/" aria-label="Wisl home"><img src="'+A+'wordmark.svg" alt="WISL"></a>'+
      '<nav aria-label="Shop"><a class="wisl-link hide-sm" href="/">Home</a><a class="wisl-link" href="/shop">Shop</a>'+
      '<a class="wisl-btn" href="/cart">Cart <span class="wisl-count">0</span></a></nav></header>');
    document.body.insertBefore(bar, document.body.firstChild);
    var cnt=bar.querySelector('.wisl-count');
    function sync(){ cnt.textContent=cartCount(); }
    sync(); setInterval(sync,1500);

    var foot=el('<footer class="wisl-foot"><img src="'+A+'wordmark.svg" alt="WISL"><span>Made in the UK · Sheffield-based team · Stay fizzy</span>'+
      '<nav aria-label="Footer"><a href="/">Home</a><a href="/shop">Shop</a><a href="https://wa.me/447405361101">WhatsApp</a><span>info@wisl.uk</span></nav></footer>');
    document.body.appendChild(foot);

    if(isList){
      var list=document.querySelector('.product-list-section, .product-list');
      if(list && !document.querySelector('.wisl-shop-hero')){
        list.parentNode.insertBefore(el('<section class="wisl-shop-hero"><h1 class="wisl-mark">Pick your pour</h1>'+
          '<p>330ml glass bottles of Wisl Cola. Free local delivery across Sheffield, delivered by us.</p></section>'), list);
      }
    }
    if(isItem){
      var add=document.querySelector('.product-add-to-cart');
      if(add && !document.querySelector('.wisl-perks')){
        add.parentNode.insertBefore(el('<ul class="wisl-perks"><li>Free local delivery in Sheffield</li><li>330ml glass bottles</li><li>Made in the UK</li></ul>'), add.nextSibling);
      }
    }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',run); else run();
})();
