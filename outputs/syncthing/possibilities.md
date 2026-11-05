# Syncthing：个人文件同步与副本管理

**范围：** 个人使用者在自己的笔记本、桌面电脑、家用服务器与可选不受信设备之间同步文件、处理冲突与保留远端变更版本；明确同步删除传播、版本保留默认关闭及独立备份边界。移动端客户端状态单独核实，未把旧手机案例当作当前支持保证。

下列项目说明文档所支持的可实现任务，不代表在某一台设备上的运行验证。

## 同步与协作维护文件

### 在自己的设备与家用节点间保持文件同步

让笔记本、桌面电脑与家用服务器上的共享文件夹相互发送并接收变更；家庭多地部署可按成员设置个人与共享文件夹。 **核心**。

条件与边界：需在设备间建立信任并分享对应文件夹；删除和修改也会同步传播。社区用户案例曾包含手机，但 Syncthing 官方 Android wrapper 的維護者公告已宣布退休，且官方 syncthing/syncthing-android 仓库当前元数据标记 archived，最后推送时间为 2024-12-03；这说明该官方 wrapper 已归档，不代表 Syncthing 同步引擎本身不能在 Android 上运行。当前移动端需依赖所选客户端与系统限制；未核实第三方维护状况及兼容性。社区案例不证明普遍可用性或备份安全。

来源：[Folder Types](https://docs.syncthing.net/users/foldertypes.html)、[Syncthing: Redundancy and Backup](https://forum.syncthing.net/t/syncthing-redundancy-and-backup/19175)、[Discontinuing syncthing-android — Syncthing Community Forum maintainer announcement](https://forum.syncthing.net/t/discontinuing-syncthing-android/23002)、[syncthing/syncthing-android GitHub repository metadata](https://api.github.com/repos/syncthing/syncthing-android)。

### 保留其他设备变更前的旧文件版本

在接收设备上归档由其他设备删除或替换的旧文件，以便需要时找回较早版本。 **核心**。

条件与边界：需在该文件夹的该设备上手动选择并配置版本策略；默认关闭。只归档从其他设备收到的变更，本机自己修改的文件不会由本机版本功能归档。它不是独立备份。

来源：[File Versioning](https://docs.syncthing.net/users/versioning.html)。

### 排除不应跨设备同步的文件

通过共享文件夹根目录中的忽略规则排除匹配的文件或路径，使其不从该设备发送或接收到其他设备。 **核心**。

条件与边界：规则按共享文件夹相对路径匹配；.stignore 文件自身不会同步，修改规则需自行管理。

来源：[Ignoring Files](https://docs.syncthing.net/users/ignoring.html)。

### 发现并保留设备间同时修改产生的冲突副本

当两台设备同时改动同一文件且内容不同时，Syncthing 将其中一个副本改名为带冲突标记的文件，让用户比较并自行决定后续处理。 **核心**。

条件与边界：Syncthing 不对文档内容做语义合并；冲突副本会作为普通文件继续传播，需由用户检查、合并或删除。

来源：[Understanding Synchronization](https://docs.syncthing.net/users/syncing.html)。

### 在无法直连时通过中继连接设备

当两个设备无法直接建立连接时，使用中继转发同步数据；Syncthing 默认启用中继并会继续尝试恢复直连。 **核心**。

条件与边界：中继通常比直连慢；链路仍端到端加密，但中继运营方可看到设备 ID、IP 地址和流量量级。若使用发现服务，设备寻址还涉及发现服务的可见信息。

来源：[Relaying](https://docs.syncthing.net/users/relaying.html)、[Security Principles](https://docs.syncthing.net/users/security.html)。

## 降低误操作与设备信任风险

### 把共享文件以加密形式放到不完全信任的设备

为指定共享文件夹设置密码，使同步到不完全信任设备上的数据以加密形式存储，并可由掌握密码的受信任设备解密。 **核心**。

条件与边界：官方文档将此功能标为 beta/testing only。需要妥善保存密码与文件夹标识；不能将其视作成熟托管云盘或经过独立安全认证的加密方案。

来源：[Untrusted (Encrypted) Devices](https://docs.syncthing.net/users/untrusted.html)。

## 待验证

- 本轮官方资料支持的主要任务均有直接引文；不同设备平台兼容性、特定网络环境下的可用性与个人恢复目标仍需结合实际环境验证。

## 资料覆盖与缺口

- 桌面与服务器以外的平台未逐一核实。官方 Android wrapper 已归档；未核实其他 Android 客户端、fork 或 iOS 客户端当前维护状态、兼容性与后台同步限制，移动设备省电策略可能影响持续同步。
- 未实机配置设备配对、目录权限、NAS/路由器、端口转发或防火墙；网络连接成功与性能取决于具体环境。
- 文件版本功能默认关闭且只保护来自其他设备的变更；未验证版本空间占用、长期保留和恢复操作。
- 加密不受信任设备仍属 beta/testing；未进行安全审计或威胁模型评估。
- 同步会传播误删和恶意修改；独立备份系统、快照保留策略、异地副本与恢复测试不属于 Syncthing 核心保障。
- 社区案例是作者自述的家庭部署，不能据此推断其他家庭可达到相同恢复能力。

## 原研究保留的未解决问题

- 没有逐一核实 Windows、macOS、Linux、Android、iOS 当前发行状态与后台运行限制；移动设备省电策略可能影响持续同步。
