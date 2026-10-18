/**
 * The evidence a Stage or Goal rests on, and whether it can be opened.
 *
 * The one rule this component exists to enforce: a citation the user cannot
 * resolve must say so. Rendering a claim as "sourced" when there is nothing to
 * open is worse than showing no citation at all, because the user stops
 * checking.
 *
 * `sources` is resolved by the backend. A ref missing from the map is
 * unresolvable, and is shown as such rather than silently dropped.
 */

export interface ResolvedSource {
  id: string;
  title: string;
  type: string;
  uri: string | null;
  status: string;
}

export interface EvidenceRef {
  source_id: string;
  segment_id?: string;
  quote_hint?: string;
}

const TYPE_LABELS: Record<string, string> = {
  text: "Pasted text",
  txt: "Text file",
  markdown: "Markdown",
  pdf: "PDF",
  url: "Web page",
  web_search: "Web research",
};

export function EvidencePanel({
  refs,
  sources,
  projectId,
  referenceMode = "project",
}: {
  refs: EvidenceRef[] | undefined;
  sources: Record<string, ResolvedSource>;
  projectId: string;
  referenceMode?: "project" | "local";
}) {
  const items = (refs ?? []).filter((ref) => ref?.source_id);
  if (items.length === 0) return null;

  return (
    <section className="evidence-panel">
      <p className="eyebrow">EVIDENCE</p>
      <ul>
        {items.map((ref, index) => {
          const resolved = sources[ref.source_id];
          return (
            <li key={`${ref.source_id}-${index}`}>
              {resolved ? (
                <a
                  className="evidence-link"
                  href={referenceMode === "local" ? `#source-${resolved.id}` : `/projects/${projectId}/sources#source-${resolved.id}`}
                >
                  <strong>{resolved.title}</strong>
                  <small>
                    {TYPE_LABELS[resolved.type] ?? resolved.type}
                    {resolved.status !== "ready" ? ` · ${resolved.status}` : ""}
                    {ref.quote_hint ? ` · “${ref.quote_hint}”` : ""}
                  </small>
                </a>
              ) : (
                // Named explicitly rather than hidden. A citation that silently
                // disappears leaves the reader believing the claim is sourced.
                <span className="evidence-missing">
                  <strong>Unresolved source: {ref.source_id}</strong>
                  <small>
                    This citation points at a source this project no longer has, so it cannot be
                    opened.
                  </small>
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
