import Link from "next/link";
import { getAllSections, getAllManifests } from "@/lib/lawEngineData";

export default async function HomePage() {
  const sections = await getAllSections();
  const manifests = await getAllManifests();
  const sectionList = Object.values(sections).sort((a, b) => a.section_id.localeCompare(b.section_id));

  return (
    <main style={{ maxWidth: 760, margin: "0 auto", padding: "2rem 1rem", fontFamily: "system-ui, sans-serif" }}>
      <h1>Law Engine</h1>
      <p>
        <Link href="/learn/orientation">Start with the UCC orientation &rarr;</Link>
        {" · "}
        <Link href="/learn">Try the interactive transaction lifecycle &rarr;</Link>
      </p>
      <h2>Sources</h2>
      <ul>
        {manifests.map((manifest) => (
          <li key={manifest.citation} style={{ marginBottom: "0.5rem", color: "#555" }}>
            {manifest.citation} — {manifest.jurisdiction}. Source:{" "}
            <a href={manifest.official_source_url}>{manifest.official_source_url}</a>. Licensing:{" "}
            {manifest.licensing_status}. Verification status: <strong>{manifest.verification_status}</strong>.
          </li>
        ))}
      </ul>
      <h2>Sections ({sectionList.length})</h2>
      <ul>
        {sectionList.map((section) => (
          <li key={section.section_id} style={{ marginBottom: "0.5rem" }}>
            <Link href={`/sections/${encodeURIComponent(section.section_id)}`}>
              {section.citation} — {section.title}
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
