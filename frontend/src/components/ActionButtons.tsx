'use client';

interface SourceCitation {
  source: string;
  section: string;
  confidence: number;
  url?: string;
}

interface ActionButtonsProps {
  sources?: string[];
  sourceUrls?: string[];
  sourceCitations?: SourceCitation[];
}

export default function ActionButtons({ sources, sourceCitations }: ActionButtonsProps) {
  if (!sources || sources.length === 0) return null;

  const sourceLabels: Record<string, string> = {
    iso_27001_2022_controls_summary: 'ISO 27001:2022',
    nist_csf_2_0_summary: 'NIST CSF 2.0',
    electronic_transactions_act_2063_key_clauses: 'Electronic Transactions Act 2063',
    nepal_cyber_security_policy_2023_summary: 'Nepal Cyber Security Policy 2023',
    privacy_act_2075_summary: 'Privacy Act 2075',
    cyber_security_bylaw_2077_checklist: 'Cyber Security Bylaw 2077',
    nrb_corporate_governance_directive: 'NRB Governance Directive',
    oecd_principles_corporate_governance: 'OECD Principles',
    nepal_companies_act_2063_summary: 'Companies Act 2063',
    iso_37000_governance_summary: 'ISO 37000',
    nepal_labour_act_2074_summary: 'Labour Act 2074',
  };

  // Build URL lookup from sourceCitations (source name → first URL found)
  const urlBySource: Record<string, string> = {};
  if (sourceCitations) {
    for (const c of sourceCitations) {
      if (c.url && !urlBySource[c.source]) {
        urlBySource[c.source] = c.url;
      }
    }
  }

  // Deduplicate sources while preserving order
  const seen = new Set<string>();
  const uniqueSources = sources.filter((s) => {
    if (seen.has(s)) return false;
    seen.add(s);
    return true;
  });

  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {uniqueSources.map((src) => {
        const url = urlBySource[src];
        if (!url) return null;
        const label = sourceLabels[src] || src.replace(/_/g, ' ');
        return (
          <a
            key={src}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-warmgray-100 text-warmgray-600 text-xs font-medium hover:bg-warmgray-200 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.813a4.5 4.5 0 00-6.364 0l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
            </svg>
            Verify {label}
          </a>
        );
      })}
    </div>
  );
}
