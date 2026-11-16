# Bitwarden 可能性地图

范围：个人与小团队的密码库、自动填写、凭据共享与账户访问恢复；明确客户端、组织/付费方案、cloud/self-host 及数据迁移边界。

## 按用户结果浏览

### 日常账户登录

- **让网站登录时自动填入匹配的账户资料**（核心）——在浏览器扩展中为网站保存登录条目并关联网址；打开匹配网站时，用 Bitwarden 把用户名和密码填入登录框。 条件：需要浏览器扩展、已解锁的 vault，以及登录条目中正确配置的网站 URI。默认页面加载自动填充关闭；不可信 iframe 或 HTTP/HTTPS 不匹配时可能警告或阻止。Safari 的右键菜单自动填充不可用。 来源：[Autofill from Browser Extension](https://bitwarden.com/help/auto-fill-browser/)。
- **为新账户生成并保存独特密码**（核心）——在 Bitwarden 应用内生成强密码或用户名，并在创建新账户时将登录资料保存到 vault。 条件：密码生成器可在所有 Bitwarden 应用中使用；用户名生成器在 Web vault、浏览器扩展、桌面和移动应用中提供。不同应用的生成设置/历史各自保存；生成历史会在退出登录时清除。 来源：[Username & Password Generator](https://bitwarden.com/help/generator/)。

### 账户安全维护

- **找出重复、弱或已泄露的密码以安排更换**（核心）——运行 vault health 报告，识别重复或弱密码及公开泄露库中出现过的密码，再为受影响账户改用新密码。 条件：大多数健康报告需个人 Premium 或付费组织方案，Data Breach 报告对所有用户免费。弱/重复报告在客户端本地运行；泄露报告会把密码哈希前五位发送给外部服务再本地比较。报告命中不等于该账户已被入侵，Bitwarden 不会替用户更改网站密码。 来源：[Vault Health Reports](https://bitwarden.com/help/reports/)。

### 共享与交付

- **通过限时链接分享敏感文本或文件**（核心）——创建 Bitwarden Send，把敏感文本或文件通过临时链接交给收件人，并设定可访问期限与隐私选项。 条件：Send 文本最多 1,000 个加密字符；文件最多 500 MB（移动设备 100 MB）。每个 Send 删除时间最长 31 天，可设到期时间、访问次数、密码或收件人邮箱验证；文件 Send 需要 Premium 或包含此功能的组织方案。组织管理员可关闭 Send。 来源：[About Send](https://bitwarden.com/help/about-send/)。
- **与家人或小团队共享一组账户资料**（核心）——建立 Bitwarden organization，将共享登录、笔记、卡片或身份资料放进 collection，并给成员或群组配置访问权限。 条件：共享资料归组织而非某个成员所有。Free organization 支持两名用户、最多两个 collections；Families 最多六人且 collections 不限；Teams/Enterprise 按用户计费并含管理功能。个人 Premium 本身不含组织共享。套餐明细以当前计划页面为准；未核实地区/付款价格。 来源：[Organizations Overview](https://bitwarden.com/help/about-organizations/)。

### 迁移与备份

- **迁移或备份 vault 资料并检查数据范围**（核心）——从其他密码管理器导入登录资料，或将个人 vault 导出为加密 JSON/含附件 ZIP，用于迁移或备份。 条件：导出通常在客户端本地解密；若不是加密导出，应避免通过不安全渠道传输并立即删除明文文件。ZIP 目前仅支持个人 vault；个人导出不包含组织所有资料；任何导出格式都不包含 Trash 或 Sends。导入不会自动检查重复项，重复导入会产生重复条目，需清理临时文件。 来源：[Import to your Vault or Collections](https://bitwarden.com/help/import-data/)、[Export Vault Data](https://bitwarden.com/help/export-your-data/)。

### 访问恢复

- **为个人 vault 预先设置可信紧急联系人**（核心）——提前指定另一个 Bitwarden 用户为可信联系人；账户持有人无法响应时，对方可按批准或等待时限取得只读访问或接管访问。 条件：须在紧急情况发生前设置。添加联系人需要 Premium（含付费组织成员）；双方须在同一 Bitwarden server。View 可读个人 vault；Takeover 会设置新的主密码并移除原两步验证。普通个人账户遗忘主密码时，Bitwarden 无法替本人取回或重置；紧急访问是预先建立的替代路径。 来源：[About Emergency Access](https://bitwarden.com/help/emergency-access/)、[Forgot My Master Password](https://bitwarden.com/help/forgot-master-password/)。
- **让管理员恢复已登记组织成员的账户访问**（核心）——组织成员失去主密码或两步验证方式时，由有权限的管理员发起恢复，成员通过邮件链接重设凭据并重新登录。 条件：仅 Enterprise 组织可用；组织须启用 Account Recovery 管理策略，成员须事先登记。角色限制谁能重置管理员/所有者；恢复不绕过组织 SSO 或身份提供商的 MFA，也不能恢复已删除账户。 来源：[About Account Recovery](https://bitwarden.com/help/account-recovery/)。

### 部署方式

- **在自己的服务器或家庭实验环境运行 vault**（核心）——把 Bitwarden 部署到自有服务器或家庭实验环境，用于管理个人或小团队的账户资料。 条件：自托管需要自己准备服务器、数据库和证书并维护安全、备份与升级。Bitwarden Lite 面向个人/home lab/轻量分享，文档要求具备中级 Linux 命令行与 Docker 能力；企业部署可选多种进阶路线。Enterprise 套餐包含自托管，但价格、服务器资源和具体支持条件未核实。多数个人/团队可用托管云服务，维护责任较少。 来源：[Self-host Bitwarden](https://bitwarden.com/help/self-host-bitwarden/)。

## 能力边界与覆盖缺口

Bitwarden 个人 vault 的忘记主密码流程无法由 Bitwarden 直接重设。个人 Premium 紧急联系人和 Enterprise 组织成员恢复是两个不同的预先配置方案；前者可给可信联系人只读或接管权限，后者要求组织策略和成员登记，且不会绕过 SSO/MFA。

托管云由 Bitwarden 运维，降低用户的服务器维护负担；self-host 可支持个人、家庭实验环境或组织部署，但须自行管理服务器、数据库/证书、备份和升级。Bitwarden Lite 的帮助页列出中级 Linux 命令行与 Docker 能力要求。

未安装或运行 Bitwarden，也未核实现价、地域、付费合同、完整平台兼容性与迁移保真度。来源与缓存时间/哈希见 [source-coverage.json](source-coverage.json)。

## 原研究保留的未解决问题

- 没有安装客户端、浏览器扩展、vault health 或 self-host 实例；无法认证个人环境下配置、兼容性、更新、备份恢复和真实账户效果。
- 套餐功能说明按官方当前帮助页核对但未购买测试；地区价格、付款、税费、存储额度和组织合同条件未核实。
- 未逐项核对所有浏览器/移动操作系统版本、自动填充 URI 例外和密码导入格式保真度。
- 未独立审查源代码、安全审计或第三方服务；Bitwarden Send 及 breached-password 报告依赖产品/外部服务，不能替代账户级安全调查。
