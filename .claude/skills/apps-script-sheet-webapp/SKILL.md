---
name: apps-script-sheet-webapp
description: 구글 시트 데이터를 휴대폰 화면으로 보여주는 개인용 Apps Script 웹앱을 만들고 배포할 때 사용. 서버·호스팅 없이 시트를 읽고 쓰는 대시보드가 필요할 때.
---

# 구글 시트 + Apps Script 웹앱

## 적용 조건
- 데이터가 구글 시트에 있고(다른 비서·폼이 채우는 경우 포함), 본인만 쓰는 화면이 필요할 때
- 정식 PWA 설치가 꼭 필요하면 쓰지 않는다 (홈 화면 바로가기만 가능)

## 입력
- 시트 이름, 탭 이름과 열 구성, 보여줄 통계

## 단계
1. `Code.gs`: `doGet()`은 `HtmlService.createHtmlOutputFromFile('Index')` + viewport 메타 태그. 데이터 함수는 시트를 읽어 단순 객체만 반환한다(Date 객체는 `yyyy-MM-dd` 글자로 바꿔서).
2. 시간대는 `ss.getSpreadsheetTimeZone() || Session.getScriptTimeZone() || 'Asia/Seoul'`. 다른 앱이 만든 시트는 시간대가 비어 있어 `잘못된 인수(timeZone)` 오류가 난다.
3. `Index.html`: 계산은 브라우저 JS에서 하고 `google.script.run.withSuccessHandler().withFailureHandler()`로 데이터를 받는다. 오류 메시지를 화면에 그대로 띄워 사용자가 캡처해 보낼 수 있게 한다.
4. 탭 이름 누락, 목표 형식 오류, 알 수 없는 항목 이름은 화면에 경고로 보여준다.

## 검증
- 로컬: Playwright로 `Index.html`을 열고 `window.google.script.run`을 가짜 객체로 바꿔 여러 데이터로 렌더링·스크린샷(밝은/어두운 모드).
- 실제: 사용자가 배포한 URL 화면 캡처로 숫자 확인.

## 사용자 안내 (배포)
1. 시트 → 확장 프로그램 → Apps Script → `Code.gs` 교체, `+ → HTML → Index` 생성 후 붙여 넣기, 저장
2. 배포 → 새 배포 → 웹 앱, 실행: 나, 액세스: 나만
3. "Google hasn't verified this app" → Advanced → Go to (프로젝트) (unsafe): 본인 스크립트라 정상
4. URL을 휴대폰 Chrome에서 열고 ⋮ → 홈 화면에 추가
5. 코드 수정 후에는 배포 관리 → 연필 → 새 버전 → 배포 (같은 URL 유지)

## 결과 형식
- `tools/<앱이름>/Code.gs`, `Index.html`, `SETUP.md`
