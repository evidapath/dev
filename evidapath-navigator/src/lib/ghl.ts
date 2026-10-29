// Client-side form submission to the EvidaPath GHL (LeadConnector) sub-account.
// GHL creates/updates a Contact from first_name/last_name/email/phone and logs
// the submission (with every field) on the contact's Activity timeline.
// IDs below are the public form-tracking identifiers (not secrets).

const GHL_ENDPOINT = "https://backend.leadconnectorhq.com/external-tracking/events";
const TRACKING_ID = "tk_bcfd78bbcbbb4908bb2735dcd5436265";
const LOCATION_ID = "N1tn8tW6XdSkuGUNa8Z6";
const PROJECT_ID = "1790101091506917993";

/**
 * Send a form submission to GHL. Resolves only when GHL confirms receipt, so
 * callers can show success honestly; throws otherwise.
 */
export async function submitGhlForm(
  formId: string,
  formName: string,
  fields: Record<string, { label: string; value: string }>,
): Promise<void> {
  const formData: Record<string, string> = {};
  const formLabels: Record<string, string> = {};
  for (const [key, { label, value }] of Object.entries(fields)) {
    if (value.trim() === "") continue;
    formData[key] = value.trim();
    formLabels[key] = label;
  }

  const payload = {
    type: "external_form_submission",
    timestamp: Date.now(),
    formId,
    formData,
    formLabels,
    url: window.location.href,
    title: document.title,
    path: window.location.pathname,
    userAgent: navigator.userAgent,
    trackingId: TRACKING_ID,
    locationId: LOCATION_ID,
    projectId: PROJECT_ID,
    sessionId: crypto.randomUUID(),
    properties: {
      deviceType: /Mobile|Android|iPhone/i.test(navigator.userAgent) ? "mobile" : "desktop",
      source: "ai_studio",
      projectId: PROJECT_ID,
      formName,
    },
  };

  const body = new FormData();
  body.append("event", JSON.stringify(payload));
  const res = await fetch(GHL_ENDPOINT, {
    method: "POST",
    headers: { version: "2021-07-28" },
    body,
  });
  if (!res.ok) throw new Error(`GHL responded ${res.status}`);
}
