# WooCommerce：个人经营者可以完成的任务

## 范围与关键依赖

这里聚焦商品店铺的日常结果。WooCommerce 核心插件运行在 WordPress 上；公开商店仍需要可用的网站托管、域名和服务器配置。商品、订单、优惠券、数字下载和 Analytics 是核心功能。承运标签、自动税额、收款网关、多币种、订阅和营销能力需按具体扩展与服务核实。

WooCommerce 报表帮助观察销售、退货和订单等结果；同一时间段的指标变化不能单独证明某个促销或产品修改造成变化。税务文档只教软件配置，不判断经营者的法定义务。

## 商品展示与管理

### 批量调整商品价格与库存

一次调整多件商品的价格和库存，减少逐件维护。 **核心**。

条件与边界：需要在 WordPress 管理后台拥有商品编辑权限。

来源：[Adding and Managing Products](https://woocommerce.com/document/managing-products/)。

### 展示可选规格并分别管理库存

让顾客选择商品规格，并为各变体设置价格、库存和图片。 **核心**。

条件与边界：需配置商品属性及变体；物流相关规格可另填重量、尺寸和运输类别。

来源：[Variable Products](https://woocommerce.com/document/variable-product/)。

## 订单与交付

### 售卖并交付数字商品

付款后向购买者发送下载链接，并在订单或账户页提供下载入口。 **核心**。

条件与边界：服务器下载模式、文件存放位置和订单付款状态会影响交付；需要检查主机文件大小/传输限制。

来源：[Digital/Downloadable Product Guide](https://woocommerce.com/document/digital-downloadable-product-handling/)。

### 更新订单并与客户沟通

在店铺后台查看和更新订单，并通过订单备注向客户沟通。 **核心**。

条件与边界：订单后台面向管理员或 Shop Manager；收款、履约、退款仍需实际支付及物流流程配合。

来源：[Managing orders](https://woocommerce.com/document/managing-orders/)。

### 从旧版独立扩展打印 USPS/DHL 标签

使用单独运行的旧版 WooCommerce Shipping & Tax 扩展购买并打印 USPS 和 DHL Express 标签。 **扩展**。

条件与边界：文档说明 3.0.2 及以上新安装将该扩展改名为 WooCommerce Tax；旧标签界面仅在该扩展单独运行时保留，范围限 USPS 与 DHL Express。若启用新的 WooCommerce Shipping，标签界面会由后者接管；本项不据旧文档推断新扩展的承运商范围。

来源：[WooCommerce Shipping & Tax: legacy shipping labels](https://woocommerce.com/document/woocommerce-shipping-and-tax/)。

## 销售运营

### 按限制发放购物优惠券

创建固定购物车、固定商品或百分比折扣，并设置适用条件和使用次数限制。 **核心**。

条件与边界：需启用优惠券并具备管理员或 Shop Manager 权限；自动化促销、礼卡等属于插件扩展范围。

来源：[Managing Coupons in WooCommerce](https://woocommerce.com/document/coupon-management/)。

### 在结账中配置税率

在 WooCommerce 中录入和配置适用的税率，让软件按设置处理结账税额。 **核心**。

条件与边界：只描述软件设置能力；税率是否适用、何时以及向谁收税须由经营者按司法辖区向合格税务专业人士确认。

来源：[Setting up taxes in WooCommerce](https://woocommerce.com/document/setting-up-taxes-in-woocommerce/)。

### 为符合资格的商家启用线上收款

符合国家资格时安装 WooPayments，在店铺后台处理付款、退款、争议和打款。 **扩展**。

条件与边界：WooPayments 是额外插件/支付服务，商家所在地必须在支持国家；需更新的 WordPress、WooCommerce、HTTPS 与 Stripe 合作伙伴核验。交易费按商家国、顾客国、币种及支付方式变化。

来源：[WooPayments in Your Country](https://woocommerce.com/document/woopayments/compatibility/countries/)、[WooPayments: Startup Guide](https://woocommerce.com/document/woopayments/startup-guide/)、[WooPayments: Fees](https://woocommerce.com/document/woopayments/fees/)。

### 用单一店铺经营多币种地区销售

把不同地区的标价和币种结算组织在一个商店中。 **扩展**。

条件与边界：真实案例使用 Braintree 与 Aelia、分开的 USD/CAD 银行账户；这些外部支付与多币种组件并非 WooCommerce 核心功能。案例只证明该商家的配置，不保证同样成本或结果。

来源：[How Landyachtz cut ecommerce costs by more than 75% and gained full control with WooCommerce](https://woocommerce.com/posts/landyachtz-woocommerce-success-story/)。

## 经营观察

### 检查销售指标并导出报表

按日期和可用筛选器查看店铺关键指标，将报表表格导出为 CSV 继续分析。 **核心**。

条件与边界：WooCommerce Analytics 根据订单数据生成指标；导出大表可能通过邮件发送。描述的是观察/汇总，不证明某项营销动作导致了变化。

来源：[Analytics and Sales Reports](https://woocommerce.com/document/woocommerce-analytics/)。

## 持续销售与服务预约

### 销售具有重复计费周期的商品订阅

为商品建立定期收费方案，设置计费频率、试用、费用和到期条件；同一商品可提供不同规格订阅选项。 **扩展**。

条件与边界：需要另购 WooCommerce Subscriptions 扩展；官方商品页在 2026-11-05 抓取时显示一年期 $279。自动续费还需支持该模式的支付网关，也可配置手动续费。价格/税费会随时间和地区变化。月度咖啡订阅是官方配置示例，不是经营成效承诺。

来源：[Creating a Subscription Product](https://woocommerce.com/document/subscriptions/creating-subscription-products/)、[Subscription Renewal Process](https://woocommerce.com/document/subscriptions/renewal-process/)、[Use Case: Monthly Coffee Subscription](https://woocommerce.com/document/subscriptions-use-case-coffee/)、[WooCommerce Subscriptions product page](https://woocommerce.com/products/woocommerce-subscriptions/)。

### 向会员开放内容并逐步解锁

设定会员才能阅读的内容，并按会员加入后的时间分批开放内容。 **扩展**。

条件与边界：需要另购 WooCommerce Memberships 扩展；官方商品页在 2026-11-05 抓取时显示一年期 $199。若销售周期性会员费，还需要单独的订阅扩展和兼容支付服务。公开内容的限制规则需要仔细配置；价格/税费可能变化。

来源：[WooCommerce Memberships](https://woocommerce.com/document/woocommerce-memberships/)、[WooCommerce Memberships product page](https://woocommerce.com/products/woocommerce-memberships/)。

### 接受按人员与可用时段预约的服务

让顾客为预约选择具体服务人员和时段，经营者按资源/人员设置各自的可用时间。 **扩展**。

条件与边界：需要另购 WooCommerce Bookings 扩展；官方商品页在 2026-11-05 抓取时显示一年期 $249，并需配置产品、时段与资源。要求兼容的 WordPress/WooCommerce/PHP 版本及可工作的 WP Cron。Salon 模板案例只是一个可行配置示例，价格可能变化。

来源：[Introduction to WooCommerce Bookings](https://woocommerce.com/document/introduction-to-woocommerce-bookings/)、[Bookings Use Case: Hair Salon (Using Resources and Availability)](https://woocommerce.com/document/introduction-to-woocommerce-bookings/woocommerce-bookings-use-cases/bookings-use-case-hair-salon/)、[WooCommerce Bookings product page](https://woocommerce.com/products/woocommerce-bookings/)。

## 尚未确认的方向

客户评价/反馈征集、订阅促销邮件与弃购触达的具体扩展流程、以及新 WooCommerce Shipping 的当前承运商/报价范围仍需针对版本和地区继续核实。

## 原研究保留的未解决问题

- 订阅、会员和预约功能依赖不同的付费扩展与支付网关；本研究未按具体商户所在地核对最新价格、收款资格、退款费率或当地履约规则。
- 未覆盖客户评论收集、邮件营销、弃购触达等相关扩展及其同意、地区和发送服务要求。
- 运输标签项严格限于旧版WooCommerce Shipping & Tax单独运行时的USPS/DHL Express路线；新WooCommerce Shipping的承运商、实时报价与追踪需另查其当前官方指南。
- 支付只详细核实 WooPayments 与一个多币种案例，未比较其他网关国家资格、争议处理或费率。
- 核心 WooCommerce 插件免费不等于开店无成本；域名、托管、主题、扩展、支付处理与维护成本依具体选择而异。
