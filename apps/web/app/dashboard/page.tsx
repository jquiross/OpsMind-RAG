"use client";

import { useQuery } from "@tanstack/react-query";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { apiGet } from "@/lib/api";

type Dashboard = {
  total_queries: number;
  insufficient_evidence_queries: number;
  feedback_positive: number;
  feedback_negative: number;
  recent_queries: { id: string; question: string; confidence: number | null; created_at: string }[];
  top_documents: { document_title: string; hits: number }[];
};

export default function DashboardPage() {
  const { data, error, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiGet<Dashboard>("/api/analytics/dashboard"),
  });

  return (
    <div className="mx-auto max-w-5xl space-y-6 px-4 py-8">
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Consultas totales</CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">
            {isLoading ? "…" : data?.total_queries ?? 0}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Sin evidencia suficiente</CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">
            {isLoading ? "…" : data?.insufficient_evidence_queries ?? 0}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Feedback + / −</CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">
            {isLoading
              ? "…"
              : `${data?.feedback_positive ?? 0} / ${data?.feedback_negative ?? 0}`}
          </CardContent>
        </Card>
      </div>
      {error ? <p className="text-sm text-destructive">{(error as Error).message}</p> : null}
      <Card>
        <CardHeader>
          <CardTitle>Últimas consultas</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Pregunta</TableHead>
                <TableHead>Confianza</TableHead>
                <TableHead>Fecha</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(data?.recent_queries ?? []).map((q) => (
                <TableRow key={q.id}>
                  <TableCell className="max-w-xl truncate">{q.question}</TableCell>
                  <TableCell>{q.confidence != null ? (q.confidence * 100).toFixed(0) + "%" : "—"}</TableCell>
                  <TableCell className="text-xs text-muted-foreground">{q.created_at}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Chunks más recuperados</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Documento</TableHead>
                <TableHead>Hits</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(data?.top_documents ?? []).map((d) => (
                <TableRow key={d.document_title}>
                  <TableCell>{d.document_title}</TableCell>
                  <TableCell>{d.hits}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
