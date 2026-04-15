# 观远接口联调说明：两步调用

本文档用于说明如何在 `https://bi.leyopharm.com` 上完成以下两步调用：

1. 通过 `domain` + `loginId` + `password` 登录，换取访问 Token
2. 将第一步返回的访问 Token 作为 `X-Auth-Token`，调用数据接口

支持两种第二步接口：
- **获取数据集数据** - `/public-api/data-source/{dsId}/data`
- **获取卡片数据** - `/public-api/card/{cardId}/data`

适用场景：

- 为 `guandata-api-skill` 梳理最小可落地的接口链路
- 先打通观远开放平台鉴权，再逐步补充后续报表或卡片查询接口

## 参考文档

### 核心接口文档
- 用户登录接口：`https://api.guandata.com/apidoc/docs-site/345092/730/api-3470502`
- 通过 loginId 登录接口：`https://api.guandata.com/apidoc/docs-site/345092/730/api-3471182`
- 数据集数据接口：`https://api.guandata.com/apidoc/docs-site/345092/730/api-3470616`
- 卡片数据接口：`https://api.guandata.com/apidoc/docs-site/345092/730/api-3471043`

### 开发指南
- Token 鉴权：`https://api.guandata.com/apidoc/docs-site/345092/730/doc-338136.md`
- 常见概念：`https://api.guandata.com/apidoc/docs-site/345092/730/doc-338158.md`
- 卡片导出接口使用说明：`https://api.guandata.com/apidoc/docs-site/345092/730/doc-338137.md`

---

## 1. 基础信息

- 业务域名：`https://bi.leyopharm.com`
- 文档域名：`https://api.guandata.com`
- 当前已验证：`https://bi.leyopharm.com` 可正常访问，且 `/public-api/...` 路径可命中真实观远服务

注意：

- 文档站点 `api.guandata.com` 只用于看接口说明，不是实际业务调用 Host
- 实际接口调用应走企业自己的观远域名，即 `https://bi.leyopharm.com`

---

## 2. 第一步：用户登录，获取访问 Token

### 2.1 接口说明

- 方法：`POST`
- 路径：`/public-api/sign-in`
- 完整地址：`https://bi.leyopharm.com/public-api/sign-in`

### 2.2 请求参数

请求体为 JSON：

```json
{
  "domain": "guanbi",
  "loginId": "LY010307",
  "password": "eUlGNnBhX2c="
}
```

字段说明：

- `domain`：观远平台域名标识，例如 `guanbi`
- `loginId`：用户登录 ID
- `password`：原始密码经过 Base64 编码后的字符串

### 2.3 curl 示例

```bash
curl --location 'https://bi.leyopharm.com/public-api/sign-in' \
  --header 'Content-Type: application/json' \
  --data '{
    "domain": "guanbi",
    "loginId": "LY010307",
    "password": "eUlGNnBhX2c="
  }'
```

### 2.4 成功响应示例

成功时会返回可用于后续接口调用的访问 Token：

```json
{
  "result": "ok",
  "response": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expireAt": "2024-09-26 13:38:39.707"
  }
}
```

### 2.5 失败响应示例

```json
{
  "result": "fail",
  "response": null,
  "error": {
    "status": 5001,
    "message": "code: 1012, messageKey: null, msg: Failed to decode password., notifyType: 1",
    "detail": {
      "notifyType": 1
    }
  }
}
```

---

## 3. 第二步：获取卡片数据

### 3.1 接口说明

- 方法：`POST`
- 路径：`/public-api/card/{cardId}/data`
- 完整地址：`https://bi.leyopharm.com/public-api/card/{cardId}/data`

### 3.2 请求头

必须带上第一步返回的访问 Token：

```http
X-Auth-Token: <第一步返回的访问Token>
Content-Type: application/json
```

### 3.3 路径参数

- `cardId`：目标卡片 ID

### 3.4 请求体示例

```json
{
  "view": "GRID",
  "offset": 0,
  "limit": 10,
  "filters": [
    {
      "name": "字段名",
      "filterType": "GT",
      "filterValue": ["10"]
    }
  ]
}
```

字段说明：

- `view`：**必填**，数据获取方式
  - `GRID`：表格形式
  - `GRAPH`：图表形式
- `offset`：数据的起始位置，默认 0
- `limit`：获取的数据条数，默认 10
- `filters`：过滤条件列表（可选）
  - `name`：字段名
  - `filterType`：过滤类型（GT, GE, LT, LE, BT, EQ, NE, IN, NI, STARTSWITH, ENDSWITH, CONTAINS, IS_NULL, NOT_NULL 等）
  - `filterValue`：过滤值列表

### 3.5 curl 示例

```bash
curl --location 'https://bi.leyopharm.com/public-api/card/<cardId>/data' \
  --header 'X-Auth-Token: <第一步返回的访问Token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "view": "GRID",
    "offset": 0,
    "limit": 10
  }'
```

### 3.6 成功响应示例

```json
{
  "result": "ok",
  "response": {
    "chartMain": {
      "offset": 0,
      "data": [
        [{"v": 700}],
        [{"v": 739}]
      ],
      "column": {
        "meta": [
          {"title": "度量", "metaType": "METRIC"}
        ],
        "values": [
          [{"title": "单价", "type": "metric", "fdType": "LONG"}]
        ]
      },
      "count": 12,
      "limit": 10,
      "hasMoreData": true
    },
    "view": "GRID",
    "chartType": "BASIC_COLUMN",
    "cardType": "CHART"
  }
}
```

---

## 4. 第二步（数据集模式）：使用访问 Token 获取数据集数据

### 4.1 接口说明

- 方法：`POST`
- 路径：`/public-api/data-source/{dsId}/data`
- 完整地址：`https://bi.leyopharm.com/public-api/data-source/{dsId}/data`

### 4.2 请求头

```http
X-Auth-Token: <第一步返回的访问Token>
Content-Type: application/json
```

### 4.3 路径参数

- `dsId`：目标数据集 ID

### 4.4 请求体示例

```json
{
  "offset": 1,
  "limit": 10,
  "sortFactor": {
    "name": "id",
    "sortType": "desc"
  }
}
```

---

## 5. 两步串联说明

整体调用顺序如下：

1. 使用 `domain` + `loginId` + `password` 调用登录接口 `/public-api/sign-in`
2. 从登录响应中取出 `response.token`
3. 将该值放入第二步请求头 `X-Auth-Token`
4. 根据需求选择对应接口：
   - 携带 `dsId` 调用数据集数据接口
   - 携带 `cardId` 和 `view` 参数调用卡片数据接口

---

## 6. 当前待补充项

要真正调通接口，还需要确认：

- `domain` 是否正确（当前使用 `guanbi`）
- `loginId` 和 `password` 是否正确
- 目标数据集 `dsId` 或卡片 `cardId`
