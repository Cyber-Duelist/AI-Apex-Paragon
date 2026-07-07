document.addEventListener('DOMContentLoaded', async () => {
    // 1. Initialize Neural Network 3D Background
    initThreeJS();

    const urlParams = new URLSearchParams(window.location.search);
    const articleId = window.location.hash ? window.location.hash.substring(1) : urlParams.get('id');
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
        const response = await fetch('articles/' + articleId + '.md');
        if (!response.ok) throw new Error('Failed to load article: ' + response.statusText);
        
        const markdownText = await response.text();
        
        // Calculate Read Time
        const wordCount = markdownText.trim().split(/\s+/).length;
        const readTime = Math.max(1, Math.ceil(wordCount / 200));
        readTimeSpan.innerHTML = '<i class="fas fa-clock"></i> ' + readTime + ' min read';
        
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
        contentDiv.innerHTML = '<h1>System Error</h1><p>Could not load the requested document.</p><p style="font-family: monospace; color: #ff3366;">' + error.message + '</p>';
    }
});

function setupRatings(articleId) {
    const stars = document.querySelectorAll('input[name="rating"]');
    const msg = document.getElementById('rating-msg');
    
    // Check if already rated
    const savedRating = localStorage.getItem('article_rating_' + articleId);
    if (savedRating) {
        const radio = document.getElementById('star' + savedRating);
        if (radio) radio.checked = true;
    }

    stars.forEach(star => {
        star.addEventListener('change', (e) => {
            const val = e.target.value;
            localStorage.setItem('article_rating_' + articleId, val);
            msg.style.display = 'block';
            msg.style.opacity = '1';
            setTimeout(() => { msg.style.opacity = '0'; setTimeout(() => msg.style.display = 'none', 500); }, 3000);
        });
    });
}

function initThreeJS() {
    if (typeof THREE === 'undefined') return;
    const canvas = document.getElementById('article-canvas');
    if (!canvas) return;

    const scene = new THREE.Scene();
    // Use the deep void background color variable if possible, otherwise solid hex
    scene.background = new THREE.Color('#030305');
    
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Neural Network Parameters
    const particlesCount = window.innerWidth < 768 ? 60 : 120;
    const maxDistance = 3.5;
    
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particlesCount * 3);
    const velocities = [];

    for(let i = 0; i < particlesCount * 3; i+=3) {
        positions[i] = (Math.random() - 0.5) * 20;     // x
        positions[i+1] = (Math.random() - 0.5) * 20;   // y
        positions[i+2] = (Math.random() - 0.5) * 15;   // z
        
        velocities.push({
            x: (Math.random() - 0.5) * 0.02,
            y: (Math.random() - 0.5) * 0.02,
            z: (Math.random() - 0.5) * 0.02
        });
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    // Glowing cyan/green material for nodes
    const material = new THREE.PointsMaterial({
        size: 0.15,
        color: 0x00f0ff,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });
    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Create lines connecting close particles
    const lineGeometry = new THREE.BufferGeometry();
    const linePositions = [];
    
    for(let i = 0; i < particlesCount; i++) {
        for(let j = i + 1; j < particlesCount; j++) {
            linePositions.push(
                positions[i*3], positions[i*3+1], positions[i*3+2],
                positions[j*3], positions[j*3+1], positions[j*3+2]
            );
        }
    }
    
    lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x00f0ff,
        transparent: true,
        opacity: 0.0,
        blending: THREE.AdditiveBlending
    });
    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(lines);

    camera.position.z = 8;

    let mouseX = 0;
    let mouseY = 0;
    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
    });

    const clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        const positions = particles.geometry.attributes.position.array;
        
        // Update positions based on velocity
        for(let i = 0; i < particlesCount; i++) {
            positions[i*3] += velocities[i].x;
            positions[i*3+1] += velocities[i].y;
            positions[i*3+2] += velocities[i].z;
            
            // Bounce off boundaries
            if(Math.abs(positions[i*3]) > 10) velocities[i].x *= -1;
            if(Math.abs(positions[i*3+1]) > 10) velocities[i].y *= -1;
            if(Math.abs(positions[i*3+2]) > 7.5) velocities[i].z *= -1;
        }
        particles.geometry.attributes.position.needsUpdate = true;
        
        // Update lines based on distance
        const linePos = lines.geometry.attributes.position.array;
        const lineColors = [];
        let lineIndex = 0;
        
        for(let i = 0; i < particlesCount; i++) {
            for(let j = i + 1; j < particlesCount; j++) {
                const dx = positions[i*3] - positions[j*3];
                const dy = positions[i*3+1] - positions[j*3+1];
                const dz = positions[i*3+2] - positions[j*3+2];
                const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
                
                linePos[lineIndex*6] = positions[i*3];
                linePos[lineIndex*6+1] = positions[i*3+1];
                linePos[lineIndex*6+2] = positions[i*3+2];
                linePos[lineIndex*6+3] = positions[j*3];
                linePos[lineIndex*6+4] = positions[j*3+1];
                linePos[lineIndex*6+5] = positions[j*3+2];
                
                let alpha = 0;
                if(dist < maxDistance) {
                    alpha = 1.0 - (dist / maxDistance);
                }
                
                lineColors.push(0, 0.94, 1, alpha); // Cyan with alpha
                lineColors.push(0, 0.94, 1, alpha);
                
                lineIndex++;
            }
        }
        
        lines.geometry.attributes.position.needsUpdate = true;
        lines.geometry.setAttribute('color', new THREE.Float32BufferAttribute(lineColors, 4));
        lines.material.vertexColors = true;

        // Subtle camera movement reacting to mouse
        camera.position.x += (mouseX * 2 - camera.position.x) * 0.05;
        camera.position.y += (mouseY * 2 - camera.position.y) * 0.05;
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
