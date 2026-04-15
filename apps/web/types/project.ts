import type { ProjectRole, InviteStatus } from "./enums";

export interface ProjectPreview {
  id: string;
  name: string;
  updatedAt: Date;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  targets: string[];
  ownerId: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ProjectMember {
  id: string;
  role: ProjectRole;
  status: InviteStatus;
  userId: string;
  projectId: string;
  invitedBy: string | null;
  joinedAt: Date | null;
  createdAt: Date;
}

export interface ProjectWithMembers extends Project {
  members: ProjectMember[];
}
