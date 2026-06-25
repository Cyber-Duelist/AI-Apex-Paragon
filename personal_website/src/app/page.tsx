"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Terminal, Zap } from "lucide-react";

export default function PersonalWebsite() {
  const [isDecrypted, setIsDecrypted] = useState(false);

  useEffect(() => {
    // Artificial delay for the decryption sequence
    const timer = setTimeout(() => {
      setIsDecrypted(true);
    }, 4500); // 4.5 seconds of glitchy terminal
    return () => clearTimeout(timer);
  }, []);

  return (
    <main className="relative min-h-screen w-full bg-black overflow-hidden flex items-center justify-center text-white selection:bg-[#00e5ff] selection:text-black">
      <AnimatePresence mode="wait">
        {!isDecrypted ? (
          <NeuralDecryption key="loader" />
        ) : (
          <EntityHub key="hub" />
        )}
      </AnimatePresence>
    </main>
  );
}

// --- Component: Neural Decryption ---
function NeuralDecryption() {
  const [lines, setLines] = useState<string[]>([]);

  useEffect(() => {
    const hexChars = "0123456789ABCDEF";
    const getRandomHex = (len: number) =>
      Array.from({ length: len })
        .map(() => hexChars[Math.floor(Math.random() * hexChars.length)])
        .join("");

    const logMessages = [
      "INITIALIZING NEURAL UPLINK...",
      "BYPASSING SECURITY PROTOCOLS [FAILED]",
      "REROUTING THROUGH PROXY: 192.168.0.x",
      "DECRYPTING CORE MAINFRAME",
      `EXTRACTING HASH: ${getRandomHex(16)}`,
      "QUANTUM STATE: STABLE",
      "AWAITING ENTITY SIGNATURE...",
      "ACCESS GRANTED.",
      "ACCESSING ENTITY MAINFRAME..."
    ];

    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < logMessages.length) {
        setLines((prev) => [...prev, logMessages[currentIndex]]);
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 400);

    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, filter: "blur(10px)", scale: 1.1 }}
      transition={{ duration: 0.8, ease: "easeInOut" }}
      className="absolute inset-0 flex flex-col justify-center items-start md:p-24 p-8 font-mono text-xs md:text-sm tracking-widest text-[#00e5ff]/70 z-50"
    >
      <div className="max-w-2xl w-full flex flex-col gap-2">
        {lines.map((line, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className={`
              ${i === lines.length - 1 ? "text-[#b44dff] font-bold animate-pulse text-base md:text-lg mt-4" : ""}
            `}
          >
            {i === lines.length - 1 ? "> " + line : `[sys_log]: ${line}`}
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

// --- Component: Entity Hub ---
function EntityHub() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 1.5, ease: [0.22, 1, 0.36, 1] }}
      className="relative z-10 flex flex-col items-center justify-center w-full max-w-5xl p-6"
    >
      {/* Central Glowing Aura */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60vw] h-[60vw] max-w-[600px] max-h-[600px] bg-[#b44dff] opacity-10 blur-[100px] md:blur-[140px] rounded-full animate-pulse pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[30vw] h-[30vw] max-w-[300px] max-h-[300px] bg-[#00e5ff] opacity-10 blur-[60px] md:blur-[100px] rounded-full animate-pulse pointer-events-none mix-blend-screen" />

      {/* Main Identity */}
      <div className="text-center z-10 mb-16 mt-8">
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 1 }}
          className="font-mono text-[#00e5ff] text-xs md:text-sm tracking-[0.4em] uppercase mb-4"
        >
          System Architect
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, filter: "blur(10px)" }}
          animate={{ opacity: 1, filter: "blur(0px)" }}
          transition={{ delay: 0.8, duration: 1.5 }}
          className="text-4xl md:text-7xl font-bold tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-br from-white via-white to-zinc-500"
        >
          ADARSH KUMAR SINGH
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2, duration: 1 }}
          className="text-[#a0a0b8] max-w-lg mx-auto text-sm md:text-base leading-relaxed"
        >
          Engineering the intersection of artificial intelligence and high-performance web ecosystems. Operating under the moniker ENTITY.
        </motion.p>
      </div>

      {/* Navigation Portals */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.5, duration: 1 }}
        className="flex flex-col md:flex-row gap-6 w-full max-w-2xl justify-center z-10"
      >
        <PortalButton 
          href="/AI-Apex-Paragon/"
          icon={<Zap className="w-5 h-5 group-hover:text-[#00e5ff] transition-colors duration-500" />}
          title="ENTER PORTFOLIO"
          subtitle="Explore highly detailed architectural case studies, the 3D Neural Swarm, and speak with my AI assistant."
          primary
        />
        <PortalButton 
          href="https://github.com/Cyber-Duelist"
          icon={<Terminal className="w-5 h-5 group-hover:text-[#b44dff] transition-colors duration-500" />}
          title="ACCESS LOGS"
          subtitle="Review raw source code, experimental commits, and repository metrics directly via GitHub."
        />
      </motion.div>
    </motion.div>
  );
}

// --- Helper: Portal Button ---
function PortalButton({ href, icon, title, subtitle, primary = false }: any) {
  return (
    <a 
      href={href}
      className={`group relative flex flex-col p-8 rounded-3xl border backdrop-blur-xl overflow-hidden transition-all duration-500 flex-1 hover:-translate-y-2 hover:shadow-[0_20px_40px_rgba(0,0,0,0.5)]
        ${primary 
          ? "bg-white/[0.03] border-white/10 hover:bg-white/10 hover:border-[#00e5ff]/40" 
          : "bg-transparent border-white/5 hover:bg-white/[0.08] hover:border-[#b44dff]/40"
        }
      `}
    >
      <div className="flex items-center gap-4 mb-4 text-[#a0a0b8]">
        {icon}
        <span className="font-mono text-xs md:text-sm tracking-[0.2em] font-medium text-white">{title}</span>
      </div>
      <p className="text-sm text-zinc-400 leading-relaxed relative z-10">
        {subtitle}
      </p>

      {/* Internal Glint hover effect */}
      <div className="absolute inset-0 w-[200%] h-full -translate-x-full group-hover:translate-x-[100%] bg-gradient-to-r from-transparent via-white/5 to-transparent transition-transform duration-1000 ease-out skew-x-[-25deg] pointer-events-none" />
    </a>
  );
}
