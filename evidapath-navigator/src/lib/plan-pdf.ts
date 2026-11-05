// Downloadable PDF of the student's documents & tests checklist: one section per
// university with its cost, next deadline and every item ticked or not.
// jsPDF is loaded only when the student asks for the PDF.

import type { DecisionAnalysis, StudentInput } from "./decision-engine";
import { GROUP_ORDER, type DocItem } from "./documents";
import type { University } from "./mock-data";

export interface PdfUni {
  u: University;
  a: DecisionAnalysis;
  items: DocItem[];
}

// The built-in PDF fonts cover Latin-1 (plus £, €, —), not arrows or symbols.
const clean = (s: string) =>
  s
    .replace(/[→⟶]/g, "->")
    .replace(/≈/g, "~")
    .replace(/[✓✔]/g, "")
    .replace(/[‘’]/g, "'")
    .replace(/[“”]/g, '"')
    .replace(/[^\x20-\x7E\u00A0-\u00FF\u2013\u2014\u2026\u20AC]/g, "");

const fmt = (iso: string) =>
  new Date(`${iso.slice(0, 10)}T00:00:00Z`).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
const usd = (n: number | null) =>
  n == null ? "Not published" : `$${Math.round(n).toLocaleString("en-US")}`;

export async function downloadPlanPdf(unis: PdfUni[], done: Set<string>, input: StudentInput) {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const W = doc.internal.pageSize.getWidth();
  const H = doc.internal.pageSize.getHeight();
  const M = 48;
  let y = M;

  const need = (h: number) => {
    if (y + h > H - M) {
      doc.addPage();
      y = M;
    }
  };
  const text = (
    s: string,
    size: number,
    opts: { bold?: boolean; color?: number; indent?: number } = {},
  ) => {
    doc.setFont("helvetica", opts.bold ? "bold" : "normal");
    doc.setFontSize(size);
    doc.setTextColor(opts.color ?? 20);
    const x = M + (opts.indent ?? 0);
    const lines = doc.splitTextToSize(clean(s), W - x - M) as string[];
    for (const line of lines) {
      need(size * 1.35);
      doc.text(line, x, y);
      y += size * 1.35;
    }
  };

  text("EvidaPath: documents & tests checklist", 18, { bold: true });
  text(
    `${input.curriculum} · ${input.subject} · budget $${input.budgetUsd.toLocaleString("en-US")}/yr · made ${fmt(new Date().toISOString())}`,
    9,
    { color: 110 },
  );
  y += 8;

  for (const { u, a, items } of unis) {
    need(70);
    y += 6;
    doc.setDrawColor(210);
    doc.line(M, y, W - M, y);
    y += 16;
    text(`${u.name} (${u.city}, ${u.country})`, 13, { bold: true });
    const next = a.admissions.nextDeadline;
    text(
      `${a.programName} · cost per year ${usd(a.financial.annualUsd)}${a.financial.annualComplete ? " all-in" : " tuition only"}${
        next ? ` · next deadline ${fmt(next.date)} (${next.label})` : ""
      }`,
      9,
      { color: 90 },
    );
    const n = items.filter((i) => done.has(i.id)).length;
    text(`${n} of ${items.length} done`, 9, { color: 90 });
    y += 4;

    for (const g of GROUP_ORDER) {
      const list = items.filter((i) => i.group === g);
      if (!list.length) continue;
      need(30);
      text(g, 10, { bold: true, color: 40 });
      for (const i of list) {
        const mark = done.has(i.id) ? "[x]" : "[  ]";
        text(`${mark}  ${i.title}${i.date ? `  (by ${fmt(i.date)})` : ""}`, 10, { indent: 8 });
        if (i.detail) text(i.detail, 8.5, { indent: 26, color: 100 });
        if (i.source) text(i.source, 7.5, { indent: 26, color: 130 });
      }
      y += 4;
    }
  }

  y += 10;
  text(
    "Figures come from official university and government pages, checked by EvidaPath. Rules and dates change: check each official page before you rely on it. The English test date is our suggestion, not a requirement.",
    8,
    { color: 120 },
  );
  doc.save("evidapath-checklist.pdf");
}
