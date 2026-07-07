
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
