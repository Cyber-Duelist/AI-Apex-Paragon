import os

html_v2 = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article | Adarsh K.S.</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    
    <!-- Modern Tools -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js" defer></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" defer></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.0/vanilla-tilt.min.js" defer></script>
    
    <style>
        /* 3D Canvas Background */
        #article-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: -1;
            background: #040406;
        }

        /* Base Typography & Layout */
        body { color: var(--text-color); margin: 0; overflow-x: hidden; }
        
        .article-container {
            max-width: 850px;
            margin: 120px auto 80px auto;
            padding: 50px;
            background: rgba(10, 10, 15, 0.65);
            border: 1px solid rgba(0, 229, 255, 0.15);
            border-radius: 16px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255,255,255,0.05);
            position: relative;
        }

        /* Read Time Badge */
        .article-meta {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 30px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            color: var(--secondary-color);
        }
        .read-time-badge {
            background: rgba(0, 229, 255, 0.1);
            border: 1px solid rgba(0, 229, 255, 0.3);
            padding: 4px 12px;
            border-radius: 20px;
            color: #00e5ff;
        }

        /* Article Content Styling */
        .article-content h1 { font-size: 2.8rem; color: var(--primary-color); margin-bottom: 25px; line-height: 1.2; letter-spacing: -0.5px; }
        .article-content h2 { font-size: 1.9rem; color: #fff; margin-top: 50px; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
        .article-content h3 { font-size: 1.5rem; color: var(--secondary-color); margin-top: 40px; margin-bottom: 15px; }
        .article-content p { font-size: 1.15rem; line-height: 1.85; color: #c4c4c4; margin-bottom: 25px; }
        .article-content a { color: var(--accent-color); text-decoration: none; border-bottom: 1px dotted var(--accent-color); transition: 0.2s; }
        .article-content a:hover { color: #fff; border-bottom-style: solid; text-shadow: 0 0 8px var(--accent-color); }
        
        .article-content code { background: rgba(255,255,255,0.08); padding: 3px 6px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.9em; color: #ff79c6; }
        .article-content pre { 
            background: #111116; 
            padding: 25px; 
            border-radius: 12px; 
            overflow-x: auto; 
            margin-bottom: 30px; 
            border: 1px solid rgba(255,255,255,0.1); 
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            transform-style: preserve-3d; /* For VanillaTilt */
        }
        .article-content pre code { background: none; color: #f8f8f2; padding: 0; font-size: 0.95em; }
        
        .article-content ul, .article-content ol { margin-bottom: 25px; padding-left: 25px; color: #c4c4c4; font-size: 1.15rem; line-height: 1.8; }
        .article-content li { margin-bottom: 10px; }
        
        .article-content blockquote { 
            border-left: 4px solid var(--accent-color); 
            margin: 30px 0; 
            padding: 15px 25px; 
            background: linear-gradient(90deg, rgba(255, 0, 110, 0.08) 0%, rgba(255, 0, 110, 0) 100%); 
            color: #e0e0e0; 
            font-style: italic; 
            border-radius: 0 8px 8px 0;
        }

        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 30px;
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
            transition: 0.3s;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 1px;
        }
        .back-btn:hover { color: #fff; text-shadow: 0 0 12px var(--primary-color); transform: translateX(-5px); }
        .loading-text { text-align: center; color: var(--primary-color); font-family: 'JetBrains Mono', monospace; padding: 50px; font-size: 1.2rem; }

        /* Author Bio Box */
        .author-bio {
            margin-top: 60px;
            padding: 30px;
            background: rgba(0, 229, 255, 0.05);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 16px;
            display: flex;
            gap: 20px;
            align-items: center;
            transform-style: preserve-3d;
        }
        .author-bio img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 2px solid var(--primary-color);
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
            object-fit: cover;
            transform: translateZ(20px);
        }
        .author-info h4 { margin: 0 0 5px 0; color: #fff; font-size: 1.2rem; }
        .author-info p { margin: 0; color: #a0a0a0; font-size: 0.95rem; line-height: 1.5; }

        /* Interactive Star Rating */
        .rating-container {
            margin-top: 40px;
            text-align: center;
            padding-top: 40px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .rating-container h4 { color: #fff; margin-bottom: 15px; font-size: 1.1rem; font-weight: 500; }
        .stars {
            display: inline-flex;
            flex-direction: row-reverse;
            gap: 8px;
        }
        .stars input { display: none; }
        .stars label {
            color: rgba(255,255,255,0.2);
            font-size: 2rem;
            cursor: pointer;
            transition: 0.2s, transform 0.2s;
        }
        .stars label:hover, .stars label:hover ~ label, .stars input:checked ~ label {
            color: #ffd700;
            text-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        }
        .stars label:hover { transform: scale(1.2); }
        .rating-msg { margin-top: 15px; font-size: 0.9rem; color: var(--secondary-color); font-family: 'JetBrains Mono', monospace; height: 20px; opacity: 0; transition: opacity 0.3s; }

        @media (max-width: 768px) {
            .article-container { margin: 100px 15px 40px 15px; padding: 25px 20px; }
            .article-content h1 { font-size: 2.2rem; }
            .author-bio { flex-direction: column; text-align: center; }
            .author-bio img { transform: translateZ(0); }
        }
    </style>
</head>
<body>
    <!-- 3D Canvas -->
    <canvas id="article-canvas"></canvas>

    <!-- Navigation -->
    <nav id="navbar" style="background: rgba(4, 4, 6, 0.7); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.05);">
        <a href="index.html" class="nav-logo glitch" data-text="AKS." style="text-decoration: none;">AKS<span class="accent">.</span></a>
        <div class="nav-links">
            <a href="index.html#articles">← Back to Portfolio</a>
        </div>
    </nav>

    <div class="article-container">
        <a href="index.html#articles" class="back-btn"><i class="fas fa-chevron-left"></i> Back to Articles</a>
        
        <div class="article-meta" id="article-meta" style="display: none;">
            <span class="read-time-badge" id="read-time">🕒 Calculating...</span>
            <span id="article-date">📅 2026</span>
        </div>

        <div id="article-content" class="article-content">
            <div class="loading-text">
                <i class="fas fa-circle-notch fa-spin"></i> Initializing Markdown Engine...
            </div>
        </div>

        <!-- Author Box -->
        <div class="author-bio" id="author-box" style="display: none;">
            <img src="ultraman.png" alt="Adarsh K.S.">
            <div class="author-info">
                <h4>Written by Adarsh K.S.</h4>
                <p>AI, ML & Data Engineer specializing in Multi-Agent Swarms, Production RAG, and classical predictive modeling. Building autonomous systems that solve real enterprise problems.</p>
            </div>
        </div>

        <!-- Rating System -->
        <div class="rating-container" id="rating-box" style="display: none;">
            <h4>Enjoyed this article? Rate it:</h4>
            <div class="stars">
                <input type="radio" id="star5" name="rating" value="5"><label for="star5" class="fas fa-star"></label>
                <input type="radio" id="star4" name="rating" value="4"><label for="star4" class="fas fa-star"></label>
                <input type="radio" id="star3" name="rating" value="3"><label for="star3" class="fas fa-star"></label>
                <input type="radio" id="star2" name="rating" value="2"><label for="star2" class="fas fa-star"></label>
                <input type="radio" id="star1" name="rating" value="1"><label for="star1" class="fas fa-star"></label>
            </div>
            <div class="rating-msg" id="rating-msg">Rating saved to local databank. Thank you!</div>
        </div>
    </div>

    <script src="article.js"></script>
</body>
</html>
'''

js_v2 = '''
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Initialize Three.js Sub-Space Background
    initThreeJS();

    const urlParams = new URLSearchParams(window.location.search);
    const articleId = urlParams.get('id');
    const contentDiv = document.getElementById('article-content');
    const metaDiv = document.getElementById('article-meta');
    const readTimeSpan = document.getElementById('read-time');
    const authorBox = document.getElementById('author-box');
    const ratingBox = document.getElementById('rating-box');

    if (!articleId) {
        contentDiv.innerHTML = '<h1>Error 404</h1><p>Article ID not specified in URL.</p>';
        return;
    }

    try {
        const response = await fetch(`articles/${articleId}.md`);
        if (!response.ok) throw new Error(`Failed to load article: ${response.status}`);
        
        const markdownText = await response.text();
        
        // Calculate Read Time (avg 200 words per minute)
        const wordCount = markdownText.trim().split(/\s+/).length;
        const readTime = Math.max(1, Math.ceil(wordCount / 200));
        readTimeSpan.innerHTML = `🕒 ${readTime} min read`;
        
        // Render Markdown
        if (typeof marked === 'undefined') throw new Error('marked.js not loaded.');
        contentDiv.innerHTML = marked.parse(markdownText);
        
        // Show Meta, Author, and Ratings
        metaDiv.style.display = 'flex';
        authorBox.style.display = 'flex';
        ratingBox.style.display = 'block';

        // Initialize 3D VanillaTilt on specific elements
        if (typeof VanillaTilt !== 'undefined') {
            VanillaTilt.init(document.querySelectorAll(".article-content pre, .author-bio"), {
                max: 3,
                speed: 400,
                glare: true,
                "max-glare": 0.15,
                perspective: 1000
            });
        }

        // Initialize Rating System
        setupRatings(articleId);

    } catch (error) {
        console.error('Error:', error);
        contentDiv.innerHTML = `<h1>System Error</h1><p>Could not load the requested document.</p><p style="font-family: monospace; color: #ff3366;">${error.message}</p>`;
    }
});

function setupRatings(articleId) {
    const stars = document.querySelectorAll('input[name="rating"]');
    const msg = document.getElementById('rating-msg');
    const storageKey = `rating_${articleId}`;

    // Check if already rated
    const savedRating = localStorage.getItem(storageKey);
    if (savedRating) {
        const starInput = document.getElementById(`star${savedRating}`);
        if (starInput) starInput.checked = true;
        msg.style.opacity = '1';
        msg.innerHTML = "You have already rated this article.";
    }

    stars.forEach(star => {
        star.addEventListener('change', (e) => {
            const val = e.target.value;
            localStorage.setItem(storageKey, val);
            msg.style.opacity = '1';
            msg.innerHTML = `Rating of ${val} stars saved to local databank. Thank you!`;
        });
    });
}

function initThreeJS() {
    if (typeof THREE === 'undefined') return;
    
    const canvas = document.getElementById('article-canvas');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    // Create subtle particles
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 400;
    const posArray = new Float32Array(particlesCount * 3);
    
    for(let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 15;
    }
    
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    
    // Very subtle, small glowing dots
    const material = new THREE.PointsMaterial({
        size: 0.02,
        color: 0x00e5ff,
        transparent: true,
        opacity: 0.4,
        blending: THREE.AdditiveBlending
    });
    
    const particlesMesh = new THREE.Points(particlesGeometry, material);
    scene.add(particlesMesh);
    
    camera.position.z = 3;
    
    // Mouse interaction
    let mouseX = 0;
    let mouseY = 0;
    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX / window.innerWidth) - 0.5;
        mouseY = (event.clientY / window.innerHeight) - 0.5;
    });
    
    const clock = new THREE.Clock();
    
    function animate() {
        requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();
        
        // Slow rotation
        particlesMesh.rotation.y = elapsedTime * 0.05;
        particlesMesh.rotation.x = elapsedTime * 0.02;
        
        // Subtle mouse parallax
        camera.position.x += (mouseX * 0.5 - camera.position.x) * 0.05;
        camera.position.y += (-mouseY * 0.5 - camera.position.y) * 0.05;
        camera.lookAt(scene.position);
        
        renderer.render(scene, camera);
    }
    
    animate();
    
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}
'''

dirs = ['docs', 'portfolio_website']
for d in dirs:
    base = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d)
    if os.path.exists(base):
        with open(os.path.join(base, 'article.html'), 'w', encoding='utf-8') as f:
            f.write(html_v2)
        with open(os.path.join(base, 'article.js'), 'w', encoding='utf-8') as f:
            f.write(js_v2)
