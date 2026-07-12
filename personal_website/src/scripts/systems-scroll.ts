import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function initSystemsScroll(): () => void {
  const section = document.getElementById('systems');
  const track = document.getElementById('systems-track');
  const nodes = document.querySelectorAll<HTMLElement>('[data-system-node]');

  if (!section || !track || nodes.length === 0) return () => {};

  const triggers: ScrollTrigger[] = [];

  const getScrollDistance = () => Math.max(0, track.scrollWidth - window.innerWidth + 80);

  const tween = gsap.to(track, {
    x: () => -getScrollDistance(),
    ease: 'none',
    scrollTrigger: {
      trigger: section,
      start: 'top top',
      end: () => `+=${getScrollDistance()}`,
      pin: true,
      scrub: 0.6,
      anticipatePin: 1,
      invalidateOnRefresh: true,
      onRefresh: () => {
        triggers.forEach((t) => t.kill());
        triggers.length = 0;
        initNodeBranches();
      },
    },
  });

  const mainTrigger = tween.scrollTrigger;
  if (mainTrigger) triggers.push(mainTrigger);

  function initNodeBranches() {
    nodes.forEach((node) => {
      const branch = node.querySelector<HTMLElement>('[data-branch]');
      if (!branch) return;

      gsap.set(branch, { scaleX: 0, transformOrigin: 'left center' });

      const st = ScrollTrigger.create({
        trigger: node,
        containerAnimation: tween,
        start: 'left 65%',
        end: 'right 35%',
        horizontal: true,
        scrub: 0.3,
        onEnter: () => node.classList.add('is-active'),
        onLeave: () => node.classList.remove('is-active'),
        onEnterBack: () => node.classList.add('is-active'),
        onLeaveBack: () => node.classList.remove('is-active'),
        onUpdate: (self) => {
          const scale = self.isActive ? self.progress : 0;
          gsap.set(branch, { scaleX: scale });
        },
      });

      triggers.push(st);
    });
  }

  initNodeBranches();

  return () => {
    tween.kill();
    triggers.forEach((t) => t.kill());
  };
}
