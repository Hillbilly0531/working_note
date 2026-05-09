---
title: 一块返利改造 - 返利协议管理 (PMS Rebate) 技术规格
date: 2026-04-28
status: draft
tags:
  - 一块返利
  - PMS
  - 返利协议
  - 协议管理
  - 技术规格
aliases:
  - 一块返利协议管理改造-技术规格
---

# 1. 概述

## 1.1 改造范围

本次改造涉及返利协议管理服务中，以下三种【普通型】协议的新增、修改、查询接口：

| 序号 | 协议类型 | 涉及改造点 |
|------|---------|-----------|
| 1 | 按采购金额-普通型 | 新增【计退规则】字段 |
| 2 | 按采购数量-普通型 | 新增【计退规则】+【返利规则】字段；阶梯字段结构变更 |
| 3 | 按销售数量-普通型 | 新增【计退规则】固定值 + 【返利规则】字段；阶梯字段结构变更 |

## 1.2 适用方差异总览

| 字段 | 一块医药 | 非一块（乐药等） |
|------|---------|-----------------|
| 计退规则 | 支持配置（按采购金额/数量）；按销售数量固定为"不计退" | 不支持，字段为 null |
| 返利规则 | 支持配置（按采购数量/销售数量） | 支持配置（按采购数量/销售数量） |
| 每满X件阶梯 | 按返利规则=每满X件时生效 | 按返利规则=每满X件时生效 |

---

# 2. 实体模型

## 2.1 新增枚举

### 2.1.1 ReturnRule（计退规则）

> **适用方**：仅一块医药
> **适用协议**：按采购金额-普通型、按采购数量-普通型
> **固定适用**：按销售数量-普通型（一块医药固定为"不计退"且不可更改）
> **不适用**：非一块（字段为 null）

| 键 | 值 | 说明 |
|----|-----|------|
| `NO_RETURN_DEDUCTION` | `"不计退"` | 计算阶梯、返利时不会减去采退/销退数据 |
| `WITH_RETURN_DEDUCTION` | `"计退"` | 计算阶梯、返利时按减去采退/销退数据算 |

### 2.1.2 RebateRule（返利规则）

> **适用方**：一块医药 & 非一块
> **适用协议**：按采购数量-普通型、按销售数量-普通型

| 键 | 值 | 说明 |
|----|-----|------|
| `PER_ITEM` | `"每1件返利"` | 按每件固定金额返利（保留现状） |
| `PER_X_ITEMS` | `"每满X件返利"` | 每满X件返固定金额，公式：ROUNDDOWN(数量÷X)×返利金额 |

## 2.2 协议实体字段

### 2.2.1 计退规则（returnRule）

```typescript
// TODO: 实际字段名以项目代码为准
interface RebateAgreement {
  // ...
  returnRule: ReturnRule | null;
  // 类型：'NO_RETURN_DEDUCTION' | 'WITH_RETURN_DEDUCTION' | null
  // 默认值：'NO_RETURN_DEDUCTION'（一块 + 采购金额/数量普通型）
  //         'NO_RETURN_DEDUCTION' 固定（一块 + 销售数量普通型）
  //         null（非一块）
  // 必填：一块下必填
  // 适用协议类型：['PURCHASE_AMOUNT_NORMAL', 'PURCHASE_QUANTITY_NORMAL', 'SALES_QUANTITY_NORMAL']
}
```

### 2.2.2 返利规则（rebateRule）

```typescript
// TODO: 实际字段名以项目代码为准
interface RebateAgreement {
  // ...
  rebateRule: RebateRule | null;
  // 类型：'PER_ITEM' | 'PER_X_ITEMS' | null
  // 默认值：'PER_ITEM'
  // 必填：是（一块 & 非一块均必填）
  // 适用协议类型：['PURCHASE_QUANTITY_NORMAL', 'SALES_QUANTITY_NORMAL']
  // null 仅当协议类型为按采购金额-普通型时不适用
}
```

## 2.3 阶梯实体字段变更

> **触发条件**：`rebateRule = 'PER_X_ITEMS'`
> **影响范围**：协议总体限制阶梯（overallLadders） + 返利商品限制阶梯（productRestriction.ladders）

### 2.3.1 原有字段

| 字段 | 处理方式 |
|------|---------|
| 每个返利金额（rebateAmountPerUnit） | `rebateRule = 'PER_X_ITEMS'` 时该字段为 null，改用 perX + rebateAmount |

### 2.3.2 新增字段

| 字段 | 类型 | 必填 | 校验规则 |
|------|------|------|---------|
| 每满X（perX） | `Integer` | 是 | ＞0 的整数 |
| 返利金额（rebateAmount） | `BigDecimal` | 是 | ＞0，最多 2 位小数 |

```typescript
// TODO: 实际字段名以项目代码为准
interface RebateLadder {
  minQuantity: number;              // 阶梯下限
  maxQuantity: number;              // 阶梯上限
  rebateAmountPerUnit?: number;     // 每个返利金额（rebateRule=PER_ITEM 时使用）
  perX?: number;                    // 每满X件（rebateRule=PER_X_ITEMS 时使用）
  rebateAmount?: number;            // 返利金额（rebateRule=PER_X_ITEMS 时使用）
}

interface ProductRebateLadder {
  productId: string;                // TODO: 确认实际字段
  purchasePrice?: number;           // 约定购进单价
  ladders: RebateLadder[];
}
```

### 2.3.3 默认值策略

| 字段 | 默认值 | 适用条件 |
|------|--------|---------|
| `returnRule` | `NO_RETURN_DEDUCTION` | 一块 + 采购金额/数量-普通型 新建时 |
| `returnRule` | `NO_RETURN_DEDUCTION`（不可更改） | 一块 + 销售数量-普通型 |
| `rebateRule` | `PER_ITEM` | 一块 & 非一块 + 采购数量/销售数量-普通型 新建时 |

---

# 3. 校验规则

> 校验触发时机：新增/修改接口入参校验。前端校验为补充，最终以后端校验为准。

## 3.1 计退规则

| 校验项 | 规则 |
|--------|------|
| 必填 | `applicableParty = 'YIKUAI'` 且协议类型为采购金额/采购数量时必填 |
| 可选值 | `NO_RETURN_DEDUCTION` / `WITH_RETURN_DEDUCTION` |
| 只读 | 协议类型为销售数量时，仅允许 `NO_RETURN_DEDUCTION` |
| 不允许 | 非一块医药时，必须为 null |

## 3.2 返利规则

| 校验项 | 规则 |
|--------|------|
| 必填 | 协议类型为采购数量/销售数量时必填 |
| 可选值 | `PER_ITEM` / `PER_X_ITEMS` |
| 不允许 | 协议类型为采购金额时，必须为 null |

## 3.3 阶梯：每满X（perX）

| 校验项 | 规则 | 错误码/提示 |
|--------|------|-----------|
| 必填 | `rebateRule = 'PER_X_ITEMS'` 时必填 | `"仅支持＞0的整数"` |
| 类型 | Integer | `"仅支持＞0的整数"` |
| 范围 | ＞0 | `"仅支持＞0的整数"` |

## 3.4 阶梯：返利金额（rebateAmount）

| 校验项 | 规则 | 错误码/提示 |
|--------|------|-----------|
| 必填 | `rebateRule = 'PER_X_ITEMS'` 时必填 | `"仅支持＞0的数字"` |
| 类型 | BigDecimal | `"仅支持＞0的数字"` |
| 范围 | ＞0 | `"仅支持＞0的数字"` |
| 精度 | 最多 2 位小数 | `"仅支持＞0的数字"` |

## 3.5 字段互斥校验

| 条件 | 规则 |
|------|------|
| `rebateRule = 'PER_ITEM'` | `perX` 和 `rebateAmount` 必须为 null；`rebateAmountPerUnit` 必填 |
| `rebateRule = 'PER_X_ITEMS'` | `rebateAmountPerUnit` 必须为 null；`perX` 和 `rebateAmount` 必填 |

> 保存接口（包含新增、修改、保存总体限制、保存商品限制等所有写接口）均以 `rebateRule` 为准做严格互斥校验：入参携带非当前规则字段时直接校验失败，不由后端静默清空，避免修改协议时残留历史字段造成计算歧义。

---

# 4. API 接口

## 4.1 接口清单

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 新增协议 | POST | `TODO: /api/rebate/agreement` | 创建返利协议 |
| 修改协议 | PUT | `TODO: /api/rebate/agreement/{id}` | 更新返利协议 |
| 查询协议详情 | GET | `TODO: /api/rebate/agreement/{id}` | 查询单个协议 |
| 查询协议列表 | GET | `TODO: /api/rebate/agreement/list` | 分页查询协议列表 |

## 4.2 请求/响应结构

> [!warning]
> 阶梯字段不得混传：
> - `rebateRule='PER_ITEM'`：仅允许 `rebateAmountPerUnit`，禁止 `perX`、`rebateAmount`
> - `rebateRule='PER_X_ITEMS'`：仅允许 `perX`、`rebateAmount`，禁止 `rebateAmountPerUnit`
> - 规则适用于总体限制阶梯与商品限制阶梯的所有保存场景

```typescript
// TODO: 以项目实际结构为准

// ===== 新增/修改请求 =====
interface SaveRebateAgreementRequest {
  // ... 原有字段
  returnRule?: string | null;          // 计退规则
  rebateRule?: string | null;          // 返利规则
  overallLadders: RebateLadder[];      // 协议总体限制阶梯
  productRestrictions: {               // 返利商品限制
    productId: string;
    purchasePrice?: number;
    ladders: RebateLadder[];
  }[];
}

// ===== 查询响应 =====
interface RebateAgreementResponse {
  id: string;
  // ... 原有字段
  returnRule: string | null;
  rebateRule: string | null;
  overallLadders: RebateLadder[];
  productRestrictions: {
    productId: string;
    purchasePrice?: number;
    ladders: RebateLadder[];
  }[];
}
```

---

# 5. 业务规则

## 5.1 字段适用矩阵

> 后端在保存/查询时，根据以下矩阵决定字段的读写行为。

| 协议类型 | 一块医药 | 非一块 |
|---------|---------|--------|
| 按采购金额 | returnRule: 可读写（可选不计退/计退） | returnRule: 强制 null |
| 按采购数量 | returnRule: 可读写（可选不计退/计退）<br>rebateRule: 可读写（可选每1件/每满X件） | returnRule: 强制 null<br>rebateRule: 可读写（可选每1件/每满X件） |
| 按销售数量 | returnRule: 可读、不可写（固定不计退）<br>rebateRule: 可读写（可选每1件/每满X件） | returnRule: 强制 null<br>rebateRule: 可读写（可选每1件/每满X件） |

## 5.2 阶梯字段规则

| rebateRule | rebateAmountPerUnit | perX | rebateAmount |
|------------|--------------------|------|-------------|
| `PER_ITEM` | 必填 | null | null |
| `PER_X_ITEMS` | null | 必填 | 必填 |
| null（按采购金额） | 必填 | null | null |

## 5.3 历史数据兼容策略

| 场景 | 处理规则 |
|------|---------|
| 一块 + 采购金额/采购数量历史协议 `returnRule` 为空 | 查询、编辑、计算前按 `NO_RETURN_DEDUCTION` 处理；如项目采用数据库迁移，可批量补为 `NO_RETURN_DEDUCTION` |
| 一块 + 销售数量历史协议 `returnRule` 为空 | 查询、编辑、计算前固定按 `NO_RETURN_DEDUCTION` 处理，并在响应中返回该值 |
| 非一块历史协议 `returnRule` 为空 | 保持 `null`，按原有逻辑处理 |
| 采购数量/销售数量历史协议 `rebateRule` 为空 | 查询、编辑、计算前按 `PER_ITEM` 处理；如项目采用数据库迁移，可批量补为 `PER_ITEM` |

> 如果项目最终选择不做数据库迁移，新增/修改/查询/计算入口都需要使用同一套默认值归一化逻辑，避免同一协议在不同接口中表现不一致。

---

# 附录A：原始截图参考

- 按采购金额-普通型：![](https://file.tapd.cn/compress/compress_img/1400/tapd_40013426_base64_1776918122_730.png?src=/tfl/captures/2026-04/tapd_40013426_base64_1776918122_730.png)
- 按采购数量-普通型：![](https://file.tapd.cn/compress/compress_img/1400/tapd_40013426_base64_1776928047_885.png?src=/tfl/captures/2026-04/tapd_40013426_base64_1776928047_885.png)
- 按销售数量-普通型：![](https://file.tapd.cn/compress/compress_img/1400/tapd_40013426_base64_1776928988_962.png?src=/tfl/captures/2026-04/tapd_40013426_base64_1776928988_962.png)
- 阶梯改造（协议总体限制）：![](https://file.tapd.cn/compress/compress_img/1400/tapd_40013426_base64_1777261847_855.png?src=/tfl/captures/2026-04/tapd_40013426_base64_1777261847_855.png)
- 阶梯改造（返利商品限制-采购数量）：![](https://file.tapd.cn/compress/compress_img/1400/tapd_40013426_base64_1777261813_657.png?src=/tfl/captures/2026-04/tapd_40013426_base64_1777261813_657.png)
- 阶梯改造（协议总体限制-销售数量）：![](https://file.tapd.cn/compress/compress_img/1400/tapd_40013426_base64_1777261950_907.png?src=/tfl/captures/2026-04/tapd_40013426_base64_1777261950_907.png)
- 阶梯改造（返利商品限制-销售数量）：![](https://file.tapd.cn/compress/compress_img/1400/tapd_40013426_base64_1777261985_772.png?src=/tfl/captures/2026-04/tapd_40013426_base64_1777261985_772.png)
