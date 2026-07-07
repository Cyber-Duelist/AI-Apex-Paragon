
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
    const storageKey = 
ating_;

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
