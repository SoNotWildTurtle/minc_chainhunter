"""Generate human-readable reports from stored scan results."""

import json
import os
import hmac
import hashlib
from datetime import datetime
from typing import List, Dict
from cryptography.fernet import Fernet


def _get_cipher() -> Fernet | None:
    key = os.getenv("MINC_ENCRYPT_KEY")
    if not key:
        return None
    try:
        return Fernet(key.encode())
    except Exception:
        return None


def load_results(db_dir: str) -> List[Dict]:
    path = os.path.join(db_dir, "results.json")
    sig_path = path + ".sig"
    if not os.path.isfile(path):
        return []
    cipher = _get_cipher()
    raw: bytes
    try:
        with open(path, "rb") as f:
            data = f.read()
        if cipher:
            raw = cipher.decrypt(data)
        else:
            raw = data
    except Exception:
        return []

    key = os.getenv("MINC_HMAC_KEY")
    if key and os.path.isfile(sig_path):
        with open(sig_path, "r", encoding="utf-8") as sf:
            expected = sf.read().strip()
        digest = hmac.new(key.encode(), raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, digest):
            return []

    try:
        return json.loads(raw.decode())
    except json.JSONDecodeError:
        return []


def save_results(results: List[Dict], db_dir: str) -> None:
    path = os.path.join(db_dir, "results.json")
    sig_path = path + ".sig"
    cipher = _get_cipher()
    os.makedirs(db_dir, exist_ok=True)
    data = json.dumps(results).encode()
    key = os.getenv("MINC_HMAC_KEY")
    if key:
        digest = hmac.new(key.encode(), data, hashlib.sha256).hexdigest()
        with open(sig_path, "w", encoding="utf-8") as sf:
            sf.write(digest)
        os.chmod(sig_path, 0o600)
    elif os.path.isfile(sig_path):
        os.remove(sig_path)
    if cipher:
        enc = cipher.encrypt(data)
        with open(path, "wb") as f:
            f.write(enc)
    else:
        with open(path, "wb") as f:
            f.write(data)
    os.chmod(path, 0o600)


def build_report(results: List[Dict], out_dir: str, fmt: str = "md", template: str | None = None) -> str:
    """Build a report in the requested format.

    If ``template`` is supplied and ``fmt`` is ``"md"``, the file is used as a
    Markdown snippet for each entry. The placeholders ``{module}``, ``{target}``,
    ``{summary}``, and ``{tags}`` are replaced with values from the stored
    results.
    """
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "json":
        report_path = os.path.join(out_dir, f"report_{ts}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        return report_path

    if fmt == "pdf":
        try:
            from fpdf import FPDF
        except Exception:
            # fallback to markdown if dependency missing
            fmt = "md"
        else:
            report_path = os.path.join(out_dir, f"report_{ts}.pdf")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, "ChainHunter Report", ln=True)
            for item in results:
                module = item.get("module", "unknown")
                target = item.get("target", "?")
                pdf.cell(0, 10, f"{module} - {target}", ln=True)
                summary = item.get("summary") or "No summary"
                pdf.multi_cell(0, 10, summary)
                tags = item.get("tags") or []
                if tags:
                    pdf.multi_cell(0, 10, "Tags: " + ", ".join(tags))
                pdf.ln()
            pdf.output(report_path)
            return report_path

    # default markdown
    report_path = os.path.join(out_dir, f"report_{ts}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        header = "# ChainHunter Report\n\n"
        f.write(header)
        tpl = None
        if template and os.path.isfile(template):
            with open(template, "r", encoding="utf-8") as tf:
                tpl = tf.read()
        for item in results:
            module = item.get("module", "unknown")
            target = item.get("target", "?")
            summary = item.get("summary") or "No summary"
            tags = ", ".join(item.get("tags") or [])
            if tpl:
                entry = tpl.format(module=module, target=target, summary=summary, tags=tags)
                f.write(entry + "\n")
            else:
                f.write(f"## {module} - {target}\n")
                f.write(summary + "\n\n")
                if tags:
                    f.write("Tags: " + tags + "\n\n")
    return report_path


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Generate ChainHunter report")
    parser.add_argument("--db_dir", default="db_data")
    parser.add_argument("--out_dir", default="reports")
    args = parser.parse_args()
    res = load_results(args.db_dir)
    path = build_report(res, args.out_dir)
    print(f"[+] Report written to {path}")


if __name__ == "__main__":
    main()
