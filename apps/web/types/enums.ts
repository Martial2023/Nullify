export const ProjectRole = {
  OWNER: "OWNER",
  ADMIN: "ADMIN",
  MEMBER: "MEMBER",
  VIEWER: "VIEWER",
} as const;
export type ProjectRole = (typeof ProjectRole)[keyof typeof ProjectRole];

export const InviteStatus = {
  PENDING: "PENDING",
  ACCEPTED: "ACCEPTED",
  DECLINED: "DECLINED",
} as const;
export type InviteStatus = (typeof InviteStatus)[keyof typeof InviteStatus];

export const MessageRole = {
  USER: "USER",
  ASSISTANT: "ASSISTANT",
  TOOL: "TOOL",
} as const;
export type MessageRole = (typeof MessageRole)[keyof typeof MessageRole];

export const ScanStatus = {
  PENDING: "PENDING",
  RUNNING: "RUNNING",
  COMPLETED: "COMPLETED",
  FAILED: "FAILED",
  CANCELLED: "CANCELLED",
} as const;
export type ScanStatus = (typeof ScanStatus)[keyof typeof ScanStatus];

export const Severity = {
  CRITICAL: "CRITICAL",
  HIGH: "HIGH",
  MEDIUM: "MEDIUM",
  LOW: "LOW",
  INFO: "INFO",
} as const;
export type Severity = (typeof Severity)[keyof typeof Severity];

export const FindingStatus = {
  OPEN: "OPEN",
  CONFIRMED: "CONFIRMED",
  FALSE_POSITIVE: "FALSE_POSITIVE",
  RESOLVED: "RESOLVED",
} as const;
export type FindingStatus =
  (typeof FindingStatus)[keyof typeof FindingStatus];

export const ReportStatus = {
  GENERATING: "GENERATING",
  READY: "READY",
  FAILED: "FAILED",
} as const;
export type ReportStatus =
  (typeof ReportStatus)[keyof typeof ReportStatus];
