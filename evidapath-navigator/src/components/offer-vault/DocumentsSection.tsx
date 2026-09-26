import { useRef, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { FileCheck2, Upload, Trash2 } from "lucide-react";
import { Button } from "../ui/button";
import { getSupabaseBrowserClient } from "../../lib/supabase-browser";
import { createDocumentRecord, deleteDocument } from "../../lib/offer-vault.functions";
import type { DocumentType, StudentOfferDocument } from "../../lib/offer-vault.types";
import { DOCUMENT_TYPES } from "../../lib/offer-vault.types";
import { SectionCard, inputCls } from "./shared";

export function DocumentsSection({
  offerId,
  documents,
  onMutated,
}: {
  offerId: string;
  documents: StudentOfferDocument[];
  onMutated: () => void;
}) {
  const createDocFn = useServerFn(createDocumentRecord);
  const deleteDocFn = useServerFn(deleteDocument);
  const fileRef = useRef<HTMLInputElement>(null);
  const [docType, setDocType] = useState<DocumentType>("offer_letter");
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const supabase = getSupabaseBrowserClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");
      const path = `${user.id}/${offerId}/${Date.now()}-${file.name}`;
      const { error: upErr } = await supabase.storage
        .from("student-documents")
        .upload(path, file, { cacheControl: "3600", upsert: false });
      if (upErr) throw new Error(upErr.message);
      await createDocFn({
        data: {
          offer_id: offerId,
          document_type: docType,
          storage_path: path,
          file_name: file.name,
          mime_type: file.type || null,
          size_bytes: file.size || null,
        },
      });
      onMutated();
      toast.success("Document uploaded.");
    } catch (e) {
      toast.error(
        (e as Error).message || "Upload failed. Ensure the student-documents bucket exists.",
      );
    } finally {
      setUploading(false);
    }
  };

  const delMut = useMutation({
    mutationFn: (id: string) => deleteDocFn({ data: { id } }),
    onSuccess: () => {
      onMutated();
      toast.success("Document removed.");
    },
    onError: (e: Error) => toast.error(e.message || "Could not remove document."),
  });

  const viewDoc = async (storagePath: string) => {
    try {
      const supabase = getSupabaseBrowserClient();
      const { data, error } = await supabase.storage
        .from("student-documents")
        .createSignedUrl(storagePath, 300);
      if (error || !data?.signedUrl) throw new Error(error?.message ?? "No URL");
      window.open(data.signedUrl, "_blank", "noopener,noreferrer");
    } catch (e) {
      toast.error((e as Error).message || "Could not open document.");
    }
  };

  return (
    <SectionCard
      title="Offer & award documents"
      subtitle="Upload letters to verify your awards. Files are private — signed-URL access only."
      action={
        <div className="flex items-center gap-2">
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value as DocumentType)}
            className="h-8 px-2 rounded-lg border border-input bg-background text-xs text-foreground"
          >
            {DOCUMENT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.replace(/_/g, " ")}
              </option>
            ))}
          </select>
          <input
            ref={fileRef}
            type="file"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) handleUpload(f);
              e.target.value = "";
            }}
          />
          <Button
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
            size="sm"
            className="bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-semibold flex items-center gap-1.5"
          >
            <Upload className="w-3.5 h-3.5" /> {uploading ? "Uploading…" : "Upload"}
          </Button>
        </div>
      }
    >
      {documents.length === 0 ? (
        <p className="text-xs text-muted-foreground py-4 text-center">
          No documents yet. Upload an offer or scholarship letter to support award verification.
        </p>
      ) : (
        <div className="space-y-2">
          {documents.map((d) => (
            <div
              key={d.id}
              className="flex items-center justify-between gap-3 rounded-xl border border-border p-3"
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <FileCheck2 className="w-4 h-4 text-primary shrink-0" />
                <div className="min-w-0">
                  <button
                    onClick={() => viewDoc(d.storage_path)}
                    className="text-sm text-foreground hover:text-primary truncate block max-w-[260px]"
                  >
                    {d.file_name}
                  </button>
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wide">
                    {d.document_type.replace(/_/g, " ")}
                  </span>
                </div>
              </div>
              <button
                onClick={() => delMut.mutate(d.id)}
                className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </SectionCard>
  );
}

// keep inputCls referenced to avoid unused import in some build configs
export const _docInputCls = inputCls;
