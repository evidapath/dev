import { useServerFn } from "@tanstack/react-start";
import { useEffect, useState } from "react";
import { currentCurriculum, defaultLanguages, GRADE_BANDS, parseLangs } from "./curricula";
import type { StudentInput } from "./decision-engine";
import { useLiveData, type LiveData } from "./use-live-data";
import { getProfile, listSavedUniversities } from "./profile.functions";
import { storedUkHome } from "./residence";

export const DEFAULT_STUDENT: StudentInput = {
  curriculum: "IB Diploma",
  gradeBand: GRADE_BANDS[1]!,
  subject: "Computer Science",
  budgetUsd: 40000,
  citizenship: "",
};

// Languages are remembered on this device (set in Find My Path).
function storedLanguages(curriculum: string): string[] {
  try {
    const v = parseLangs(localStorage.getItem("evidapath.languages"));
    if (v.length) return v;
  } catch {
    /* storage unavailable */
  }
  return defaultLanguages(curriculum);
}

/**
 * Everything a page needs to judge universities for this student: live data,
 * their answers (or sensible defaults when they haven't answered), and the
 * universities saved to their path.
 */
export function useStudent(): {
  data: LiveData | null;
  input: StudentInput;
  hasProfile: boolean;
  savedIds: string[];
  loading: boolean;
} {
  const { data, loading } = useLiveData();
  const fetchProfile = useServerFn(getProfile);
  const fetchSaved = useServerFn(listSavedUniversities);
  const [input, setInput] = useState<StudentInput>(DEFAULT_STUDENT);
  const [hasProfile, setHasProfile] = useState(false);
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let live = true;
    Promise.all([fetchProfile().catch(() => null), fetchSaved().catch(() => [])])
      .then(([p, saved]) => {
        if (!live) return;
        setSavedIds(saved.map((x) => x.sanity_university_id));
        if (p) {
          setHasProfile(true);
          setInput({
            curriculum: currentCurriculum(p.curriculum) || DEFAULT_STUDENT.curriculum,
            gradeBand: p.grade_band || DEFAULT_STUDENT.gradeBand,
            subject: p.intended_subject || DEFAULT_STUDENT.subject,
            budgetUsd: p.annual_budget ?? DEFAULT_STUDENT.budgetUsd,
            citizenship: p.citizenship || "",
            languages: storedLanguages(p.curriculum || DEFAULT_STUDENT.curriculum),
            ukHome: storedUkHome(),
          });
        }
      })
      .finally(() => live && setReady(true));
    return () => {
      live = false;
    };
  }, [fetchProfile, fetchSaved]);

  return { data, input, hasProfile, savedIds, loading: loading || !ready };
}
