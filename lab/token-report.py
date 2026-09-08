#!/usr/bin/env python3
"""세션 로그에서 토큰 회계를 뽑는다.

클로드 코드는 턴마다 사용량을 세션 트랜스크립트(JSONL)에 기록한다.
이 스크립트는 그것을 읽어 실험 결과표에 붙일 수 있는 숫자로 바꾼다.

사용법:
    python3 lab/token-report.py                 # 가장 최근 세션
    python3 lab/token-report.py <파일.jsonl>    # 특정 세션
    python3 lab/token-report.py --turns         # 턴별 표까지
    python3 lab/token-report.py --csv           # 실험 노트에 붙일 CSV 한 줄

로그 위치: ~/.claude/projects/<프로젝트>/<세션UUID>.jsonl
"""
import json, sys, os, glob

def find_latest():
    base = os.path.expanduser("~/.claude/projects")
    files = glob.glob(os.path.join(base, "**", "*.jsonl"), recursive=True)
    if not files:
        sys.exit(f"세션 로그를 찾지 못했습니다: {base}")
    return max(files, key=os.path.getmtime)

def load(path):
    turns, tools = [], {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") != "assistant":
                continue
            msg = rec.get("message") or {}
            for block in msg.get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    name = block.get("name", "?")
                    tools[name] = tools.get(name, 0) + 1
            u = msg.get("usage")
            if not u:
                continue
            turns.append({
                "ts": rec.get("timestamp", ""),
                "model": msg.get("model", "?"),
                "in": u.get("input_tokens", 0),
                "cw": u.get("cache_creation_input_tokens", 0),   # 캐시 기록(cache write)
                "cr": u.get("cache_read_input_tokens", 0),       # 캐시 재사용(cache read)
                "out": u.get("output_tokens", 0),
                "think": (u.get("output_tokens_details") or {}).get("thinking_tokens", 0),
            })
    return turns, tools

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    path = args[0] if args else find_latest()
    turns, tools = load(path)
    if not turns:
        sys.exit(f"사용량 기록이 있는 어시스턴트 턴이 없습니다: {path}")

    tot = {k: sum(t[k] for t in turns) for k in ("in", "cw", "cr", "out", "think")}
    billed_in = tot["in"] + tot["cw"] + tot["cr"]
    hit = tot["cr"] / billed_in * 100 if billed_in else 0.0
    tool_total = sum(tools.values())

    if "--csv" in flags:
        print("turns,input,cache_write,cache_read,output,thinking,cache_hit_pct,tool_calls")
        print(f'{len(turns)},{tot["in"]},{tot["cw"]},{tot["cr"]},{tot["out"]},'
              f'{tot["think"]},{hit:.1f},{tool_total}')
        return

    print(f"세션      {os.path.basename(path)}")
    print(f"모델      {turns[-1]['model']}")
    print(f"기간      {turns[0]['ts'][:19]} → {turns[-1]['ts'][:19]}")
    print(f"턴 수     {len(turns)}")
    print()
    print(f"입력(신규)         {tot['in']:>12,}")
    print(f"캐시 기록(write)   {tot['cw']:>12,}")
    print(f"캐시 재사용(read)  {tot['cr']:>12,}   ← 캐시 적중률 {hit:.1f}%")
    print(f"출력               {tot['out']:>12,}   (사고 {tot['think']:,})")
    print(f"입력 합계          {billed_in:>12,}")
    print()
    print(f"도구 호출 {tool_total}회")
    for name, n in sorted(tools.items(), key=lambda kv: -kv[1]):
        print(f"  {name:<24}{n:>4}")

    if "--turns" in flags:
        print()
        print(f'{"#":>3} {"입력":>8} {"캐시W":>9} {"캐시R":>9} {"출력":>7}  모델')
        for i, t in enumerate(turns, 1):
            print(f'{i:>3} {t["in"]:>8,} {t["cw"]:>9,} {t["cr"]:>9,} {t["out"]:>7,}  {t["model"]}')

if __name__ == "__main__":
    main()
