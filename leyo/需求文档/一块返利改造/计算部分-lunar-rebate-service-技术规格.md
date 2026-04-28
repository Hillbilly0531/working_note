---
title: 一块返利改造 - 计算部分 (Lunar Rebate Service) 技术规格
date: 2026-04-28
status: draft
tags:
  - 一块返利
  - Lunar Rebate
  - 返利计算
  - 技术规格
aliases:
  - 一块返利计算改造-技术规格
---

# 1. 概述

## 1.1 改造范围

本次改造涉及 Lunar Rebate Service 中三种普通型返利协议的计算逻辑：

| 序号 | 协议类型 | 涉及改动 |
|------|---------|---------|
| 1 | 按采购金额-普通型 | 所属阶梯 + 计算应返：按【计退规则】分支处理 |
| 2 | 按采购数量-普通型 | 所属阶梯 + 计算应返：按【计退规则】分支；计返公式：按【返利规则】分支 |
| 3 | 按销售数量-普通型 | 归属合同 + 计算应返：按【计退规则】分支；计返公式：按【返利规则】分支 |

## 1.2 适用方差异总览

| 计算节点 | 一块医药 | 非一块（乐药等） |
|---------|---------|-----------------|
| 计退规则 | 按配置值（不计退/计退）执行对应分支 | 计退规则＝空，保留现状 |
| 返利规则 | 按配置值（每1件/每满X件）执行对应公式 | 现有类型为"每1件返利"，新增"每满X件返利" |
| 归属合同（按销售数量） | 计退规则≠空时按出库时间，否则按支付时间 | 保留现状（按支付时间） |

---

# 2. 数据模型

## 2.1 输入参数

### 2.1.1 协议配置

```typescript
// TODO: 实际类型名以项目代码为准
interface RebateAgreementConfig {
  agreementType: 'PURCHASE_AMOUNT' | 'PURCHASE_QUANTITY' | 'SALES_QUANTITY';
  subType: 'NORMAL'; // 普通型
  applicableParty: 'YIKUAI' | 'NON_YIKUAI'; // 一块 / 非一块
  returnRule?: 'NO_RETURN_DEDUCTION' | 'WITH_RETURN_DEDUCTION'; // 计退规则，非一块为 undefined
  rebateRule?: 'PER_ITEM' | 'PER_X_ITEMS'; // 返利规则（仅采购数量/销售数量有此字段）

  // 协议总体限制 - 阶梯列表
  overallLadders: RebateLadder[];

  // 返利商品限制 - 商品列表，每个商品含阶梯列表
  productRestrictions: ProductRebateLadder[];
}

interface RebateLadder {
  minQuantity: number;      // 阶梯下限
  maxQuantity: number;      // 阶梯上限
  rebateAmountPerUnit?: number; // 每个返利金额（返利规则=每1件时使用）
  perX?: number;            // 每满X件（返利规则=每满X件时使用）
  rebateAmount?: number;    // 返利金额（返利规则=每满X件时使用）
}
```

### 2.1.2 业务数据

```typescript
// TODO: 实际类型名以项目代码为准
interface RebateBusinessData {
  // --- 按采购金额/采购数量 ---
  purchaseOrderTime?: Date;        // 采购订单下单时间
  purchaseInboundAmount?: number;  // 采购入库金额
  purchaseInboundQuantity?: number; // 采购入库数量
  purchaseReturnOutAmount?: number; // 采退出库金额
  purchaseReturnOutQuantity?: number; // 采退出库数量

  // --- 按销售数量 ---
  salesPayTime?: Date;             // 销售单支付时间
  salesOutTime?: Date;             // 销售单出库时间
  salesOutQuantity?: number;       // 销售出库数量
  salesReturnInQuantity?: number;  // 销退入库数量
}
```

## 2.2 输出结果

```typescript
// TODO: 实际类型名以项目代码为准
interface RebateCalculationResult {
  contractOwnership: any;           // 归属合同信息（TODO: 确认结构）
  matchedLadder: RebateLadder;      // 命中的阶梯
  ladderQuantity: number;           // 用于阶梯匹配的数量值
  rebateFormula: string;            // 计返公式描述
  rebateAmount: number;             // 应返金额
  overallRebateAmount: number;      // 总体限制模块返利金额
  productRebateAmounts: number[];   // 各商品限制模块返利金额
  totalRebateAmount: number;        // 总返利金额 = overallRebateAmount + ΣproductRebateAmounts
}
```

## 2.3 枚举定义

与协议管理文档 [2.1 节](./页面部分-pms-rebate-技术规格.md#21-新增枚举) 共用：

| 枚举 | 值 | 说明 |
|------|-----|------|
| `ReturnRule` | `NO_RETURN_DEDUCTION` / `WITH_RETURN_DEDUCTION` | 计退规则 |
| `RebateRule` | `PER_ITEM` / `PER_X_ITEMS` | 返利规则 |

---

# 3. 计算逻辑

> **通用规则**：`totalRebateAmount = overallRebateAmount + ΣproductRebateAmounts`
> 即总返利 = 协议总体限制模块返利 + 各商品限制模块返利之和

---

## 3.1 按采购金额-普通型

### 3.1.1 归属合同

| 适用方 | 规则 |
|--------|------|
| 一块 & 非一块 | 按采购订单的【下单时间】计（**保留现状，不受改造影响**） |

### 3.1.2 所属阶梯

| 计退规则 | 阶梯计算基数 | 说明 |
|---------|------------|------|
| 空（非一块） | `purchaseInboundAmount` | 保留现状 |
| `NO_RETURN_DEDUCTION` | `purchaseInboundAmount` | 采购入库金额 |
| `WITH_RETURN_DEDUCTION` | `purchaseInboundAmount - purchaseReturnOutAmount` | 采购入库金额 - 采退出库金额 |

```pseudocode
function getLadderQuantity(input) {
  if (input.returnRule === undefined) {
    return input.purchaseInboundAmount                    // 保留现状
  }
  if (input.returnRule === 'NO_RETURN_DEDUCTION') {
    return input.purchaseInboundAmount
  }
  if (input.returnRule === 'WITH_RETURN_DEDUCTION') {
    return input.purchaseInboundAmount - input.purchaseReturnOutAmount
  }
}
```

### 3.1.3 计算应返

| 计退规则 | 应返计算公式 | 说明 |
|---------|------------|------|
| 空（非一块） | 按 `purchaseInboundAmount` 计返 - 按 `purchaseReturnOutAmount` 计返 | 保留现状 |
| `NO_RETURN_DEDUCTION` | 按 `purchaseInboundAmount` 计返 | — |
| `WITH_RETURN_DEDUCTION` | 按 `purchaseInboundAmount - purchaseReturnOutAmount` 计返 | — |

### 3.1.4 计返公式

**保留现状**，不受改造影响。

> 该协议类型不涉及每件/每满X件的区分，仅按金额阶梯计算返利金额。

---

## 3.2 按采购数量-普通型

### 3.2.1 归属合同

| 适用方 | 规则 |
|--------|------|
| 一块 & 非一块 | 按采购订单的【下单时间】计（**保留现状，不受改造影响**） |

### 3.2.2 所属阶梯

| 计退规则 | 阶梯计算基数 | 说明 |
|---------|------------|------|
| 空（非一块） | `purchaseInboundQuantity` | 保留现状 |
| `NO_RETURN_DEDUCTION` | `purchaseInboundQuantity` | 采购入库数量 |
| `WITH_RETURN_DEDUCTION` | `purchaseInboundQuantity - purchaseReturnOutQuantity` | 采购入库数量 - 采退出库数量 |

```pseudocode
function getLadderQuantity(input) {
  if (input.returnRule === undefined) {
    return input.purchaseInboundQuantity                  // 保留现状
  }
  if (input.returnRule === 'NO_RETURN_DEDUCTION') {
    return input.purchaseInboundQuantity
  }
  if (input.returnRule === 'WITH_RETURN_DEDUCTION') {
    return input.purchaseInboundQuantity - input.purchaseReturnOutQuantity
  }
}
```

### 3.2.3 计算应返

| 计退规则 | 应返计算公式 | 说明 |
|---------|------------|------|
| 空（非一块） | 按 `purchaseInboundQuantity` 计返 - 按 `purchaseReturnOutQuantity` 计返 | 保留现状 |
| `NO_RETURN_DEDUCTION` | 按 `purchaseInboundQuantity` 计返 | — |
| `WITH_RETURN_DEDUCTION` | 按 `purchaseInboundQuantity - purchaseReturnOutQuantity` 计返 | — |

### 3.2.4 计返公式

#### 总公式

```
totalRebateAmount = overallRebateAmount + Σ productRebateAmounts
```

单个模块（总体限制 / 商品限制）的返利金额计算取决于返利规则：

---

#### 返利规则 = `PER_ITEM`（每1件返利）

**保留现状**：

**以最高阶梯计算**：
```
rebate = min(quantity, ladder.maxQuantity) × ladder.rebateAmountPerUnit
```

**以分级阶梯计算**：
```
// 伪代码
total = 0
remainingQty = min(quantity, currentLadder.maxQuantity)
for each ladder from lowest to current:
  tierQty = ladder.maxQuantity - (prevLadder?.maxQuantity ?? 0)
  if remainingQty > tierQty:
    total += tierQty × ladder.rebateAmountPerUnit
    remainingQty -= tierQty
  else:
    total += remainingQty × ladder.rebateAmountPerUnit
    break
```

---

#### 返利规则 = `PER_X_ITEMS`（每满X件返利）

**以最高阶梯计算**：
```
rebate = ROUNDDOWN( min(quantity, ladder.maxQuantity) ÷ ladder.perX ) × ladder.rebateAmount
```

**以分级阶梯计算**：
```
所属阶梯返利 = ROUNDDOWN( (min(quantity, currentLadder.maxQuantity) - nextLowerLadder.maxQuantity) ÷ currentLadder.perX ) × currentLadder.rebateAmount

各下级阶梯返利 = ( (ladder.maxQuantity - nextLowerLadder.maxQuantity) ÷ ladder.perX ) × ladder.rebateAmount

// 注意：所属阶梯用 ROUNDDOWN，各下级阶梯是否 ROUNDDOWN 取决于实现（原文未标注）
// TODO: 确认下级阶梯是否也需 ROUNDDOWN
```

### 3.2.5 计算示例

**示例1**：协议采购每满 10 个返 3 元，不计采退，以最高阶梯计算，最高阶梯为 5000

| 参数 | 值 |
|------|-----|
| 采购入库数量 | 1003 |
| 每满X | 10 |
| 返利金额 | 3 |
| 最高阶梯上限 | 5000 |

```
rebate = ROUNDDOWN( min(1003, 5000) ÷ 10 ) × 3
       = ROUNDDOWN( 1003 ÷ 10 ) × 3
       = ROUNDDOWN( 100.3 ) × 3
       = 100 × 3
       = 300
```

**示例2**：协议采购每满 10 个返 1 个（等价于返等值金额），不计采退，以最高阶梯计算

| 参数 | 值 |
|------|-----|
| 每满X | 11 |
| 返利金额 | 等于"约定购进单价" |

> 协议配置时按【商品 + 约定购进单价】设置，每 11 个返利金额 = 约定购进单价，计算按 `PER_X_ITEMS` 公式即可。

---

## 3.3 按销售数量-普通型

### 3.3.1 归属合同

| 计退规则 | 规则 | 说明 |
|---------|------|------|
| 空（非一块） | 按销售单的【支付时间】计 | 保留现状 |
| ≠空（一块） | 按销售单的【出库时间】计 | **改造点** |

```pseudocode
function getContractTime(input) {
  if (input.returnRule === undefined) {
    return input.salesPayTime     // 保留现状：按支付时间
  }
  return input.salesOutTime       // 一块：按出库时间
}
```

### 3.3.2 所属阶梯

**保留现状，不受改造影响**：

| 适用方 | 阶梯计算基数 |
|--------|------------|
| 一块 & 非一块 | 按 `salesOutQuantity`（销售出库数量）|

### 3.3.3 计算应返

| 计退规则 | 应返计算公式 | 说明 |
|---------|------------|------|
| 空（非一块） | 按 `salesOutQuantity` 计返 - 按 `salesReturnInQuantity` 计返 | 保留现状（销售出库 - 销退入库） |
| `NO_RETURN_DEDUCTION` | 按 `salesOutQuantity` 计返 | 一块：不计退，仅按销售出库 |

> **注意**：按销售数量的协议，一块仅支持"不计退"，因此计退规则 ≠ 空 时直接按销售出库数量计返，不减去销退。

### 3.3.4 计返公式

与 [3.2.4 按采购数量-计返公式](#324-计返公式) 完全一致：

```
totalRebateAmount = overallRebateAmount + Σ productRebateAmounts
```

| 返利规则 | 以最高阶梯 | 以分级阶梯 |
|---------|----------|----------|
| `PER_ITEM` | `min(quantity, maxQuantity) × rebateAmountPerUnit` | 保留现状 |
| `PER_X_ITEMS` | `ROUNDDOWN(min(quantity, maxQuantity) ÷ perX) × rebateAmount` | 见 3.2.4 公式 |

### 3.3.5 计算示例

**示例1**：协议销售每满 10 个返 3 元，以最高阶梯计算，最高阶梯为 5000

| 参数 | 值 |
|------|-----|
| 销售出库数量 | 1003 |
| 每满X | 10 |
| 返利金额 | 3 |
| 最高阶梯上限 | 5000 |

```
rebate = ROUNDDOWN( min(1003, 5000) ÷ 10 ) × 3
       = ROUNDDOWN( 100.3 ) × 3
       = 300
```

**示例2**：协议销售每满 10 个返 1 个（等价于返等值金额），以最高阶梯计算

> 协议配置时按【商品 + 约定购进单价】设置，每 11 个返利金额 = 约定购进单价。计算按规则即可。

---

# 4. 接口契约

> **TODO**: 以下为占位，以项目实际 API 为准

## 4.1 计算请求

```typescript
// TODO: 确认实际请求结构
interface CalculateRebateRequest {
  agreementId: string;                    // 协议ID
  agreementConfig: RebateAgreementConfig; // 协议配置（或从服务端按ID读取）
  businessDataList: RebateBusinessData[]; // 待计算的业务数据列表
}
```

## 4.2 计算响应

```typescript
// TODO: 确认实际响应结构
interface CalculateRebateResponse {
  results: RebateCalculationResult[];
  summary?: {
    totalRebateAmount: number;
    count: number;
  };
}
```

---

# 附录A：公式速查表

## A.1 计退规则对计算基数的影响

| 协议类型 | 计退规则 = 空 | `NO_RETURN_DEDUCTION` | `WITH_RETURN_DEDUCTION` |
|---------|-------------|----------------------|------------------------|
| 按采购金额 | `inboundAmount` | `inboundAmount` | `inboundAmount - returnOutAmount` |
| 按采购数量 | `inboundQuantity` | `inboundQuantity` | `inboundQuantity - returnOutQuantity` |
| 按销售数量 | `outQuantity`（计返减 `returnInQuantity`） | `outQuantity` | —（不支持计退） |

## A.2 返利规则对计返公式的影响

| 返利规则 | 最高阶梯公式 | 分级阶梯公式 |
|---------|------------|------------|
| `PER_ITEM` | `min(Q, max) × amountPerUnit` | 保留现状（逐级计算） |
| `PER_X_ITEMS` | `ROUNDDOWN(min(Q, max) ÷ X) × amount` | `ROUNDDOWN(tierQty ÷ X) × amount`（逐级） |

---

# 附录B：计算决策树

```
输入：协议类型、返利规则、计退规则、业务数据

1. 确定归属合同
   └── 判断依据：协议类型(仅销售数量需判断) + 计退规则
       ├── 销售数量 + 计退≠空 → 出库时间
       └── 其他 → 保留现状

2. 确定所属阶梯（计算阶梯匹配基数）
   └── 判断依据：计退规则
       ├── 空 → 保留现状
       ├── 不计退 → 入库/出库数量（不扣减退货）
       └── 计退 → 入库数量 - 退货数量

3. 匹配阶梯 → 确定层级

4. 计算应返
   └── 判断依据：计退规则 + 阶梯匹配方式
       ├── 空 → 保留现状（入-退分算）
       ├── 不计退 → 按入/出库直接计返
       └── 计退 → 按(入-退)直接计返

5. 计返公式计算
   └── 判断依据：返利规则 + 阶梯计算方式
       ├── 每1件 → 保留现状（逐级累加）
       └── 每满X件 → ROUNDDOWN公式
           ├── 最高阶梯：ROUNDDOWN(min(Q, max) ÷ X) × amount
           └── 分级阶梯：逐级 ROUNDDOWN(tierQty ÷ X) × amount

6. 汇总：总体返利 + Σ商品返利 = 总返利
```
