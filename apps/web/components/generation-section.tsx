"use client";

import { useRouter } from "next/navigation";

import { GenerationPanel } from "./generation-panel";

interface GenerationSectionProps {
  projectId: string;
  topic: string;
  scopeHint: string;
  learnerLevel: "new" | "some_experience" | "advanced";
  depth: "fast" | "standard" | "deep";
  sourceIds: string[];
}

/**
 * Client wrapper that revalidates the server-rendered project page once a
 * candidate exists, so the overview switches from setup mode to the published
 * workspace without the user having to reload by hand.
 */
export function GenerationSection(props: GenerationSectionProps) {
  const router = useRouter();
  return (
    <GenerationPanel
      {...props}
      onCandidateReady={() => router.refresh()}
    />
  );
}
