import { useServerFn } from "@tanstack/react-start";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { useAuth } from "../components/AuthContext";
import { listSavedUniversities, saveUniversity } from "./profile.functions";

// Saving a university needs an account. Signed in, it goes to the account
// (Supabase, RLS-scoped). Signed out, the pick is remembered on this device, the
// student is sent to sign up, and PendingSavesSync saves it once they're in.

const KEY = "evidapath.pendingSaves";
const EVENT = "evidapath:pending-saves";

export type PendingSave = { id: string; name: string | null };

export function readPendingSaves(): PendingSave[] {
  try {
    const v = JSON.parse(localStorage.getItem(KEY) || "[]");
    return Array.isArray(v) ? v.filter((x) => x && typeof x.id === "string") : [];
  } catch {
    return [];
  }
}

function writePendingSaves(list: PendingSave[]) {
  try {
    if (list.length) localStorage.setItem(KEY, JSON.stringify(list));
    else localStorage.removeItem(KEY);
  } catch {
    // Storage blocked (private mode): the save still shows for this visit.
  }
  window.dispatchEvent(new Event(EVENT));
}

export function addPendingSaves(items: PendingSave[]) {
  const cur = readPendingSaves();
  const have = new Set(cur.map((x) => x.id));
  writePendingSaves([...cur, ...items.filter((x) => !have.has(x.id))]);
}

export function clearPendingSaves(ids: string[]) {
  const drop = new Set(ids);
  writePendingSaves(readPendingSaves().filter((x) => !drop.has(x.id)));
}

/** Where a signed-out Save goes: the sign-up page, then back to this page. */
export function signUpHref() {
  const back = window.location.pathname + window.location.search;
  return `/sign-in?mode=signup&redirect=${encodeURIComponent(back)}`;
}

/**
 * Saved universities plus a save() that works for everyone. `savedIds` covers the
 * account's list when signed in and the device's list when signed out.
 */
export function useSaveUniversity() {
  const { user } = useAuth();
  const saveFn = useServerFn(saveUniversity);
  const listFn = useServerFn(listSavedUniversities);
  const [accountIds, setAccountIds] = useState<Set<string>>(new Set());
  const [deviceIds, setDeviceIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    const sync = () => setDeviceIds(new Set(readPendingSaves().map((x) => x.id)));
    sync();
    window.addEventListener(EVENT, sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener(EVENT, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  useEffect(() => {
    let active = true;
    if (!user) {
      setAccountIds(new Set());
      return;
    }
    listFn()
      .then((rows) => active && setAccountIds(new Set(rows.map((r) => r.sanity_university_id))))
      .catch(() => {});
    return () => {
      active = false;
    };
    // deviceIds: re-read the account after PendingSavesSync moves device saves into it.
  }, [user, listFn, deviceIds]);

  const savedIds = user ? new Set([...accountIds, ...deviceIds]) : deviceIds;

  /** Save one or more universities. Resolves true when all were saved to the account. */
  const save = useCallback(
    async (items: PendingSave[], label: string): Promise<boolean> => {
      const fresh = items.filter((x) => !accountIds.has(x.id));
      if (!user) {
        // Keep what they picked, then ask them to create an account first.
        // PendingSavesSync saves it to the new account once they're signed in.
        addPendingSaves(fresh);
        toast(`Create a free account to save ${label}.`);
        window.location.assign(signUpHref());
        return false;
      }
      const results = await Promise.allSettled(
        fresh.map((x) => saveFn({ data: { sanity_university_id: x.id, university_name: x.name } })),
      );
      const ok = fresh.filter((_, i) => results[i]!.status === "fulfilled").map((x) => x.id);
      setAccountIds((s) => new Set([...s, ...ok]));
      if (ok.length === fresh.length) return true;
      const err = results.find((r) => r.status === "rejected") as PromiseRejectedResult | undefined;
      console.error("[save university] failed:", err?.reason);
      toast.error("Could not save — please try again.");
      return false;
    },
    [user, accountIds, saveFn],
  );

  return { savedIds, save, signedIn: !!user };
}
