"""
Sync Terraform outputs (dev environment) into docs/infra/environments/dev/README.md.

Requirements on CI/local:
- Terraform installed and initialized (terraform init)
- AWS creds available (if using remote backend)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_DIR = REPO_ROOT / "terraform" / "environments" / "dev"
DOC_PATH = REPO_ROOT / "docs" / "infra" / "environments" / "dev" / "README.md"


def run_command(command: list[str], cwd: Path | None = None) -> str:
    try:
        output = subprocess.check_output(
            command,
            cwd=str(cwd) if cwd else None,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return output
    except subprocess.CalledProcessError as exc:
        print(exc.output)
        raise


def safe_get(obj: dict, path: list[str], default):
    cur = obj
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def main() -> int:
    try:
        tf_out = run_command(["terraform", "output", "-json"], cwd=ENV_DIR)
    except Exception:
        print(
            "ERROR: terraform output failed. Ensure Terraform is installed,"
            " initialized (terraform init), and AWS credentials are configured.",
            file=sys.stderr,
        )
        return 1

    data = json.loads(tf_out)

    def val(key: str, default=None):
        v = data.get(key, {}).get("value")
        return v if v is not None else default

    api_url = val("api_gateway_url", "-")
    ws_url = val("websocket_api_url", "-")
    frontend = val("frontend_website", {}) or {}
    cf_url = frontend.get("cloudfront_url", "-")
    s3_site = frontend.get("website_endpoint", "-")

    vpc_id = val("vpc_id", "-")
    cidr = val("vpc_cidr_block", "-")
    priv = val("private_subnet_ids", []) or []
    publ = val("public_subnet_ids", []) or []

    lambdas = val("lambda_functions", {}) or {}
    layer_arn = safe_get(val("lambda_layer", {}) or {}, ["common_utils", "arn"], "-")
    role_arn = safe_get(val("iam_roles", {}) or {}, ["lambda_exec_role"], "-")

    sns = val("sns_topics", {}) or {}

    lines: list[str] = []
    lines.append("# Dev Environment")
    lines.append("")
    lines.append("## Endpoints")
    lines.append(f"- HTTP API: `{api_url}`")
    lines.append(f"- WebSocket API: `{ws_url}`")
    lines.append(f"- Frontend (CloudFront): `{cf_url}`")
    lines.append(f"- Frontend (S3 website): `{s3_site}`")
    lines.append("")

    lines.append("## Networking")
    lines.append(f"- VPC: `{vpc_id}` (CIDR `{cidr}`)")
    if priv:
        lines.append("- Private subnets: " + ", ".join(f"`{x}`" for x in priv))
    if publ:
        lines.append("- Public subnets: " + ", ".join(f"`{x}`" for x in publ))
    lines.append("")

    lines.append("## Lambda Layer & IAM")
    lines.append(f"- Common utils layer: `{layer_arn}`")
    lines.append(f"- Lambda exec role: `{role_arn}`")
    lines.append("")

    lines.append("## Lambda Functions")
    for name in sorted(lambdas.keys()):
        obj = lambdas.get(name, {}) or {}
        n = obj.get("name", "-")
        a = obj.get("arn", "-")
        lines.append(f"- {name}: `{n}` | `{a}`")
    lines.append("")

    lines.append("## SNS Topics (legacy)")
    for k in sorted(sns.keys()):
        lines.append(f"- {k}: `{sns[k]}`")
    lines.append("")

    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Updated {DOC_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


