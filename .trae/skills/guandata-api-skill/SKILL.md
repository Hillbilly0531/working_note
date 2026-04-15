---
name: guandata-api-skill
description: 用于观远开放平台接口联调与两步调用。 当需要根据企业观远域名先通过 loginId 登录换取访问 Token，再调用数据集或卡片接口获取数据时使用；支持获取数据集数据和获取卡片数据两种第二步接口。
---

# 观远接口联调 Skill

## 概览

围绕观远开放平台的最小可落地链路工作：先登录，再取数据。

支持两种第二步接口：
1. **获取数据集数据** - `/public-api/data-source/{dsId}/data`
2. **获取卡片数据** - `/public-api/card/{cardId}/data`

优先输出第二步接口的返回结果；只有在失败时，才补充说明失败发生在第几步以及缺少什么关键信息。

## 快速流程

按下面顺序执行：

1. 确认实际业务域名，不要把 `api.guandata.com` 当成调用 Host。
2. 用 `baseUrl + /public-api/user/loginId/sign-in` 发起登录。
3. 从登录响应中提取 `response.token`。
4. 根据用户选择的类型，调用对应接口：
   - 数据集：`baseUrl + /public-api/data-source/{dsId}/data`
   - 卡片：`baseUrl + /public-api/card/{cardId}/data`
5. 最终以第二步接口的响应 JSON 作为主要结果返回。

## 输入要求

### 通用输入（第一步登录）

```json
{
  "baseUrl": "https://bi.leyopharm.com",
  "appToken": "<应用Token>",
  "loginId": "<用户loginId>"
}
```

### 第二步输入

**获取数据集数据：**
```json
{
  "type": "dataset",
  "dsId": "<数据集ID>"
}
```

**获取卡片数据：**
```json
{
  "type": "card",
  "cardId": "<卡片ID>"
}
```

如未提供第二步请求体，默认使用：

```json
{
  "offset": 1,
  "limit": 10
}
```

## 执行要点

### 1. 识别真实调用地址

- 文档站点 `https://api.guandata.com` 只用来看接口说明。
- 真正调用时必须走企业自己的观远域名，例如 `https://bi.leyopharm.com`。

### 2. 第一步只负责拿访问 Token

- 登录请求体中的 `token` 是应用 Token，不是访问 Token。
- 第二步请求头中的 `X-Auth-Token` 必须使用第一步返回的访问 Token。

### 3. 优先返回第二步结果

- 如果两步都成功，直接返回第二步 JSON。
- 不要把结果包装成额外层级，除非用户明确要求。
- 如果用户只关心数据，优先保留观远原始响应结构中的 `result`、`response` 等字段。

### 4. 失败时的排查顺序

按这个顺序检查：

1. `baseUrl` 是否为企业观远域名
2. `appToken` 是否正确
3. `loginId` 是否正确
4. `dsId`/`cardId` 是否存在且当前账号有权限
5. 第二步请求体字段是否符合目标数据要求

### 5. 使用脚本执行

优先使用脚本：

`scripts/guandata_two_step.py`

**示例 - 获取数据集数据：**

```bash
python scripts/guandata_two_step.py ^
  --base-url "https://bi.leyopharm.com" ^
  --app-token "<应用Token>" ^
  --login-id "<用户loginId>" ^
  --type dataset ^
  --ds-id "<数据集ID>" ^
  --body "{\"offset\":1,\"limit\":10}"
```

**示例 - 获取卡片数据：**

```bash
python scripts/guandata_two_step.py ^
  --base-url "https://bi.leyopharm.com" ^
  --app-token "<应用Token>" ^
  --login-id "<用户loginId>" ^
  --type card ^
  --card-id "<卡片ID>" ^
  --body "{\"offset\":1,\"limit\":10}"
```

脚本标准输出只打印第二步接口响应 JSON。

## 参考资料

需要查看接口链路、示例请求或排查说明时，读取：

- `references/guandata-two-step.md`

## 输出约定

- 成功：返回第二步接口的原始 JSON 结果。
- 失败：简要指出失败步骤，并附上关键错误信息。
