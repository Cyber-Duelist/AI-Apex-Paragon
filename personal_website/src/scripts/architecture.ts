import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function initArchitecturePipelines(): () => void {
  const pipelines = document.querySelectorAll<HTMLElement>('[data-pipeline]');
  const triggers: ScrollTrigger[] = [];

  pipelines.forEach((pipeline) => {
    const nodes = pipeline.querySelectorAll<HTMLElement>('[data-pipeline-node]');
    const connectors = pipeline.querySelectorAll<HTMLElement>('[data-pipeline-connector]');
    const totalSteps = nodes.length;

    const st = ScrollTrigger.create({
      trigger: pipeline,
      start: 'top 75%',
      end: 'bottom 25%',
      scrub: 0.5,
      onUpdate: (self) => {
        const litCount = Math.floor(self.progress * totalSteps * 1.2);

        nodes.forEach((node, i) => {
          node.classList.toggle('is-lit', i < litCount);
        });

        connectors.forEach((connector, i) => {
          connector.classList.toggle('is-lit', i < litCount - 1);
        });
      },
    });

    triggers.push(st);
  });

  return () => {
    triggers.forEach((t) => t.kill());
  };
}
