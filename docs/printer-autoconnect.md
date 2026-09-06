# 라벨 프린터 자동연결 · 무인 인쇄 (Android)

## 0. 현재 상태

| 단계 | 상태 |
|---|---|
| ① 원두 정보 입력 → 라벨 PNG 자동 생성 | **완료** (`bean-label-maker.html`) |
| ② 저장 → 공유 → Deli 앱 인쇄 | 지금 바로 사용 가능 (탭 2~3회) |
| ③ 앱 실행 → 프린터 자동연결 → 자동 인쇄 | **프린터 모델·프로토콜 확인 필요** |

③은 프린터가 쓰는 BLE 명령 규격을 모르면 코드를 확정할 수 없습니다.
아래 A에서 그 규격을 확보하고, B의 골격에 인코더만 채우면 완성됩니다.

---

## A. 프로토콜 확보 — 30분이면 끝나는 절차

### A-1. 모델명 확인
프린터 바닥 라벨 또는 Deli 앱 → 기기 정보. (예: DL-886A / DL-888B / DL-720W …)
모델명만 알려주셔도 아래 B의 상수 대부분을 좁힐 수 있습니다.

### A-2. BLE 서비스·특성 UUID 확인 — nRF Connect (무료 앱)
1. Play스토어에서 **nRF Connect for Mobile** 설치
2. 프린터 전원 ON → SCAN → 프린터 이름 선택 → CONNECT
3. 나오는 **Service UUID**와, 그 아래 **Characteristic UUID + 속성(WRITE / WRITE NO RESPONSE / NOTIFY)** 화면을 캡처
   - 보통 쓰기 1개(WRITE NO RESPONSE)와 알림 1개(NOTIFY) 조합입니다.
   - 흔한 값: `0000ff00-…`, `0000ffe0-…`, `49535343-…`(Microchip 투명 UART), `6e400001-…`(Nordic UART)

### A-3. 실제 인쇄 명령 캡처 — HCI 스누프 로그
1. 안드로이드 **개발자 옵션 → 블루투스 HCI 스누프 로그 사용** ON (기기에 따라 재부팅 필요)
2. **Deli 앱으로 라벨 1장 인쇄** (반드시 성공적으로 1장만)
3. 개발자 옵션 → **버그 신고서 작성**(또는 `/sdcard/Android/data/.../btsnoop_hci.log`) 으로 로그 추출
4. 그 파일을 주시면 ATT Write 패킷에서 **헤더 · 래스터 인코딩 · 종료 명령**을 뽑아 인코더를 작성합니다.

> 참고: 40 × 12 mm 라벨을 203dpi로 찍으면 **320 × 96 dot**, 1bpp(흑백 1비트) 래스터 = 한 줄 12바이트 × 96줄 형태가 표준입니다. 만들어드린 `320 × 96 px` PNG가 그대로 들어갑니다.

### A-4. 정식 경로 (병행 권장)
Deli/Feioou는 파트너에게 **라벨 프린터 SDK(Android aar)** 를 제공합니다.
`support@delicloud.com` 또는 국내 총판에 모델명과 함께 SDK 요청 메일을 보내면
리버스 엔지니어링 없이 A-2/A-3을 건너뛸 수 있습니다.

---

## B. 자동연결 골격 (Kotlin, 검증 전 코드)

> Android SDK가 이 환경에 없어 **컴파일·실기 테스트는 하지 못했습니다.**
> 구조 참고용이며, A 완료 후 `buildPrintPayload()` 를 채우고 함께 다듬으면 됩니다.

```kotlin
// BleAutoPrinter.kt  —  "앱 켜면 알아서 붙는다"의 핵심은 autoConnect = true + MAC 기억
class BleAutoPrinter(private val ctx: Context) {

    companion object {
        // ↓ A-2에서 확인한 값으로 교체
        val SVC   = UUID.fromString("0000ff00-0000-1000-8000-00805f9b34fb")
        val WRITE = UUID.fromString("0000ff02-0000-1000-8000-00805f9b34fb")
        val NOTIFY= UUID.fromString("0000ff01-0000-1000-8000-00805f9b34fb")
        const val PREF = "printer_mac"
    }

    private var gatt: BluetoothGatt? = null
    private var wch: BluetoothGattCharacteristic? = null
    private val sp = ctx.getSharedPreferences("ble", Context.MODE_PRIVATE)

    /** 앱 시작 시 1회 호출. 저장된 MAC이 있으면 스캔 없이 바로 재연결 시도 */
    fun autoConnect(onReady: () -> Unit) {
        val mac = sp.getString(PREF, null) ?: return scanOnce(onReady)
        val dev = BluetoothAdapter.getDefaultAdapter().getRemoteDevice(mac)
        // autoConnect=true : 프린터가 꺼져 있어도 켜지는 순간 OS가 알아서 붙여줌 (핵심)
        gatt = dev.connectGatt(ctx, /* autoConnect = */ true, cb, BluetoothDevice.TRANSPORT_LE)
    }

    /** 최초 1회만: 이름으로 찾아 MAC을 저장해 두면 이후부터는 자동 */
    private fun scanOnce(onReady: () -> Unit) {
        val scanner = BluetoothAdapter.getDefaultAdapter().bluetoothLeScanner
        scanner.startScan(null, ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY).build(),
            object : ScanCallback() {
                override fun onScanResult(t: Int, r: ScanResult) {
                    val name = r.device.name ?: return
                    if (!name.contains("DL", true) && !name.contains("Deli", true)) return
                    scanner.stopScan(this)
                    sp.edit().putString(PREF, r.device.address).apply()
                    gatt = r.device.connectGatt(ctx, true, cb, BluetoothDevice.TRANSPORT_LE)
                }
            })
    }

    private val cb = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(g: BluetoothGatt, s: Int, newState: Int) {
            when (newState) {
                BluetoothProfile.STATE_CONNECTED    -> g.requestMtu(247)   // 큰 MTU = 인쇄 빠름
                BluetoothProfile.STATE_DISCONNECTED -> g.connect()         // 끊기면 무한 자동 재연결
            }
        }
        override fun onMtuChanged(g: BluetoothGatt, mtu: Int, st: Int) { g.discoverServices() }
        override fun onServicesDiscovered(g: BluetoothGatt, st: Int) {
            wch = g.getService(SVC)?.getCharacteristic(WRITE)
            g.getService(SVC)?.getCharacteristic(NOTIFY)?.let {
                g.setCharacteristicNotification(it, true)
                it.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"))?.apply {
                    value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE; g.writeDescriptor(this)
                }
            }
            /* 준비 완료 → 대기 중이던 인쇄 작업 실행 */
        }
    }

    /** 라벨 Bitmap(320 × 96) → 프린터 명령 바이트열
     *  ★ A-3 로그 분석 후 이 함수만 채우면 끝 */
    private fun buildPrintPayload(bmp: Bitmap): List<ByteArray> = TODO("HCI 로그 기반 인코딩")

    fun print(bmp: Bitmap) {
        val ch = wch ?: return
        for (chunk in buildPrintPayload(bmp)) {
            ch.writeType = BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE
            ch.value = chunk
            gatt?.writeCharacteristic(ch)
            Thread.sleep(12)   // 흐름 제어: NOTIFY ack 방식이면 그쪽으로 대체
        }
    }
}
```

### 필수 매니페스트/런타임 권한
```xml
<uses-permission android:name="android.permission.BLUETOOTH_SCAN"
    android:usesPermissionFlags="neverForLocation" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
```
+ **설정 → 앱 → 배터리 → 제한 없음** 으로 두어야 백그라운드 연결이 유지됩니다.

---

## C. 코드 없이 지금 바로 반자동으로 쓰는 법

1. `bean-label-maker.html` 로 라벨 생성 → **길게 눌러 이미지 저장**
2. 갤러리 → **공유 → Deli 앱**
3. Deli 앱은 마지막 프린터로 자동 재연결되므로 **인쇄 버튼 1회**

여기에 **MacroDroid** 매크로(트리거: 블루투스 기기 연결됨 = 프린터 → 액션: 앱 실행)를
얹으면 프린터 전원만 켜도 앱이 뜹니다.
