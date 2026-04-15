import Link from "next/link";

const links = [
  { href: "/", label: "Chat" },
  { href: "/upload", label: "Ingesta" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/eval", label: "Evaluación" },
];

export function SiteHeader() {
  return (
    <header className="border-b bg-background/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <div className="flex flex-col">
          <span className="text-sm font-semibold tracking-tight">OpsMind RAG</span>
          <span className="text-xs text-muted-foreground">Soporte técnico con recuperación híbrida</span>
        </div>
        <nav className="flex flex-wrap gap-2 text-sm">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="rounded-md px-2 py-1 text-muted-foreground hover:bg-muted hover:text-foreground"
            >
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
