"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { apiGet, apiUpload } from "@/lib/api";

type DocRow = {
  id: string;
  title: string;
  source_type: string;
  processing_status: string;
  created_at: string;
};

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const docs = useQuery({
    queryKey: ["documents"],
    queryFn: () => apiGet<DocRow[]>("/api/documents"),
  });
  const upload = useMutation({
    mutationFn: async (f: File) => apiUpload(f),
    onSuccess: (data) => {
      setMsg(`Documento indexado: ${data.document_id}`);
      void docs.refetch();
    },
    onError: (e: Error) => setMsg(e.message),
  });

  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 py-8">
      <Card>
        <CardHeader>
          <CardTitle>Subir documento</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            type="file"
            accept=".txt,.md,.pdf,.json"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <Button
            disabled={!file || upload.isPending}
            onClick={() => file && upload.mutate(file)}
          >
            {upload.isPending ? "Procesando…" : "Subir e indexar"}
          </Button>
          {msg ? <p className="text-sm text-muted-foreground">{msg}</p> : null}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Documentos cargados</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Título</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Estado</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(docs.data ?? []).map((d) => (
                <TableRow key={d.id}>
                  <TableCell>{d.title}</TableCell>
                  <TableCell>{d.source_type}</TableCell>
                  <TableCell>{d.processing_status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
