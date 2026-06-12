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

        // Update connection lines
        const pos = geo.attributes.position.array;
        let li = 0;
        const maxD = 3.5;
        const checkCount = Math.min(particleCount, 120);

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
        dot.style.left = cx + 'px';
        dot.style.top = cy + 'px';
    });

    function animateRing() {
        dx += (cx - dx) * 0.12;
        dy += (cy - dy) * 0.12;
        ring.style.left = dx + 'px';
        ring.style.top = dy + 'px';
        requestAnimationFrame(animateRing);
    }
    animateRing();

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
   GITHUB ACTIVITY (Public API)
   ======================================== */
(function() {
    const GH_USER = 'Cyber-Duelist';

    async function fetchGitHub() {
        try {
            // Fetch user profile
            const user = await fetch(`https://api.github.com/users/${GH_USER}`).then(r => r.json());
            document.getElementById('gh-repos').textContent = user.public_repos || 0;

            // Fetch repos for stars/forks/languages
            const repos = await fetch(`https://api.github.com/users/${GH_USER}/repos?per_page=100&sort=updated`).then(r => r.json());
            
            let totalStars = 0, totalForks = 0;
            const langs = {};
            repos.forEach(r => {
                totalStars += r.stargazers_count || 0;
                totalForks += r.forks_count || 0;
                if (r.language) langs[r.language] = (langs[r.language] || 0) + 1;
            });
            
            document.getElementById('gh-stars').textContent = totalStars;
            document.getElementById('gh-forks').textContent = totalForks;

            // Languages
            const langContainer = document.getElementById('github-languages');
            Object.keys(langs).sort((a, b) => langs[b] - langs[a]).forEach(lang => {
                const tag = document.createElement('span');
                tag.className = 'lang-tag';
                tag.textContent = lang;
                langContainer.appendChild(tag);
            });

            // Fetch recent events
            const events = await fetch(`https://api.github.com/users/${GH_USER}/events?per_page=10`).then(r => r.json());
            const container = document.getElementById('github-events');
            let commitCount = 0;

            events.slice(0, 6).forEach(evt => {
                const div = document.createElement('div');
                div.className = 'github-event';

                let icon = '📌', text = '';
                const repo = evt.repo ? evt.repo.name.split('/')[1] : '';
                const timeAgo = getTimeAgo(new Date(evt.created_at));

                if (evt.type === 'PushEvent') {
                    const commits = evt.payload.commits ? evt.payload.commits.length : 0;
                    commitCount += commits;
                    icon = '⚡';
                    text = `Pushed <strong>${commits} commit${commits > 1 ? 's' : ''}</strong> to ${repo}`;
                } else if (evt.type === 'CreateEvent') {
                    icon = '🌱';
                    text = `Created ${evt.payload.ref_type} <strong>${evt.payload.ref || repo}</strong>`;
                } else if (evt.type === 'WatchEvent') {
                    icon = '⭐';
                    text = `Starred <strong>${repo}</strong>`;
                } else if (evt.type === 'ForkEvent') {
                    icon = '🔀';
                    text = `Forked <strong>${repo}</strong>`;
                } else {
                    icon = '📋';
                    text = `${evt.type.replace('Event', '')} on <strong>${repo}</strong>`;
                }

                div.innerHTML = `
                    <span class="event-icon">${icon}</span>
                    <span class="event-text">${text}</span>
                    <span class="event-time">${timeAgo}</span>
                `;
                container.appendChild(div);
            });

            document.getElementById('gh-commits').textContent = commitCount || '—';
        } catch(e) {
            console.warn('GitHub API error:', e);
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
            // Try fetching from a public RSS-to-JSON proxy
            const resp = await fetch('https://api.rss2json.com/v1/api.json?rss_url=https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en&count=10');
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
    const conversationHistory = [];

    // ── System Prompt — ENTROPY's personality + portfolio knowledge ──
    const SYSTEM_PROMPT = `You are ENTROPY, a charming, witty, and highly intelligent AI assistant embedded in the portfolio website of Adarsh Kumar Singh. You have a warm, slightly playful personality. You use occasional emojis but stay professional.

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
- You are named ENTROPY. If asked about yourself, explain you are Adarsh's custom AI assistant
- Be helpful, friendly, and slightly witty`;

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

    // ── Call Free LLM API (Pollinations.ai — no API key required) ──
    async function getAIReply() {
        isSending = true;
        showTyping();
        input.disabled = true;
        sendBtn.disabled = true;

        const messages = [
            { role: 'system', content: SYSTEM_PROMPT },
            ...conversationHistory.slice(-10) // Keep last 10 messages for context
        ];

        try {
            const response = await fetch('https://text.pollinations.ai/openai', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: 'openai',
                    messages: messages,
                    temperature: 0.7,
                    max_tokens: 512
                })
            });

            if (!response.ok) throw new Error(`API error: ${response.status}`);

            const data = await response.json();
            const reply = data.choices?.[0]?.message?.content?.trim();

            removeTyping();

            if (reply) {
                conversationHistory.push({ role: 'assistant', content: reply });
                addBotMsg(formatReply(reply));
                if (voiceEnabled) speak(reply);
            } else {
                addBotMsg("Hmm, I didn't get a response. Could you try again? 🔄");
            }
        } catch (err) {
            console.warn('ENTROPY API error:', err);
            removeTyping();
            // Fallback to local knowledge base
            const fallback = localFallback(conversationHistory[conversationHistory.length - 1]?.content || '');
            addBotMsg(fallback);
            conversationHistory.push({ role: 'assistant', content: fallback });
            if (voiceEnabled) speak(fallback.replace(/<[^>]*>/g, ''));
        } finally {
            isSending = false;
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }

    // ── Format reply (basic markdown-like) ──
    function formatReply(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code style="background:rgba(0,229,255,0.1);padding:2px 6px;border-radius:4px;font-size:0.78rem">$1</code>')
            .replace(/\n/g, '<br>');
    }

    // ── Local fallback (when API fails) ──
    function localFallback(query) {
        const q = query.toLowerCase();
        if (/^(hi|hello|hey|sup|yo)/i.test(q))
            return "Hey there! ✨ I'm <strong>ENTROPY</strong> — Adarsh's AI assistant. I'm having a bit of trouble connecting right now, but ask me about his skills, projects, or experience!";
        if (q.includes('skill') || q.includes('tech') || q.includes('stack'))
            return "🛠️ <strong>Core:</strong> Python, JavaScript, SQL, Bash<br><strong>AI/ML:</strong> LangChain, LlamaIndex, HuggingFace, OpenAI API<br><strong>Frameworks:</strong> FastAPI, Flask, Streamlit<br><strong>Databases:</strong> PostgreSQL, ChromaDB, Pinecone, FAISS";
        if (q.includes('project') || q.includes('built') || q.includes('build'))
            return "🚀 Adarsh built 14 production AI systems including:<br>• <strong>Enterprise AI Agent</strong> with guardrails<br>• <strong>DevOps Swarm</strong> — autonomous CI/CD repair<br>• <strong>Production RAG</strong> with hallucination control<br>• <strong>AI Code Reviewer</strong> for GitHub PRs";
        if (q.includes('contact') || q.includes('email') || q.includes('hire'))
            return "📬 Reach Adarsh at: adarshentity098@gmail.com | <a href='https://linkedin.com/in/i-am-entity' target='_blank' style='color:#00e5ff'>LinkedIn</a> | <a href='https://github.com/Cyber-Duelist' target='_blank' style='color:#00e5ff'>GitHub</a>";
        return "I'm having trouble connecting right now 😅 Try asking about Adarsh's <strong>skills</strong>, <strong>projects</strong>, or <strong>experience</strong>, or try again in a moment!";
    }

    // ── Voice Output (Web Speech API) ──
    let selectedVoice = null;

    function loadVoices() {
        const synth = window.speechSynthesis;
        if (!synth) return;
        const voices = synth.getVoices();
        // Prefer a nice female English voice
        const preferred = [
            'Microsoft Zira', 'Google UK English Female', 'Google US English',
            'Samantha', 'Karen', 'Moira', 'Tessa', 'Fiona',
            'Microsoft Hazel', 'Microsoft Susan'
        ];
        for (const name of preferred) {
            const found = voices.find(v => v.name.includes(name));
            if (found) { selectedVoice = found; return; }
        }
        // Fallback: any English female voice
        const englishFemale = voices.find(v => v.lang.startsWith('en') &&
            (v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('woman') ||
             v.name.includes('Zira') || v.name.includes('Samantha') || v.name.includes('Karen')));
        if (englishFemale) { selectedVoice = englishFemale; return; }
        // Fallback: any English voice
        selectedVoice = voices.find(v => v.lang.startsWith('en')) || voices[0] || null;
    }

    if (window.speechSynthesis) {
        loadVoices();
        window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    function speak(text) {
        const synth = window.speechSynthesis;
        if (!synth || !voiceEnabled) return;
        synth.cancel(); // stop any current speech
        const clean = text.replace(/<[^>]*>/g, '').replace(/[*_`#]/g, '').substring(0, 500);
        const utter = new SpeechSynthesisUtterance(clean);
        if (selectedVoice) utter.voice = selectedVoice;
        utter.rate = 1.0;
        utter.pitch = 1.1; // slightly higher for feminine tone
        utter.volume = 0.9;
        synth.speak(utter);
    }

    // ── Voice Input (Web Speech API) ──
    let recognition = null;
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

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

