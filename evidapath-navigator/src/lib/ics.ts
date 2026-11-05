// Calendar file (.ics) for plan deadlines, with alerts 14, 3 and 1 day before.
// Works with Google Calendar, Apple Calendar and Outlook, so students get
// reminders on their phone without any account or email set up.

export interface CalendarItem {
  id: string;
  date: string; // YYYY-MM-DD
  title: string;
  uni: string;
  source?: string;
}

const esc = (s: string) =>
  s
    .replace(/\\/g, "\\\\")
    .replace(/[,;]/g, (m) => `\\${m}`)
    .replace(/\n/g, "\\n");

/** Lines longer than 75 octets are folded, as the iCalendar format requires. */
function fold(line: string): string {
  const enc = new TextEncoder();
  const out: string[] = [];
  let cur = "";
  let bytes = 0;
  for (const ch of line) {
    const n = enc.encode(ch).length;
    if (bytes + n > 74) {
      out.push(cur);
      cur = " ";
      bytes = 1;
    }
    cur += ch;
    bytes += n;
  }
  out.push(cur);
  return out.join("\r\n");
}

function nextDay(d: string): string {
  const t = new Date(`${d}T00:00:00Z`);
  t.setUTCDate(t.getUTCDate() + 1);
  return t.toISOString().slice(0, 10).replace(/-/g, "");
}

export function buildIcs(items: CalendarItem[]): string {
  const stamp = new Date()
    .toISOString()
    .replace(/[-:]/g, "")
    .replace(/\.\d+Z$/, "Z");
  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//EvidaPath//Plan deadlines//EN",
    "CALSCALE:GREGORIAN",
    "X-WR-CALNAME:EvidaPath deadlines",
  ];
  for (const i of items) {
    const day = i.date.slice(0, 10);
    lines.push(
      "BEGIN:VEVENT",
      `UID:${esc(i.id)}@evidapath`,
      `DTSTAMP:${stamp}`,
      `DTSTART;VALUE=DATE:${day.replace(/-/g, "")}`,
      `DTEND;VALUE=DATE:${nextDay(day)}`,
      `SUMMARY:${esc(`${i.uni}: ${i.title}`)}`,
      `DESCRIPTION:${esc(
        `Deadline from your EvidaPath plan.${i.source ? `\nOfficial source: ${i.source}` : ""}\nCheck the official page before you rely on it.`,
      )}`,
      ...(i.source ? [`URL:${i.source}`] : []),
    );
    for (const before of ["P14D", "P3D", "P1D"])
      lines.push(
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        `DESCRIPTION:${esc(`${i.uni}: ${i.title}`)}`,
        `TRIGGER:-${before}`,
        "END:VALARM",
      );
    lines.push("END:VEVENT");
  }
  lines.push("END:VCALENDAR");
  return lines.map(fold).join("\r\n") + "\r\n";
}

export function downloadIcs(items: CalendarItem[], filename = "evidapath-deadlines.ics") {
  const blob = new Blob([buildIcs(items)], { type: "text/calendar;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
