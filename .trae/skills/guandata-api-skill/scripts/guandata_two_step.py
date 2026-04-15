#!/usr/bin/env python3
import argparse
import base64
import json
import sys
import urllib.error
import urllib.request


def post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)

    req = urllib.request.Request(url=url, data=data, headers=request_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            return json.loads(body)
        except json.JSONDecodeError as json_error:
            raise RuntimeError(f"HTTP {exc.code}: {body}") from json_error
    except urllib.error.URLError as exc:
        raise RuntimeError(f"请求失败: {exc}") from exc


def parse_body(raw: str | None, default_view: str = "GRID") -> dict:
    if not raw:
        return {"view": default_view, "offset": 0, "limit": 10}
    try:
        body = json.loads(raw)
        # 确保有 view 参数
        if "view" not in body:
            body["view"] = default_view
        return body
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"--body 不是合法 JSON: {exc}") from exc


def extract_access_token(login_response: dict) -> str:
    token = login_response.get("response", {}).get("token")
    if not token:
        raise RuntimeError(
            "登录失败，未返回访问 Token。"
            f" 原始响应: {json.dumps(login_response, ensure_ascii=False)}"
        )
    return token


def login_with_password(base_url: str, domain: str, login_id: str, password: str) -> dict:
    """使用 domain + loginId + password 登录"""
    login_url = f"{base_url}/public-api/sign-in"
    
    login_payload = {
        "domain": domain,
        "loginId": login_id,
        "password": password,  # 已经是 Base64 编码，直接使用
    }
    
    print(f"正在登录: {login_url}", file=sys.stderr)
    print(f"登录参数: domain={domain}, loginId={login_id}", file=sys.stderr)
    
    return post_json(login_url, login_payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="观远两步调用脚本")
    parser.add_argument("--base-url", required=True, help="观远业务域名，例如 https://bi.leyopharm.com")
    parser.add_argument("--domain", default="guanbi", help="观远平台域名标识，默认 guanbi")
    parser.add_argument("--login-id", required=True, help="用户 loginId")
    parser.add_argument("--password", required=True, help="用户密码（Base64 编码）")
    parser.add_argument(
        "--type",
        choices=["dataset", "card"],
        default="card",
        help="第二步接口类型: dataset(数据集) 或 card(卡片)，默认 card",
    )
    parser.add_argument("--ds-id", help="数据集 dsId（当 type=dataset 时必填）")
    parser.add_argument("--card-id", help="卡片 cardId（当 type=card 时必填）")
    parser.add_argument("--body", help="第二步请求体 JSON 字符串，默认包含 view: GRID")
    parser.add_argument("--view", default="GRID", choices=["GRID", "GRAPH"], help="数据视图类型: GRID(表格) 或 GRAPH(图表)，默认 GRID")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    body = parse_body(args.body, default_view=args.view)

    # 验证参数
    if args.type == "dataset" and not args.ds_id:
        parser.error("当 --type=dataset 时，--ds-id 为必填参数")
    if args.type == "card" and not args.card_id:
        parser.error("当 --type=card 时，--card-id 为必填参数")

    # 第一步：登录获取访问 Token
    login_response = login_with_password(base_url, args.domain, args.login_id, args.password)
    
    print(f"登录响应: {json.dumps(login_response, ensure_ascii=False, indent=2)}", file=sys.stderr)
    
    if login_response.get("result") != "ok":
        error_msg = login_response.get("error", {}).get("message", "未知错误")
        raise RuntimeError(f"登录失败: {error_msg}")
    
    access_token = extract_access_token(login_response)
    
    print(f"获取访问 Token 成功", file=sys.stderr)

    # 第二步：根据类型调用对应接口
    if args.type == "dataset":
        data_url = f"{base_url}/public-api/data-source/{args.ds_id}/data"
    else:  # card
        data_url = f"{base_url}/public-api/card/{args.card_id}/data"

    print(f"正在获取数据: {data_url}", file=sys.stderr)
    print(f"请求体: {json.dumps(body, ensure_ascii=False)}", file=sys.stderr)
    
    data_response = post_json(
        data_url,
        body,
        headers={"X-Auth-Token": access_token},
    )

    sys.stdout.write(json.dumps(data_response, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"错误: {str(exc)}", file=sys.stderr)
        raise SystemExit(1)
