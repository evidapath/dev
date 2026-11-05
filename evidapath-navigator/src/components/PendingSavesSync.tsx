import { useServerFn } from "@tanstack/react-start";
import { useEffect, useRef } from "react";
import { toast } from "sonner";
import { useAuth } from "./AuthContext";
import { saveUniversity } from "../lib/profile.functions";
import { clearPendingSaves, readPendingSaves } from "../lib/use-save-university";

/**
 * Moves universities saved while signed out (kept on this device) into the
 * student's account as soon as they sign in or sign up. Renders nothing.
 */
export function PendingSavesSync() {
  const { user } = useAuth();
  const saveFn = useServerFn(saveUniversity);
  const running = useRef(false);

  useEffect(() => {
    if (!user || running.current) return;
    const pending = readPendingSaves();
    if (!pending.length) return;
    running.current = true;
    Promise.allSettled(
      pending.map((x) => saveFn({ data: { sanity_university_id: x.id, university_name: x.name } })),
    )
      .then((results) => {
        const ok = pending.filter((_, i) => results[i]!.status === "fulfilled").map((x) => x.id);
        clearPendingSaves(ok);
        if (ok.length)
          toast.success(
            `Added ${ok.length} saved universit${ok.length === 1 ? "y" : "ies"} to your path.`,
          );
        if (ok.length < pending.length)
          console.error("[pending saves] some saves failed; kept on this device to retry.");
      })
      .finally(() => {
        running.current = false;
      });
  }, [user, saveFn]);

  return null;
}
