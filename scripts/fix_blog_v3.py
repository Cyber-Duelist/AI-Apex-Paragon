import os

html_v3 = '''<!DOCTYPE html>
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
            background: var(--bg-void, #050505);
        }

        /* Base Typography & Layout */
        body { color: var(--text-white, #f0f0f8); margin: 0; overflow-x: hidden; font-family: 'Inter', sans-serif; }
        
        .article-container {
            max-width: 850px;
            margin: 120px auto 80px auto;
            padding: 50px 60px;
            background: rgba(10, 10, 15, 0.65);
            border: 1px solid var(--glass-border, rgba(0, 240, 255, 0.2));
            border-radius: 16px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255,255,255,0.05);
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
            color: var(--text-silver, #a0a0b8);
        }
        .read-time-badge {
            background: rgba(0, 240, 255, 0.1);
            border: 1px solid rgba(0, 240, 255, 0.3);
            padding: 6px 14px;
            border-radius: 20px;
            color: var(--accent-2, #00f0ff);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.8rem;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.2);
        }

        /* Article Content Styling */
        .article-content h1 { 
            font-size: 3rem; 
            color: var(--text-white, #fff); 
            margin-bottom: 25px; 
            line-height: 1.2; 
            letter-spacing: -1px; 
            text-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
        }
        .article-content h2 { font-size: 2rem; color: var(--accent-2, #00f0ff); margin-top: 50px; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
        .article-content h3 { font-size: 1.6rem; color: var(--accent-1, #00ff66); margin-top: 40px; margin-bottom: 15px; }
        .article-content p { font-size: 1.15rem; line-height: 1.85; color: var(--text-silver, #a0a0b8); margin-bottom: 25px; }
        .article-content a { color: var(--accent-2, #00f0ff); text-decoration: none; border-bottom: 1px dotted var(--accent-2); transition: 0.2s; }
        .article-content a:hover { color: #fff; border-bottom-style: solid; text-shadow: 0 0 8px var(--accent-2); }
        
        .article-content strong { color: var(--text-white, #fff); font-weight: 600; }
        
        .article-content code { background: rgba(255,255,255,0.08); padding: 3px 6px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.9em; color: var(--accent-3, #8a2be2); }
        .article-content pre { 
            background: var(--bg-deep, #0a0a0a); 
            padding: 25px; 
            border-radius: 12px; 
            overflow-x: auto; 
            margin-bottom: 30px; 
            border: 1px solid rgba(0, 240, 255, 0.15); 
            box-shadow: 0 8px 24px rgba(0,0,0,0.6);
            transform-style: preserve-3d;
        }
        .article-content pre code { background: none; color: #f8f8f2; padding: 0; font-size: 0.95em; }
        
        .article-content ul, .article-content ol { margin-bottom: 25px; padding-left: 25px; color: var(--text-silver, #a0a0b8); font-size: 1.15rem; line-height: 1.8; }
        .article-content li { margin-bottom: 10px; }
        
        .article-content blockquote { 
            border-left: 4px solid var(--accent-1, #00ff66); 
            margin: 30px 0; 
            padding: 20px 25px; 
            background: linear-gradient(90deg, rgba(0, 255, 102, 0.05) 0%, rgba(0, 255, 102, 0) 100%); 
            color: var(--text-white, #f0f0f8); 
            font-style: italic; 
            border-radius: 0 8px 8px 0;
            font-size: 1.25rem;
            line-height: 1.6;
        }

        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 30px;
            color: var(--accent-2, #00f0ff);
            text-decoration: none;
            font-weight: 600;
            transition: 0.3s;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 1px;
        }
        .back-btn:hover { color: #fff; text-shadow: 0 0 12px var(--accent-2); transform: translateX(-5px); }
        .loading-text { text-align: center; color: var(--accent-1, #00ff66); font-family: 'JetBrains Mono', monospace; padding: 50px; font-size: 1.2rem; }

        /* Author Bio Box */
        .author-bio {
            margin-top: 60px;
            padding: 30px;
            background: rgba(0, 240, 255, 0.05);
            border: 1px solid rgba(0, 240, 255, 0.2);
            border-radius: 16px;
            display: flex;
            gap: 20px;
            align-items: center;
            transform-style: preserve-3d;
            box-shadow: 0 8px 32px rgba(0, 240, 255, 0.1);
        }
        .author-bio img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 2px solid var(--accent-2, #00f0ff);
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
            object-fit: cover;
            transform: translateZ(20px);
        }
        .author-info h4 { margin: 0 0 5px 0; color: var(--text-white); font-size: 1.2rem; }
        .author-info p { margin: 0; color: var(--text-silver); font-size: 0.95rem; line-height: 1.5; }

        /* Interactive Star Rating */
        .rating-container {
            margin-top: 40px;
            text-align: center;
            padding-top: 40px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .rating-container h4 { color: var(--text-white); margin-bottom: 15px; font-size: 1.1rem; font-weight: 500; }
        .stars {
            display: inline-flex;
            flex-direction: row-reverse;
            gap: 8px;
        }
        .stars input { display: none; }
        .stars label {
            color: rgba(255,255,255,0.2);
            font-size: 2.5rem;
            cursor: pointer;
            transition: 0.2s, transform 0.2s;
        }
        .stars label:hover, .stars label:hover ~ label, .stars input:checked ~ label {
            color: var(--accent-1, #00ff66);
            text-shadow: 0 0 20px rgba(0, 255, 102, 0.6);
        }
        .stars label:hover { transform: scale(1.2) translateY(-5px); }
        .rating-msg { margin-top: 15px; font-size: 0.95rem; color: var(--accent-2, #00f0ff); font-family: 'JetBrains Mono', monospace; height: 20px; opacity: 0; transition: opacity 0.3s; text-shadow: 0 0 10px rgba(0,240,255,0.4); }

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
    <nav id="navbar" style="background: rgba(5, 5, 5, 0.85); backdrop-filter: blur(15px); border-bottom: 1px solid rgba(255,255,255,0.05); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; position: fixed; width: 100%; top: 0; z-index: 100; box-sizing: border-box;">
        <a href="index.html" class="nav-logo glitch" data-text="AKS." style="text-decoration: none; font-size: 1.5rem; font-weight: 800; color: #fff;">AKS<span class="accent" style="color: var(--accent-1, #00ff66);">.</span></a>
        <div class="nav-links">
            <a href="index.html#articles" style="color: #fff; text-decoration: none; font-weight: 500; font-size: 0.9rem; letter-spacing: 1px; text-transform: uppercase;">? Back to Portfolio</a>
        </div>
    </nav>

    <div class="article-container">
        <a href="index.html#articles" class="back-btn"><i class="fas fa-chevron-left"></i> Portfolio</a>
        
        <div class="article-meta" id="article-meta" style="display: none;">
            <span class="read-time-badge" id="read-time">?? Calculating...</span>
            <span id="article-date">?? 2026</span>
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
            <h4>Enjoyed this article? Leave a rating:</h4>
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

js_v3 = '''
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Initialize Neural Network 3D Background
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
        const response = await fetch(rticles/.md);
        if (!response.ok) throw new Error(Failed to load article: );
        
        const markdownText = await response.text();
        
        // Calculate Read Time
        const wordCount = markdownText.trim().split(/\s+/).length;
        const readTime = Math.max(1, Math.ceil(wordCount / 200));
        readTimeSpan.innerHTML = ??  min read;
        
        // Render Markdown
        if (typeof marked === 'undefined') throw new Error('marked.js not loaded.');
        contentDiv.innerHTML = marked.parse(markdownText);
        
        // Show Meta, Author, and Ratings
        metaDiv.style.display = 'flex';
        authorBox.style.display = 'flex';
        ratingBox.style.display = 'block';

        // Initialize 3D VanillaTilt
        if (typeof VanillaTilt !== 'undefined') {
            VanillaTilt.init(document.querySelectorAll(".article-content pre, .author-bio"), {
                max: 3,
                speed: 400,
                glare: true,
                "max-glare": 0.2,
                perspective: 1000
            });
        }

        // Initialize Rating System
        setupRatings(articleId);

    } catch (error) {
        console.error('Error:', error);
        contentDiv.innerHTML = <h1>System Error</h1><p>Could not load the requested document.</p><p style="font-family: monospace; color: #ff3366;"></p>;
    }
});

function setupRatings(articleId) {
    const stars = document.querySelectorAll('input[name="rating"]');
    const msg = document.getElementById('rating-msg');
    const storageKey = ating_;

    const savedRating = localStorage.getItem(storageKey);
    if (savedRating) {
        const starInput = document.getElementById(star);
        if (starInput) starInput.checked = true;
        msg.style.opacity = '1';
        msg.innerHTML = "You have already rated this article.";
    }

    stars.forEach(star => {
        star.addEventListener('change', (e) => {
            const val = e.target.value;
            localStorage.setItem(storageKey, val);
            msg.style.opacity = '1';
            msg.innerHTML = [?] Rating of  stars saved to local databank. Thank you!;
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
    
    // Create Neural Network Particles
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 200; // Less particles but connected
    const posArray = new Float32Array(particlesCount * 3);
    
    for(let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 12; // Spread
    }
    
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    
    const material = new THREE.PointsMaterial({
        size: 0.03,
        color: 0x00f0ff,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });
    
    const particlesMesh = new THREE.Points(particlesGeometry, material);
    scene.add(particlesMesh);
    
    // Add Lines (Neural connections)
    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x00ff66,
        transparent: true,
        opacity: 0.15
    });
    
    // Create lines connecting close particles
    const lineGeometry = new THREE.BufferGeometry();
    const linePositions = [];
    
    for(let i = 0; i < particlesCount; i++) {
        for(let j = i + 1; j < particlesCount; j++) {
            const dx = posArray[i*3] - posArray[j*3];
            const dy = posArray[i*3+1] - posArray[j*3+1];
            const dz = posArray[i*3+2] - posArray[j*3+2];
            const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
            
            if(dist < 1.5) {
                linePositions.push(
                    posArray[i*3], posArray[i*3+1], posArray[i*3+2],
                    posArray[j*3], posArray[j*3+1], posArray[j*3+2]
                );
            }
        }
    }
    
    lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
    const linesMesh = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(linesMesh);

    camera.position.z = 4;
    
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
        
        particlesMesh.rotation.y = elapsedTime * 0.03;
        particlesMesh.rotation.x = elapsedTime * 0.01;
        linesMesh.rotation.y = elapsedTime * 0.03;
        linesMesh.rotation.x = elapsedTime * 0.01;
        
        camera.position.x += (mouseX * 1.5 - camera.position.x) * 0.05;
        camera.position.y += (-mouseY * 1.5 - camera.position.y) * 0.05;
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
            f.write(html_v3)
        with open(os.path.join(base, 'article.js'), 'w', encoding='utf-8') as f:
            f.write(js_v3)
