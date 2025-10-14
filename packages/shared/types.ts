// Shared types between frontend and backend

export interface ResumeDoc {
  id: string;
  sections: Section[];
}

export interface Section {
  id: string;
  title: string;
  roles?: Role[];
}

export interface Role {
  id: string;
  title: string;
  company: string;
  bullets: Bullet[];
}

export interface Bullet {
  id: string;
  text: string;
  targetPath: string;
}
