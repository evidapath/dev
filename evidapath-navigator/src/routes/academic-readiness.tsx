import { createFileRoute, redirect } from "@tanstack/react-router";

// The old readiness form asked the same questions as Find My Path but didn't save
// them to the profile. Old links and bookmarks now land on Find My Path, which
// saves the answers and sends the same lead form to the EvidaPath team.
export const Route = createFileRoute("/academic-readiness")({
  beforeLoad: () => {
    throw redirect({ to: "/find-my-path", replace: true });
  },
});
