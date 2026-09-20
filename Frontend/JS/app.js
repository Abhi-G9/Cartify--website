let allProducts = [];

// 1. हर प्रोडक्ट के नाम के हिसाब से 100% वर्किंग इमेज मैपर
function getProductImage(product) {
  const name = (product.name || '').toLowerCase();
  
  if (name.includes('phone') || name.includes('smartphone')) {
    return 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80';
  }
  if (name.includes('laptop') || name.includes('ultrabook')) {
    return 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&q=80';
  }
  if (name.includes('earbuds') || name.includes('audio') || name.includes('headphone')) {
    return 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80';
  }
  if (name.includes('watch')) {
    return 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80';
  }
  if (name.includes('keyboard')) {
    return 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&q=80';
  }
  if (name.includes('mouse')) {
    return 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&q=80';
  }
  if (name.includes('speaker')) {
    return 'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500&q=80';
  }
  if (name.includes('power bank')) {
    return 'https://images.unsplash.com/photo-1609592424097-9e0ce84b2c15?w=500&q=80';
  }
  if (name.includes('backpack')) {
    return 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80';
  }
  if (name.includes('cable')) {
    return 'https://images.unsplash.com/photo-1588508065123-287b28e013da?w=500&q=80';
  }

  return product.image || 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=500&q=80';
}

// 2. BACKEND SE PRODUCTS FETCH KARNA
async function loadProducts() {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/products');
    if (!res.ok) throw new Error("Network response was not ok");
    allProducts = await res.json();
    renderProducts(allProducts);
  } catch (err) {
    console.error("Error loading products:", err);
  }
}

// 3. PRODUCTS GRID RENDER KARNA
function renderProducts(products) {
  const container = document.getElementById('product-list');
  container.innerHTML = '';

  if (products.length === 0) {
    container.innerHTML = `<p style="color: #94a3b8; text-align: center; width: 100%;">No products found in this category.</p>`;
    return;
  }

  products.forEach(p => {
    const imgUrl = getProductImage(p);
    const mrp = Math.round(p.price * 1.25);
    const card = document.createElement('div');
    card.className = 'product-card';
    card.innerHTML = `
      <img src="${imgUrl}" class="product-img" alt="${p.name}" />
      <div class="prod-category">${p.category || 'Electronics'}</div>
      <div class="prod-title">${p.name}</div>
      <div class="prod-rating">★★★★★ <span style="color:#94a3b8; font-size: 11px;">(4.8)</span></div>
      <div class="price-row">
        <span class="curr-price">₹${p.price.toLocaleString('en-IN')}</span>
        <span class="mrp-price">₹${mrp.toLocaleString('en-IN')}</span>
        <span class="discount-tag">20% off</span>
      </div>
      <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart(${p.id})">
        <i class="fa-solid fa-cart-plus"></i> Add to Cart
      </button>
    `;
    card.onclick = () => openModal(p, imgUrl);
    container.appendChild(card);
  });
}

// 4. CATEGORY FILTER
function filterProducts(cat, element) {
  document.querySelectorAll('.category-card').forEach(el => el.classList.remove('active'));
  if (element) element.classList.add('active');

  if (cat === 'All') {
    renderProducts(allProducts);
  } else {
    const filtered = allProducts.filter(p => 
      (p.category && p.category.toLowerCase().includes(cat.toLowerCase())) ||
      (p.name && p.name.toLowerCase().includes(cat.toLowerCase()))
    );
    renderProducts(filtered);
  }
}

// 5. LIVE SEARCH FILTER
function searchProducts() {
  const query = document.getElementById('searchInput').value.toLowerCase();
  const filtered = allProducts.filter(p => 
    p.name.toLowerCase().includes(query) || 
    (p.category && p.category.toLowerCase().includes(query))
  );
  renderProducts(filtered);
}

// 6. ADD TO CART
async function addToCart(productId) {
  const email = localStorage.getItem('user_email') || 'abhinavgautam196186@gmail.com';
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/cart?email=${encodeURIComponent(email)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, quantity: 1 })
    });
    if (res.ok) {
      alert('✅ Added to Cartify Cart!');
      const badge = document.getElementById('cartCount');
      if (badge) badge.innerText = parseInt(badge.innerText || '0') + 1;
    } else {
      alert('Could not add to cart.');
    }
  } catch (err) {
    alert('Backend connection error.');
  }
}

// 7. PRODUCT DETAILS MODAL
function openModal(p, imgUrl) {
  document.getElementById('modalImg').src = imgUrl;
  document.getElementById('modalTitle').innerText = p.name;
  document.getElementById('modalCategory').innerText = p.category || 'Gadgets';
  document.getElementById('modalPrice').innerText = '₹' + p.price.toLocaleString('en-IN');
  document.getElementById('modalMrp').innerText = '₹' + Math.round(p.price * 1.25).toLocaleString('en-IN');
  document.getElementById('modalDesc').innerText = p.description || 'Authentic top-quality hardware with official 1-year brand warranty.';
  document.getElementById('modalAddBtn').onclick = () => addToCart(p.id);
  document.getElementById('prodModal').style.display = 'flex';
}

function closeModal() {
  document.getElementById('prodModal').style.display = 'none';
}

window.onclick = function(e) {
  const modal = document.getElementById('prodModal');
  if (e.target === modal) {
    closeModal();
  }
};

loadProducts();