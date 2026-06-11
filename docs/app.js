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
