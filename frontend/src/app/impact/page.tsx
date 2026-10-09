"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";

interface StoryStep {
  id: number;
  title: string;
  badge: string;
  highlightColor: string;
  borderColor: string;
  description: string;
  stat: string;
  statLabel: string;
  // Free stock HD video background loops
  videoUrl: string;
}

const STORY_STEPS: StoryStep[] = [
  {
    id: 1,
    title: "Massive Food Overproduction",
    badge: "1. Overproduction & Prep",
    highlightColor: "text-amber-400",
    borderColor: "border-amber-500/40",
    description:
      "Every single day, institutional canteens over-prepare food by 15% to 30%. Unconsumed rice, gravies, and meals are dumped directly into waste bins at scale.",
    stat: "1.3 Billion Tons",
    statLabel: "Global food wasted annually",
    videoUrl:
      "https://assets.mixkit.co/videos/preview/mixkit-throwing-food-into-the-trash-can-42289-large.mp4",
  },
  {
    id: 2,
    title: "Methane & Greenhouse Gas Emissions",
    badge: "2. Environmental Rot",
    highlightColor: "text-emerald-400",
    borderColor: "border-emerald-500/40",
    description:
      "As wasted food decomposes in landfills without oxygen, it creates potent methane gas (CH₄)—a greenhouse gas over 28 times more destructive than CO₂.",
    stat: "8% - 10%",
    statLabel: "Of global greenhouse emissions come from food waste",
    videoUrl:
      "https://assets.mixkit.co/videos/preview/mixkit-smoke-and-pollution-from-factory-chimneys-42864-large.mp4",
  },
  {
    id: 3,
    title: "Financial & Resource Drain",
    badge: "3. Direct Economic Loss",
    highlightColor: "text-red-400",
    borderColor: "border-red-500/40",
    description:
      "Over-preparing food wastes water, agricultural land, and energy—draining kitchen budgets by thousands of rupees monthly in discarded raw ingredients.",
    stat: "₹1,00,000+",
    statLabel: "Lost monthly per canteen facility in preventable waste",
    videoUrl:
      "https://assets.mixkit.co/videos/preview/mixkit-aerial-view-of-a-large-landfill-42291-large.mp4",
  },
];

export default function GlobalImpactVideoPage() {
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);

  const currentStep = STORY_STEPS[activeStepIndex];

  // Auto-advance video story every 7 seconds
  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(() => {
      setActiveStepIndex((prev) => (prev + 1) % STORY_STEPS.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [isPlaying]);

  return (
    <div className="relative min-h-screen bg-black text-white font-sans antialiased overflow-hidden flex flex-col justify-between">
      {/* Background Video Engine */}
      {STORY_STEPS.map((step, index) => (
        <video
          key={step.id}
          autoPlay
          loop
          muted
          playsInline
          className={`fixed inset-0 w-full h-full object-cover transition-opacity duration-1000 ${
            index === activeStepIndex ? "opacity-40 scale-105" : "opacity-0 scale-100"
          } transition-transform duration-10000 ease-linear`}
        >
          <source src={step.videoUrl} type="video/mp4" />
        </video>
      ))}

      {/* Dark Vignette Overlay for Text Readability */}
      <div className="fixed inset-0 bg-gradient-to-t from-black via-black/60 to-black/80 pointer-events-none" />

      {/* Header */}
      <header className="relative z-10 max-w-6xl mx-auto w-full p-6 md:p-8 flex justify-between items-center border-b border-white/10">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🌍</span>
          <h1 className="text-lg md:text-xl font-black tracking-wide uppercase">
            The Global Impact of Food Waste
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-white/20 bg-black/50 hover:bg-white/10 transition-all backdrop-blur-md"
          >
            {isPlaying ? "⏸️ Pause Story" : "▶️ Play Story"}
          </button>
          <Link
            href="/"
            className="text-xs font-bold bg-orange-600 hover:bg-orange-500 text-white px-4 py-2 rounded-xl transition-all shadow-lg shadow-orange-600/30"
          >
            Go to AI Predictor →
          </Link>
        </div>
      </header>

      {/* Main Content & Text Animation Area */}
      <main className="relative z-10 max-w-4xl mx-auto w-full px-6 py-12 my-auto">
        {/* Step Selector Controls */}
        <div className="flex justify-center gap-2 md:gap-4 mb-8">
          {STORY_STEPS.map((s, idx) => (
            <button
              key={s.id}
              onClick={() => {
                setActiveStepIndex(idx);
                setIsPlaying(false);
              }}
              className={`text-xs md:text-sm font-bold px-4 py-2 rounded-full border transition-all ${
                idx === activeStepIndex
                  ? "bg-orange-600 border-orange-500 text-white shadow-lg shadow-orange-600/40 scale-105"
                  : "bg-black/60 border-white/10 text-slate-400 hover:text-white backdrop-blur-md"
              }`}
            >
              {s.badge}
            </button>
          ))}
        </div>

        {/* Animated Text Display */}
        <div key={currentStep.id} className="animate-fade-in space-y-6 text-center md:text-left">
          <div className="inline-block px-3.5 py-1 rounded-full text-xs font-extrabold uppercase tracking-widest bg-white/10 border border-white/20 backdrop-blur-md">
            {currentStep.badge}
          </div>

          <h2 className={`text-3xl md:text-5xl font-black tracking-tight ${currentStep.highlightColor}`}>
            {currentStep.title}
          </h2>

          <p className="text-slate-200 text-base md:text-xl leading-relaxed max-w-3xl backdrop-blur-sm bg-black/20 p-4 rounded-2xl border border-white/5">
            {currentStep.description}
          </p>

          <div className={`inline-flex flex-col border-l-4 p-4 bg-black/50 backdrop-blur-md rounded-r-2xl ${currentStep.borderColor}`}>
            <span className={`text-3xl md:text-4xl font-extrabold ${currentStep.highlightColor}`}>
              {currentStep.stat}
            </span>
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider mt-1">
              {currentStep.statLabel}
            </span>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 max-w-6xl mx-auto w-full p-6 border-t border-white/10 flex flex-col md:flex-row justify-between items-center text-xs text-slate-400 gap-3">
        <p>AI Canteen Waste Optimization & Predictive Analytics System</p>
        <Link href="/" className="text-white hover:underline font-semibold">
          Return to Dashboard →
        </Link>
      </footer>
    </div>
  );
}