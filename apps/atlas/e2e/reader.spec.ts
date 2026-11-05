import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("library shows real counts and plans never masquerade as generated content", async ({
  page,
}) => {
  const requests: string[] = [];
  page.on("request", (r) => requests.push(r.url()));
  await page.goto("./");
  await expect(
    page.getByRole("heading", { name: "已上线的主题" }),
  ).toBeVisible();
  await expect(page.locator(".topic-card")).toHaveCount(3);
  await expect(page.locator(".plan-card")).toHaveCount(17);
  for (const [slug, count] of [
    ["ggplot2", "74"],
    ["langchain-agent", "53"],
    ["obsidian", "63"],
  ])
    await expect(
      page.locator(".tone-" + slug + " .topic-count strong"),
    ).toHaveText(count);
  await page.getByRole("link", { name: /Agent Harness/ }).click();
  await expect(page.getByText("待研究 · 尚未上线")).toBeVisible();
  await expect(page.getByText(/尚无可能性条目/)).toBeVisible();
  expect(requests.some((u) => u.includes("content/agent-harness"))).toBe(false);
});
test("all three maps and their entire P sets are readable", async ({
  page,
}) => {
  for (const [slug, count] of [
    ["ggplot2", 74],
    ["langchain-agent", 53],
    ["obsidian", 63],
  ] as const) {
    await page.goto("./#/topic/" + slug);
    await expect(page.locator(".p-card")).toHaveCount(count);
    await expect(
      page.getByRole("link", { name: "研究报告", exact: true }),
    ).toBeVisible();
    await page.locator(".p-card").last().click();
    await expect(
      page.getByRole("region", { name: "可能性详情" }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "条件与边界", exact: true }),
    ).toBeVisible();
  }
});
test("deep links survive refresh and unknown IDs fail visibly", async ({
  page,
}) => {
  await page.goto("./#/topic/obsidian/p/p-knowledge-network");
  await expect(page.locator(".detail h2")).toHaveText(
    "建立能双向追溯的知识网络",
  );
  await page.reload();
  await expect(page.locator(".detail h2")).toHaveText(
    "建立能双向追溯的知识网络",
  );
  await page.goto("./#/topic/obsidian/p/no-such-p");
  await expect(
    page.getByRole("heading", { name: "没有找到这个 P" }),
  ).toBeVisible();
  await page.goto("./#/topic/not-a-topic");
  await expect(
    page.getByRole("heading", { name: "没有找到这个页面" }),
  ).toBeVisible();
});
test("categories, combined filters, empty results and selected filter permalinks work", async ({
  page,
  isMobile,
}) => {
  await page.goto("./#/topic/obsidian");
  await expect(page.locator(".p-card")).toHaveCount(63);
  if (isMobile) {
    await page.getByRole("button", { name: "☰ 用途分类" }).click();
    await page
      .getByRole("dialog")
      .getByRole("button", { name: /连接、找回与重用已有知识/ })
      .click();
    await expect(page.getByRole("dialog")).not.toBeVisible();
  } else
    await page
      .getByRole("navigation", { name: "用途分类", exact: true })
      .getByRole("button", { name: /连接、找回与重用已有知识/ })
      .click();
  await expect(page.locator(".p-card")).toHaveCount(7);
  await page.getByLabel("能力路径", { exact: true }).selectOption("extension");
  await expect(page.locator(".p-card")).toHaveCount(2);
  await page.locator(".p-card").first().click();
  expect(page.url()).toContain("availability=extension");
  expect(page.url()).toContain("group=g-connect");
  await expect(page.locator(".detail")).toBeVisible();
  await page
    .getByLabel("在当前主题中搜索")
    .fill("absolutely-no-matching-result");
  await expect(
    page.getByRole("heading", { name: "没有匹配的可能性" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "清除全部条件" }).click();
  await expect(page.locator(".p-card")).toHaveCount(63);
});
test("site search finds aliases and proposed remains visibly separate", async ({
  page,
}) => {
  await page.goto("./");
  await page.getByLabel("搜索主题与可能性").fill("生成式界面");
  await expect(page.locator(".search-grid .p-card")).toHaveCount(1);
  await page.locator(".search-grid .p-card").click();
  await expect(page.locator(".proposed-notice")).toContainText(
    "这是一项待验证方向",
  );
  await expect(page.locator(".detail")).not.toContainText("人工复核");
  await page.goto("./#/topic/langchain-agent");
  await expect(
    page
      .getByRole("region", { name: "待验证方向", exact: true })
      .locator(".p-card"),
  ).toHaveCount(1);
  await page.getByLabel("证据状态", { exact: true }).selectOption("supported");
  await expect(page.locator(".p-card")).toHaveCount(52);
  await page.getByLabel("证据状态", { exact: true }).selectOption("proposed");
  await expect(page.locator(".p-card")).toHaveCount(1);
});
test("all source records, original excerpts and source permalinks are available", async ({
  page,
}) => {
  await page.goto("./#/topic/obsidian/sources");
  await expect(page.locator(".source-card")).toHaveCount(76);
  await page.getByLabel("搜索来源").fill("s-pdf");
  await expect(page.locator(".source-card")).toHaveCount(2);
  await page.goto("./#/topic/obsidian/sources/s-pdf");
  await expect(page.locator("#source-s-pdf")).toBeVisible();
  await expect(page.locator("#source-s-pdf blockquote")).toContainText(
    "export any note",
  );
  const a = page.locator("#source-s-pdf h3 a");
  await expect(a).toHaveAttribute("target", "_blank");
  await expect(a).toHaveAttribute("rel", "noopener noreferrer");
  await page.reload();
  await expect(page.locator("#source-s-pdf")).toBeVisible();
});
test("full Markdown report keeps coverage, internal navigation and safe raw links", async ({
  page,
}) => {
  await page.goto("./#/topic/obsidian/report");
  await expect(page.locator(".prose")).toContainText("必须保留的冲突与限制");
  await expect(page.locator(".prose")).toContainText(
    "资料覆盖、发现过程与缺口",
  );
  await page
    .getByRole("navigation", { name: "研究报告目录" })
    .getByRole("link", { name: "资料覆盖、发现过程与缺口" })
    .click();
  expect(page.url()).toContain("/report");
  const internal = page.locator('.prose a[href="#report-g-capture"]').first();
  await internal.click();
  expect(page.url()).toContain("/report");
  await expect(page.locator(".prose script")).toHaveCount(0);
  await page.locator(".report-validation summary").click();
  await expect(page.locator(".report-validation pre")).toContainText(
    "Ran 14 tests",
  );
});
test("copy uses real clipboard and manual fallback retains the whole request", async ({
  page,
  context,
}) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.goto("./#/topic/obsidian/p/p-knowledge-network");
  await page.getByRole("button", { name: /复制需求描述/ }).click();
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  expect(copied).toContain("主题：Obsidian");
  expect(copied).toContain("建立能双向追溯的知识网络");
  expect(copied).toContain("条件与边界");
  expect(copied).toContain("https://obsidian.md/help/links");
  await page.addInitScript(() =>
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: {
        writeText: async () => {
          throw new Error("denied");
        },
      },
    }),
  );
  await page.reload();
  await page.getByRole("button", { name: /复制需求描述/ }).click();
  const manual = page.getByLabel("自动复制不可用。请选中下方文字手动复制。");
  await expect(manual).toBeVisible();
  expect(await manual.inputValue()).toBe(copied);
});
test("loading failure can retry without a backend", async ({ page }) => {
  await page.route("**/content/obsidian.json", (r) =>
    r.fulfill({ status: 503, body: "unavailable" }),
  );
  await page.goto("./#/topic/obsidian");
  await expect(page.getByRole("alert")).toContainText("未能载入");
  await page.unroute("**/content/obsidian.json");
  await page.getByRole("button", { name: "重新加载" }).click();
  await expect(page.locator(".p-card")).toHaveCount(63);
});
test("responsive reading is accessible and requests only static site resources", async ({
  page,
}) => {
  const external: string[] = [];
  page.on("request", (r) => {
    if (
      new URL(r.url()).origin !== new URL(page.url() || r.url()).origin &&
      page.url() !== "about:blank"
    )
      external.push(r.url());
  });
  await page.goto("./");
  await expect(page.locator(".topic-card")).toHaveCount(3);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.goto("./#/topic/obsidian/p/p-knowledge-network");
  await expect(page.locator(".detail h2")).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  expect(external).toEqual([]);
});

test('keyboard navigation, drawer focus and desktop pane controls work', async ({page,isMobile}) => {
  await page.goto('./');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link',{name:'跳到正文'})).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main-content')).toBeFocused();
  await page.goto('./#/topic/obsidian');
  await expect(page.locator('.p-card')).toHaveCount(63);
  if (isMobile) {
    const button=page.getByRole('button',{name:'☰ 用途分类'});
    await button.focus(); await page.keyboard.press('Enter');
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(button).toBeFocused();
  } else {
    const collapse=page.getByRole('button',{name:'收起分类',exact:true});
    await collapse.focus(); await page.keyboard.press('Enter');
    await expect(page.getByRole('navigation',{name:'用途分类',exact:true})).toHaveCount(0);
    await page.getByRole('button',{name:'展开分类',exact:true}).click();
    await page.getByRole('button',{name:'收起详情',exact:true}).click();
    await expect(page.getByRole('region',{name:'可能性详情'})).toHaveCount(0);
    await page.getByRole('button',{name:'展开详情',exact:true}).click();
    await expect(page.getByRole('region',{name:'可能性详情'})).toBeVisible();
  }
});
