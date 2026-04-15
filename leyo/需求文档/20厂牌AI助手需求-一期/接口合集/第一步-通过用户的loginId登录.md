````
# 用户登录

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /public-api/sign-in:
    post:
      summary: 用户登录
      deprecated: false
      description: |-
        :::note[接口简介]
        通过个人账号与密码登录，获取合法的用户Token。
        :::
      tags:
        - 身份认证
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                domain:
                  type: string
                  title: 域名
                loginId:
                  type: string
                  description: "用户界面登录以及通过api管理用户属性的id\t"
                  title: 登录用户的loginId
                password:
                  type: string
                  title: "密码\t"
                  description: 原始密码经过Base64编码后的字符串
              required:
                - domain
                - loginId
                - password
              x-apifox-orders:
                - domain
                - loginId
                - password
            example:
              domain: demo
              loginId: Id1
              password: my_password_base64_encoded
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: object
                    properties:
                      token:
                        type: string
                        title: uIdToken
                      expireAt:
                        type: string
                        title: 过期时间
                    x-apifox-orders:
                      - token
                      - expireAt
                    title: 响应结果
                    description: 响应结果
                    required:
                      - token
                      - expireAt
                  result:
                    type: string
                    title: 请求状态
                    description: '枚举值: ok、fail'
                x-apifox-orders:
                  - result
                  - response
                required:
                  - response
                  - result
              example:
                result: ok
                response:
                  token: >-
                    eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxLVNRZE5XVXRGajZ3ZE5jQjJBNmF5cU5yZDlueFdwL1RSSk5vYWJHTFh0UitkeUwwSVRVVjNLMXpMNnBYNFNiaU1oeXltWk1ZUlAzTUhhUWVXT2phdklidGtNNzJIRkN1UVZpM1Fid0x1aUQyc3A4clhlcWsyZTV5L1B6aU5Pdz09IiwiaXNzIjoiZ3VhbmRhdGEuY29tIiwiZXhwIjoxNzI4NDUyMzE5LCJpYXQiOjE3MjcyNDI3MTksImluaXRUaW1lIjoiMjAyNC0wOS0yNSAxMzozODozOS43MDYiLCJqdGkiOiIxOGFjYzgxZmU3NGQ5NzBkZGYzNmZmNzAwMTM3OGE0N2U4NjExZWNkMTk2ZGMzZjE3MjUxZmQ0MmNiOGQ2NmNjOGE0MGJmYzg1MDZlMjQzODAxODE1ODY2M2RmYWUzMTA1M2MzODFkMzkzNmZjMmYwOTA2ZjU0NGE1YzRmMmNiOWVlNDM0ZjFmNDk0ZDRmMWIwMjAxMjJhMmM2ZDQzZGQwYjViZGE0YTc4YmY5MmI0Y2Y1NzM5ZmI4ZjQ4ZjE1MTY4OWZlOTBiMWFhMTExYjI5ZWJhYzc2ZDU4OTBlZWQwOGVhYTE2ZDI4NjEwYWNjMDM1MzhlNWJmNjA2Y2JjOGY3IiwicHdkVmVyc2lvbiI6MS4wfQ._XUe3kHbLVac8EcrJq8EtrcnMdxdwkkZvHkd523phI4
                  expireAt: '2024-09-26 13:38:39.707'
          headers: {}
          x-apifox-name: 成功
        '500':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  result:
                    type: string
                    title: 请求状态
                    description: '枚举值: ok、fail'
                  response:
                    type: 'null'
                    title: 响应结果
                    description: ''
                  error:
                    type: object
                    properties:
                      status:
                        type: integer
                        title: 错误码
                        description: ''
                      message:
                        type: string
                        title: 信息
                        description: ''
                      detail:
                        type: object
                        properties:
                          notifyType:
                            type: integer
                            title: 错误消息类型
                            description: 枚举值：0、1
                        required:
                          - notifyType
                        x-apifox-orders:
                          - notifyType
                        title: 详情
                        description: ''
                    required:
                      - status
                      - message
                      - detail
                    x-apifox-orders:
                      - status
                      - message
                      - detail
                    title: 错误信息
                    description: ''
                required:
                  - result
                  - response
                  - error
                x-apifox-orders:
                  - result
                  - response
                  - error
              example:
                result: fail
                response: null
                error:
                  status: 5001
                  message: >-
                    code: 1012, messageKey: null, msg: Failed to decode
                    password., notifyType: 1
                  detail:
                    notifyType: 1
          headers: {}
          x-apifox-name: 密码错误
      security: []
      x-apifox-folder: 身份认证
      x-apifox-status: released
      x-run-in-apifox: https://api.guandata.com/web/project/345092/apis/api-3470502-run
components:
  schemas: {}
  securitySchemes: {}
servers: []
security: []

```
````

