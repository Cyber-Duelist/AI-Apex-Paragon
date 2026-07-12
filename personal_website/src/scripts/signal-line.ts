import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

type Point = { x: number; y: number };

const SIGNAL_X = 40;

function getAnchorPoints(): Point[] {
  const anchors = document.querySelectorAll<HTMLElement>('[data-signal-anchor]');
  return Array.from(anchors).map((el) => {
    const rect = el.getBoundingClientRect();
    const y = rect.top + window.scrollY + Math.min(rect.height * 0.35, 120);
    return { x: SIGNAL_X, y };
  });
}

function buildPath(points: Point[]): string {
  if (points.length < 2) return '';

  let d = `M ${points[0].x} ${points[0].y}`;

  for (let i = 1; i < points.length; i++) {
    const prev = points[i - 1];
    const curr = points[i];
    const midY = (prev.y + curr.y) / 2;

    // Slight horizontal jog at each section for circuit-trace feel
    const jog = i % 2 === 0 ? 18 : -8;
    d += ` C ${prev.x + jog} ${midY}, ${curr.x - jog} ${midY}, ${curr.x} ${curr.y}`;
  }

  return d;
}

function setPathLength(path: SVGPathElement): number {
  const length = path.getTotalLength();
  path.style.strokeDasharray = `${length}`;
  path.style.strokeDashoffset = `${length}`;
  return length;
}

function moveGlow(glow: HTMLElement, path: SVGPathElement, progress: number) {
  const length = path.getTotalLength();
  const point = path.getPointAtLength(length * progress);
  glow.style.left = `${point.x}px`;
  glow.style.top = `${point.y}px`;
}

export function initSignalLine(): () => void {
  const overlay = document.getElementById('signal-overlay') as SVGSVGElement | null;
  const mainPath = document.getElementById('main-signal-path') as SVGPathElement | null;
  const previewPath = document.getElementById('preview-signal-path') as SVGPathElement | null;
  const glow = document.getElementById('signal-glow');
  const navItems = document.querySelectorAll<HTMLElement>('.pipeline-nav__item');
  const connectSection = document.getElementById('connect');

  if (!overlay || !mainPath || !previewPath || !glow) return () => {};

  let pathLength = 0;
  let scrollTrigger: ScrollTrigger | null = null;

  const refresh = () => {
    const points = getAnchorPoints();
    const d = buildPath(points);
    mainPath.setAttribute('d', d);
    previewPath.setAttribute('d', d);

    const svgHeight = document.documentElement.scrollHeight;
    overlay.setAttribute('viewBox', `0 0 ${window.innerWidth} ${svgHeight}`);
    overlay.style.height = `${svgHeight}px`;

    pathLength = setPathLength(mainPath);
    const previewLen = setPathLength(previewPath);
    previewPath.style.strokeDashoffset = `${previewLen * 0.15}`;

    scrollTrigger?.kill();
    scrollTrigger = ScrollTrigger.create({
      trigger: document.body,
      start: 'top top',
      end: 'bottom bottom',
      scrub: 0.4,
      onUpdate: (self) => {
        const progress = self.progress;
        mainPath.style.strokeDashoffset = `${pathLength * (1 - progress)}`;
        moveGlow(glow, mainPath, progress);

        // Pipeline nav highlighting
        const stageCount = navItems.length;
        navItems.forEach((item, i) => {
          const threshold = (i + 0.5) / stageCount;
          item.classList.toggle('is-active', progress >= i / stageCount && progress < threshold + 0.15);
          item.classList.toggle('is-passed', progress >= threshold);
        });

        // Resolved terminal point
        if (connectSection) {
          const connectRect = connectSection.getBoundingClientRect();
          const nearEnd = connectRect.top < window.innerHeight * 0.6;
          glow.classList.toggle('is-resolved', nearEnd);
        }
      },
    });

    ScrollTrigger.refresh();
  };

  // Hero intro: draw preview + partial main line
  glow.classList.add('is-visible');
  refresh();

  const introOffset = { value: pathLength };
  gsap.to(introOffset, {
    value: pathLength * 0.12,
    duration: 1.8,
    ease: 'power2.inOut',
    onUpdate: () => {
      mainPath.style.strokeDashoffset = `${introOffset.value}`;
      const progress = 1 - introOffset.value / pathLength;
      moveGlow(glow, mainPath, Math.max(0, progress));
    },
    onComplete: () => {
      ScrollTrigger.refresh();
    },
  });

  window.addEventListener('resize', refresh);

  return () => {
    scrollTrigger?.kill();
    window.removeEventListener('resize', refresh);
  };
}
