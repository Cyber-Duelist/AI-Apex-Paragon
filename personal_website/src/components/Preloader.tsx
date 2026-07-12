"use client";

import { useEffect, useRef } from "react";

const LOGS = [
  "initializing neural uplink",
  "loading agent runtime",
  "verifying guardrails",
  "mounting rag index",
  "entity signature confirmed",
];

export default function Preloader({ onDone }: { onDone: () => void }) {
  const root = useRef<HTMLDivElement | null>(null);
  const countRef = useRef<HTMLDivElement | null>(null);
  const barRef = useRef<HTMLSpanElement | null>(null);
  const logRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      onDone();
      return;
    }

    let raf = 0;
    let exitTimer = 0;
    let doneTimer = 0;
    const start = performance.now();
    const duration = 2100;

    const tick = (now: number) => {
      const linear = Math.min(1, (now - start) / duration);
      const progress = 1 - Math.pow(1 - linear, 3);
      const value = Math.round(progress * 100);

      if (countRef.current) {
        countRef.current.textContent = String(value).padStart(3, "0");
      }
      if (barRef.current) {
        barRef.current.style.width = `${progress * 100}%`;
      }
      if (logRef.current) {
        const i = Math.min(LOGS.length - 1, Math.floor(linear * LOGS.length));
        logRef.current.textContent = `> ${LOGS[i]}`;
      }

      if (linear < 1) {
        raf = window.requestAnimationFrame(tick);
        return;
      }

      exitTimer = window.setTimeout(() => {
        if (root.current) {
          root.current.style.opacity = "0";
          root.current.style.transform = "translateY(-2%)";
        }
        doneTimer = window.setTimeout(onDone, 520);
      }, 180);
    };

    raf = window.requestAnimationFrame(tick);

    return () => {
      window.cancelAnimationFrame(raf);
      window.clearTimeout(exitTimer);
      window.clearTimeout(doneTimer);
    };
  }, [onDone]);

  return (
    <div
      className="preloader"
      ref={root}
      style={{ transition: "opacity 500ms ease, transform 500ms ease" }}
    >
      <div className="preloader__inner">
        <div className="preloader__row">
          <span className="preloader__tag">Entity // boot sequence</span>
          <span className="preloader__tag">v4.0</span>
        </div>
        <div className="preloader__count" ref={countRef}>
          000
        </div>
        <div className="preloader__bar">
          <span ref={barRef} />
        </div>
        <div className="preloader__log" ref={logRef}>
          &gt; initializing neural uplink
        </div>
      </div>
    </div>
  );
}
