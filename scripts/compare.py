#!/usr/bin/env python3
"""Show textual changes for synthetic prompt regression samples; no semantic verdict."""

import argparse
import difflib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CASES = ("straight", "factcheck", "inquiry")


def read(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def show_diff(left: str, right: str, left_name: str, right_name: str) -> None:
    lines = difflib.unified_diff(
        left.splitlines(keepends=True),
        right.splitlines(keepends=True),
        fromfile=left_name,
        tofile=right_name,
    )
    result = "".join(lines)
    print(result if result else "(텍스트 차이 없음)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True, help="변경 전 출력 폴더")
    parser.add_argument("--after", type=Path, required=True, help="변경 후 출력 폴더")
    args = parser.parse_args()

    missing = []
    for case in CASES:
        paths = (
            ROOT / "prompts" / f"{case}.md",
            ROOT / "fixtures" / f"{case}.json",
            ROOT / "expected" / f"{case}.md",
            args.before / f"{case}.md",
            args.after / f"{case}.md",
        )
        missing.extend(str(path) for path in paths if not path.is_file())
    if missing:
        parser.error("필요한 파일이 없습니다:\n" + "\n".join(missing))

    for case in CASES:
        fixture = json.loads(read(ROOT / "fixtures" / f"{case}.json"))
        if fixture.get("id") != case or fixture.get("synthetic") is not True:
            parser.error(f"{case}: 가상 사례 id/synthetic를 확인하세요")
        if "{{INPUT}}" not in read(ROOT / "prompts" / f"{case}.md"):
            parser.error(f"{case}: 프롬프트에 {{{{INPUT}}}} 자리표시자가 없습니다")
        before_path = args.before / f"{case}.md"
        after_path = args.after / f"{case}.md"
        reference_path = ROOT / "expected" / f"{case}.md"
        before, after, reference = map(read, (before_path, after_path, reference_path))
        print(f"\n=== {case}: 변경 전 → 변경 후 ===")
        show_diff(before, after, str(before_path), str(after_path))
        print(f"\n=== {case}: 참고 출력 → 변경 전 ===")
        show_diff(reference, before, str(reference_path), str(before_path))
        print(f"\n=== {case}: 참고 출력 → 변경 후 ===")
        show_diff(reference, after, str(reference_path), str(after_path))
    print("\n텍스트 비교 완료. 합격 판정은 TEST_CRITERIA.md에 따라 사람이 수행합니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
