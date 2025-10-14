import type { ResumeDoc, Section, Role, Bullet } from "../../../packages/shared/types";

// TipTap JSON structure
interface TipTapNode {
  type: string;
  attrs?: Record<string, unknown>;
  content?: TipTapNode[];
  text?: string;
  marks?: Array<{ type: string; attrs?: Record<string, unknown> }>;
}

interface TipTapDoc {
  type: "doc";
  content: TipTapNode[];
}

/**
 * Convert ResumeDoc to TipTap JSON format
 */
export function resumeToTipTap(resume: ResumeDoc): TipTapDoc {
  const content: TipTapNode[] = [];

  for (const section of resume.sections) {
    // Add section heading
    content.push({
      type: "heading",
      attrs: {
        level: 2,
        id: section.id,
        targetPath: `sections.${section.id}`,
      },
      content: [{ type: "text", text: section.title }],
    });

    // Add roles if present
    if (section.roles && section.roles.length > 0) {
      for (const role of section.roles) {
        // Role heading
        content.push({
          type: "heading",
          attrs: {
            level: 3,
            id: role.id,
            targetPath: `sections.${section.id}.roles.${role.id}`,
          },
          content: [
            { type: "text", text: `${role.title} at ${role.company}` },
          ],
        });

        // Bullet list for role
        const bulletListItems: TipTapNode[] = role.bullets.map((bullet) => ({
          type: "listItem",
          attrs: {
            id: bullet.id,
            targetPath: bullet.targetPath,
          },
          content: [
            {
              type: "paragraph",
              content: [{ type: "text", text: bullet.text }],
            },
          ],
        }));

        content.push({
          type: "bulletList",
          content: bulletListItems,
        });
      }
    }
  }

  return {
    type: "doc",
    content,
  };
}

/**
 * Convert TipTap JSON back to ResumeDoc format
 */
export function tipTapToResume(doc: TipTapDoc, resumeId: string): ResumeDoc {
  const sections: Section[] = [];
  let currentSection: Section | null = null;
  let currentRole: Role | null = null;

  for (const node of doc.content) {
    if (node.type === "heading" && node.attrs?.level === 2) {
      // Start new section
      if (currentSection) {
        if (currentRole) {
          currentSection.roles?.push(currentRole);
          currentRole = null;
        }
        sections.push(currentSection);
      }

      currentSection = {
        id: (node.attrs.id as string) || `section_${sections.length}`,
        title: extractText(node),
        roles: [],
      };
    } else if (node.type === "heading" && node.attrs?.level === 3) {
      // Start new role
      if (currentRole && currentSection) {
        currentSection.roles?.push(currentRole);
      }

      const titleText = extractText(node);
      const [title, company] = titleText.split(" at ");

      currentRole = {
        id: (node.attrs.id as string) || `role_${Date.now()}`,
        title: title || "Untitled Role",
        company: company || "Unknown Company",
        bullets: [],
      };
    } else if (node.type === "bulletList" && currentRole) {
      // Add bullets to current role
      const bullets: Bullet[] = (node.content || []).map((listItem, idx) => {
        const text = extractText(listItem);
        const bulletId =
          (listItem.attrs?.id as string) || `bullet_${Date.now()}_${idx}`;
        const targetPath =
          (listItem.attrs?.targetPath as string) ||
          `sections.${currentSection?.id}.roles.${currentRole?.id}.bullets.${bulletId}`;

        return {
          id: bulletId,
          text,
          targetPath,
        };
      });

      currentRole.bullets.push(...bullets);
    }
  }

  // Add remaining section and role
  if (currentRole && currentSection) {
    currentSection.roles?.push(currentRole);
  }
  if (currentSection) {
    sections.push(currentSection);
  }

  return {
    id: resumeId,
    sections,
  };
}

/**
 * Extract plain text from a TipTap node
 */
function extractText(node: TipTapNode): string {
  if (node.text) {
    return node.text;
  }

  if (node.content && node.content.length > 0) {
    return node.content.map(extractText).join("");
  }

  return "";
}

/**
 * Test round-trip fidelity
 */
export function testRoundTrip(resume: ResumeDoc): boolean {
  const tipTap = resumeToTipTap(resume);
  const restored = tipTapToResume(tipTap, resume.id);

  // Deep equality check
  return JSON.stringify(resume) === JSON.stringify(restored);
}
