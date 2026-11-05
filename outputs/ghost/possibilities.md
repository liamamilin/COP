# Ghost：个人创作者与经营者可以完成的任务

## 范围与依赖

这里研究以内容出版为中心的具体任务：发布、读者邮件、会员、反馈、分析和迁移。Ghost 的发布、会员管理、内容权限与数据导出属于软件能力；收费会员需要 Stripe 账户，Stripe 商家地区和处理费会影响是否可用及成本。Ghost(Pro) 是付费托管服务，按当前计划提供不同功能；自托管则由经营者管理服务器和邮件/分析等外部服务。

开放/点击/注册等指标和来源归因可用来观察内容表现，但归因记录不能证明某篇内容造成了购买或收入。Ghost 官方的 Rediverge 案例只说明一个出版者曾采用会员定价、现有受众和 Ghost；不能视作通用业绩承诺。

## 写作与分发

### 发布或定时发送文章与 newsletter

将文章发布到网站、同时发送为 newsletter，或安排文章/邮件之后发布。 **核心**。

条件与边界：发布与预览使用 Ghost 编辑器；若选择邮件分发，须另行配置 newsletter 邮件发送。

来源：[Publishing and scheduling](https://ghost.org/help/publishing-content/)。

### 为不同内容建立独立 newsletter

建立多份各自订阅设置和模板的 newsletter，形成读者可单独选择的邮件内容流。 **核心**。

条件与边界：读者可在注册或邮件偏好设置中选择不同邮件；具体主题和发送频率由经营者提供。邮件送达仍依赖托管方案或自托管邮件配置。

来源：[Setting up email newsletters](https://ghost.org/help/setup-email-newsletters/)。

### 让自托管 Ghost 发送事务邮件与 Mailgun newsletters

自行托管 Ghost 时，配置事务邮件送达，并通过 Mailgun Bulk Email API 发送 newsletter。 **扩展**。

条件与边界：交易/事务邮件（如邀请、密码重置、登录链接）可配置任意 SMTP 或其他邮件服务；newsletter 批量发送不能用普通 SMTP，当前官方支持的 Bulk Email API 为 Mailgun。Amazon SES 示例只是 SMTP 配置示例，不能据此推断 SES 可发送 Ghost newsletters。自托管者须自行管理服务账户、SMTP/DNS 配置与相关费用；Ghost(Pro) 管理发送服务。

来源：[Why do I have to set up Mailgun?](https://docs.ghost.org/faq/mailgun-newsletters)。

## 会员与订阅

### 按会员权限开放文章

将单篇文章的访问范围设为公开或会员可读，安排公开内容与会员专属内容。 **核心**。

条件与边界：付费会员与特定付费 tier 需要 Stripe 订阅功能；付费内容访问由主题/Portal 的会员流程呈现。

来源：[Preparing posts for publishing](https://ghost.org/help/post-settings/)。

### 配置月付/年付的会员等级

创建有不同价格和权益的订阅等级，并将适用内容分配给相应会员。 **核心**。

条件与边界：需要连接自己的 Stripe 账户；Stripe 商家账户仅在其支持的国家/地区可以开立，交易处理费由 Stripe 依付款方式等计收。Ghost(Pro) 的当前计划表显示付费订阅并非每档都包含，需按现行计划确认。Rediverge 案例只是该发布者的做法与结果，不能当作收入/增长保证。

来源：[Create paid tiers](https://ghost.org/help/tiers/)、[Stripe + Ghost](https://ghost.org/integrations/stripe/)、[Stripe global availability](https://stripe.com/global)、[Stripe pricing and fees](https://stripe.com/pricing)、[Ghost(Pro) plans and pricing](https://ghost.org/pricing)、[The ultimate creators guide to membership websites](https://ghost.org/resources/membership-sites/)。

## 受众运营与反馈

### 筛选会员并建立可复用受众视图

按标签、邮件订阅状态或会员状态筛选成员，并保存常用视图以便后续管理。 **核心**。

条件与边界：可将筛选受众用于定向发送或导出；数据是否齐备取决于会员实际订阅与活动记录。

来源：[Member management](https://ghost.org/help/member-management/)。

### 在 newsletter 中征集读者反馈

让读者在阅读邮件后提交对内容的反馈，并在文章分析或会员资料中查看响应。 **核心**。

条件与边界：需在具体 newsletter 的设计设置中启用反馈；读者选择是否响应，反馈不代表全体受众观点。

来源：[Audience feedback](https://ghost.org/help/audience-feedback/)。

### 按会员群组发送定向邮件

选择会员状态、newsletter 订阅、等级或标签，将文章邮件发给指定成员群体。 **核心**。

条件与边界：适用于 Ghost 会员与 newsletter 邮件流程；遵守订阅偏好，并检查发送前的收件人摘要。自托管需要配置送信服务。

来源：[Delivering emails to your audience](https://ghost.org/help/delivering-emails/)。

## 内容观察

### 观察文章流量、互动和转化归属

查看单篇内容的流量、邮件互动和会员转化归属指标，识别哪些内容与注册路径相关。 **核心**。

条件与边界：会员/营收指标要求启用对应会员能力；Ghost 展示的归属数据是观察与归因口径，不证明文章对注册或收入的因果影响。

来源：[Post analytics](https://ghost.org/help/post-analytics/)。

## 数据导出与迁移

### 导出 Ghost 站点数据包

从 Ghost Admin 将站点数据导出为归档包，供存档或迁移时继续处理。 **核心**。

条件与边界：数据包括内容/设置、会员和文章分析等 JSON/CSV 项目；媒体文件在 Ghost(Pro) 的导出选项中可用，托管方式影响下载流程。

来源：[Exporting content and data](https://ghost.org/help/exports/)。

### 将已有出版内容与成员迁入 Ghost

从受支持平台导入文章/图片，并用会员 CSV 导入现有订阅名单。 **核心**。

条件与边界：不同来源需使用相应迁移器、导出格式和字段映射；WordPress 导入有文件大小/文章数量与不支持内容限制。导入名单不等于自动转移旧支付合约；已有付费成员需匹配 Stripe 客户数据。

来源：[Importing content](https://ghost.org/help/imports/)、[Import members](https://ghost.org/help/import-members/)、[Migrating from WordPress](https://docs.ghost.org/migration/wordpress)。

## 尚未确认的方向

高级主题、自动化工作流、外部 CRM/社区联动和自托管复杂部署需要按具体方案进一步核实；本图不将连接器/API名称本身当作用户结果。

## 原研究保留的未解决问题

- 当前 Ghost(Pro) 计划资格、金额和会员上限可能变化；只按 2026-11-05 抓取的计划表说明功能分层，不作长期报价。
- Stripe 商家资格、费率和支付方式需按所在国家/地区及客户付款方式复核；本研究不评估某一用户的资格或实际商户费率。
- 自托管的邮件送达和服务器维护可能需更多 DNS、SMTP、备份、CDN 与分析服务；未逐一估算或部署测试。
- 真实案例为 Ghost 官方发布的单个出版者案例；没有独立核实其经营结果，也不能据此预测其他创作者表现。
- 具体迁移平台的字段、图片、付费订阅和自定义内容保真度各异；未实跑导入。
