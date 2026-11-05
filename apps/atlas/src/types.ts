export interface Source {
  id: string;
  title: string;
  url: string;
  evidence: string;
  location?: string;
  source_type?: string;
  source_class?: string;
  [key: string]: unknown;
}
export interface Possibility {
  id: string;
  title: string;
  result: string;
  status: "source_supported" | "proposed" | "reviewed";
  availability: "core" | "extension" | "unknown";
  conditions?: string;
  group_ids: string[];
  source_ids: string[];
  evidence_refs?: { source_id: string; quote: string; location?: string; url?: string }[];
  aliases?: string[];
  keywords?: string[];
  capability_layer?: string;
  required_components?: string[];
  reviewed_by?: unknown;
  [key: string]: unknown;
}
export interface Topic {
  slug: string;
  title: string;
  domain_id: string;
  status: "ready" | "planned";
  priority: number;
  description: string;
}
export interface Summary {
  slug: string;
  count: number;
  groups: number;
  supported: number;
  proposed: number;
  researchDate: string;
  scope: string;
}
export interface AtlasMap {
  topic: { name: string; scope: string; [key: string]: unknown };
  sources: Source[];
  groups: { id: string; name: string }[];
  possibilities: Possibility[];
  coverage_gaps: string[];
  [key: string]: unknown;
}
export interface Bundle {
  slug: string;
  map: AtlasMap;
  markdown: string;
  validationReport: string;
  provenance: { revision: string; jsonSha256: string; markdownSha256: string };
}
export interface Library {
  catalog: {
    domains: { id: string; title: string; description: string }[];
    topics: Topic[];
  };
  summaries: Summary[];
  search: { slug: string; possibility: Possibility }[];
  revision: string;
}
export interface Route {
  slug?: string;
  pid?: string;
  view: "map" | "report" | "sources";
  sourceId?: string;
  q: string;
  group: string;
  availability: string;
  status: string;
  domain: string;
  invalid?: boolean;
}
