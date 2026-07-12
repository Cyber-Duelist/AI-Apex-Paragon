# Adarsh Kumar Singh — Portfolio

A scroll-driven portfolio built with **Astro + GSAP**. The page structure follows a request traveling through a multi-agent AI pipeline, with a continuous SVG signal line as the navigational spine.

## Stack

- Astro 7 (static site, GitHub Pages deployable)
- GSAP + ScrollTrigger (free core)
- IBM Plex Mono / IBM Plex Sans

## Development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

Output is written to `dist/` and configured for deployment at `https://cyber-duelist.github.io/AI-Apex-Paragon/`.

## Concept

Each section maps to a pipeline stage:

1. **Hero** — request enters
2. **Identity** — router resolves caller
3. **Capabilities** — known domains
4. **Systems** — multi-agent swarm (horizontal scroll)
5. **Architecture** — pipeline diagrams scrubbed to scroll
6. **Credentials** — guardrail checkpoint
7. **Connect** — verified output

The signal line (`stroke-dashoffset` driven by scroll progress) connects every section.
