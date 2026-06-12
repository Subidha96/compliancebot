'use client';

import { useState, useRef, useEffect } from 'react';

interface TooltipProps {
  term: string;
  definition: string;
  children: React.ReactNode;
}

export default function Tooltip({ term, definition, children }: TooltipProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  return (
    <span ref={ref} className="relative inline-block">
      <span
        className="tooltip-term"
        onClick={() => setOpen(!open)}
        onKeyDown={(e) => e.key === 'Enter' && setOpen(!open)}
        role="button"
        tabIndex={0}
        aria-label={`${term}: ${definition}`}
      >
        {children}
      </span>

      {open && (
        <span className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-warmgray-800 text-white text-xs rounded-xl shadow-lg animate-fade-in">
          <span className="font-medium block mb-1">{term}</span>
          <span className="text-warmgray-300">{definition}</span>
          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-warmgray-800" />
        </span>
      )}
    </span>
  );
}

export const TERM_DEFINITIONS: Record<string, string> = {
  'Data Fiduciary': 'An organization that collects and manages personal data and is responsible for protecting it.',
  'DPIA': 'Data Protection Impact Assessment — a process to identify and minimize data protection risks.',
  'ISMS': 'Information Security Management System — a set of policies for managing digital security.',
  'ISO 27001': 'An international standard for managing information security.',
  'NIST CSF': 'A voluntary framework from the US National Institute of Standards for managing cybersecurity.',
  'ETA 2063': 'Nepal\'s Electronic Transactions Act — the primary law governing cybercrime.',
  'NTA': 'Nepal Telecommunications Authority — the telecom regulator.',
  'PII': 'Personally Identifiable Information — any data that can identify an individual.',
  'GDPR': 'General Data Protection Regulation — the EU\'s data protection law.',
  'Incident Response': 'The process of identifying, containing, and recovering from security incidents.',
  'Access Control': 'Methods to restrict who can view or use resources in a computing environment.',
  'Third-Party Risk': 'Risks that come from vendors, suppliers, or partners who access your data or systems.',
};
