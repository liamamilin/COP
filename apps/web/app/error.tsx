"use client";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main className="fatal-state">
      <p className="eyebrow">WORKSPACE UNAVAILABLE</p>
      <h1>无法载入这个 COP。</h1>
      <p>请确认 API 正在运行，且参考项目已经导入。</p>
      <button type="button" onClick={reset}>重新尝试</button>
    </main>
  );
}

