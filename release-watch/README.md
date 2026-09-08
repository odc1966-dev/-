# Release watch

클로드 코드는 주 단위로 기능이 바뀐다. 커리큘럼(`claude-code-mastery.html`)이
낡지 않게 하려면 변경 로그를 계속 따라가야 한다 — Phase 7의 "릴리스 워치 자동화" 항목.

## 어떻게 도는가

Routine(Anthropic 관리 인프라에서 실행, 컴퓨터가 꺼져 있어도 동작)이
**매주 월요일 아침 08:53 KST**에 새 세션을 띄워서:

1. `release-watch/STATE.md`에서 마지막 검토 버전을 읽는다
2. 공식 변경 로그를 받아 그 이후 릴리스만 추린다
3. 항목마다 — 한국어 한 줄 요약 / 영향받는 Phase / 조치 필요 여부
4. `release-watch/<날짜>.md`로 다이제스트를 쓰고 `STATE.md`를 갱신한다
5. `claude/release-watch` 브랜치에 커밋·푸시한다 (PR은 만들지 않는다)

새 릴리스가 없으면 `STATE.md`의 날짜만 바꾸고 끝낸다.
**없는 변경을 지어내지 않는 것이 이 루틴의 제1 규칙이다.**

## 손으로 조정하기

- 일정 변경·중지: claude.ai 또는 데스크톱 앱의 Routines 목록, CLI에서는 `/schedule`
- 검토 기준점을 되돌리려면 `STATE.md`의 "마지막으로 검토한 버전"을 낮추면 된다
