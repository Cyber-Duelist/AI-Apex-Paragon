"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  animate,
  createScope,
  createTimeline,
  onScroll,
  stagger,
  utils,
  type Scope,
} from "animejs";
import Preloader from "@/components/Preloader";
import Cursor from "@/components/Cursor";
import HeroField from "@/components/HeroField";
import {
  CAPABILITIES,
  CERTS,
  METRICS,
  NAV_LINKS,
  PROFILE,
  PROJECTS,
  SOCIALS,
  STACK,
} from "@/content/data";

function SplitLine({ text }: { text: string }) {
  return (
    <span className="row" aria-hidden="true">
      {Array.from(text).map((ch, i) => (
        <span className="char" key={`${ch}-${i}`}>
          {ch === " " ? "\u00a0" : ch}
        </span>
      ))}
    </span>
  );
}

export default function Home() {
  const [booted, setBooted] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const pageRef = useRef<HTMLDivElement | null>(null);
  const navRef = useRef<HTMLElement | null>(null);

  const onDone = useCallback(() => setBooted(true), []);

  // Nav sticky state
  useEffect(() => {
    const nav = navRef.current;
    if (!nav) return;
    const onScrollWin = () => {
      if (window.scrollY > 40) nav.classList.add("is-stuck");
      else nav.classList.remove("is-stuck");
    };
    onScrollWin();
    window.addEventListener("scroll", onScrollWin, { passive: true });
    return () => window.removeEventListener("scroll", onScrollWin);
  }, []);

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  // Main animation choreography, runs once booted
  useEffect(() => {
    if (!booted) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let scope: Scope | null = null;

    scope = createScope({ root: pageRef }).add(() => {
      if (!reduce) {
        const tl = createTimeline({ defaults: { ease: "out(3)" } });
        tl.add(".hero__tag", { opacity: [0, 1], y: [20, 0], duration: 600 })
          .add(
            ".hero__title .char",
            {
              opacity: [0, 1],
              y: ["120%", "0%"],
              rotate: ["6deg", "0deg"],
              duration: 900,
              delay: stagger(22),
            },
            "-=280",
          )
          .add(".hero__lead", { opacity: [0, 1], y: [24, 0], duration: 700 }, "-=520")
          .add(
            ".hero__meta > *",
            { opacity: [0, 1], y: [16, 0], duration: 600, delay: stagger(70) },
            "-=420",
          );
      }

      // Scroll reveals
      utils.$(".reveal").forEach((el) => {
        animate(el, {
          opacity: [0, 1],
          translateY: [46, 0],
          duration: 950,
          ease: "out(3)",
          autoplay: onScroll({ target: el as HTMLElement, enter: "bottom-=60 top", repeat: false }),
        });
      });

      // Metric counters
      utils.$(".metric__num").forEach((el) => {
        const node = el as HTMLElement;
        const target = Number(node.dataset.count || "0");
        const suffix = node.dataset.suffix || "";
        const obj = { v: 0 };
        node.textContent = `0${suffix}`;
        animate(obj, {
          v: target,
          duration: 1700,
          ease: "out(4)",
          autoplay: onScroll({ target: node, enter: "bottom-=40 top", repeat: false }),
          onUpdate: () => {
            node.textContent = `${Math.round(obj.v)}${suffix}`;
          },
        });
      });
    });

    return () => {
      scope?.revert();
    };
  }, [booted]);

  // Card tilt + glow
  useEffect(() => {
    if (!booted) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const cards = Array.from(document.querySelectorAll<HTMLElement>(".card"));

    const handlers: Array<() => void> = [];
    cards.forEach((card) => {
      const onMove = (e: PointerEvent) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width;
        const py = (e.clientY - r.top) / r.height;
        card.style.setProperty("--mx", `${px * 100}%`);
        card.style.setProperty("--my", `${py * 100}%`);
        if (!reduce) {
          const rx = (0.5 - py) * 8;
          const ry = (px - 0.5) * 8;
          card.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-4px)`;
        }
      };
      const onLeave = () => {
        card.style.transform = "";
      };
      card.addEventListener("pointermove", onMove);
      card.addEventListener("pointerleave", onLeave);
      handlers.push(() => {
        card.removeEventListener("pointermove", onMove);
        card.removeEventListener("pointerleave", onLeave);
      });
    });

    return () => handlers.forEach((fn) => fn());
  }, [booted]);

  return (
    <div ref={pageRef}>
      {!booted && <Preloader onDone={onDone} />}
      <Cursor />

      <nav className="nav" ref={navRef}>
        <a className="nav__brand" href="#top">
          <span className="dot" />
          {PROFILE.alias}
        </a>
        <div className="nav__links">
          {NAV_LINKS.map((l) => (
            <a key={l.href} href={l.href}>
              {l.label}
            </a>
          ))}
        </div>
        <a className="nav__cta" href={`mailto:${PROFILE.email}`}>
          Let&apos;s talk
        </a>
        <button
          className="nav__toggle"
          type="button"
          aria-label={mobileOpen ? "Close navigation" : "Open navigation"}
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen((open) => !open)}
        >
          <span />
          <span />
        </button>
      </nav>

      <div
        className={`mobile-nav${mobileOpen ? " is-open" : ""}`}
        aria-hidden={!mobileOpen}
      >
        <div className="mobile-nav__links">
          {NAV_LINKS.map((link, index) => (
            <a
              key={link.href}
              href={link.href}
              tabIndex={mobileOpen ? 0 : -1}
              onClick={() => setMobileOpen(false)}
            >
              <span>{String(index + 1).padStart(2, "0")}</span>
              {link.label}
            </a>
          ))}
        </div>
        <a
          className="mobile-nav__mail"
          href={`mailto:${PROFILE.email}`}
          tabIndex={mobileOpen ? 0 : -1}
          onClick={() => setMobileOpen(false)}
        >
          {PROFILE.email} ↗
        </a>
      </div>

      <main className="shell" id="top">
        {/* HERO */}
        <section className="hero wrap">
          <HeroField />
          <div className="hero__grid">
            <span className="hero__tag">
              {PROFILE.role} — {PROFILE.location}
            </span>
            <h1 className="hero__title">
              <span className="sr-only">
                {PROFILE.headline.join(" ")}
              </span>
              {PROFILE.headline.map((line) => (
                <SplitLine key={line} text={line} />
              ))}
            </h1>
            <p className="hero__lead">{PROFILE.intro}</p>
            <div className="hero__meta">
              <span>{PROFILE.name}</span>
              <span>Available for AI / ML roles</span>
              <span>Est. 2024</span>
            </div>
          </div>
          <div className="scroll-hint">
            <span>Scroll</span>
            <span className="rail" />
          </div>
        </section>

        {/* MARQUEE */}
        <div className="marquee" aria-hidden="true">
          <div className="marquee__track">
            {[0, 1].map((dup) => (
              <span className="marquee__group" key={dup}>
                {[
                  "Generative AI",
                  "Multi-Agent Systems",
                  "RAG Pipelines",
                  "Production Guardrails",
                  "Model Routing",
                ].map((t) => (
                  <span className="marquee__item" key={t}>
                    <span className="star">✦</span> {t}
                  </span>
                ))}
              </span>
            ))}
          </div>
        </div>

        {/* ABOUT */}
        <section className="section wrap" id="about">
          <span className="eyebrow reveal">About</span>
          <div className="about__grid" style={{ marginTop: "2.5rem" }}>
            <div>
              <p className="about__lead reveal">
                I build <b>autonomous AI systems</b> that ship — not tutorials. From{" "}
                <b>multi-agent orchestration</b> to <b>production RAG</b>, I care about the
                parts that break in the real world: latency, safety, failover and cost.
              </p>
              <p className="about__body reveal">
                Backend and AI engineer focused on turning research-grade ideas into
                dependable services. My work pairs LLM reasoning with rigorous engineering —
                typed APIs, guardrails, evaluation loops and observability — so systems stay
                trustworthy under pressure.
              </p>
            </div>
            <div className="metrics reveal">
              {METRICS.map((m) => (
                <div className="metric" key={m.label}>
                  <div
                    className="metric__num gradient-text"
                    data-count={m.value}
                    data-suffix={m.suffix}
                  >
                    {m.value}
                    {m.suffix}
                  </div>
                  <div className="metric__label">{m.label}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="caps">
            {CAPABILITIES.map((c) => (
              <div className="cap reveal" key={c.index}>
                <span className="cap__idx">{c.index}</span>
                <h3 className="cap__title">{c.title}</h3>
                <div>
                  <p className="cap__blurb">{c.blurb}</p>
                  <div className="cap__tags">
                    {c.tags.map((t) => (
                      <span className="chip" key={t}>
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* WORK */}
        <section className="section wrap" id="work">
          <div className="work__head">
            <div>
              <span className="eyebrow reveal">Selected work</span>
              <h2 className="section-title reveal">
                Systems, <span className="gradient-text">shipped.</span>
              </h2>
            </div>
            <span className="work__count reveal">
              {String(PROJECTS.length).padStart(2, "0")} projects
            </span>
          </div>

          <div className="cards">
            {PROJECTS.map((p) => (
              <article className="card reveal" data-accent={p.accent} key={p.id}>
                <div className="card__top">
                  <span className="card__accent" />
                  <span>{p.year}</span>
                </div>
                <div>
                  <p className="card__kicker">{p.kicker}</p>
                  <h3 className="card__name">{p.name}</h3>
                </div>
                <p className="card__summary">{p.summary}</p>
                <div className="card__stack">
                  {p.stack.map((s) => (
                    <span className="chip" key={s}>
                      {s}
                    </span>
                  ))}
                </div>
                <div className="card__links">
                  <a href={p.repo} target="_blank" rel="noopener noreferrer">
                    Code <span className="arrow">↗</span>
                  </a>
                  {p.live && (
                    <a href={p.live} target="_blank" rel="noopener noreferrer">
                      Live <span className="arrow">↗</span>
                    </a>
                  )}
                </div>
              </article>
            ))}
          </div>
        </section>

        {/* STACK */}
        <section className="section wrap" id="stack">
          <div className="stack__grid">
            <div>
              <span className="eyebrow reveal">Stack</span>
              <h2 className="section-title reveal">Tools I reach for.</h2>
              <div className="taglist">
                {STACK.map((s) => (
                  <span className="chip reveal" key={s}>
                    {s}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="eyebrow reveal">Certified</span>
              <div className="certs">
                {CERTS.map((c, i) => (
                  <div className="cert reveal" key={c}>
                    <span className="idx">{String(i + 1).padStart(2, "0")}</span>
                    <span>{c}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CONTACT */}
        <section className="section wrap contact" id="contact">
          <span className="eyebrow reveal" style={{ justifyContent: "center" }}>
            Contact
          </span>
          <h2 className="contact__big reveal">
            Let&apos;s build <span className="gradient-text">something</span> real.
          </h2>
          <a className="contact__mail reveal" href={`mailto:${PROFILE.email}`}>
            {PROFILE.email}
          </a>

          <div className="socials reveal">
            {SOCIALS.map((s) => (
              <a
                className="social"
                key={s.label}
                href={s.href}
                target={s.href.startsWith("http") ? "_blank" : undefined}
                rel={s.href.startsWith("http") ? "noopener noreferrer" : undefined}
              >
                <span className="social__label">{s.label}</span>
                <span className="social__handle">
                  {s.handle} <span className="arrow">↗</span>
                </span>
              </a>
            ))}
          </div>

          <div className="footer">
            <span>© {new Date().getFullYear()} {PROFILE.name}</span>
            <a className="to-top" href="#top">
              Back to top ↑
            </a>
          </div>
        </section>
      </main>
    </div>
  );
}
