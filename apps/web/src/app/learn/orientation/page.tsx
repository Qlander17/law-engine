// Law Engine -- UCC orientation page (Live Run 1.45, Mission 5/V1).
// Real, pre-built content (services/ucc_orientation.py), wired to a
// route for the first time -- previously existed only as a Python
// object. This is the "why does this exist, what is the big picture"
// on-ramp the zero-assumption pedagogy design calls for before a
// learner is dropped into section-by-section detail or MCQs.

import Link from "next/link";
import { getOrientation } from "@/lib/lawEngineData";

export default async function OrientationPage() {
  const orientation = await getOrientation();

  return (
    <main style={{ maxWidth: 820, margin: "0 auto", padding: "2rem 1rem", fontFamily: "system-ui, sans-serif" }}>
      <p>
        <Link href="/">&larr; All sections</Link>
      </p>
      <h1>UCC Orientation</h1>

      <section style={{ marginBottom: "2rem" }}>
        <h2>Why does uniform commercial law exist?</h2>
        <p>{orientation.why_uniform_commercial_law_exists}</p>

        <h2>What does &quot;uniform&quot; actually mean in practice?</h2>
        <p>{orientation.what_uniform_means_in_practice}</p>

        <h2>Is the UCC itself binding law?</h2>
        <p>{orientation.is_the_ucc_itself_binding_law}</p>

        <h2>Why is it split into Articles?</h2>
        <p>{orientation.why_split_into_articles}</p>
      </section>

      <h2>The 11 Articles</h2>
      <p style={{ color: "#555" }}>
        Articles with real, ingested statutory text in this project are linked to their sections. Every other
        Article shown here is a real, sourced overview — but has no ingested text yet.
      </p>

      {orientation.articles.map((article) => (
        <article
          key={article.article}
          style={{ border: "1px solid #ddd", borderRadius: 6, padding: "1rem", marginBottom: "1rem" }}
        >
          <h3 style={{ marginTop: 0 }}>
            Article {article.article} — {article.display_name}{" "}
            {article.has_ingested_coverage ? (
              <span style={{ color: "#0a7", fontSize: "0.8em" }}>(ingested)</span>
            ) : (
              <span style={{ color: "#999", fontSize: "0.8em" }}>(orientation only)</span>
            )}
          </h3>
          <p>
            <strong>What it covers:</strong> {article.subject_matter}
          </p>
          <p>
            <strong>Why a separate Article:</strong> {article.why_separate_article}
          </p>
          <p>
            <strong>Real-world example:</strong> {article.real_world_example}
          </p>
          <p style={{ color: "#555" }}>{article.ingested_coverage_note}</p>
        </article>
      ))}

      <h2>Article 12</h2>
      <p>{orientation.article_12_note}</p>

      <h2>Sources</h2>
      <ul>
        {orientation.sources.map((source) => (
          <li key={source}>
            <a href={source}>{source}</a>
          </li>
        ))}
      </ul>
    </main>
  );
}
