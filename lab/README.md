# lab — 측정 도구

커리큘럼 Phase 0 "실험실을 먼저 짓는다"의 산출물.
읽기만 하면 L2에서 멈춘다. 숫자를 볼 수 있어야 L4로 간다.

## token-report.py

세션 트랜스크립트(JSONL)에서 토큰 회계를 뽑는다.
클로드 코드는 턴마다 사용량을 `~/.claude/projects/<프로젝트>/<세션UUID>.jsonl`에 남긴다.

```bash
python3 lab/token-report.py            # 가장 최근 세션
python3 lab/token-report.py --turns    # 턴별 표까지
python3 lab/token-report.py --csv      # 실험 노트에 붙일 CSV 한 줄
python3 lab/token-report.py <파일.jsonl>
```

출력 예:

```
턴 수     61
입력(신규)                  122
캐시 기록(write)      1,086,754
캐시 재사용(read)     6,254,317   ← 캐시 적중률 85.2%
출력                    116,734   (사고 43,420)
도구 호출 32회
  Bash                      22
```

### 여기서 읽어야 할 것

- **입력(신규)가 캐시에 비해 극히 작다** — 긴 세션에서 실제 비용은 대부분 캐시 재사용이다.
  프롬프트 앞부분을 흔들면 이 구조가 무너진다. (Phase 2 · 프롬프트 캐싱)
- **캐시 적중률**이 실험 조건별로 어떻게 달라지는지가 Phase 2 실험의 핵심 지표다.
- **도구 호출 분포**는 같은 과제를 다르게 표현했을 때 행동이 어떻게 바뀌는지 보여준다.
  (Phase 1 · 표현이 바뀌면 행동이 바뀐다)

## EXPERIMENT-TEMPLATE.md

실험 노트 서식. `exp/EXP-0xx-제목.md`로 복사해 쓴다.
**반증 조건 칸을 비운 실험은 실험이 아니다.**
