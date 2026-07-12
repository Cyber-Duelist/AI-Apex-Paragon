"use client";

import { useEffect, useRef } from "react";

export default function Cursor() {
  const dotRef = useRef<HTMLDivElement | null>(null);
  const ringRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    if (!fine) return;

    const dot = dotRef.current;
    const ring = ringRef.current;
    if (!dot || !ring) return;

    let mx = window.innerWidth / 2;
    let my = window.innerHeight / 2;
    let rx = mx;
    let ry = my;
    let raf = 0;

    const move = (e: PointerEvent) => {
      mx = e.clientX;
      my = e.clientY;
      dot.style.transform = `translate(${mx}px, ${my}px) translate(-50%, -50%)`;
    };

    const loop = () => {
      rx += (mx - rx) * 0.18;
      ry += (my - ry) * 0.18;
      ring.style.transform = `translate(${rx}px, ${ry}px) translate(-50%, -50%)`;
      raf = window.requestAnimationFrame(loop);
    };

    const over = (e: Event) => {
      const t = e.target as HTMLElement;
      if (t.closest("a, button, .card, .social")) {
        ring.style.width = "62px";
        ring.style.height = "62px";
        ring.style.borderColor = "rgba(53,224,255,0.9)";
      } else {
        ring.style.width = "40px";
        ring.style.height = "40px";
        ring.style.borderColor = "rgba(255,255,255,0.6)";
      }
    };

    window.addEventListener("pointermove", move);
    window.addEventListener("pointerover", over);
    raf = window.requestAnimationFrame(loop);

    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerover", over);
      window.cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <>
      <div className="cursor-dot" ref={dotRef} aria-hidden="true" />
      <div className="cursor-ring" ref={ringRef} aria-hidden="true" />
    </>
  );
}
