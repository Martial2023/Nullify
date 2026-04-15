import type { ReportStatus } from "./enums";

export interface Report {
  id: string;
  title: string;
  summary: string | null;
  content: Record<string, unknown> | null;
  status: ReportStatus;
  projectId: string;
  createdBy: string | null;
  createdAt: Date;
  updatedAt: Date;
}
