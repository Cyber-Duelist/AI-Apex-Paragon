import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { scrambleText } from './scramble';
import { getCamera, initBlackHole } from './blackhole';

gsap.registerPlugin(ScrollTrigger);

function initCinematicScroll() {
  const curtain = document.getElementById('load-curtain');
  
  // Custom Cursor
  const cursor = document.querySelector('.cursor') as HTMLElement;
  const cursorDot = document.querySelector('.cursor-dot') as HTMLElement;
  
  if (cursor && cursorDot) {
    if (window.matchMedia('(pointer: fine)').matches) {
      window.addEventListener('mousemove', (e) => {
        gsap.to(cursorDot, { x: e.clientX, y: e.clientY, xPercent: -50, yPercent: -50, duration: 0 });
        gsap.to(cursor, { x: e.clientX, y: e.clientY, xPercent: -50, yPercent: -50, duration: 0.15, ease: 'power2.out' });
      });
      
      document.querySelectorAll('a, button, .magnetic-link').forEach(link => {
        link.addEventListener('mouseenter', () => {
          cursor.classList.add('hover');
          cursorDot.style.transform = 'translate(-50%, -50%) scale(0.5)';
        });
        link.addEventListener('mouseleave', () => {
          cursor.classList.remove('hover');
          cursorDot.style.transform = 'translate(-50%, -50%) scale(1)';
        });
      });
    } else {
      cursor.style.display = 'none';
      cursorDot.style.display = 'none';
    }
  }

  // Scramble text intro
  const headline = document.getElementById('hero-headline');
  const role = document.getElementById('hero-role');
  if (headline && role) {
    const origHtml = headline.innerHTML;
    
    headline.textContent = 'INITIALIZING SYSTEM...';
    role.textContent = 'DECRYPTING IDENTITY...';
    role.style.opacity = '1';

    scrambleText(headline, 'Breathing life into the machine.', 1.0, () => {
      headline.innerHTML = origHtml;
      
      scrambleText(role, 'Adarsh Kumar Singh / AI Systems Engineer', 0.8, () => {
        // Animate out curtain
        curtain?.classList.add('is-done');
        setTimeout(() => curtain?.remove(), 1200);

        // Fade in hero content
        gsap.fromTo('.scroll-indicator', 
          { opacity: 0, y: 30 },
          { 
            opacity: 1, 
            y: 0, 
            duration: 2.0, 
            delay: 0.2, 
            ease: 'expo.out',
            onComplete: () => {
              // Smooth, cinematic pulsing blink on the text itself
              gsap.to('.scroll-text', {
                opacity: 0.2,
                duration: 1.2,
                yoyo: true,
                repeat: -1,
                ease: 'sine.inOut'
              });
            }
          }
        );
      });
    });
  }

  // Setup GSAP for each cinematic scene
  const scenes = document.querySelectorAll('.scene-content');
  
  // Hero Scroll Fade (Cinematic Dissolve)
  gsap.to('.fade-on-scroll', {
    y: -80,
    opacity: 0,
    filter: 'blur(10px)',
    scale: 0.9,
    ease: 'power2.inOut',
    scrollTrigger: {
      trigger: '#scene-hero',
      start: 'top top',
      end: 'top -40%', // Fades out very quickly when they start scrolling
      scrub: 1
    }
  });

  gsap.to('.glitch-wrapper', {
    y: -150,
    opacity: 0,
    filter: 'blur(20px)',
    scale: 1.15, // Moves towards camera
    ease: 'power2.inOut',
    scrollTrigger: {
      trigger: '#scene-hero',
      start: 'top top',
      end: 'bottom top',
      scrub: 1.5
    }
  });

  scenes.forEach((scene) => {
    if (scene.closest('#scene-hero')) {
      return;
    }

    gsap.fromTo(scene, 
      { opacity: 0, y: 100 },
      { 
        opacity: 1, 
        y: 0, 
        duration: 1.5,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: scene.parentElement,
          start: 'top 75%',
          toggleActions: 'play none none reverse'
        }
      }
    );
  });

  // Floating Tags Parallax (Desktop Only to prevent overlapping on tightly packed mobile flex layout)
  let mm = gsap.matchMedia();
  mm.add("(min-width: 768px)", () => {
    const tags = document.querySelectorAll('.float-tag');
    tags.forEach((tag) => {
      const speed = parseFloat(tag.getAttribute('data-speed') || '1');
      gsap.to(tag, {
        y: -200 * speed,
        rotation: speed * 15,
        ease: 'none',
        scrollTrigger: {
          trigger: '#scene-capabilities',
          start: 'top bottom',
          end: 'bottom top',
          scrub: true
        }
      });
    });
  });

  // System Fragments Parallax & 3D Tilt
  const fragments = document.querySelectorAll('.fragment');
  fragments.forEach((fragment, i) => {
    gsap.fromTo(fragment,
      { opacity: 0, x: i % 2 === 0 ? -80 : 80, y: 150 },
      {
        opacity: 1,
        x: 0,
        y: 0,
        duration: 1.2,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: fragment,
          start: 'top 95%',
          toggleActions: 'play none none reverse'
        }
      }
    );

    // Mouse-driven 3D Tilt
    fragment.addEventListener('mousemove', (e) => {
      const rect = fragment.getBoundingClientRect();
      const x = (e as MouseEvent).clientX - rect.left;
      const y = (e as MouseEvent).clientY - rect.top;
      
      const xPct = x / rect.width - 0.5;
      const yPct = y / rect.height - 0.5;
      
      gsap.to(fragment, {
        rotationY: xPct * 15,
        rotationX: -yPct * 15,
        boxShadow: `${-xPct * 20}px ${-yPct * 20}px 30px rgba(0, 240, 255, 0.1)`,
        duration: 0.5,
        ease: 'power2.out',
      });
    });

    fragment.addEventListener('mouseleave', () => {
      gsap.to(fragment, {
        rotationY: 0,
        rotationX: 0,
        boxShadow: 'none',
        duration: 0.5,
        ease: 'power2.out',
      });
      fragment.classList.remove('is-glitching');
    });

    // Hover Glitch
    fragment.addEventListener('mouseenter', () => {
      fragment.classList.add('is-glitching');
      setTimeout(() => fragment.classList.remove('is-glitching'), 300);
    });
  });

  // Velocity Noise Effect
  const noiseOverlay = document.querySelector('.noise-overlay');
  if(noiseOverlay) {
    ScrollTrigger.create({
      trigger: document.body,
      start: "top top",
      end: "bottom bottom",
      onUpdate: (self) => {
        const velocity = Math.abs(self.getVelocity());
        if (velocity > 500) {
          gsap.to(noiseOverlay, { opacity: 0.08, duration: 0.2 });
        } else {
          gsap.to(noiseOverlay, { opacity: 0.03, duration: 0.5 });
        }
      }
    });
  }

// Connect links Magnetic hover
  const links = document.querySelectorAll('.magnetic-link');
  links.forEach(link => {
    link.addEventListener('mousemove', (e) => {
      const rect = link.getBoundingClientRect();
      const x = (e as MouseEvent).clientX - rect.left - rect.width / 2;
      const y = (e as MouseEvent).clientY - rect.top - rect.height / 2;
      gsap.to(link, { x: x * 0.2, y: y * 0.2, duration: 0.3, ease: 'power2.out' });
    });
    link.addEventListener('mouseleave', () => {
      gsap.to(link, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.3)' });
    });
  });

  // Init Three.js
  initBlackHole();
  const camera = getCamera();
  
  if (camera) {
    // 3D Camera Dive Animation via GSAP ScrollTrigger
    // We start at y: 150, z: 400
    // We dive into y: 0, z: 0, rotation.x: Math.PI / 2
    
    gsap.to(camera.position, {
      y: -150,
      z: 10,
      ease: "power2.inOut",
      scrollTrigger: {
        trigger: ".cinematic-container",
        start: "top top",
        end: "bottom bottom",
        scrub: 1.5,
      }
    });

    gsap.to(camera.rotation, {
      x: Math.PI / 3, // Look down into the black hole!
      ease: "power2.inOut",
      scrollTrigger: {
        trigger: ".cinematic-container",
        start: "top top",
        end: "bottom bottom",
        scrub: 1.5,
      }
    });
  }
}

function initAmbientAudio() {
  let audioCtx: AudioContext | null = null;
  let isPlaying = false;

  const startAudio = () => {
    if (audioCtx) return;
    audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    
    // Create deep drone oscillators
    const osc1 = audioCtx.createOscillator();
    const osc2 = audioCtx.createOscillator();
    const lfo = audioCtx.createOscillator();
    const filter = audioCtx.createBiquadFilter();
    const gainNode = audioCtx.createGain();

    osc1.type = 'sine';
    osc1.frequency.value = 55; // Deep bass A1

    osc2.type = 'triangle';
    osc2.frequency.value = 55.5; // Slight detune for phasing

    lfo.type = 'sine';
    lfo.frequency.value = 0.1; // Slow sweep

    filter.type = 'lowpass';
    filter.frequency.value = 200;

    // Connect LFO to filter frequency
    const lfoGain = audioCtx.createGain();
    lfoGain.gain.value = 100;
    lfo.connect(lfoGain);
    lfoGain.connect(filter.frequency);

    gainNode.gain.value = 0.0; // Start silent

    osc1.connect(filter);
    osc2.connect(filter);
    filter.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    osc1.start();
    osc2.start();
    lfo.start();

    // Fade in
    gainNode.gain.setTargetAtTime(0.15, audioCtx.currentTime, 5.0);
    isPlaying = true;
  };

  // Start audio on first interaction (browser requirement)
  document.body.addEventListener('click', startAudio, { once: true });
  document.body.addEventListener('wheel', startAudio, { once: true });
}

export function init() {
  initCinematicScroll();
  initAmbientAudio();
  window.addEventListener('load', () => ScrollTrigger.refresh());

  return () => {
    ScrollTrigger.getAll().forEach((st) => st.kill());
  };
}

if (typeof window !== 'undefined') {
  const ready = () => init();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ready);
  } else {
    ready();
  }
}
