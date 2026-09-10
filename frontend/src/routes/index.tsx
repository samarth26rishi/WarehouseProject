import { createFileRoute } from "@tanstack/react-router";
import { ArrowRight, Box, Check, ChevronRight, Eye, GitBranch, Layers3, MessageSquareText, ScanLine, ShieldCheck, Sparkles, Video } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Warehouse AI Field Intelligence — Prevent handling damage" },
      { name: "description", content: "AI video intelligence that helps warehouse teams catch risky handling before it becomes damage." },
      { property: "og:title", content: "Warehouse AI Field Intelligence" },
      { property: "og:description", content: "Catch risky handling before it becomes damage." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <main className="min-h-screen overflow-hidden bg-background text-foreground">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
        <div className="flex items-center gap-3">
          <div className="flex size-9 items-center justify-center border border-amber/60 bg-amber/10 text-amber"><ScanLine size={20} /></div>
          <div><p className="font-display text-sm font-semibold tracking-tight">WAREHOUSE AI</p><p className="text-[10px] uppercase tracking-[0.22em] text-muted-foreground">Field intelligence</p></div>
        </div>
        <div className="hidden items-center gap-8 text-sm text-muted-foreground md:flex"><a href="#approach" className="transition-colors hover:text-foreground">The shift</a><a href="#capabilities" className="transition-colors hover:text-foreground">Capabilities</a><a href="#trust" className="transition-colors hover:text-foreground">Responsible AI</a></div>
        <a href="/dashboard" className="group inline-flex items-center gap-2 border border-border px-4 py-2 text-sm font-semibold text-foreground transition-colors hover:border-amber/60 hover:bg-amber/10">Open dashboard <ArrowRight size={15} className="transition-transform group-hover:translate-x-0.5" /></a>
      </nav>

      <section className="relative mx-auto grid max-w-7xl items-center gap-16 px-6 pb-24 pt-14 lg:grid-cols-[0.9fr_1.1fr] lg:px-10 lg:pb-36 lg:pt-20">
        <div className="relative z-10"><div className="mb-7 flex items-center gap-3 text-xs font-semibold uppercase tracking-[0.24em] text-amber"><span className="h-px w-10 bg-amber" /> Live operational intelligence</div><h1 className="max-w-xl text-balance text-5xl font-medium leading-[0.98] tracking-tight sm:text-7xl">Catch risky handling <span className="text-amber">before</span> it becomes damage.</h1><p className="mt-7 max-w-lg text-lg leading-8 text-muted-foreground">Turn loading-bay footage into clear, coachable signals. Warehouse AI helps teams spot unsafe patterns early, understand why they matter, and improve the next move.</p><div className="mt-9 flex flex-wrap items-center gap-4"><a href="/dashboard" className="group inline-flex items-center gap-3 bg-amber px-5 py-3 text-sm font-bold text-amber-foreground transition-transform hover:-translate-y-0.5">Launch demo <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" /></a><span className="text-xs text-muted-foreground">Mock operations environment · Shift A</span></div></div>
        <div className="relative min-h-[380px] lg:min-h-[500px]"><div className="absolute inset-0 border border-border/70 bg-surface-inset scanline" /><div className="absolute -left-3 top-8 h-16 w-1 border-l border-t border-amber/80" /><div className="absolute -right-3 bottom-8 h-16 w-1 border-b border-r border-cyan/80" /><div className="absolute inset-8 border border-cyan/30"><div className="absolute left-[16%] top-[18%] h-[56%] w-[16%] border border-cyan/70 bg-cyan/5" /><div className="absolute left-[18%] top-[12%] bg-cyan px-2 py-1 text-[9px] font-bold uppercase tracking-widest text-cyan-foreground">person_02 · 92%</div><div className="absolute left-[49%] top-[48%] h-[24%] w-[23%] border border-amber bg-amber/10" /><div className="absolute left-[50%] top-[42%] bg-amber px-2 py-1 text-[9px] font-bold uppercase tracking-widest text-amber-foreground">box_07 · risk</div><div className="absolute bottom-[18%] left-[12%] right-[10%] h-px bg-cyan/30" /><div className="absolute bottom-[18%] left-[12%] h-4 w-px bg-cyan/60" /><div className="absolute bottom-[18%] right-[10%] h-4 w-px bg-cyan/60" /><div className="absolute bottom-5 left-5 flex items-center gap-2 text-[10px] uppercase tracking-widest text-cyan"><span className="size-1.5 animate-pulse bg-cyan" /> Tracking active</div><div className="absolute bottom-5 right-5 font-mono text-[10px] text-muted-foreground">BAY 01 / CAM 01 / 00:02:14</div></div><div className="absolute right-0 top-0 flex items-center gap-2 border border-border bg-card px-3 py-2 text-xs text-muted-foreground"><span className="size-2 bg-risk-high" /> High-risk event detected</div><div className="absolute bottom-0 left-0 border border-border bg-card p-4"><p className="text-[10px] uppercase tracking-widest text-muted-foreground">Observed behaviour</p><p className="mt-1 font-display text-sm font-semibold">Loss of hand contact</p><div className="mt-3 flex items-center gap-2 text-[10px] text-amber"><span className="h-px w-6 bg-amber" /> potential damage risk</div></div></div>
      </section>

      <section id="approach" className="border-y border-border bg-surface-2"><div className="mx-auto max-w-7xl px-6 py-20 lg:px-10"><div className="max-w-2xl"><p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan">The shift we're building toward</p><h2 className="mt-4 text-3xl font-medium tracking-tight sm:text-5xl">From reviewing incidents to preventing them.</h2></div><div className="mt-14 grid gap-10 lg:grid-cols-2"><Pipeline label="Traditional CCTV" muted items={["Camera", "Recording", "Human review", "Incident discovered", "Corrective action"]} /><Pipeline label="Warehouse AI" items={["Camera", "AI perception", "Behaviour understanding", "Risk detection", "Alert", "Intervention", "Learning"]} /></div></div></section>

      <section id="capabilities" className="mx-auto max-w-7xl px-6 py-24 lg:px-10"><div className="flex flex-wrap items-end justify-between gap-8"><div><p className="text-xs font-semibold uppercase tracking-[0.22em] text-amber">A clearer operational picture</p><h2 className="mt-4 text-3xl font-medium tracking-tight sm:text-5xl">Signals your team can act on.</h2></div><p className="max-w-sm text-sm leading-6 text-muted-foreground">The system turns complex footage into a shared language for safer, more consistent handling.</p></div><div className="mt-14 grid border-l border-t border-border sm:grid-cols-2 lg:grid-cols-3">{capabilities.map((item) => <div key={item.title} className="group min-h-52 border-b border-r border-border p-7 transition-colors hover:bg-surface-2"><div className="flex size-10 items-center justify-center border border-border text-amber transition-colors group-hover:border-amber/60 group-hover:bg-amber/10">{item.icon}</div><h3 className="mt-6 font-display text-lg font-semibold">{item.title}</h3><p className="mt-2 text-sm leading-6 text-muted-foreground">{item.copy}</p></div>)}</div></section>

      <section id="trust" className="mx-auto max-w-7xl px-6 pb-24 lg:px-10"><div className="border border-cyan/40 bg-cyan/5 p-7 sm:p-10"><div className="flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between"><div className="flex gap-5"><div className="flex size-12 shrink-0 items-center justify-center border border-cyan/50 text-cyan"><ShieldCheck size={24} /></div><div><p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan">Responsible by design</p><h2 className="mt-3 text-2xl font-medium">Evidence before conclusions.</h2><p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">Warehouse AI separates what the camera observes from what it means operationally. It never automatically claims damage occurred without evidence.</p></div></div><div className="grid shrink-0 gap-2 text-sm sm:min-w-64"><TrustStep icon={<Eye size={14} />} text="Observed behaviour" /><TrustStep icon={<GitBranch size={14} />} text="Potential risk" /><TrustStep icon={<Check size={14} />} text="Confirmed damage" /></div></div></div></section>

      <footer className="border-t border-border"><div className="mx-auto flex max-w-7xl flex-col gap-8 px-6 py-12 sm:flex-row sm:items-center sm:justify-between lg:px-10"><div><p className="font-display font-semibold">Better signals. Better handling.</p><p className="mt-1 text-sm text-muted-foreground">A field intelligence prototype for warehouse teams.</p></div><a href="/dashboard" className="group inline-flex items-center gap-2 text-sm font-semibold text-amber">Explore the dashboard <ChevronRight size={16} className="transition-transform group-hover:translate-x-1" /></a></div></footer>
    </main>
  );
}

const capabilities = [
  { title: "AI video understanding", copy: "Read movement, objects, and context across loading-bay footage.", icon: <Video size={19} /> },
  { title: "Behaviour detection", copy: "Identify drops, drags, rough handling, and unstable stacking.", icon: <ScanLine size={19} /> },
  { title: "Damage-risk detection", copy: "Prioritise the moments most likely to lead to product damage.", icon: <ShieldCheck size={19} /> },
  { title: "AI operations assistant", copy: "Ask plain-language questions and get answers grounded in events.", icon: <MessageSquareText size={19} /> },
  { title: "Visual alerts", copy: "Bring important events forward with clear, consistent signals.", icon: <Sparkles size={19} /> },
  { title: "Prevention & learning", copy: "Turn recurring patterns into focused process improvements.", icon: <Layers3 size={19} /> },
];

function Pipeline({ label, items, muted = false }: { label: string; items: string[]; muted?: boolean }) {
  return <div className={muted ? "opacity-65" : ""}><div className="mb-4 flex items-center justify-between"><p className="text-sm font-semibold">{label}</p><span className="text-[10px] uppercase tracking-widest text-muted-foreground">{muted ? "after the fact" : "in the moment"}</span></div><div className="flex flex-wrap items-center gap-2">{items.map((item, index) => <div key={item} className="flex items-center gap-2"><span className={`border px-3 py-2 text-xs ${muted ? "border-border bg-card text-muted-foreground" : index > 3 ? "border-amber/50 bg-amber/10 text-amber" : "border-cyan/40 bg-cyan/5 text-cyan"}`}>{item}</span>{index < items.length - 1 && <ArrowRight size={13} className="shrink-0 text-muted-foreground" />}</div>)}</div></div>;
}

function TrustStep({ icon, text }: { icon: React.ReactNode; text: string }) { return <div className="flex items-center gap-3 border-b border-cyan/20 pb-2 text-sm last:border-0">{icon}<span>{text}</span></div>; }
