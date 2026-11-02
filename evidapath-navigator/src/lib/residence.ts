// Whether the student has lived in the UK for the last 3 years (UK "Home" fee
// status). Not part of the saved profile; remembered on this device, like
// study languages.
const KEY = "evidapath.ukHome";

export function storedUkHome(): boolean {
  try {
    return localStorage.getItem(KEY) === "1";
  } catch {
    return false;
  }
}

export function storeUkHome(v: boolean) {
  try {
    localStorage.setItem(KEY, v ? "1" : "0");
  } catch {
    /* storage unavailable */
  }
}
