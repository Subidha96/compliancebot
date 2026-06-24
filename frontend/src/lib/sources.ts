const SOURCE_MAP: Record<string, { name: string; icon: string; color: string }> = {
  iso_27001_2022_controls_summary: {
    name: 'ISO 27001:2022',
    icon: '🛡️',
    color: 'blue',
  },
  nist_csf_2_0_summary: {
    name: 'NIST CSF 2.0',
    icon: 'Framework',
    color: 'indigo',
  },
  nepal_cyber_security_policy_2023_summary: {
    name: 'Nepal Cyber Security Policy 2023',
    icon: '🇳🇵',
    color: 'emerald',
  },
  electronic_transactions_act_2063_key_clauses: {
    name: 'Electronic Transactions Act 2063',
    icon: '⚖️',
    color: 'amber',
  },
  privacy_act_2075_summary: {
    name: 'Privacy Act 2075',
    icon: '🔒',
    color: 'rose',
  },
  cyber_security_bylaw_2077_checklist: {
    name: 'Cyber Security Bylaw 2077',
    icon: '📋',
    color: 'violet',
  },
};

const COLOR_MAP: Record<string, { bg: string; bgDark: string; text: string; textDark: string; border: string; borderDark: string }> = {
  blue: {
    bg: 'bg-blue-50',
    bgDark: 'bg-blue-950/40',
    text: 'text-blue-700',
    textDark: 'text-blue-300',
    border: 'border-blue-200',
    borderDark: 'border-blue-800',
  },
  indigo: {
    bg: 'bg-indigo-50',
    bgDark: 'bg-indigo-950/40',
    text: 'text-indigo-700',
    textDark: 'text-indigo-300',
    border: 'border-indigo-200',
    borderDark: 'border-indigo-800',
  },
  emerald: {
    bg: 'bg-emerald-50',
    bgDark: 'bg-emerald-950/40',
    text: 'text-emerald-700',
    textDark: 'text-emerald-300',
    border: 'border-emerald-200',
    borderDark: 'border-emerald-800',
  },
  amber: {
    bg: 'bg-amber-50',
    bgDark: 'bg-amber-950/40',
    text: 'text-amber-700',
    textDark: 'text-amber-300',
    border: 'border-amber-200',
    borderDark: 'border-amber-800',
  },
  rose: {
    bg: 'bg-rose-50',
    bgDark: 'bg-rose-950/40',
    text: 'text-rose-700',
    textDark: 'text-rose-300',
    border: 'border-rose-200',
    borderDark: 'border-rose-800',
  },
  violet: {
    bg: 'bg-violet-50',
    bgDark: 'bg-violet-950/40',
    text: 'text-violet-700',
    textDark: 'text-violet-300',
    border: 'border-violet-200',
    borderDark: 'border-violet-800',
  },
};

export function getSourceInfo(source: string) {
  return SOURCE_MAP[source] ?? {
    name: source.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    icon: '📄',
    color: 'gray',
  };
}

export function getColors(color: string, dark: boolean) {
  const palette = COLOR_MAP[color] ?? COLOR_MAP.blue;
  return dark
    ? { bg: palette.bgDark, text: palette.textDark, border: palette.borderDark }
    : { bg: palette.bg, text: palette.text, border: palette.border };
}

export function cleanSectionName(section: string): string {
  let cleaned = section
    .replace(/\s*\(part\s*\d+\)/gi, '')
    .replace(/\s*\(Part\s*\d+\)/g, '')
    .replace(/^part-\d+$/i, 'Reference')
    .replace(/^CHAPTER\s+(\d+),?\s*/i, 'Ch. $1: ')
    .replace(/^Sections?\s*/i, 'Sec. ');
  if (cleaned.length > 60) {
    cleaned = cleaned.slice(0, 57) + '...';
  }
  return cleaned;
}

export const ALL_SOURCES = Object.entries(SOURCE_MAP).map(([key, val]) => ({
  id: key,
  ...val,
}));
