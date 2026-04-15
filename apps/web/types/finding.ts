import type { Severity, FindingStatus } from "./enums";

export interface Finding {
  id: string;
  severity: Severity;
  status: FindingStatus;
  title: string;
  description: string;
  target: string | null;
  evidence: string | null;
  remediation: string | null;
  scanId: string;
  createdAt: Date;
  updatedAt: Date;
}
