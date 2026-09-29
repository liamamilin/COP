import Link from "next/link";

export default function NotFound() {
  return (
    <main className="home-shell">
      <section className="empty-state">
        <span className="empty-glyph" aria-hidden="true">?</span>
        <div>
          <p className="eyebrow">NOT FOUND</p>
          <h3>This COP page is no longer available.</h3>
          <p>The project, version, or entity may have been removed.</p>
          <Link className="primary-link" href="/">Return to projects</Link>
        </div>
      </section>
    </main>
  );
}
