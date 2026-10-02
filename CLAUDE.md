# 아델라인 빌리지 (Adeline Village) — 프로젝트 지침

포근한 도트풍 단일 HTML 캔버스 게임. 마법학교가 있는 작은 마을에서 신입생 **아멜리아**가 보내는 가을 학기 이야기.
현재 버전: **v0.43 데모** (아래 "현재 상태" 참고).

## 사용자와 일하는 규칙 (매우 중요)
- 사용자(아멜리아)는 **한국어**로 대화한다. 답변도 **한국어, 짧고 쉽게**: "무엇이 바뀌었는지 + 사용자가 해야 할 일"만.
- 그림(스프라이트·배경·초상화)은 원칙적으로 사용자가 Google Flow 등으로 만들어 준다. 그림이 없을 땐 **임시 이미지**를 쓰고, 나중에 교체한다.
- 사용자가 특히 중요하게 보는 것: **그림이 겹치거나 잘려 보이는 것, 캐릭터 디자인이 이상하게 표시되는 것.** 화면을 고칠 때마다 반드시 스크린샷으로 직접 확인한다.
- 수정 후에는 **직접 플레이(봇)로 돌려 확인**하고 나서 보고한다. 추측으로 "됐다"고 말하지 않는다.
- **미리보기 제공:** 작업이 끝날 때마다 사용자가 직접 조작해 볼 수 있게 해 준다. 빌드 후 `game.html` 의 전체 경로를 알려 주고(더블클릭하면 브라우저에서 바로 실행), 가능하면 `python3 -m http.server 8000` 을 백그라운드로 켜 두고 `http://localhost:8000/game.html` 링크도 같이 준다. 무엇을 눌러 보면 바뀐 걸 확인할 수 있는지 한 줄로 안내한다.
- **중요한 일은 먼저 묻는다:** 이야기 줄거리·결말, 캐릭터 설정이나 말투 변경, 큰 구조 변경, 되돌리기 어려운 변경(파일 삭제·덮어쓰기), 그림 교체 방향처럼 사용자가 정해야 할 일은 임의로 진행하지 말고 선택지(추천안 표시)를 2~3개 제시해 묻는다. 사소한 버그 수정이나 문구 다듬기는 알아서 하고 결과만 알려 준다.
- **문서 동기화:** 기능을 바꾸거나 이야기·퀘스트·버전을 추가하면 같은 작업 안에서 이 `CLAUDE.md`(현재 상태, 다음 할 일, 임시 이미지 목록, 버전)와 `script.html` 의 VERSION/CHANGES 도 함께 갱신한다. 갱신했다고 한 줄로 알려 준다.
- 이모지·과한 서식 금지. 문제를 발견하면 숨기지 말고 솔직하게 말한다.

## 폴더 구조
```
src/head.html      HTML/CSS (UI, 부팅 화면 포함)
src/script.html    게임 JS 전부 (약 2400줄)
assets/            그림 파일 (스프라이트 240x330 RGBA, 배경 1116x2000, 초상화 등). *_orig/_src/_old 는 백업
source_images/     원본 업로드 이미지 (tavern/school/inn1 배경 원본)
fonts/             Galmuri11.ttf (빌드 시 글자만 잘라 woff2로 내장)
build.py           src + assets 를 base64로 합쳐 game.html 생성
tools/             테스트 봇(playtest_*.py), 과거 1회성 가공 스크립트(patch_attic.py, unify_npcs.py)
game.html          빌드 결과 (배포 파일)
game_dbg.html      디버그 빌드 (window.__g 훅 포함, 테스트 전용, git 제외)
index.html         홈 화면 추가용 빌드 (game.html + viewport/manifest/서비스워커 등록). build.py 가 함께 만듦
manifest.json, sw.js, pwa/   홈 화면 앱 이름·아이콘(임시: 아멜리아 얼굴)·오프라인 저장. sw.js 캐시 이름은 빌드마다 자동으로 바뀜
```

## 빌드·테스트
```
pip install pillow numpy opencv-python fonttools brotli playwright && playwright install chromium
# 클라우드 세션: 브라우저가 미리 깔려 있으니 playwright install 대신
#   pip install pillow numpy opencv-python-headless fonttools brotli playwright==1.56.0
#   (빌드하면 assets/*_bg.png 가 압축만 다르게 다시 저장될 수 있음 → 그림은 같으니 git checkout 으로 되돌림)
python3 build.py          # -> game.html (배포용)
python3 build.py dbg      # -> game_dbg.html (테스트용, __g 훅)
python3 tools/playtest_boot.py     # 오류 없이 부팅되는지
python3 tools/playtest_objects.py inn1,attic,tavern,school,shop,plaza   # 모든 사물 눌러보기
python3 tools/playtest_story.py 8  # 1일차~5일차 수업 흐름 자동 진행
python3 tools/playtest_late.py [스크린샷폴더]  # 5~10일차: 마법서 5장·엔딩·부탁 3개·이야기 2편
```
- 테스트 봇은 프로젝트 루트에서 실행 (현재 폴더의 game.html / game_dbg.html 사용).
- 봇 주의: 연출(cut) 중에는 화면을 누르지 말 것. 대화창은 `mouse.click(280,880)`로 넘기고 선택지는 `#dlg .ch > *` 요소를 클릭. 미니게임은 `__g.mini()`로 얻은 M 에 `n=need, ok=true, fin=0.01` 로 성공 처리.
- `pkill -f 스크립트이름` 은 자기 셸까지 죽일 수 있으니 쓰지 말 것.
- 배포: GitHub 공개 저장소 https://github.com/lewfot-crypto/adlvillage (main 브랜치, GitHub Pages → https://lewfot-crypto.github.io/adlvillage/). 사용자는 폰에서 이 주소를 "홈 화면에 추가"해서 플레이한다. 빌드 후 index.html/sw.js 까지 커밋·푸시해야 폰에 반영됨(앱을 완전히 껐다 켜기). 예전 Artifact 링크(https://claude.ai/artifact/KmAe9zmoZ4Gb7mZN3Mf2sj)는 game.html 로 갱신 가능. 클라우드 세션에서 미리보기는 game.html 을 Artifact 로 게시해서 제공(채팅 창에서 바로 플레이).

## 게임 구조 요약
- 월드 1116x2000. 장면 SC.{attic, inn1, tavern, school, shop, plaza}. 상태 boot/title/play/dialog/trans/fade/menu/mini/cut.
- 플레이어 히트박스 px,py = 좌상단, HW=80, HH=36. 컷신 walk 좌표는 발 중심.
- 컷신 엔진 CUTS/playCut: 단계 {walk,x,y,speed,diag,dface,nou},{scene,spawn},{say}… (diag=직선 이동+얼굴 고정, nou=밀어내기 방지 생략).
- 길찾기 planPath(격자 20), 사물 `at` 서는 자리, 출구 C.exit(+door band/innerPath) / 광장 C.exits. fg 조각(rect/poly)을 플레이어 위에 덮어 가림.
- NPC: NPCDEF 의 spots[phase]. `behind`=가구(fg) 번호 뒤에 서서 아랫부분이 가려짐, `dy`=위치 보정. **npcHere() 의 키는 'alesendo','owl','orga','bran','master','wella','sina'** (LORE 의 'ales' 와 다름 — 과거에 이 혼동으로 마법서 4장이 막힌 버그가 있었음).
- 달력: S.cal(연호 엘리시아 52년 9월 1일 시작). 날짜는 **잠잘 때만** 증가. 수확 등불제 10/15~19. weekOne()=2~7일차(퀘스트·목표 없음, 마을 이야기만). 8일차부터 부탁 시작.
- 시간대 S.phase 0아침/1낮/2저녁/3밤. 설정의 timeMode 가 story/real.
- 마을 이야기(LORE/tellLore): 하루 한 가지씩, 일지 "이야기" 탭.
- 마법: SPELLS(flame, breeze, ripple, shadow, whisper, glow), 미니게임, 마법서 5장(BOOK).
- 퀘스트: QUESTS (main 순서 목록 + 부탁 퀘스트 herb(브란), leaves(웰라), lights(오르가, 이야기 1편), bell(시나, 이야기 2편)).
- 디버그 훅(game_dbg.html): `__g.set(scene,x,y,face)`, `go(scene,spawn)`, `ia(id)`, `tapObj`, `cut(id)`, `S()`, `st()`, `wp()`, `pos()`, `ap()`(NPC 재배치), `mini()`, `devTo(m,d)`, `devSkip(n)` 등.

## 캐릭터·세계관 (설정집 요약)
- 마을·게임 이름: 아델라인 빌리지. 연호: "엘리시아 52년" ("제국력" 표기 쓰지 않음).
- 오르가: 여관 주인(할머니, 다정). 브란: 선술집 주인(말수 적음, …로 시작). 웰라: 마법 견습생(해요체, "하하!"). 시나: 검은 고양이("…" + "~다냥"), 마법냥이 모드는 보라색. 알레센도: 마법 상점 서기관(정중, 이름으로 부름). 올빼미: 밤의 상점지기("호오…", 하게체). 마법스승: 엄격하지만 정 많음(담백한 해라체, 처음엔 아멜리아를 모름).
- 분위기: 위험·공포 없는 포근한 일상 판타지.

## 현재 상태 (v0.43)
- 완료: 1일차~8일차 흐름(카운터→열쇠→다락방→짐→잠→웰라→학교 수업→촛불→바람결→빛모으기→마법서 발견), 마을 이야기 27편, 등불제, 마법서 5장+엔딩, 이야기 1편 「사라진 가을 불빛」(오르가 부탁→브란·마법스승 단서→상점 첫 등불→푸른 꽃 빛 모으기→저녁 광장 시나와 점등).
- 5~10일차 점검 완료(v0.41, `tools/playtest_late.py`): 마법서 1~5장·엔딩, 약초·단풍잎·사라진 가을 불빛 모두 오류 없이 진행. 분수 서는 자리 수정, 아침 문구 수정. 상점 404 네온 간판 → 나무 간판(`tools/patch_shop_sign.py`, 원본 `assets/shop_bg_orig.jpg`). 카페 이름 '404 DRINK BAR' 설정은 유지.
- v0.42: 알레센도 스프라이트를 사용자의 예전 게임 도트(`source_images/alesendo_oldgame.jpg`)로 교체. `tools/make_alesendo.py`가 칸(약 21.7px) 단위로 다시 뽑아 6배로 키움. 옷 색은 바꾸지 말 것(사용자 요청, 파란 로브). 이전 그림은 `assets/npc_alesendo_old.png`. sc 1.16, 상점 dy 40(카운터에 허리 아래 가려짐). 초상화는 그대로(짙은 회색 옷), 웃는 초상화는 넣지 않기로 함.
- v0.43: 이야기 2편 「시나의 잃어버린 방울」(퀘스트 id `bell`). 사라진 가을 불빛을 끝낸 **다음 날**부터(S.lightsDay) 광장 시나에게 말 걸면 시작 → 오르가·브란 단서(S.bl) → 광장 분수(단풍나무) 앞에서 바람결 미니게임 → 웰라 빗자루에 엉킨 은방울(silverbell) → 시나에게 돌려주기(40G). `tools/playtest_late.py` 에 포함.
- 설정(왼쪽 위 메뉴) → 테스트 탭에 '미니게임 바로 해 보기'(devMini, 마법 6종, 진행·숙련도 영향 없음). 릴리스 전 테스트 탭 숨길 때 같이 숨김.
- 완료된 최근 수정: 계단 오를 땐 왼쪽·내려갈 땐 오른쪽을 봄, 알레센도 초상화 배경 제거, 상점 NPC 카운터 겹침 수정, 첫 실행(터치 대기) 화면 꾸밈.
- 임시 이미지(그림 생기면 교체): 시작 화면 배경 title_bg.jpg / 로고 title_logo.png, 다락방 배경(attic_bg), 마법스승 웃는 초상화, 올빼미.

## 다음 할 일 (우선순위)
1. 이야기 1편·마법서 미니게임 손맛 확인(봇은 성공 처리만 함, 사람이 직접 해 봐야 함). 약초 부탁의 상점 구매 화면은 봇이 건너뜀.
2. 이야기 3편 이후 작성 (후보: 올빼미가 들려주는 '첫 등불의 약속'·마을 이름 유래, 브란의 가을 수프 대회). 2편 바람결 미니게임 손맛도 사람이 확인.
3. 오디오·아이폰 실기기 확인(미검증, 홈 화면 앱으로), 앱 아이콘 그림 교체(지금은 임시), 릴리스 전 일지의 "테스트" 탭 숨기기.
4. 그림 교체(위 임시 이미지 목록). 새 그림을 넣으면 반드시 겹침/크기/외곽선을 기존 캐릭터와 맞춰 스크린샷으로 확인(NPC 높이 기준: 아멜리아=100 대비 orga87, bran106, master104, alesendo106(새 도트 기준 sc1.16), wella91).

## 알려진 한계
- 마스터/오르가/브란 스프라이트의 픽셀 밀도가 서로 달라 완전히 통일하려면 다시 그려야 함.
- 계단 주변 아주 희미한 얼룩이 남아 있을 수 있음(사용자가 거슬려하면 추가 정리).
