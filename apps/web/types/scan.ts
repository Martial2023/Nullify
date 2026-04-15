import type { ScanStatus } from "./enums";
import type { Finding } from "./finding";

export interface Scan {
  id: string;
  tool: string;
  target: string;
  args: Record<string, unknown>;
  status: ScanStatus;
  output: string | null;
  error: string | null;
  projectId: string;
  startedBy: string | null;
  startedAt: Date;
  endedAt: Date | null;
}

export interface ScanWithFindings extends Scan {
  findings: Finding[];
}
