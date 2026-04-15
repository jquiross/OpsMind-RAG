import { ChatPanel } from "@/components/chat/chat-panel";

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6 space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Chat de soporte</h1>
        <p className="text-sm text-muted-foreground">
          Respuestas fundamentadas en documentación indexada, con citas y triage de incidentes.
        </p>
      </div>
      <ChatPanel />
    </div>
  );
}
