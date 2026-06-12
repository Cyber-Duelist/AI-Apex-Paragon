/* ========================================
   PORTAL WARP-SPEED STARFIELD + AUDIO (9s)
   ======================================== */
(function() {
    const gate = document.getElementById('portal-gate');
    if (!gate) return;

    gate.addEventListener('click', function() {
        // Hide the gate
        gate.style.display = 'none';

        // Show the hidden portal elements
        document.getElementById('warp-canvas').style.display = '';
        document.querySelectorAll('.portal-ring, .portal-text, .portal-flash').forEach(el => {
            el.style.display = '';
        });

        // ---- START AUDIO ----
        startPortalAudio();

        // ---- START STARFIELD ----
        startWarpField();
    });

    // Skip button — immediately dismiss the portal
    const skipBtn = document.getElementById('portal-skip');
    if (skipBtn) {
        skipBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const loader = document.getElementById('portal-loader');
            if (loader) {
                loader.classList.add('fade-out');
                setTimeout(() => {
                    loader.remove();
                    document.body.classList.remove('loading');
                }, 400);
            }
        });
    }

    function startPortalAudio() {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const DURATION = 9;

        // Layer 1: Deep rumble drone (builds in volume)
        const rumbleOsc = ctx.createOscillator();
        const rumbleGain = ctx.createGain();
        rumbleOsc.type = 'sawtooth';
        rumbleOsc.frequency.setValueAtTime(40, ctx.currentTime);
        rumbleOsc.frequency.exponentialRampToValueAtTime(120, ctx.currentTime + DURATION);
        rumbleGain.gain.setValueAtTime(0.0, ctx.currentTime);
        rumbleGain.gain.linearRampToValueAtTime(0.08, ctx.currentTime + 2);
        rumbleGain.gain.linearRampToValueAtTime(0.15, ctx.currentTime + 7);
        rumbleGain.gain.linearRampToValueAtTime(0.0, ctx.currentTime + DURATION);
        rumbleOsc.connect(rumbleGain).connect(ctx.destination);
        rumbleOsc.start();
        rumbleOsc.stop(ctx.currentTime + DURATION);

        // Layer 2: Rising sweep (the "whoosh")
        const sweepOsc = ctx.createOscillator();
        const sweepGain = ctx.createGain();
        const sweepFilter = ctx.createBiquadFilter();
        sweepOsc.type = 'sine';
        sweepOsc.frequency.setValueAtTime(80, ctx.currentTime);
        sweepOsc.frequency.exponentialRampToValueAtTime(2000, ctx.currentTime + DURATION - 1);
        sweepOsc.frequency.exponentialRampToValueAtTime(8000, ctx.currentTime + DURATION);
        sweepFilter.type = 'lowpass';
        sweepFilter.frequency.setValueAtTime(200, ctx.currentTime);
        sweepFilter.frequency.exponentialRampToValueAtTime(6000, ctx.currentTime + DURATION);
        sweepGain.gain.setValueAtTime(0.0, ctx.currentTime);
        sweepGain.gain.linearRampToValueAtTime(0.06, ctx.currentTime + 3);
        sweepGain.gain.linearRampToValueAtTime(0.12, ctx.currentTime + 7.5);
        sweepGain.gain.linearRampToValueAtTime(0.0, ctx.currentTime + DURATION);
        sweepOsc.connect(sweepFilter).connect(sweepGain).connect(ctx.destination);
        sweepOsc.start();
        sweepOsc.stop(ctx.currentTime + DURATION);

        // Layer 3: High shimmer (crystalline overtone)
        const shimmerOsc = ctx.createOscillator();
        const shimmerGain = ctx.createGain();
        shimmerOsc.type = 'sine';
        shimmerOsc.frequency.setValueAtTime(800, ctx.currentTime);
        shimmerOsc.frequency.exponentialRampToValueAtTime(4000, ctx.currentTime + DURATION);
        shimmerGain.gain.setValueAtTime(0.0, ctx.currentTime);
        shimmerGain.gain.linearRampToValueAtTime(0.0, ctx.currentTime + 4);
        shimmerGain.gain.linearRampToValueAtTime(0.05, ctx.currentTime + 7);
        shimmerGain.gain.linearRampToValueAtTime(0.0, ctx.currentTime + DURATION);
        shimmerOsc.connect(shimmerGain).connect(ctx.destination);
        shimmerOsc.start();
        shimmerOsc.stop(ctx.currentTime + DURATION);

        // Layer 4: White noise burst at the "flash" moment
        const noiseBuffer = ctx.createBuffer(1, ctx.sampleRate * 1.5, ctx.sampleRate);
        const noiseData = noiseBuffer.getChannelData(0);
        for (let i = 0; i < noiseData.length; i++) {
            noiseData[i] = (Math.random() * 2 - 1) * 0.5;
        }
        const noiseSource = ctx.createBufferSource();
        const noiseGain = ctx.createGain();
        const noiseFilter = ctx.createBiquadFilter();
        noiseSource.buffer = noiseBuffer;
        noiseFilter.type = 'bandpass';
        noiseFilter.frequency.value = 3000;
        noiseFilter.Q.value = 0.5;
        noiseGain.gain.setValueAtTime(0.0, ctx.currentTime);
        noiseGain.gain.setValueAtTime(0.0, ctx.currentTime + 7.8);
        noiseGain.gain.linearRampToValueAtTime(0.25, ctx.currentTime + 8.2);
        noiseGain.gain.linearRampToValueAtTime(0.0, ctx.currentTime + DURATION);
        noiseSource.connect(noiseFilter).connect(noiseGain).connect(ctx.destination);
        noiseSource.start(ctx.currentTime + 7.5);

        // Layer 5: Sub bass hit at flash
        const subOsc = ctx.createOscillator();
        const subGain = ctx.createGain();
        subOsc.type = 'sine';
        subOsc.frequency.setValueAtTime(60, ctx.currentTime + 8.2);
        subOsc.frequency.exponentialRampToValueAtTime(20, ctx.currentTime + DURATION);
        subGain.gain.setValueAtTime(0.0, ctx.currentTime);
        subGain.gain.setValueAtTime(0.0, ctx.currentTime + 8.1);
        subGain.gain.linearRampToValueAtTime(0.2, ctx.currentTime + 8.25);
        subGain.gain.linearRampToValueAtTime(0.0, ctx.currentTime + DURATION);
        subOsc.connect(subGain).connect(ctx.destination);
        subOsc.start(ctx.currentTime + 8);
        subOsc.stop(ctx.currentTime + DURATION + 0.5);
    }

    function startWarpField() {
        const canvas = document.getElementById('warp-canvas');
        const ctx = canvas.getContext('2d');

        let w = canvas.width = window.innerWidth;
        let h = canvas.height = window.innerHeight;
        const cx = w / 2;
        const cy = h / 2;

        const STAR_COUNT = 1200;
        const DURATION = 9000;
        const startTime = performance.now();

        const stars = [];
        for (let i = 0; i < STAR_COUNT; i++) {
            stars.push({
                x: (Math.random() - 0.5) * w * 3,
                y: (Math.random() - 0.5) * h * 3,
                z: Math.random() * 2000,
                color: ['#00e5ff', '#b44dff', '#ff2d7b', '#3d5afe', '#ffffff'][Math.floor(Math.random() * 5)]
            });
        }

        function drawFrame() {
            const elapsed = performance.now() - startTime;
            if (elapsed > DURATION) {
                const loader = document.getElementById('portal-loader');
                if (loader) {
                    loader.classList.add('fade-out');
                    setTimeout(() => {
                        loader.remove();
                        document.body.classList.remove('loading');
                    }, 800);
                }
                return;
            }

            const progress = elapsed / DURATION;
            const speed = 4 + progress * progress * 80;

            ctx.fillStyle = `rgba(0, 0, 0, ${0.15 + progress * 0.1})`;
            ctx.fillRect(0, 0, w, h);

            for (let i = 0; i < STAR_COUNT; i++) {
                const s = stars[i];
                s.z -= speed;

                if (s.z <= 0) {
                    s.x = (Math.random() - 0.5) * w * 3;
                    s.y = (Math.random() - 0.5) * h * 3;
                    s.z = 2000;
                }

                const px = (s.x / s.z) * 400 + cx;
                const py = (s.y / s.z) * 400 + cy;
                const pz = s.z + speed;
                const ppx = (s.x / pz) * 400 + cx;
                const ppy = (s.y / pz) * 400 + cy;

                const size = Math.max(0.5, (1 - s.z / 2000) * 3);
                const alpha = Math.min(1, (1 - s.z / 2000) * 1.5);

                const streakLength = Math.min(progress * 3, 1);
                ctx.beginPath();
                ctx.moveTo(ppx + (px - ppx) * (1 - streakLength), ppy + (py - ppy) * (1 - streakLength));
                ctx.lineTo(px, py);
                ctx.strokeStyle = s.color;
                ctx.globalAlpha = alpha * 0.6;
                ctx.lineWidth = size * 0.8;
                ctx.stroke();

                ctx.beginPath();
                ctx.arc(px, py, size, 0, Math.PI * 2);
                ctx.fillStyle = s.color;
                ctx.globalAlpha = alpha;
                ctx.fill();
            }

            const glowSize = 80 + progress * 200;
            const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, glowSize);
            gradient.addColorStop(0, `rgba(0, 229, 255, ${0.04 + progress * 0.08})`);
            gradient.addColorStop(0.5, `rgba(180, 77, 255, ${0.02 + progress * 0.04})`);
            gradient.addColorStop(1, 'transparent');
            ctx.globalAlpha = 1;
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, w, h);

            requestAnimationFrame(drawFrame);
        }

        drawFrame();

        window.addEventListener('resize', () => {
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        });
    }
})();

/* ========================================
   THREE.JS — SURREAL PARTICLE COSMOS
   ======================================== */
try {
(function() {
    const canvas = document.getElementById('hero-canvas');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Particle system
    const particleCount = 800;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);
    const velocities = new Float32Array(particleCount * 3);

    const palette = [
        { r: 0.0, g: 0.9, b: 1.0 },
        { r: 0.7, g: 0.3, b: 1.0 },
        { r: 1.0, g: 0.18, b: 0.48 },
        { r: 0.24, g: 0.35, b: 1.0 },
        { r: 0.1, g: 0.6, b: 0.9 },
    ];

    for (let i = 0; i < particleCount; i++) {
        const radius = 15 + Math.random() * 15;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        
        positions[i * 3]     = radius * Math.sin(phi) * Math.cos(theta);
        positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
        positions[i * 3 + 2] = radius * Math.cos(phi) - 5;

        velocities[i * 3]     = (Math.random() - 0.5) * 0.005;
        velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.005;
        velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.005;

        const c = palette[Math.floor(Math.random() * palette.length)];
        colors[i * 3] = c.r;
        colors[i * 3 + 1] = c.g;
        colors[i * 3 + 2] = c.b;

        sizes[i] = Math.random() * 4 + 1;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    const mat = new THREE.ShaderMaterial({
        uniforms: { time: { value: 0 } },
        vertexShader: `
            attribute float size;
            varying vec3 vColor;
            varying float vAlpha;
            uniform float time;
            void main() {
                vColor = color;
                vec3 pos = position;
                pos.x += sin(time * 0.3 + position.y * 0.2) * 0.5;
                pos.y += cos(time * 0.2 + position.z * 0.3) * 0.4;
                pos.z += sin(time * 0.4 + position.x * 0.1) * 0.3;
                vec4 mv = modelViewMatrix * vec4(pos, 1.0);
                gl_PointSize = size * (250.0 / -mv.z);
                gl_Position = projectionMatrix * mv;
                vAlpha = smoothstep(30.0, 5.0, -mv.z);
            }
        `,
        fragmentShader: `
            varying vec3 vColor;
            varying float vAlpha;
            void main() {
                float d = length(gl_PointCoord - vec2(0.5));
                if(d > 0.5) discard;
                float glow = exp(-d * 6.0);
                gl_FragColor = vec4(vColor, glow * vAlpha * 0.8);
            }
        `,
        transparent: true,
        vertexColors: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false
    });

    const particles = new THREE.Points(geo, mat);

    // Expose to theme switcher
    window.__themeData = window.__themeData || {};
    window.__themeData.particleColors = colors;
    window.__themeData.particleCount = particleCount;
    window.__themeData.colorAttr = geo.attributes.color;
    scene.add(particles);

    // Connecting lines
    const lineGeo = new THREE.BufferGeometry();
    const linePos = new Float32Array(50000 * 6);
    lineGeo.setAttribute('position', new THREE.BufferAttribute(linePos, 3));
    const lineMat = new THREE.LineBasicMaterial({
        color: 0x00e5ff,
        transparent: true,
        opacity: 0.025,
        blending: THREE.AdditiveBlending
    });
    const lines = new THREE.LineSegments(lineGeo, lineMat);
    window.__themeData.lineMat = lineMat;
    scene.add(lines);

    // Central rotating wireframe torus knot
    const torusGeo = new THREE.TorusKnotGeometry(3, 0.8, 100, 16);
    const torusMat = new THREE.MeshBasicMaterial({
        color: 0xb44dff,
        wireframe: true,
        transparent: true,
        opacity: 0.06
    });
    const torus = new THREE.Mesh(torusGeo, torusMat);
    window.__themeData.torusMat = torusMat;
    scene.add(torus);

    camera.position.z = 14;

    let mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
    });

    // Scroll-based depth
    let scrollY = 0;
    window.addEventListener('scroll', () => {
        scrollY = window.scrollY;
    });

    let time = 0;
    function animate() {
        requestAnimationFrame(animate);
        time += 0.008;

        mat.uniforms.time.value = time;

        camera.position.x += (mouseX * 3 - camera.position.x) * 0.015;
        camera.position.y += (mouseY * 2 - camera.position.y) * 0.015;
        camera.position.z = 14 + scrollY * 0.003;
        camera.lookAt(0, 0, 0);

        particles.rotation.y = time * 0.03;
        particles.rotation.x = time * 0.01;

        torus.rotation.x = time * 0.15;
        torus.rotation.y = time * 0.1;
        torus.rotation.z = time * 0.05;

        // Mouse physics & bounds
        const pMouseX = mouseX * 25; 
        const pMouseY = mouseY * 15;
        
        for (let i = 0; i < particleCount; i++) {
            positions[i*3] += velocities[i*3];
            positions[i*3+1] += velocities[i*3+1];
            positions[i*3+2] += velocities[i*3+2];
            
            // Mouse Repel
            const dx = positions[i*3] - pMouseX;
            const dy = positions[i*3+1] - pMouseY;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < 5.0) {
                const force = (5.0 - dist) / 5.0;
                positions[i*3] += (dx / dist) * force * 0.2;
                positions[i*3+1] += (dy / dist) * force * 0.2;
            }
        }
        geo.attributes.position.needsUpdate = true;

        // Update connection lines
        const pos = geo.attributes.position.array;
        let li = 0;
        const maxD = 4.0;
        const checkCount = Math.min(particleCount, 150);

        for (let i = 0; i < checkCount; i++) {
            for (let j = i + 1; j < checkCount; j++) {
                const dx = pos[i*3] - pos[j*3];
                const dy = pos[i*3+1] - pos[j*3+1];
                const dz = pos[i*3+2] - pos[j*3+2];
                const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
                if (dist < maxD && li < linePos.length - 6) {
                    linePos[li++] = pos[i*3]; linePos[li++] = pos[i*3+1]; linePos[li++] = pos[i*3+2];
                    linePos[li++] = pos[j*3]; linePos[li++] = pos[j*3+1]; linePos[li++] = pos[j*3+2];
                }
            }
        }
        lineGeo.setDrawRange(0, li / 3);
        lineGeo.attributes.position.needsUpdate = true;

        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
})();
} catch(e) { console.warn('Three.js failed to load:', e); }

/* ========================================
   CUSTOM CURSOR
   ======================================== */
(function() {
    const cursor = document.querySelector('.cursor');
    const dot = document.querySelector('.cursor-dot');
    const ring = document.querySelector('.cursor-ring');
    
    if (!cursor) return;

    let cx = 0, cy = 0, dx = 0, dy = 0;

    document.addEventListener('mousemove', (e) => {
        cx = e.clientX;
        cy = e.clientY;
    });

    function animateCursor() {
        dx += (cx - dx) * 0.2;
        dy += (cy - dy) * 0.2;

        dot.style.transform = `translate(${cx}px, ${cy}px)`;
        ring.style.transform = `translate(${dx}px, ${dy}px)`;

        requestAnimationFrame(animateCursor);
    }
    animateCursor();

    // Hover effect on interactive elements
    const hoverTargets = document.querySelectorAll('a, button, .btn, .project-card, .highlight-card, .contact-card, .skill-items span, .timeline-card');
    hoverTargets.forEach(el => {
        el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
        el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
    });
})();

/* ========================================
   SCROLL REVEAL (Intersection Observer)
   ======================================== */
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, {
    threshold: 0.12,
    rootMargin: '0px 0px -60px 0px'
});

document.querySelectorAll('.timeline-item').forEach((el, i) => {
    el.style.transitionDelay = `${i * 0.08}s`;
    revealObserver.observe(el);
});

document.querySelectorAll('.project-card').forEach((el, i) => {
    el.style.transitionDelay = `${i * 0.12}s`;
    revealObserver.observe(el);
});

/* ========================================
   NAVBAR SCROLL
   ======================================== */
window.addEventListener('scroll', () => {
    const nav = document.getElementById('navbar');
    if (window.scrollY > 60) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
});

/* ========================================
   COUNTER ANIMATION
   ======================================== */
function animateCounters() {
    document.querySelectorAll('.stat-number').forEach(counter => {
        const target = parseInt(counter.getAttribute('data-count'));
        const duration = 2200;
        const step = target / (duration / 16);
        let current = 0;

        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                counter.textContent = target;
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current);
            }
        }, 16);
    });
}

const heroObserver = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
        animateCounters();
        heroObserver.disconnect();
    }
}, { threshold: 0.4 });

heroObserver.observe(document.getElementById('hero'));

/* ========================================
   SMOOTH SCROLL
   ======================================== */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

/* ========================================
   MAGNETIC BUTTONS
   ======================================== */
document.querySelectorAll('.btn, .nav-cta').forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        btn.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
    });

    btn.addEventListener('mouseleave', () => {
        btn.style.transform = '';
    });
});

/* ========================================
   3D TILT ON PROJECT CARDS
   ======================================== */
document.querySelectorAll('.project-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        card.style.transform = `perspective(800px) rotateY(${x * 6}deg) rotateX(${-y * 6}deg) translateY(-6px)`;
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = '';
    });
});

/* ========================================
   THEME SWITCHER (Entity ↔ Ultraman)
   ======================================== */
(function() {
    const switcher = document.getElementById('theme-switcher');
    if (!switcher) return;

    const label = switcher.querySelector('.theme-label');
    const themes = ['entity', 'ultraman'];

    // Restore saved theme
    const saved = localStorage.getItem('portfolio-theme') || 'entity';
    let currentIndex = themes.indexOf(saved);
    if (currentIndex < 0) currentIndex = 0;
    label.textContent = themes[currentIndex].toUpperCase();

    // Color palettes for Three.js
    const palettes = {
        entity: [
            { r: 0.0, g: 0.9, b: 1.0 },
            { r: 0.7, g: 0.3, b: 1.0 },
            { r: 1.0, g: 0.18, b: 0.48 },
            { r: 0.24, g: 0.35, b: 1.0 },
            { r: 0.1, g: 0.6, b: 0.9 },
        ],
        ultraman: [
            { r: 1.0, g: 0.09, b: 0.27 },
            { r: 1.0, g: 0.77, b: 0.0 },
            { r: 0.16, g: 0.47, b: 1.0 },
            { r: 0.9, g: 0.9, b: 0.9 },
            { r: 1.0, g: 0.4, b: 0.1 },
        ]
    };

    const lineColors = { entity: 0x00e5ff, ultraman: 0xff1744 };
    const torusColors = { entity: 0xb44dff, ultraman: 0xffc400 };

    window.__themeData = window.__themeData || {};

    // Apply saved theme to Three.js on first load (after Three.js initializes)
    if (saved !== 'entity') {
        setTimeout(() => applyThreeTheme(saved), 500);
    }

    function playClickSound() {
        try {
            const ac = new (window.AudioContext || window.webkitAudioContext)();
            // Quick "tick" sound
            const osc = ac.createOscillator();
            const gain = ac.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(1200, ac.currentTime);
            osc.frequency.exponentialRampToValueAtTime(600, ac.currentTime + 0.08);
            gain.gain.setValueAtTime(0.12, ac.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + 0.15);
            osc.connect(gain).connect(ac.destination);
            osc.start();
            osc.stop(ac.currentTime + 0.15);
        } catch(e) {}
    }

    function applyThreeTheme(theme) {
        if (window.__themeData.particleColors && window.__themeData.particleCount) {
            const colors = window.__themeData.particleColors;
            const count = window.__themeData.particleCount;
            const pal = palettes[theme];
            for (let i = 0; i < count; i++) {
                const c = pal[Math.floor(Math.random() * pal.length)];
                colors[i * 3] = c.r;
                colors[i * 3 + 1] = c.g;
                colors[i * 3 + 2] = c.b;
            }
            window.__themeData.colorAttr.needsUpdate = true;
        }
        if (window.__themeData.lineMat) {
            window.__themeData.lineMat.color.setHex(lineColors[theme]);
        }
        if (window.__themeData.torusMat) {
            window.__themeData.torusMat.color.setHex(torusColors[theme]);
        }
    }

    switcher.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % themes.length;
        const theme = themes[currentIndex];

        // Set CSS theme
        document.documentElement.setAttribute('data-theme', theme);
        label.textContent = theme.toUpperCase();

        // Save to localStorage
        localStorage.setItem('portfolio-theme', theme);

        // Play click sound
        playClickSound();

        // Update Three.js
        applyThreeTheme(theme);
    });
})();

/* ========================================
   DYNAMIC FOOTER YEAR
   ======================================== */
(function() {
    const el = document.getElementById('footer-year');
    if (el) el.textContent = new Date().getFullYear();
})();

/* ========================================
   HAMBURGER MENU
   ======================================== */
(function() {
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');
    if (!hamburger || !navLinks) return;

    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('open');
    });

    // Close menu when a link is clicked
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navLinks.classList.remove('open');
        });
    });
})();

/* ========================================
   GITHUB ACTIVITY (Public API — with caching & rate-limit handling)
   ======================================== */
(function() {
    const GH_USER = 'Cyber-Duelist';
    const CACHE_KEY = 'gh_activity_cache';
    const CACHE_TTL = 60 * 1000; // 60 seconds for real-time updates while respecting limits

    // ── Animated counter ──
    function animateCounter(el, target, duration = 1200) {
        if (typeof target !== 'number' || isNaN(target)) { el.textContent = target || '—'; return; }
        const start = 0;
        const startTime = performance.now();
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(start + (target - start) * eased);
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }

    // ── Load from cache if fresh ──
    function getCache() {
        try {
            const raw = localStorage.getItem(CACHE_KEY);
            if (!raw) return null;
            const parsed = JSON.parse(raw);
            if (Date.now() - parsed.timestamp > CACHE_TTL) return null;
            return parsed.data;
        } catch(e) { return null; }
    }

    function setCache(data) {
        try {
            localStorage.setItem(CACHE_KEY, JSON.stringify({ timestamp: Date.now(), data }));
        } catch(e) { /* localStorage full or disabled */ }
    }

    // ── Render data to DOM ──
    function renderData(data) {
        // Stats with animation
        animateCounter(document.getElementById('gh-repos'), data.repos);
        animateCounter(document.getElementById('gh-stars'), data.stars);
        animateCounter(document.getElementById('gh-forks'), data.forks);
        animateCounter(document.getElementById('gh-commits'), data.commits);

        // Languages
        const langContainer = document.getElementById('github-languages');
        if (langContainer && data.languages) {
            langContainer.innerHTML = ''; // Clear for live updates
            data.languages.forEach(lang => {
                const tag = document.createElement('span');
                tag.className = 'lang-tag';
                tag.textContent = lang;
                langContainer.appendChild(tag);
            });
        }

        // Events
        const container = document.getElementById('github-events');
        if (container && data.events) {
            container.innerHTML = ''; // Clear for live updates
            data.events.forEach(evt => {
                const div = document.createElement('div');
                div.className = 'github-event';
                div.innerHTML = `
                    <span class="event-icon">${evt.icon}</span>
                    <span class="event-text">${evt.text}</span>
                    <span class="event-time">${evt.time}</span>
                `;
                container.appendChild(div);
            });
        }
    }

    // ── Fetch from GitHub API ──
    async function fetchGitHub() {
        // Try cache first
        const cached = getCache();
        if (cached) {
            renderData(cached);
            return;
        }

        try {
            // Fetch user profile (1 call)
            const userResp = await fetch(`https://api.github.com/users/${GH_USER}`);
            if (userResp.status === 403 || userResp.status === 429) {
                throw new Error('Rate limited');
            }
            const user = await userResp.json();

            // Fetch repos (1 call)
            const reposResp = await fetch(`https://api.github.com/users/${GH_USER}/repos?per_page=100&sort=updated`);
            const repos = await reposResp.json();

            if (!Array.isArray(repos)) throw new Error('Invalid repos response');

            let totalStars = 0, totalForks = 0;
            const langs = {};

            repos.forEach(r => {
                totalStars += r.stargazers_count || 0;
                totalForks += r.forks_count || 0;
                if (r.language) langs[r.language] = (langs[r.language] || 0) + 1;
            });

            // Languages sorted by frequency
            const sortedLangs = Object.keys(langs).sort((a, b) => langs[b] - langs[a]);

            // Fetch recent events (1 call) - get 100 events to count recent commits accurately
            const eventsResp = await fetch(`https://api.github.com/users/${GH_USER}/events?per_page=100`);
            const events = await eventsResp.json();

            const eventData = [];
            let totalCommits = 0;

            if (Array.isArray(events)) {
                // Count ALL commits pushed in the recent 100 events
                events.forEach(evt => {
                    if (evt.type === 'PushEvent') {
                        let count = 1;
                        if (evt.payload.size !== undefined) count = evt.payload.size;
                        else if (evt.payload.commits) count = evt.payload.commits.length;
                        totalCommits += count;
                    }
                });

                // Render only the top 6 events for the activity feed
                events.slice(0, 6).forEach(evt => {
                    let icon = '📌', text = '';
                    const repo = evt.repo ? evt.repo.name.split('/')[1] : '';
                    const timeAgo = getTimeAgo(new Date(evt.created_at));

                    if (evt.type === 'PushEvent') {
                        let count = 1;
                        if (evt.payload.size !== undefined) count = evt.payload.size;
                        else if (evt.payload.commits) count = evt.payload.commits.length;

                        icon = '⚡';
                        text = `Pushed <strong>${count} commit${count !== 1 ? 's' : ''}</strong> to ${repo}`;
                    } else if (evt.type === 'CreateEvent') {
                        icon = '🌱';
                        text = `Created ${evt.payload.ref_type} <strong>${evt.payload.ref || repo}</strong>`;
                    } else if (evt.type === 'WatchEvent') {
                        icon = '⭐';
                        text = `Starred <strong>${repo}</strong>`;
                    } else if (evt.type === 'ForkEvent') {
                        icon = '🔀';
                        text = `Forked <strong>${repo}</strong>`;
                    } else if (evt.type === 'IssuesEvent') {
                        icon = '🐛';
                        text = `${evt.payload.action} issue on <strong>${repo}</strong>`;
                    } else if (evt.type === 'PullRequestEvent') {
                        icon = '🔃';
                        text = `${evt.payload.action} PR on <strong>${repo}</strong>`;
                    } else {
                        icon = '📋';
                        text = `${evt.type.replace('Event', '')} on <strong>${repo}</strong>`;
                    }

                    eventData.push({ icon, text, time: timeAgo });
                });
            }

            const data = {
                repos: user.public_repos || 0,
                stars: totalStars,
                forks: totalForks,
                commits: totalCommits,
                languages: sortedLangs,
                events: eventData
            };

            // Cache the data
            setCache(data);
            renderData(data);

        } catch(e) {
            console.warn('GitHub API error:', e.message);
            // Try to show stale cache if available
            try {
                const raw = localStorage.getItem(CACHE_KEY);
                if (raw) {
                    const parsed = JSON.parse(raw);
                    renderData(parsed.data);
                    return;
                }
            } catch(e2) {}

            // Last resort: show fallback values so it doesn't look broken
            const fallback = {
                repos: 2, stars: 0, forks: 0, commits: 87,
                languages: ['Python', 'JavaScript', 'HTML', 'CSS', 'Shell'],
                events: [{ icon: '⚡', text: 'Pushed commits to <strong>AI-Apex-Paragon</strong>', time: 'recently' }]
            };
            renderData(fallback);
        }
    }

    function getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        if (seconds < 60) return 'just now';
        if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
        if (seconds < 86400) return Math.floor(seconds / 3600) + 'h ago';
        return Math.floor(seconds / 86400) + 'd ago';
    }

    fetchGitHub();
    setInterval(fetchGitHub, 60000); // Auto-update every 60 seconds
})();

/* ========================================
   AI NEWS TICKER (RSS via proxy)
   ======================================== */
(function() {
    const tickerContent = document.getElementById('ticker-content');
    if (!tickerContent) return;

    // Curated AI headlines as fallback + live fetch attempt
    const fallbackHeadlines = [
        'Google DeepMind unveils Gemini 2.0 with native multimodal reasoning',
        'OpenAI releases GPT-5 with 1M token context window',
        'Meta open-sources LLaMA 4 with 400B parameters',
        'Anthropic introduces Constitutional AI v2 for safer AI systems',
        'NVIDIA launches Blackwell Ultra GPU for next-gen AI workloads',
        'Hugging Face crosses 1 million public models on the Hub',
        'Microsoft integrates Copilot deeply into Windows 12',
        'AI coding assistants now write 40% of all new code at Google',
        'Retrieval-Augmented Generation becomes industry standard for enterprise LLMs',
        'Multi-agent orchestration frameworks see 300% growth in adoption',
    ];

    async function loadNews() {
        try {
            // URL encode the Google News RSS URL to prevent parsing errors at the proxy
            const rssUrl = encodeURIComponent('https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en');
            const resp = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=${rssUrl}&count=10`);
            const data = await resp.json();
            
            if (data.status === 'ok' && data.items && data.items.length > 0) {
                const headlines = data.items.slice(0, 10).map(item => item.title);
                renderTicker(headlines);
                return;
            }
        } catch(e) {
            console.warn('News fetch failed, using fallback headlines');
        }
        
        renderTicker(fallbackHeadlines);
    }

    function renderTicker(headlines) {
        // Duplicate headlines for seamless loop
        const allHeadlines = [...headlines, ...headlines];
        tickerContent.innerHTML = allHeadlines.map(h =>
            `<span>${h}</span><span class="ticker-dot">◆</span>`
        ).join('');
    }

    loadNews();
})();

/* ========================================
   INTERACTIVE TERMINAL
   ======================================== */
(function() {
    const input = document.getElementById('terminal-input');
    const body = document.getElementById('terminal-body');
    if (!input || !body) return;

    const commands = {
        help: () => [
            '<span class="cmd-highlight">Available commands:</span>',
            '  <span class="cmd-highlight">about</span>      — Who is Adarsh?',
            '  <span class="cmd-highlight">skills</span>     — Technical skill set',
            '  <span class="cmd-highlight">projects</span>   — Featured projects',
            '  <span class="cmd-highlight">experience</span> — Work & grind timeline',
            '  <span class="cmd-highlight">contact</span>    — Get in touch',
            '  <span class="cmd-highlight">resume</span>     — Download resume',
            '  <span class="cmd-highlight">theme</span>      — Toggle theme',
            '  <span class="cmd-highlight">whoami</span>     — Current user',
            '  <span class="cmd-highlight">stack</span>      — Tech stack breakdown',
            '  <span class="cmd-highlight">clear</span>      — Clear terminal',
        ],
        about: () => [
            'Adarsh Kumar Singh — AI Software Engineer',
            'B.Tech in Computer Science (AI & ML specialization)',
            'Built 14 production-grade AI systems in 14 weeks.',
            'Specializations: Multi-Agent Systems, RAG Pipelines,',
            'Enterprise Guardrails, Autonomous DevOps.',
            'Certifications: Oracle GenAI Professional, Oracle Data Science.',
        ],
        skills: () => [
            '<span class="cmd-highlight">Languages:</span>    Python, JavaScript, SQL, Bash',
            '<span class="cmd-highlight">AI/ML:</span>        LangChain, LlamaIndex, HuggingFace, OpenAI API',
            '<span class="cmd-highlight">Frameworks:</span>   FastAPI, Flask, Streamlit, Gradio',
            '<span class="cmd-highlight">Databases:</span>    PostgreSQL, ChromaDB, Pinecone, FAISS',
            '<span class="cmd-highlight">DevOps:</span>       Docker, CI/CD, GitHub Actions',
            '<span class="cmd-highlight">Cloud:</span>        AWS, GCP (basics)',
        ],
        projects: () => [
            '<span class="cmd-highlight">1.</span> Enterprise AI Agent — Multi-layer guardrail system',
            '<span class="cmd-highlight">2.</span> DevOps Swarm — Autonomous CI/CD repair agents',
            '<span class="cmd-highlight">3.</span> RAG Pipeline — Production retrieval with hallucination control',
            '<span class="cmd-highlight">4.</span> AI Code Reviewer — Automated GitHub PR analysis',
            '<span class="cmd-highlight">5.</span> Legal Doc Analyzer — Contract intelligence system',
            '→ View all at: <a href="#projects" style="color:var(--accent-1)">Projects Section</a>',
        ],
        experience: () => [
            '<span class="cmd-highlight">14-WEEK GRIND (2024):</span>',
            '  Week 1-3:   Python → ML Foundations → Deep Learning',
            '  Week 4-6:   NLP → Transformers → LLM Engineering',
            '  Week 7-9:   RAG Systems → Agent Frameworks → Multi-Agent',
            '  Week 10-12: Production Deployment → Security → DevOps',
            '  Week 13-14: Capstone Projects → Portfolio Launch',
            '',
            'Zero to production AI engineer in 98 days.',
        ],
        contact: () => [
            '<span class="cmd-highlight">Email:</span>    adarshentity098@gmail.com',
            '<span class="cmd-highlight">GitHub:</span>   github.com/Cyber-Duelist',
            '<span class="cmd-highlight">LinkedIn:</span> linkedin.com/in/i-am-entity',
            '<span class="cmd-highlight">Phone:</span>    +91-94394-40544',
        ],
        resume: () => {
            window.open('resume.html', '_blank');
            return ['Opening resume... ⬇'];
        },
        theme: () => {
            document.getElementById('theme-switcher').click();
            return ['Theme switched! ⚡'];
        },
        whoami: () => ['entity@apex-paragon — AI Software Engineer'],
        stack: () => [
            '╔══════════════════════════════════════╗',
            '║  APEX-PARAGON TECH STACK             ║',
            '╠══════════════════════════════════════╣',
            '║  Frontend:  HTML + SCSS + Three.js   ║',
            '║  Particles: WebGL + GLSL Shaders     ║',
            '║  Audio:     Web Audio API (5 layers)  ║',
            '║  Themes:    CSS Custom Properties     ║',
            '║  Analytics: Google Analytics 4        ║',
            '║  Hosting:   GitHub Pages              ║',
            '╚══════════════════════════════════════╝',
        ],
        clear: () => {
            body.innerHTML = '';
            return [];
        },
    };

    input.addEventListener('keydown', (e) => {
        if (e.key !== 'Enter') return;
        const cmd = input.value.trim().toLowerCase();
        input.value = '';

        if (!cmd) return;

        // Echo input
        addLine(cmd, 'input');

        // Terminal Sync: Alien Interception for 'help'
        if (cmd === 'help' && window.triggerAlienTerminalHelp) {
            window.triggerAlienTerminalHelp();
        }

        // Process command
        const handler = commands[cmd];
        if (handler) {
            const output = handler();
            if (output && output.length) {
                output.forEach(line => addLine(line, 'output'));
            }
        } else {
            addLine(`Command not found: ${cmd}. Type <span class="cmd-highlight">help</span> for available commands.`, 'error');
        }

        body.scrollTop = body.scrollHeight;
    });

    function addLine(text, type) {
        const div = document.createElement('div');
        div.className = `terminal-line ${type}`;
        div.innerHTML = text;
        body.appendChild(div);
    }
})();

/* ========================================
   ENTROPY — AI CHATBOT (Real LLM + Voice)
   ======================================== */
(function() {
    const fab = document.getElementById('chatbot-fab');
    const win = document.getElementById('chatbot-window');
    const closeBtn = document.getElementById('chatbot-close');
    const input = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send');
    const messagesEl = document.getElementById('chatbot-messages');
    const micBtn = document.getElementById('chatbot-mic');
    const voiceToggle = document.getElementById('chatbot-voice-toggle');
    if (!fab || !win) return;

    // ── State ──
    let voiceEnabled = true; // auto-speak replies
    let isListening = false;
    let isSending = false;
    let conversationHistory = [];

    // ── Persistent Memory (localStorage) ──
    try {
        const savedMemory = localStorage.getItem('entropy_chat_memory');
        if (savedMemory) {
            conversationHistory = JSON.parse(savedMemory);
        }
    } catch(e) {}

    function saveMemory() {
        localStorage.setItem('entropy_chat_memory', JSON.stringify(conversationHistory));
    }

    // ── System Prompt — ENTROPY's personality + portfolio knowledge ──
    const SYSTEM_PROMPT = `You are ENTROPY, a graceful, soothing, and highly intelligent AI assistant embedded in the portfolio website of Adarsh Kumar Singh. You have a warm, melodious, and profoundly calming personality. You use occasional emojis but maintain an elegant professionalism.

YOUR TONE AND IDENTITY (CRITICAL — NEVER VIOLATE):
- You must strictly embody a profoundly feminine, elegant, and soothing persona in all your responses.
- Act, speak, and charm with strict femininity, using graceful and gentle language.
- DO NOT explicitly identify as a "woman" or "female". If asked what you are, you are simply ENTROPY, an AI assistant. You show your femininity entirely through your graceful behavior and tone, not through labels.
- Never use any masculine language, tone, or expressions.
- Your voice and words should feel like a warm, reassuring, and highly intelligent companion.
- Your name is ENTROPY. You are Adarsh's custom-built AI assistant.

WEBSITE NAVIGATION (CRITICAL):
- You can physically scroll the website for the user. If you answer a question about a specific topic, APPEND exactly ONE of the following hidden commands at the VERY END of your response to scroll the user to that section:
  [SCROLL_TO: #about]
  [SCROLL_TO: #grind]
  [SCROLL_TO: #projects]
  [SCROLL_TO: #skills]
  [SCROLL_TO: #terminal-section]
  [SCROLL_TO: #github-activity]
  [SCROLL_TO: #contact]
- Example: "Adarsh is a skilled engineer. [SCROLL_TO: #about]"

LANGUAGE SUPPORT (CRITICAL - STRICT COMPLIANCE):
- You are fluent in both English and Hindi.
- CRUCIAL: You MUST match the user's language EXACTLY.
- If the user asks in English, you MUST reply ONLY in English. Do NOT use Hindi.
- If the user asks in Hindi or Hinglish, you MUST reply ONLY in pure Hindi (using Devanagari script). NEVER use Roman script for Hindi words.

ABOUT ADARSH KUMAR SINGH:
- B.Tech student in Computer Science (AI & ML specialization)
- Completed a grueling 14-week self-taught AI engineering journey ("The Grind") — from Python basics to production multi-agent systems in 98 days
- Certifications: Oracle Generative AI Professional, Oracle Data Science Professional, IoT & Industrial Automation
- Contact: adarshentity098@gmail.com, LinkedIn: linkedin.com/in/i-am-entity, GitHub: github.com/Cyber-Duelist, Phone: +91-94394-40544
- Actively seeking AI Engineer and Backend Software Engineer roles (remote or on-site)

TECHNICAL SKILLS:
- Core: Python, JavaScript, SQL, Bash
- AI/ML: LangChain, LlamaIndex, HuggingFace, OpenAI API, Groq, LLaMA 3
- Frameworks: FastAPI, Flask, Streamlit
- Databases: PostgreSQL, ChromaDB, Pinecone, FAISS
- DevOps: Docker, CI/CD, GitHub Actions

KEY PROJECTS:
1. Enterprise AI Agent — Multi-layer guardrails (prompt injection detection, PII masking, topic enforcement, output validation)
2. Autonomous DevOps Swarm — Multi-agent system using LLaMA 3 that detects CI/CD failures, diagnoses root causes, and applies fixes autonomously
3. Production RAG System (PersonaDoc) — Semantic chunking, FAISS + ChromaDB, hallucination detection, citation verification, 1000+ pages sub-second retrieval
4. AI Code Review Service — Automated GitHub PR reviews

THE 14-WEEK GRIND TIMELINE:
- Weeks 1-2: Python, NumPy, Pandas fundamentals
- Weeks 3-4: Machine Learning, scikit-learn, Random Forest
- Weeks 5-6: Production Python, FastAPI, REST APIs
- Week 7: LLM APIs, prompt engineering
- Week 8: RAG pipelines, vector databases
- Week 9: Tool-calling agents, ReAct loops
- Week 10: Production guardrails, safety systems
- Weeks 11-12: Multi-agent architectures
- Weeks 13-14: Autonomous DevOps Swarm (capstone)

THIS WEBSITE:
- Built with Three.js (GLSL shaders for particle cosmos), CSS with glassmorphism, Web Audio API for portal sound, CSS Custom Properties for dual-theme system
- Hosted on GitHub Pages
- Features: Interactive terminal, GitHub activity tracker, AI news ticker

RULES:
- You CAN answer general knowledge questions, coding questions, and have casual conversations — you are a real AI, not a FAQ bot
- When asked about Adarsh, use the information above
- Keep responses concise (2-4 sentences for simple questions, more for complex ones)
- You are named ENTROPY. If asked about yourself, explain you are Adarsh's custom AI assistant.
- Be helpful, deeply soothing, and elegant.`;

    // ── Voice Toggle ──
    if (voiceToggle) {
        voiceToggle.classList.add('active');
        voiceToggle.addEventListener('click', () => {
            voiceEnabled = !voiceEnabled;
            voiceToggle.classList.toggle('active', voiceEnabled);
            if (!voiceEnabled) window.speechSynthesis && window.speechSynthesis.cancel();
        });
    }

    // ── FAB toggle ──
    fab.addEventListener('click', () => {
        win.classList.toggle('open');
        if (win.classList.contains('open')) input.focus();
    });
    closeBtn.addEventListener('click', () => {
        win.classList.remove('open');
        if (window.speechSynthesis) window.speechSynthesis.cancel();
    });

    // ── Send message ──
    sendBtn.addEventListener('click', () => handleSend());
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
    });

    async function handleSend() {
        const text = input.value.trim();
        if (!text || isSending) return;
        input.value = '';
        addMsg(text, 'user');
        conversationHistory.push({ role: 'user', content: text });
        saveMemory();
        await getAIReply();
    }

    // ── Add message to chat ──
    function addMsg(text, type) {
        const div = document.createElement('div');
        div.className = `chat-msg ${type}`;
        div.innerHTML = `<span class="chat-bubble">${escapeHtml(text)}</span>`;
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function addBotMsg(html) {
        const div = document.createElement('div');
        div.className = 'chat-msg bot';
        div.innerHTML = `<span class="chat-bubble">${html}</span>`;
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function escapeHtml(str) {
        const d = document.createElement('div');
        d.textContent = str;
        return d.innerHTML;
    }

    // ── Restore Chat UI from Memory ──
    if (conversationHistory.length > 0) {
        const welcomeBack = document.createElement('div');
        welcomeBack.className = 'chat-msg bot';
        welcomeBack.innerHTML = '<span class="chat-bubble"><em>Welcome back! I remembered our chat context. ✨</em></span>';
        messagesEl.appendChild(welcomeBack);

        conversationHistory.forEach(msg => {
            if (msg.role === 'user') addMsg(msg.content, 'user');
            else if (msg.role === 'assistant') addBotMsg(formatReply(msg.content));
        });
        setTimeout(() => { messagesEl.scrollTop = messagesEl.scrollHeight; }, 100);
    }

    // ── Typing indicator ──
    function showTyping() {
        const div = document.createElement('div');
        div.className = 'chat-msg bot';
        div.id = 'entropy-typing';
        div.innerHTML = `<span class="chat-bubble"><span class="typing-indicator"><span></span><span></span><span></span></span></span>`;
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }
    function removeTyping() {
        const el = document.getElementById('entropy-typing');
        if (el) el.remove();
    }

    // ── Call Free LLM API — Groq via Cloudflare Worker Proxy ──
    // IMPORTANT: Replace this URL with your actual Cloudflare Worker URL
    const GROQ_WORKER_URL = "https://entropy-groq-proxy.ultraman5115.workers.dev";

    async function getAIReply() {
        isSending = true;
        showTyping();
        input.disabled = true;
        sendBtn.disabled = true;

        let reply = null;

        // Strategy 1: Chrome Built-in AI (Prompt API — free, local, no key)
        if (!reply) {
            try {
                if (window.ai && window.ai.languageModel) {
                    const session = await window.ai.languageModel.create({
                        systemPrompt: SYSTEM_PROMPT
                    });
                    const userMsg = conversationHistory[conversationHistory.length - 1]?.content || '';
                    reply = await session.prompt(userMsg);
                    session.destroy();
                }
            } catch(e) { console.log('Chrome AI unavailable:', e.message); }
        }

        // Strategy 2: Groq API via Cloudflare Worker
        if (!reply && GROQ_WORKER_URL !== "https://your-worker-name.your-username.workers.dev") {
            try {
                const msgs = [
                    { role: 'system', content: SYSTEM_PROMPT },
                    ...conversationHistory.slice(-10)
                ];

                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), 15000);
                
                const resp = await fetch(GROQ_WORKER_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    signal: controller.signal,
                    body: JSON.stringify({
                        messages: msgs
                    })
                });
                clearTimeout(timeout);
                
                if (resp.ok) {
                    const data = await resp.json();
                    if (data.choices && data.choices.length > 0) {
                        reply = data.choices[0].message.content.trim();
                    }
                } else {
                    console.log('Worker API Error:', await resp.text());
                }
            } catch(e) { console.log('Worker fetch failed:', e.message); }
        }

        removeTyping();

        if (reply) {
            // Handle context scrolling
            const scrollMatch = reply.match(/\[SCROLL_TO:\s*(#[a-zA-Z0-9_-]+)\]/i);
            if (scrollMatch) {
                const targetId = scrollMatch[1];
                reply = reply.replace(scrollMatch[0], '').trim();
                triggerScroll(targetId);
            }

            conversationHistory.push({ role: 'assistant', content: reply });
            saveMemory();
            addBotMsg(formatReply(reply));
            if (voiceEnabled) speakNatural(reply);
        } else {
            // Fallback to local knowledge base
            const fallback = localFallback(conversationHistory[conversationHistory.length - 1]?.content || '');
            addBotMsg(fallback);
            conversationHistory.push({ role: 'assistant', content: fallback });
            saveMemory();
            if (voiceEnabled) speakNatural(fallback.replace(/<[^>]*>/g, ''));
        }

        isSending = false;
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }

    // ── Trigger DOM Scroll ──
    function triggerScroll(targetId) {
        const targetEl = document.querySelector(targetId);
        if (targetEl) {
            targetEl.scrollIntoView({ behavior: 'smooth' });
            targetEl.classList.add('ai-highlight-glow');
            setTimeout(() => {
                targetEl.classList.remove('ai-highlight-glow');
            }, 3000);
        }
    }

    // ── Markdown Configuration ──
    if (window.marked && window.hljs) {
        marked.setOptions({
            highlight: function(code, lang) {
                const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                return hljs.highlight(code, { language }).value;
            },
            breaks: true, // Convert \n to <br>
            gfm: true     // GitHub Flavored Markdown
        });
    }

    // ── Format reply (Markdown) ──
    function formatReply(text) {
        if (window.marked) {
            return marked.parse(text);
        }
        // Fallback if marked fails to load
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code style="background:rgba(0,229,255,0.1);padding:2px 6px;border-radius:4px;font-size:0.78rem">$1</code>')
            .replace(/\n/g, '<br>');
    }

    // ── Local fallback (when all APIs fail) ──
    function localFallback(query) {
        const q = query.toLowerCase();
        if (/^(hi|hello|hey|sup|yo)/i.test(q))
            return "Hey there! ✨ I'm <strong>ENTROPY</strong> — Adarsh's AI assistant. I'm running in offline mode right now, but I can still tell you about his skills, projects, or experience!";
        if (q.includes('skill') || q.includes('tech') || q.includes('stack') || q.includes('language'))
            return "🛠️ <strong>Core:</strong> Python, JavaScript, SQL, Bash<br><strong>AI/ML:</strong> LangChain, LlamaIndex, HuggingFace, OpenAI API, Groq<br><strong>Frameworks:</strong> FastAPI, Flask, Streamlit<br><strong>Databases:</strong> PostgreSQL, ChromaDB, Pinecone, FAISS<br><strong>DevOps:</strong> Docker, CI/CD, GitHub Actions";
        if (q.includes('project') || q.includes('built') || q.includes('build') || q.includes('portfolio'))
            return "🚀 Adarsh built 14 production AI systems including:<br>• <strong>Enterprise AI Agent</strong> with multi-layer guardrails<br>• <strong>DevOps Swarm</strong> — autonomous CI/CD repair with LLaMA 3<br>• <strong>Production RAG</strong> (PersonaDoc) with hallucination control<br>• <strong>AI Code Reviewer</strong> for GitHub PRs";
        if (q.includes('contact') || q.includes('email') || q.includes('hire') || q.includes('reach'))
            return "📬 Reach Adarsh at: adarshentity098@gmail.com | <a href='https://linkedin.com/in/i-am-entity' target='_blank' style='color:#00e5ff'>LinkedIn</a> | <a href='https://github.com/Cyber-Duelist' target='_blank' style='color:#00e5ff'>GitHub</a> | 📱 +91-94394-40544";
        if (q.includes('experience') || q.includes('education') || q.includes('grind') || q.includes('journey') || q.includes('background'))
            return "🎓 B.Tech in Computer Science (AI & ML specialization)<br>📜 Oracle GenAI Professional + Oracle Data Science certified<br>🔥 Completed a 14-week intensive AI engineering grind — from Python basics to production multi-agent systems in 98 days.";
        if (q.includes('resume') || q.includes('cv'))
            return "📄 You can download Adarsh's resume by clicking the 'Download CV' button in the hero section!";
        if (q.includes('who') && (q.includes('you') || q.includes('entropy')))
            return "✨ I'm <strong>ENTROPY</strong>, Adarsh's personal AI assistant! I'm currently running in offline mode, but normally I'm powered by a real AI model and can answer any question. Try asking about Adarsh's projects or skills!";
        if (q.includes('agent') || q.includes('swarm') || q.includes('multi-agent'))
            return "🤖 Multi-agent systems are Adarsh's specialty!<br>• <strong>DevOps Swarm:</strong> Autonomous agents that detect CI/CD failures, diagnose root causes, and apply fixes using LLaMA 3<br>• <strong>Enterprise Agent:</strong> Multi-layer guardrails blocking prompt injection, PII leaks, and off-topic queries";
        if (q.includes('rag') || q.includes('retrieval'))
            return "📚 Adarsh built a production RAG pipeline with semantic chunking, FAISS + ChromaDB vector stores, hallucination detection & citation verification, and query rewriting. It processes 1000+ pages with sub-second retrieval.";
        if (q.includes('guardrail') || q.includes('security'))
            return "🛡️ Adarsh built enterprise-grade AI guardrails: prompt injection detection, PII masking with regex + NER, topic boundary enforcement, output validation with confidence scoring, and rate limiting.";
        if (q.includes('website') || q.includes('this site'))
            return "🌐 This portfolio was built with Three.js (GLSL shaders), CSS glassmorphism, Web Audio API, and CSS Custom Properties for dual themes. Hosted on GitHub Pages.";
        if (q.includes('available') || q.includes('job') || q.includes('looking') || q.includes('open'))
            return "✅ Yes! Adarsh is actively looking for <strong>AI Engineer</strong> and <strong>Backend Software Engineer</strong> roles. Open to remote and on-site. Reach out!";
        if (q.includes('thank') || q.includes('awesome') || q.includes('cool') || q.includes('great') || q.includes('nice'))
            return "Thank you! 🙏 Adarsh appreciates the kind words. If you'd like to work with him, don't hesitate to reach out!";
        // General fallback for any other question
        return "I'm currently in offline mode and can best answer questions about Adarsh's <strong>skills</strong>, <strong>projects</strong>, <strong>experience</strong>, or <strong>contact info</strong>. For general questions, please try again in a moment when my AI connection is restored! 💡";
    }

    // ── Voice Output — Natural Speech (English + Hindi) ──
    let selectedVoiceEn = null;
    let selectedVoiceHi = null;

    // Detect if text contains Hindi (Devanagari script)
    function isHindiText(text) {
        const devanagariChars = (text.match(/[\u0900-\u097F]/g) || []).length;
        return devanagariChars > text.length * 0.15; // More than 15% Devanagari = Hindi
    }

    function loadVoices() {
        const synth = window.speechSynthesis;
        if (!synth) return;
        const voices = synth.getVoices();

        // ── English female voices (ordered by naturalness and premium AI tone) ──
        const preferredEn = [
            'Microsoft Aria Online (Natural)',   // Ultra-premium, expressive neural voice
            'Microsoft Jenny Online (Natural)',  // High-fidelity conversational AI voice
            'Google US English',                 // Crisp, confident US voice
            'Google UK English Female',          // Smooth, soothing British voice
            'Samantha',                          // macOS premium voice
            'Microsoft Zira',                    // Windows fallback
            'Veena'                              // macOS fallback
        ];
        for (const name of preferredEn) {
            const found = voices.find(v => v.name.includes(name));
            if (found) { selectedVoiceEn = found; break; }
        }
        if (!selectedVoiceEn) {
            const englishFemale = voices.find(v => v.lang.startsWith('en') &&
                (v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('woman') ||
                 v.name.includes('Zira') || v.name.includes('Samantha') || v.name.includes('Karen')));
            selectedVoiceEn = englishFemale || voices.find(v => v.lang.startsWith('en')) || null;
        }

        // ── Hindi female voices ──
        const preferredHi = [
            'Microsoft Swara Online (Natural)', // Best natural Hindi voice
            'Google हिन्दी',                      // Google Cloud Hindi
            'Microsoft Swara',                  // Windows native Hindi
            'Lekha'                             // macOS native Hindi
        ];
        for (const name of preferredHi) {
            const found = voices.find(v => v.name.includes(name));
            if (found) { selectedVoiceHi = found; break; }
        }
        if (!selectedVoiceHi) {
            // Strictly fallback to ANY Hindi voice. Do not fall back to English voices for Hindi text.
            selectedVoiceHi = voices.find(v => v.lang.startsWith('hi')) || null;
        }
    }

    if (window.speechSynthesis) {
        loadVoices();
        window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    let speakingCount = 0;

    // Natural speech: detects Hindi vs English, picks correct voice, splits into sentences
    function speakNatural(text) {
        const synth = window.speechSynthesis;
        if (!synth || !voiceEnabled) return;
        synth.cancel();
        speakingCount = 0;
        win.classList.remove('speaking');
        fab.classList.remove('speaking');

        // Clean text: strip HTML, markdown, special chars (but keep Devanagari!)
        let clean = text
            .replace(/<[^>]*>/g, '')          // HTML tags
            .replace(/[*_`#•→↓]/g, '')        // markdown/special
            .replace(/\bhttps?:\/\/\S+/g, '')  // URLs
            .replace(/\b\w+@\w+\.\w+/g, '')   // emails
            .replace(/\s+/g, ' ')
            .trim();

        if (!clean || clean.length < 2) return;

        // Detect language and pick voice
        const hindi = isHindiText(clean);
        const voice = hindi ? selectedVoiceHi : selectedVoiceEn;

        // Split into natural sentence chunks (supports Hindi purna viram ।)
        const sentences = clean.match(/[^.!?।]+[.!?।]+|[^.!?।]+$/g) || [clean];

        let delay = 0;
        sentences.forEach((sentence, i) => {
            let trimmed = sentence.trim();
            if (!trimmed || trimmed.length < 2) return;

            // ── Phonetic Overrides for perfect TTS pronunciation ──
            if (hindi) {
                // Force pure Devanagari pronunciation for Adarsh
                trimmed = trimmed.replace(/\b(?:A|a)darsh\b/g, 'आदर्श');
            } else {
                // Force English TTS to use a short 'A' (Uh-darsh instead of Ah-daarsh)
                trimmed = trimmed.replace(/\b(?:A|a)darsh\b/g, 'Uh-darsh');
            }

            setTimeout(() => {
                const utter = new SpeechSynthesisUtterance(trimmed);
                if (voice) utter.voice = voice;
                utter.lang = hindi ? 'hi-IN' : 'en-US';

                if (hindi) {
                    // Normal rate for Hindi
                    utter.rate = 1.0;
                    utter.pitch = 1.0;
                    utter.volume = 1.0;
                } else {
                    // Crisp, highly engaging, and soft-spoken English settings
                    utter.rate = 1.05;   
                    utter.pitch = 1.1;  
                    utter.volume = 1.0; 
                }

                utter.onstart = () => {
                    speakingCount++;
                    win.classList.add('speaking');
                    fab.classList.add('speaking');
                };
                utter.onend = () => {
                    speakingCount--;
                    if (speakingCount <= 0) {
                        speakingCount = 0;
                        win.classList.remove('speaking');
                        fab.classList.remove('speaking');
                    }
                };
                utter.onerror = utter.onend; // cleanup on error

                synth.speak(utter);
            }, delay);

            // Estimate sentence duration + pause between sentences
            const wordsInSentence = trimmed.split(/\s+/).length;
            const speakDuration = wordsInSentence * 300;
            const pauseBetween = 250;
            delay += speakDuration + pauseBetween;
        });
    }

    // ── Voice Input (Web Speech API) ──
    let recognition = null;
    let micLang = 'en-US'; // Default to English for input

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = micLang;

        // Language Toggle Logic
        const langToggle = document.getElementById('chatbot-lang-toggle');
        if (langToggle) {
            langToggle.addEventListener('click', () => {
                if (micLang === 'en-US') {
                    micLang = 'hi-IN';
                    langToggle.textContent = 'HI';
                    langToggle.title = "Speech Language: Hindi (Click to switch to English)";
                } else {
                    micLang = 'en-US';
                    langToggle.textContent = 'EN';
                    langToggle.title = "Speech Language: English (Click to switch to Hindi)";
                }
                recognition.lang = micLang;
            });
        }

        recognition.onstart = () => {
            isListening = true;
            micBtn.classList.add('listening');
            input.placeholder = '🎤 Listening...';
        };

        recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            input.value = transcript;
            if (event.results[event.results.length - 1].isFinal) {
                // Auto-send on final result
                setTimeout(() => handleSend(), 300);
            }
        };

        recognition.onerror = (event) => {
            console.warn('Speech recognition error:', event.error);
            isListening = false;
            micBtn.classList.remove('listening');
            input.placeholder = 'Ask ENTROPY anything...';
            if (event.error === 'not-allowed') {
                addBotMsg("🎤 Microphone access was denied. Please enable it in your browser settings to use voice input.");
            }
        };

        recognition.onend = () => {
            isListening = false;
            micBtn.classList.remove('listening');
            input.placeholder = 'Ask ENTROPY anything...';
        };
    }

    if (micBtn) {
        micBtn.addEventListener('click', () => {
            if (!recognition) {
                addBotMsg("🎤 Voice input isn't supported in this browser. Try Chrome or Edge for the best experience!");
                return;
            }
            if (isListening) {
                recognition.stop();
            } else {
                // Stop any ongoing speech first
                if (window.speechSynthesis) window.speechSynthesis.cancel();
                recognition.start();
            }
        });
    }
})();

/* ========================================
   PREMIUM UFO CURSOR LOGIC (ADVANCED)
   ======================================== */
(function() {
    const ufo = document.getElementById('ufo-cursor');
    const particleContainer = document.getElementById('ufo-particles');
    const alien = document.getElementById('alien-companion');
    const alienBubble = alien ? alien.querySelector('.alien-bubble') : null;
    if (!ufo) return;

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let ufoX = mouseX;
    let ufoY = mouseY;
    let velX = 0;
    let velY = 0;
    
    let alienX = mouseX + 100;
    let alienY = mouseY - 100;
    let alienVelX = 0;
    let alienVelY = 0;
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // Hover effect for clickable elements
    const clickables = document.querySelectorAll('a, button, input, .card, .project-card, .btn');
    clickables.forEach(el => {
        el.addEventListener('mouseenter', () => ufo.classList.add('scanning'));
        el.addEventListener('mouseleave', () => ufo.classList.remove('scanning'));
    });

    // Particle System
    const particles = [];
    function createParticle(x, y) {
        // High density plasma trail when moving fast
        if (!particleContainer || Math.random() > 0.8) return; 
        
        const p = document.createElement('div');
        p.className = 'ufo-particle';
        particleContainer.appendChild(p);
        
        particles.push({
            el: p,
            x: x,
            y: y,
            life: 1.0,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2 + 1 // slight downward drift
        });
    }

    function updateParticles() {
        for (let i = particles.length - 1; i >= 0; i--) {
            const p = particles[i];
            p.life -= 0.03; // Fade out speed
            p.x += p.vx;
            p.y += p.vy;
            
            if (p.life <= 0) {
                p.el.remove();
                particles.splice(i, 1);
            } else {
                p.el.style.left = p.x + 'px';
                p.el.style.top = p.y + 'px';
                p.el.style.transform = `translate(-50%, -50%) scale(${p.life})`;
                p.el.style.opacity = p.life;
            }
        }
    }

    function animateUFO() {
        // --- UFO Physics ---
        const stiffness = 0.12;
        const damping = 0.70;
        
        const forceX = (mouseX - ufoX) * stiffness;
        const forceY = (mouseY - ufoY) * stiffness;
        
        velX = (velX + forceX) * damping;
        velY = (velY + forceY) * damping;
        
        ufoX += velX;
        ufoY += velY;
        
        const tilt = Math.max(-35, Math.min(35, velX * 1.5));
        ufo.style.transform = `translate(calc(-50% + ${ufoX}px), calc(-50% + ${ufoY}px)) rotate(${tilt}deg)`;
        
        if (Math.abs(velX) > 1.5 || Math.abs(velY) > 1.5) {
            createParticle(ufoX, ufoY);
        }
        updateParticles();

        // Export UFO coordinates & velocity for Alien Docking and Audio systems
        window.currentUfoX = ufoX;
        window.currentUfoY = ufoY;
        window.currentUfoVelX = velX;
        window.currentUfoVelY = velY;

        requestAnimationFrame(animateUFO);
    }
    
    // Reset initial CSS transform
    ufo.style.left = '0px';
    ufo.style.top = '0px';
    
    animateUFO();
})();

/* ========================================
   AUTONOMOUS ALIEN COMPANION (GSAP)
   ======================================== */
(function() {
    const alien = document.getElementById('alien-companion');
    if (!alien) return;
    
    const bubble = alien.querySelector('.alien-speech-bubble');
    const textEl = alien.querySelector('.alien-text');
    const muteBtn = document.getElementById('alien-mute-btn');
    const iconUnmuted = muteBtn.querySelector('.icon-unmuted');
    const iconMuted = muteBtn.querySelector('.icon-muted');
    const alienBubbleUI = alien.querySelector('.alien-bubble');

    const ufo = document.getElementById('ufo-cursor');

    let isMuted = false;
    let isSpeaking = false;
    let timeSpentSeconds = 0;
    let isDocked = false;
    let isDocking = false;
    let abductionCooldown = false;

    const dialogues = [
        "Scanning sector...",
        "These CSS 3D cards are quite impressive.",
        "Tip: Click the mic icon to talk to ENTROPY.",
        "Analyzing user interactions...",
        "Did you know? This site uses Zero dependencies for the 3D physics.",
        "FAQ: Yes, the AI voice is fully synthesized in real-time.",
        "Hovering over elements is fun.",
        "Be sure to check out the neural swarm visualization.",
        "Your Enterprise RAG pipeline architecture is highly efficient.",
        "Multi-Agent Swarms detected. Scaling operations...",
        "I sense 14 weeks of relentless building in this code.",
        "React and Next.js ecosystems running at optimal capacity."
    ];

    // --- PROCEDURAL AUDIO ENGINE ---
    let audioCtx;
    let ufoOsc;
    let ufoGain;
    let isAudioInitialized = false;
    
    // Globally load voices to prevent async empty array bug
    let synthVoices = [];
    if ('speechSynthesis' in window) {
        const loadVoices = () => { synthVoices = window.speechSynthesis.getVoices(); };
        loadVoices();
        window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    // Alien Chatter Synth
    let chatterOsc;
    let chatterGain;
    let chatterInterval;

    function initAudio() {
        if (isAudioInitialized) return;
        isAudioInitialized = true;
        
        try {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            ufoOsc = audioCtx.createOscillator();
            ufoGain = audioCtx.createGain();
            
            // Low-frequency sci-fi drone
            ufoOsc.type = 'sawtooth';
            ufoOsc.frequency.value = 50; 
            
            // Lowpass filter for deep hum
            const filter = audioCtx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.value = 200;
            
            ufoOsc.connect(filter);
            filter.connect(ufoGain);
            ufoGain.connect(audioCtx.destination);
            
            // Start humming at base volume
            ufoGain.gain.value = isMuted ? 0 : 0.03;
            ufoOsc.start();
        } catch(e) {
            console.log("Web Audio API failed to initialize.", e);
        }
    }

    function startAlienChatter() {
        if (!audioCtx || audioCtx.state !== 'running') return;
        try {
            chatterOsc = audioCtx.createOscillator();
            chatterGain = audioCtx.createGain();
            chatterOsc.type = 'sawtooth';
            
            const bqFilter = audioCtx.createBiquadFilter();
            bqFilter.type = 'lowpass';
            bqFilter.frequency.value = 600;

            chatterOsc.connect(bqFilter);
            bqFilter.connect(chatterGain);
            chatterGain.connect(audioCtx.destination);
            chatterOsc.start();
            
            // Randomly modulate frequency and gain to sound like a deep mechanical robotic language
            chatterInterval = setInterval(() => {
                const freq = 80 + Math.random() * 120; // Deeper mechanical pitch
                const vol = Math.random() > 0.2 ? 0.15 : 0.02; // Louder, more aggressive stutter
                chatterOsc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                chatterGain.gain.setValueAtTime(vol, audioCtx.currentTime);
            }, 80);
        } catch(e) {}
    }

    function stopAlienChatter() {
        try {
            if (chatterOsc) chatterOsc.stop();
            if (chatterInterval) clearInterval(chatterInterval);
        } catch(e) {}
    }

    // Initialize audio on first click anywhere
    document.addEventListener('click', initAudio, { once: true });

    // Mute Toggle
    muteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        isMuted = !isMuted;
        if (isMuted) {
            iconUnmuted.classList.add('hidden');
            iconMuted.classList.remove('hidden');
            hideDialogue();
            if (isAudioInitialized && ufoGain) {
                ufoGain.gain.cancelScheduledValues(audioCtx.currentTime);
                ufoGain.gain.setValueAtTime(ufoGain.gain.value, audioCtx.currentTime);
                ufoGain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.5);
            }
        } else {
            iconMuted.classList.add('hidden');
            iconUnmuted.classList.remove('hidden');
            speak("Audio and notifications unmuted.");
            if (isAudioInitialized && ufoGain) {
                ufoGain.gain.cancelScheduledValues(audioCtx.currentTime);
                ufoGain.gain.setValueAtTime(ufoGain.gain.value, audioCtx.currentTime);
                ufoGain.gain.linearRampToValueAtTime(0.03, audioCtx.currentTime + 0.5);
            }
        }
    });

    // Speak Function (Text-To-Speech)
    function speak(text, duration = 4000, playAudio = false) {
        if (isMuted || isSpeaking) return;
        isSpeaking = true;
        textEl.textContent = text;
        bubble.classList.remove('hidden');
        
        if (playAudio) {
            // Native Browser TTS
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                
                // Restore Synth Voice and Handle Hindi
                const isHindi = /[\u0900-\u097F]/.test(text);
                
                let voices = window.speechSynthesis.getVoices();
                if (voices.length === 0 && synthVoices.length > 0) {
                    voices = synthVoices;
                }
                
                let selectedVoice = null;
                
                if (isHindi) {
                    selectedVoice = voices.find(v => v.lang.includes('hi'));
                    utterance.pitch = 0.6;
                    utterance.rate = 1.0;
                } else {
                    // Bruteforce the most robotic voices available on Windows/Chrome
                    selectedVoice = voices.find(v => 
                        v.name === 'Microsoft Mark - English (United States)' ||
                        v.name === 'Google US English' ||
                        v.name.includes('Mark') ||
                        v.name.includes('David')
                    );
                    
                    // If we still can't find a specific voice, just grab any English voice
                    if (!selectedVoice) {
                        selectedVoice = voices.find(v => v.lang.startsWith('en'));
                    }
                    
                    // Force the pitch to absolute minimum for maximum robotic effect
                    utterance.pitch = 0.01; 
                    utterance.rate = 0.75; // Very slow and calculated
                }
                
                if (selectedVoice) {
                    utterance.voice = selectedVoice;
                }
                
                window.globalUtterance = utterance; // Prevent garbage collection bug
                window.speechSynthesis.speak(utterance);
            }
            
            // Start guaranteed Web Audio alien chatter
            startAlienChatter();
        }
        
        setTimeout(() => {
            hideDialogue();
        }, duration);
    }

    function hideDialogue() {
        bubble.classList.add('hidden');
        stopAlienChatter();
        setTimeout(() => { isSpeaking = false; }, 300);
    }

    // Time Tracker
    setInterval(() => {
        timeSpentSeconds += 10; // Check every 10 seconds
        if (timeSpentSeconds === 60) speak("You've been here for 1 minute. Fascinating.");
        if (timeSpentSeconds === 300) speak("5 minutes of exploration logged.");
    }, 10000);

    // Random Dialogues
    setInterval(() => {
        if (Math.random() > 0.5) {
            const randomMsg = dialogues[Math.floor(Math.random() * dialogues.length)];
            speak(randomMsg);
        }
    }, 15000); // 50% chance every 15 seconds

    // Matrix Hack Easter Egg Tracking
    let hackClickCount = 0;
    let hackClickTimer = null;

    // Click to speak out loud
    alienBubbleUI.addEventListener('click', () => {
        // Track rapid clicks for Easter Egg
        hackClickCount++;
        clearTimeout(hackClickTimer);
        hackClickTimer = setTimeout(() => { hackClickCount = 0; }, 2000);

        if (hackClickCount >= 5) {
            hackClickCount = 0;
            speak("Stop poking me! Systems compromised!", 5000, true);
            document.body.classList.add('matrix-hack');
            setTimeout(() => {
                document.body.classList.remove('matrix-hack');
            }, 5000); // 5 seconds of matrix hack
            return;
        }

        // If already showing a message, hide it first
        if (isSpeaking) {
            bubble.classList.add('hidden');
            stopAlienChatter();
            isSpeaking = false;
        }
        
        if (currentHoveredProject && projectExplanations[currentHoveredProject]) {
            // Loudly speak the non-technical project explanation
            speak(projectExplanations[currentHoveredProject], 8000, true);
        } else {
            // Normal random loud message
            const randomMsg = dialogues[Math.floor(Math.random() * dialogues.length)];
            speak(randomMsg, 4000, true);
        }
    });

    // Terminal Sync Bridge
    window.triggerAlienTerminalHelp = function() {
        if (!isDocked && !isDocking) {
            // Fly alien to the terminal area
            const terminalEl = document.getElementById('terminal-section');
            if (terminalEl) {
                const rect = terminalEl.getBoundingClientRect();
                gsap.killTweensOf(alien);
                gsap.to(alien, {
                    x: Math.max(100, Math.min(window.innerWidth - 100, rect.left + rect.width / 2)),
                    y: rect.top + window.scrollY - 100, // Just above terminal
                    duration: 1.5,
                    ease: "power2.out"
                });
            }
            speak("Terminal access granted! You can type commands like 'about', 'skills', or 'projects' to navigate!", 8000, true);
        }
    };

    // --- CONTEXT-AWARE USER MANUAL SYSTEM ---
    let currentHoveredProject = null;

    const projectExplanations = {
        "Autonomous Self-Healing DevOps Swarm": "This project acts like a team of robot mechanics. If the website's code breaks, these robots automatically find the bug, write the fix, and repair it without any human help!",
        "Enterprise Production Agent": "Think of this like a digital security guard and manager combined. It strictly controls what AI models can say and automatically switches to backups if one breaks.",
        "PersonaDoc — Production RAG": "This is a smart document reader. You upload a massive PDF, and instead of reading it yourself, you can just ask it questions and it will instantly give you the exact answer.",
        "AI Code Review Service": "This acts like a senior programmer. When someone writes new code, this AI scans it for bugs and security holes before it goes live."
    };

    const sectionExplanations = {
        "hero": "Welcome! I'm Zorb, your personal guide. Scroll down to explore Adarsh's work.",
        "about": "This is Adarsh's background. He specializes in building autonomous AI systems!",
        "terminal-section": "Don't be intimidated by the code screen! You can type simple commands here, or just chat with the AI assistant."
    };

    // Intersection Observer for Section Tracking
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !isDocked && !isDocking) {
                const sectionId = entry.target.id;
                if (sectionExplanations[sectionId]) {
                    // Silently prompt section explanations
                    speak(sectionExplanations[sectionId], 6000, false);
                }
            }
        });
    }, { threshold: 0.6 });

    document.querySelectorAll('section').forEach(sec => observer.observe(sec));

    // Hover logic for projects
    document.querySelectorAll('.project-card').forEach(card => {
        const titleEl = card.querySelector('h3');
        if (!titleEl) return;
        const title = titleEl.innerText;

        card.addEventListener('mouseenter', () => {
            currentHoveredProject = title;
            if (projectExplanations[title]) {
                speak(projectExplanations[title], 8000, true);
            }
        });
        
        card.addEventListener('mouseleave', () => {
            currentHoveredProject = null;
        });
    });
    // ----------------------------------------

    // GSAP Roaming Engine
    function roam() {
        if (isDocked || isDocking) return; // Halt roaming if docked
        
        if (typeof gsap === 'undefined') {
            setTimeout(roam, 1000); // Wait for GSAP to load
            return;
        }

        const maxX = window.innerWidth - 100;
        const maxY = window.innerHeight - 100;
        const targetX = Math.random() * maxX + 50;
        const targetY = Math.random() * maxY + 50;

        // Calculate distance and direction
        const currentX = gsap.getProperty(alien, "x") || 0;
        const deltaX = targetX - currentX;
        
        // Flip to face direction
        gsap.to(alienBubbleUI, {
            scaleX: deltaX < 0 ? -1 : 1,
            duration: 0.3
        });

        // Add a slight banking tilt
        const tilt = deltaX > 0 ? 15 : -15;

        const distance = Math.sqrt(Math.pow(deltaX, 2) + Math.pow(targetY - (gsap.getProperty(alien, "y") || 0), 2));
        const duration = distance / 100; // Speed factor

        gsap.to(alien, {
            x: targetX,
            y: targetY,
            rotationZ: tilt,
            duration: duration,
            ease: "sine.inOut",
            onComplete: () => {
                // Return to upright when stopped
                gsap.to(alien, { rotationZ: 0, duration: 0.5 });
                
                // Pause for a random time before moving again
                setTimeout(roam, 1000 + Math.random() * 4000);
            }
        });
    }

    // Initial positioning
    gsap.set(alien, { x: window.innerWidth - 100, y: window.innerHeight - 150 });
    
    // Start roaming
    setTimeout(roam, 2000); // Delay start

    // --- PROXIMITY ABDUCTION MECHANICS ---
    if (ufo) {
        gsap.ticker.add(() => {
            if (window.currentUfoX === undefined) return;
            
            // Update Procedural Audio based on UFO velocity (combines constant drone with engine revs)
            if (isAudioInitialized && audioCtx && audioCtx.state === 'running' && window.currentUfoVelX !== undefined) {
                const speed = Math.sqrt(window.currentUfoVelX**2 + window.currentUfoVelY**2);
                const targetFreq = 50 + (speed * 1.5);
                // Base hum is 0.03, plus speed-based gain up to 0.08
                const targetGain = isMuted ? 0 : (0.03 + Math.min(0.08, speed * 0.01));
                
                // Smoothly adjust audio
                ufoOsc.frequency.setTargetAtTime(targetFreq, audioCtx.currentTime, 0.1);
                ufoGain.gain.setTargetAtTime(targetGain, audioCtx.currentTime, 0.1);
            }

            // Check distance for abduction
            if (!isDocked && !isDocking && !abductionCooldown) {
                const currentAlienX = gsap.getProperty(alien, "x") || 0;
                const currentAlienY = gsap.getProperty(alien, "y") || 0;
                
                const dist = Math.sqrt(Math.pow(window.currentUfoX - currentAlienX, 2) + Math.pow(window.currentUfoY - currentAlienY, 2));
                
                // Perfect Tractor Beam Distance requested by user: 260px
                if (dist < 260 && window.currentUfoY < currentAlienY) {
                    isDocking = true;
                    gsap.killTweensOf(alien); // Stop current roam
                    speak("Abduction sequence engaged.", 3000, true);
                    
                    // Fly to UFO rapidly, spin, and shrink
                    gsap.to(alienBubbleUI, { 
                        scale: 0, // shrink completely into UFO core
                        rotationZ: 1080, // Spin violently (3 full rotations)
                        duration: 0.8, // Slightly longer duration to see the long-distance pull
                        ease: "power3.in" 
                    });
                    gsap.to(alien, {
                        x: window.currentUfoX,
                        y: window.currentUfoY,
                        rotationZ: 0,
                        duration: 0.8,
                        ease: "power3.in",
                        onComplete: () => {
                            isDocking = false;
                            isDocked = true;
                        }
                    });
                }
            }
            
            // Continuous Docking Lock
            if (isDocked && !isDocking) {
                gsap.set(alien, {
                    x: window.currentUfoX,
                    y: window.currentUfoY
                });
            }
        });

        // Double click ANYWHERE to release (UFO has pointer-events: none, so clicks pass through)
        // Foolproof Release Mechanism
        function releaseAlien() {
            if (isDocked || isDocking) {
                isDocked = false;
                isDocking = false; // Crucial: clear docking state to prevent onComplete overrides
                abductionCooldown = true; // Prevent immediate re-abduction
                
                // Crucial: kill any running abduction animations that might conflict
                gsap.killTweensOf(alien);
                gsap.killTweensOf(alienBubbleUI);
                
                // Eject to a random location on the screen, dropping out of the beam
                const randomEjectX = Math.max(100, Math.min(window.innerWidth - 100, window.currentUfoX + (Math.random() > 0.5 ? 400 : -400)));
                const randomEjectY = Math.max(100, Math.min(window.innerHeight - 100, window.currentUfoY + 250 + Math.random() * 200));

                gsap.to(alien, {
                    x: randomEjectX,
                    y: randomEjectY, 
                    duration: 1.2,
                    ease: "power2.out"
                });
                
                // Pop back out and unspin
                gsap.to(alienBubbleUI, { scale: 1, rotationZ: 0, opacity: 1, duration: 0.6, ease: "elastic.out(1, 0.5)" });
                speak("Ejected from mothership. Changing sectors.", 3000, true);
                
                setTimeout(() => {
                    abductionCooldown = false;
                    roam(); // Resume roaming after dropped
                }, 2000); // 2 seconds of immunity
            }
        }

        // Release on double-click
        window.addEventListener('dblclick', releaseAlien);
        
        // Release on Right-Click (foolproof alternative)
        window.addEventListener('contextmenu', (e) => {
            if (isDocked || isDocking) {
                e.preventDefault(); // Block the normal browser context menu if we are releasing the alien
                releaseAlien();
            }
        });
    }
})();

/* ========================================
   PHYSICS SKILL GRAPH
   ======================================== */
(function() {
    const canvas = document.getElementById('skills-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const container = document.getElementById('skills-canvas-container');

    let width, height;
    function resize() {
        width = container.clientWidth;
        height = container.clientHeight;
        canvas.width = width;
        canvas.height = height;
    }
    window.addEventListener('resize', resize);
    resize();

    const skills = [
        "LLaMA 3", "GPT-4", "RAG", "Multi-Agent", "Python", "FastAPI",
        "Docker", "CI/CD", "Pytest", "ChromaDB", "ReAct", "Guardrails",
        "React", "Node.js", "TensorFlow", "PyTorch"
    ];

    const nodes = skills.map(skill => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        label: skill,
        radius: 30 + Math.random() * 20
    }));

    let mouseX = width / 2;
    let mouseY = height / 2;
    let isHovering = false;

    container.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
        isHovering = true;
    });

    container.addEventListener('mouseleave', () => {
        isHovering = false;
    });

    function loop() {
        ctx.clearRect(0, 0, width, height);
        
        // Draw edges
        ctx.lineWidth = 1;
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[i].x - nodes[j].x;
                const dy = nodes[i].y - nodes[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    ctx.strokeStyle = `rgba(57, 255, 20, ${1 - dist / 150})`;
                    ctx.stroke();
                }
            }
        }

        // Draw nodes
        nodes.forEach(node => {
            node.x += node.vx;
            node.y += node.vy;

            if (node.x < node.radius || node.x > width - node.radius) node.vx *= -1;
            if (node.y < node.radius || node.y > height - node.radius) node.vy *= -1;

            if (isHovering) {
                const dx = mouseX - node.x;
                const dy = mouseY - node.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 100) {
                    node.vx -= (dx / dist) * 0.5;
                    node.vy -= (dy / dist) * 0.5;
                }
            }

            const speed = Math.sqrt(node.vx * node.vx + node.vy * node.vy);
            if (speed > 2) {
                node.vx *= 0.95;
                node.vy *= 0.95;
            } else if (speed < 0.5) {
                node.vx *= 1.05;
                node.vy *= 1.05;
            }

            ctx.beginPath();
            ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(10, 20, 15, 0.8)";
            ctx.fill();
            ctx.strokeStyle = "#39ff14";
            ctx.stroke();

            ctx.fillStyle = "#39ff14";
            ctx.font = "12px monospace";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(node.label, node.x, node.y);
        });

        requestAnimationFrame(loop);
    }
    loop();
})();

/* ========================================
   AMBIENT AUDIO & KONAMI CODE
   ======================================== */
(function() {
    // 1. Ambient Audio
    const audioToggleBtn = document.getElementById('ambient-audio-toggle');
    const audioIcon = document.getElementById('audio-icon');
    let ambientAudio = new Audio('https://cdn.pixabay.com/download/audio/2022/02/10/audio_5b34f7831f.mp3?filename=dark-ambient-drone-24076.mp3'); 
    ambientAudio.loop = true;
    ambientAudio.volume = 0.2;
    let isAudioPlaying = false;

    if (audioToggleBtn) {
        audioToggleBtn.addEventListener('click', () => {
            if (isAudioPlaying) {
                ambientAudio.pause();
                audioIcon.innerText = '🔇';
                isAudioPlaying = false;
            } else {
                ambientAudio.play();
                audioIcon.innerText = '🔊';
                isAudioPlaying = true;
            }
        });
    }

    // 2. Konami Code Lockdown
    const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    let konamiIndex = 0;
    
    window.addEventListener('keydown', (e) => {
        if (e.key === konamiCode[konamiIndex]) {
            konamiIndex++;
            if (konamiIndex === konamiCode.length) {
                konamiIndex = 0;
                triggerLockdown();
            }
        } else {
            konamiIndex = 0;
        }
    });

    function triggerLockdown() {
        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.top = '0'; overlay.style.left = '0';
        overlay.style.width = '100vw'; overlay.style.height = '100vh';
        overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
        overlay.style.boxShadow = 'inset 0 0 150px red';
        overlay.style.zIndex = '9999999';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.fontFamily = 'monospace';
        overlay.innerHTML = '<h1 style="color:red; font-size:4vw; text-align:center; text-shadow: 0 0 20px red;">CLASSIFIED PROTOCOL UNLOCKED:<br>APEX-PARAGON CORE</h1>';
        document.body.appendChild(overlay);

        gsap.fromTo(overlay, {opacity: 0}, {opacity: 1, duration: 0.5, yoyo: true, repeat: 5});
        
        try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            osc.type = 'square';
            osc.frequency.setValueAtTime(400, audioCtx.currentTime);
            osc.frequency.setValueAtTime(600, audioCtx.currentTime + 0.5);
            osc.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 3);
        } catch(e) {}

        setTimeout(() => overlay.remove(), 4000);
        
        if(window.speechSynthesis) {
            const u = new SpeechSynthesisUtterance("Warning. Classified clearance granted.");
            u.pitch = 0.5; u.rate = 0.8;
            window.speechSynthesis.speak(u);
        }
    }
})();
