"use client";

import { useMutation } from "@tanstack/react-query";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { apiPost } from "@/lib/api";
import type { ChatResponse } from "@/types/chat";

export function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const chatMutation = useMutation({
    mutationFn: async (q: string) =>
      apiPost<ChatResponse>("/api/chat", {
        question: q,
        retrieval_strategy: "hybrid_rerank",
        use_query_rewrite: true,
      }),
    onSuccess: (data) => {
      setAnswer(data);
      setError(null);
    },
    onError: (e: Error) => setError(e.message),
  });

  const feedbackMutation = useMutation({
    mutationFn: async (payload: { query_id: string; rating: number }) =>
      apiPost("/api/feedback", payload),
  });

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
      <Card>
        <CardHeader>
          <CardTitle>Consulta</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Textarea
            placeholder="Ej.: Why are users getting 401 after the SSO provider change?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={5}
          />
          <Button
            onClick={() => chatMutation.mutate(question)}
            disabled={!question.trim() || chatMutation.isPending}
          >
            {chatMutation.isPending ? "Pensando…" : "Enviar"}
          </Button>
          {error ? <p className="text-sm text-destructive">{error}</p> : null}
          {answer ? (
            <div className="space-y-3 pt-2">
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">Confianza {(answer.confidence * 100).toFixed(0)}%</Badge>
                <Badge variant="outline">Severidad {answer.severity}</Badge>
                {answer.insufficient_evidence ? (
                  <Badge variant="destructive">Evidencia insuficiente</Badge>
                ) : null}
              </div>
              <div>
                <h3 className="text-sm font-semibold">Resumen</h3>
                <p className="text-sm text-muted-foreground">{answer.summary}</p>
              </div>
              <div>
                <h3 className="text-sm font-semibold">Causa probable</h3>
                <p className="text-sm text-muted-foreground">{answer.probable_cause}</p>
              </div>
              <div>
                <h3 className="text-sm font-semibold">Pasos sugeridos</h3>
                <ul className="list-inside list-disc text-sm text-muted-foreground">
                  {answer.suggested_steps.map((s) => (
                    <li key={s}>{s}</li>
                  ))}
                </ul>
              </div>
              <Separator />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() =>
                    feedbackMutation.mutate({ query_id: answer.query_id, rating: 1 })
                  }
                >
                  <ThumbsUp className="mr-1 h-4 w-4" /> Útil
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() =>
                    feedbackMutation.mutate({ query_id: answer.query_id, rating: -1 })
                  }
                >
                  <ThumbsDown className="mr-1 h-4 w-4" /> No útil
                </Button>
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>
      <Card className="h-fit">
        <CardHeader>
          <CardTitle className="text-base">Fuentes</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[420px] pr-3">
            {answer?.citations?.length ? (
              <ul className="space-y-3 text-sm">
                {answer.citations.map((c) => (
                  <li key={c.chunk_id} className="rounded-md border p-2">
                    <div className="font-medium">{c.document_title}</div>
                    <div className="text-xs text-muted-foreground">chunk {c.chunk_id}</div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">Las citas aparecerán tras una respuesta.</p>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
