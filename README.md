# 우격자의 관 포터블 한글 패치 (PSP / ULJS00216)

『雨格子の館 Portable ～一柳和、最初の受難～』 PSP판의 비공식 한국어 번역 패치입니다.

배포물은 **xdelta 바이너리 패치 한 개**입니다. 게임 데이터는 일절 포함하지 않으며, 적용하려면 본인이 소유한 정품 UMD에서 직접 만든 ISO가 필요합니다.

---

## 1. 준비물

| 항목 | 내용 |
|---|---|
| 원본 ISO | `Amagoushi no Yakata Portable - Ichiyanagi Nagomu, Saisho no Junan (Japan).iso` — 아래 해시와 **정확히 일치**해야 합니다 |
| 패치 파일 | `Amagoushi_KR_v1.0.xdelta` ([릴리스](../../releases)에서 내려받기) |
| 적용 도구 | [xdelta3](https://github.com/jmacd/xdelta-gpl/releases) 또는 xdeltaUI |

### 원본 ISO 해시

```
크기 : 900,038,656 바이트
MD5  : fb0d9108f16d63a603f08a11b5a2a0d7
```

### 적용 후 결과물 해시

```
크기 : 904,925,184 바이트
MD5  : 97782dcc726bf2719d32688d36f954c4
```

## 2. 패치 방법

### 방법 A — 명령줄

```bash
xdelta3 -d -f -s "Amagoushi no Yakata Portable - Ichiyanagi Nagomu, Saisho no Junan (Japan).iso" "Amagoushi_KR_v1.0.xdelta" "Amagoushi no Yakata Portable (Korean).iso"
```

### 방법 B — xdeltaUI

1. `xdeltaUI.exe` 실행 → **Apply Patch**
2. Patch: `Amagoushi_KR_v1.0.xdelta` / Source File: 원본 ISO / Output File: 만들 파일 이름
3. **Apply**

PPSSPP에서는 ISO를 그대로 열면 됩니다. 실기(CFW)는 `ms0:/ISO/`에 넣습니다.

---

## 3. 번역 범위

| 대상 | 분량 |
|---|---|
| 본편 스크립트(대사·선택지·예/아니오) | 162개 파일, 46,190블록 (고유 32,704블록, 약 80만 자) |
| 화자 이름·명령·지도 이동 장소 (`STS_DEF.TOB`) | 92개 |
| 선택 메뉴(인물 선택 등) | 134개 |
| 실행 파일(EBOOT) 문자열 | 2,500여 개 — 원본과 같은 태그(d9160bf0)로 재서명 |
| 키워드 / 나고무 메모 | 141개 / 86건 |
| 이미지 | 오프닝 자막, 탈출 장면 무전 대사 270장, 튜토리얼(설명·캡처 화면), 사이드 메뉴, 예/아니오, 옵션, 캘린더, 종이 페이지 제목, 살해 순서 메모, 힌트 시, 알리바이표 73장, 1·2층·지하 지도와 방 이름표, 스태프롤, 면책 문구, 타이틀 부제 |

한글 글꼴은 **서울한강체 B**(대사)·**EB**(이미지)를 사용했습니다. 타이틀 로고 「雨格子の館」은 원본을 보존하고 옆에 「우격자의 관」을 표기했습니다.

## 4. 알려진 제한

- 실기(PSP 본체)에서는 테스트하지 않았습니다. PPSSPP 기준으로 제작했습니다.
- 서고 튜토리얼 캡처의 책등 제목 일부는 원본 글씨가 흐려 추정 번역입니다.
- 메모 화면의 가나 색인 탭(あかさたな…)은 정렬 순서 때문에 그대로 두었습니다.

## 5. 직접 빌드하기

- Python 3.11+, `pip install numpy pillow opencv-python`
- 원본 ISO, 서울한강체 TTF(`SeoulHangangB.ttf`, `SeoulHangangEB.ttf`)를 작업 폴더에
- `tools/`의 추출 스크립트로 `work/`를 만든 뒤 `python tools/build.py 출력.iso`
- EBOOT 재서명에 `_seboot.exe`(sign_eboot) 경로를 `tools/build_eboot.py`에서 지정

### 포맷 메모

- `DATA.DAT`: PSPFS_V1 아카이브(청크 gzip). `DATA2.DAT`는 난수 더미.
- `STS.DAT`: 색인 +0x7F 난독화, 안의 `.tob` 스크립트 문자열은 XOR 0xDA, 참조는 u16×4.
- 폰트 `FONT.MPB`(16×16 4bpp, 스위즐, IMY LZ, 64행 청크) + `FONT.BIN`(코드·폭 표).
- 1바이트 코드 0xA6~0xDF(원래 히라가나)를 가장 자주 쓰는 한글 58자에 배정. 이름칸·EBOOT 문자열은 2바이트 코드만 사용.

## 6. 저작권

번역문과 도구는 자유롭게 쓰셔도 됩니다. 게임의 저작권은 FOG / 日本一ソフトウェア에 있습니다.
