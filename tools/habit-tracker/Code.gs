// 습관기록 웹앱 (구글 시트 > 확장 프로그램 > Apps Script 에 붙여 넣기)
// 시트 구성: "기록" 탭(날짜·항목·수치·단위·메모), "목표" 탭(항목·주기·목표횟수·올해 기존)

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('습관기록')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// 화면이 부르는 함수. 계산은 화면(Index.html)에서 한다.
function getData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tz = ss.getSpreadsheetTimeZone();
  const recSheet = ss.getSheetByName('기록');
  const goalSheet = ss.getSheetByName('목표');
  if (!recSheet || !goalSheet) {
    throw new Error('"기록" 탭과 "목표" 탭이 모두 있어야 합니다.');
  }

  const records = recSheet.getDataRange().getValues().slice(1)
    .map(r => ({ date: toDateText(r[0], tz), item: String(r[1]).trim() }))
    .filter(r => r.date && r.item);

  const goals = goalSheet.getDataRange().getValues().slice(1)
    .map(r => ({
      item: String(r[0]).trim(),
      period: String(r[1]).trim(),
      target: Number(r[2]) || 0,
      prior: Number(r[3]) || 0
    }))
    .filter(g => g.item && g.target > 0);

  return {
    records: records,
    goals: goals,
    today: Utilities.formatDate(new Date(), tz, 'yyyy-MM-dd')
  };
}

// 날짜 칸이 날짜 형식이든 "2026-10-06", "2026.10.6" 같은 글자든 yyyy-MM-dd 로 맞춘다.
function toDateText(v, tz) {
  if (v instanceof Date) return Utilities.formatDate(v, tz, 'yyyy-MM-dd');
  const m = String(v).match(/(\d{4})\D+(\d{1,2})\D+(\d{1,2})/);
  if (!m) return '';
  return m[1] + '-' + ('0' + m[2]).slice(-2) + '-' + ('0' + m[3]).slice(-2);
}
