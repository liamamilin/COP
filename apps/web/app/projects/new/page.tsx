import Link from "next/link";

import { NewProjectForm } from "../../../components/new-project-form";

export default function NewProjectPage() {
  return (
    <main className="wizard-shell">
      <Link className="back-link" href="/">← All projects</Link>
      <div className="wizard-grid">
        <header>
          <p className="eyebrow">NEW COP · STEP 1 OF 2</p>
          <h1>Start with a<br />capability.</h1>
          <p>先描述你最终要做到什么。来源可以稍后添加，结构会围绕目标而不是目录生成。</p>
        </header>
        <NewProjectForm />
      </div>
    </main>
  );
}

