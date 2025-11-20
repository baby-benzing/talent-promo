import { resumeToTipTap, tipTapToResume, testRoundTrip } from "../lib/resumeSerializer";
import type { ResumeDoc } from "../../../packages/shared/types";

describe("Resume Serializer", () => {
  const mockResume: ResumeDoc = {
    id: "resume_123",
    sections: [
      {
        id: "section_1",
        title: "Experience",
        roles: [
          {
            id: "role_1",
            title: "Software Engineer",
            company: "Tech Corp",
            bullets: [
              {
                id: "bullet_1",
                text: "Built scalable web applications",
                targetPath: "sections.section_1.roles.role_1.bullets.bullet_1",
              },
              {
                id: "bullet_2",
                text: "Led team of 5 engineers",
                targetPath: "sections.section_1.roles.role_1.bullets.bullet_2",
              },
            ],
          },
        ],
      },
      {
        id: "section_2",
        title: "Education",
        roles: [
          {
            id: "role_2",
            title: "BS Computer Science",
            company: "State University",
            bullets: [
              {
                id: "bullet_3",
                text: "Graduated with honors",
                targetPath: "sections.section_2.roles.role_2.bullets.bullet_3",
              },
            ],
          },
        ],
      },
    ],
  };

  test("converts ResumeDoc to TipTap format", () => {
    const tipTap = resumeToTipTap(mockResume);

    expect(tipTap.type).toBe("doc");
    expect(tipTap.content).toBeDefined();
    expect(tipTap.content.length).toBeGreaterThan(0);

    // Check for section heading
    const firstHeading = tipTap.content[0];
    expect(firstHeading.type).toBe("heading");
    expect(firstHeading.attrs?.level).toBe(2);
    expect(firstHeading.attrs?.id).toBe("section_1");
  });

  test("converts TipTap format back to ResumeDoc", () => {
    const tipTap = resumeToTipTap(mockResume);
    const restored = tipTapToResume(tipTap, mockResume.id);

    expect(restored.id).toBe(mockResume.id);
    expect(restored.sections.length).toBe(mockResume.sections.length);
    expect(restored.sections[0].title).toBe(mockResume.sections[0].title);
  });

  test("maintains round-trip fidelity", () => {
    const isEqual = testRoundTrip(mockResume);
    expect(isEqual).toBe(true);
  });

  test("preserves targetPath across conversions", () => {
    const tipTap = resumeToTipTap(mockResume);
    const restored = tipTapToResume(tipTap, mockResume.id);

    const originalBullet = mockResume.sections[0].roles?.[0].bullets[0];
    const restoredBullet = restored.sections[0].roles?.[0].bullets[0];

    expect(restoredBullet?.targetPath).toBe(originalBullet?.targetPath);
  });

  test("handles empty sections", () => {
    const emptyResume: ResumeDoc = {
      id: "resume_empty",
      sections: [
        {
          id: "section_empty",
          title: "Empty Section",
          roles: [],
        },
      ],
    };

    const tipTap = resumeToTipTap(emptyResume);
    const restored = tipTapToResume(tipTap, emptyResume.id);

    expect(restored.sections.length).toBe(1);
    expect(restored.sections[0].roles?.length).toBe(0);
  });

  test("preserves structural stability after edits", () => {
    const tipTap = resumeToTipTap(mockResume);

    // Simulate an edit: change bullet text
    const bulletList = tipTap.content.find((node) => node.type === "bulletList");
    if (bulletList?.content?.[0]?.content?.[0]?.content?.[0]) {
      bulletList.content[0].content[0].content[0].text = "Updated text";
    }

    const restored = tipTapToResume(tipTap, mockResume.id);
    const updatedBullet = restored.sections[0].roles?.[0].bullets[0];

    // Path should remain stable even after text edit
    expect(updatedBullet?.targetPath).toBe(
      "sections.section_1.roles.role_1.bullets.bullet_1"
    );
  });
});
