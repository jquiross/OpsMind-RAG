"use client";

import { useQuery } from "@tanstack/react-query";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { apiGet } from "@/lib/api";

type EvalRun = {
  id: string;
  name: string;
  dataset_name: string;
  created_at: string;
  metrics_json: Record<string, Record<string, number>>;
};

export default function EvalPage() {
  const { data } = useQuery({
    queryKey: ["eval-runs"],
    queryFn: () => apiGet<EvalRun[]>("/api/eval/runs"),
  });

  const latest = data?.[0];

  return (
    <div className="mx-auto max-w-5xl space-y-6 px-4 py-8">
      <Card>
        <CardHeader>
          <CardTitle>Última corrida de evaluación</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          {latest ? (
            <p>
              {latest.name} — {latest.dataset_name} — {latest.created_at}
            </p>
          ) : (
            <p>Ejecuta `python scripts/run_eval.py` para generar métricas.</p>
          )}
        </CardContent>
      </Card>
      {latest?.metrics_json ? (
        <Card>
          <CardHeader>
            <CardTitle>Comparativa de estrategias</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Estrategia</TableHead>
                  <TableHead>hit@5</TableHead>
                  <TableHead>precision@5</TableHead>
                  <TableHead>MRR</TableHead>
                  <TableHead>p50 ms</TableHead>
                  <TableHead>p95 ms</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(latest.metrics_json).map(([name, m]) => (
                  <TableRow key={name}>
                    <TableCell className="font-medium">{name}</TableCell>
                    <TableCell>{(m["hit_rate@5"] ?? 0).toFixed(3)}</TableCell>
                    <TableCell>{(m["precision@5"] ?? 0).toFixed(3)}</TableCell>
                    <TableCell>{(m["mrr"] ?? 0).toFixed(3)}</TableCell>
                    <TableCell>{(m["latency_p50_ms"] ?? 0).toFixed(1)}</TableCell>
                    <TableCell>{(m["latency_p95_ms"] ?? 0).toFixed(1)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
