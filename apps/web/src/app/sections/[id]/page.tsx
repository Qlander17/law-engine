import { notFound } from "next/navigation";
import Link from "next/link";
import { getSection, getSyntaxAnalysis } from "@/lib/lawEngineData";
import LanguageAnalysisPanel from "./LanguageAnalysisPanel";

export default async function SectionPage({ params }: { params: { id: string } }) {
  const section = await getSection(decodeURIComponent(params.id));
  if (!section) {
    notFound();
  }
  const analysis = await getSyntaxAnalysis(section.section_id);

  return (
    <main style={{ maxWidth: 760, margin: "0 auto", padding: "2rem 1rem", fontFamily: "system-ui, sans-serif" }}>
      <p>
        <Link href="/">&larr; All sections</Link>
      </p>
      <h1>{section.citation}</h1>
      <h2 style={{ fontWeight: 400 }}>{section.title}</h2>
      {section.paragraphs.map((paragraph, i) => (
        <p key={i}>{paragraph}</p>
      ))}
      {section.defined_terms.length > 0 && (
        <p>
          <strong>Defined terms:</strong> {section.defined_terms.join(", ")}
        </p>
      )}
      {section.topics.length > 0 && (
        <p>
          <strong>Topics:</strong> {section.topics.join(", ")}
        </p>
      )}
      {section.cross_references.length > 0 && (
        <p>
          <strong>Cross-references:</strong>{" "}
          {section.cross_references.map((ref) => (
            <Link key={ref} href={`/sections/${encodeURIComponent(ref)}`} style={{ marginRight: "0.5rem" }}>
              § {ref}
            </Link>
          ))}
        </p>
      )}
      <LanguageAnalysisPanel section={section} analysis={analysis} />
    </main>
  );
}
