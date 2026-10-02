# 아델라인 빌리지 (Adeline Village) — 프로젝트 지침

포근한 도트풍 단일 HTML 캔버스 게임. 마법학교가 있는 작은 마을에서 신입생 **아멜리아**가 보내는 가을 학기 이야기.
현재 버전: **v0.51 데모** (아래 "현재 상태" 참고).

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
assets/ui/         UI 도트 틀(tools/make_ui.py 가 생성: 나무 틀·양피지 무늬·버튼 판). build.py 가 CSS 변수 --ui-* 로 내장
assets/            그림 파일 (스프라이트 240x330 RGBA, 배경 1116x2000, 초상화 등). *_orig/_src/_old 는 백업
source_images/     원본 업로드 이미지 (tavern/school/inn1 배경 원본)
fonts/             Galmuri11.ttf (빌드 시 글자만 잘라 woff2로 내장)
build.py           src + assets 를 base64(WebP)로 합쳐 game.html 생성
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
python3 tools/playtest_late.py [스크린샷폴더]  # 5~13일차: 마법서 5장·엔딩·부탁 3개·이야기 2~6편·작은 부탁 3개(13일차까지, 약 12분)
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
- 퀘스트: QUESTS (main 순서 목록 + 부탁 퀘스트 herb(브란), leaves(웰라), lights(오르가, 이야기 1편), bell(시나, 이야기 2편), soup(브란, 이야기 3편), cloud(웰라, 이야기 4편), promise(올빼미, 이야기 5편), firstcandle(마법스승, 이야기 6편), 작은 부탁 milk(오르가)·ink(알레센도)·thanks(시나)).
- 디버그 훅(game_dbg.html): `__g.set(scene,x,y,face)`, `go(scene,spawn)`, `ia(id)`, `tapObj`, `cut(id)`, `S()`, `st()`, `wp()`, `pos()`, `ap()`(NPC 재배치), `mini()`, `devTo(m,d)`, `devSkip(n)` 등.

## 캐릭터·세계관 (설정집 요약)
- 마을·게임 이름: 아델라인 빌리지. 연호: "엘리시아 52년" ("제국력" 표기 쓰지 않음).
- 오르가: 여관 주인(할머니, 다정). 브란: 선술집 주인(말수 적음, …로 시작). 웰라: 마법 견습생(해요체, "하하!"). 시나: 검은 고양이("…" + "~다냥"), 마법냥이 모드는 보라색. 알레센도: 마법 상점 서기관(정중, 이름으로 부름). 올빼미: 밤의 상점지기("호오…", 하게체). 마법스승: 엄격하지만 정 많음(담백한 해라체, 처음엔 아멜리아를 모름).
- 분위기: 위험·공포 없는 포근한 일상 판타지.

## 현재 상태 (v0.51)
- 완료: 1일차~8일차 흐름(카운터→열쇠→다락방→짐→잠→웰라→학교 수업→촛불→바람결→빛모으기→마법서 발견), 마을 이야기 46편, 등불제, 마법서 5장+엔딩, 이야기 1편 「사라진 가을 불빛」(오르가 부탁→브란·마법스승 단서→상점 첫 등불→푸른 꽃 빛 모으기→저녁 광장 시나와 점등).
- 5~10일차 점검 완료(v0.41, `tools/playtest_late.py`): 마법서 1~5장·엔딩, 약초·단풍잎·사라진 가을 불빛 모두 오류 없이 진행. 분수 서는 자리 수정, 아침 문구 수정. 상점 404 네온 간판 → 나무 간판(`tools/patch_shop_sign.py`, 원본 `assets/shop_bg_orig.jpg`). 카페 이름 '404 DRINK BAR' 설정은 유지.
- v0.42: 알레센도 스프라이트를 사용자의 예전 게임 도트(`source_images/alesendo_oldgame.jpg`)로 교체. `tools/make_alesendo.py`가 칸(약 21.7px) 단위로 다시 뽑아 6배로 키움. 옷 색은 바꾸지 말 것(사용자 요청, 파란 로브). 이전 그림은 `assets/npc_alesendo_old.png`. sc 1.16, 상점 dy 40(카운터에 허리 아래 가려짐). 초상화는 그대로(짙은 회색 옷), 웃는 초상화는 넣지 않기로 함.
- v0.43: 이야기 2편 「시나의 잃어버린 방울」(퀘스트 id `bell`). 사라진 가을 불빛을 끝낸 **다음 날**부터(S.lightsDay) 광장 시나에게 말 걸면 시작 → 오르가·브란 단서(S.bl) → 광장 분수(단풍나무) 앞에서 바람결 미니게임 → 웰라 빗자루에 엉킨 은방울(silverbell) → 시나에게 돌려주기(40G). `tools/playtest_late.py` 에 포함.
- 설정(왼쪽 위 메뉴) → 테스트 탭에 '미니게임 바로 해 보기'(devMini, 마법 6종, 진행·숙련도 영향 없음). 타이틀에서 누르면 바로 시작 후 타이틀로 복귀, 게임 중에는 devMiniQ 로 걸어 다닐 수 있을 때 시작. 끝나거나 그만두면 devMiniBack 으로 테스트 탭 복귀. 연습(practice) 미니게임은 '그만두기' 버튼 #mquit / Esc 로 중단 가능(보상 없음, M.onQuit), 수업(lesson) 미니게임은 중단 불가. 릴리스 전 테스트 탭 숨길 때 같이 숨김.
- v0.44: 미니게임·UI 도트 개편(사용자 선택: 나무+양피지 마법책 스타일). 미니게임은 drawMini 가 1/6 크기 캔버스(MGW 186x334)에 그린 뒤 픽셀 그대로 6배 확대 + 4단계 디더링(mgPosterize), 글자는 큰 화면에 따로 씀(fx.fillText 를 모아 둠). 효과는 책 페이지 안으로 잘림. 펼친 책 판은 mgDrawBook. 미니게임 소품은 PXA 도구(도트 칸 좌표, 가운데 AX93·AY170)로 직접 찍음: runeTablet(룬 석판, RUNE_GLYPH), runeCircle(마법진), 촛대·수정구·종·물방울·해달 메달은 각 MINI.*.draw 안. UI 는 head.html 의 .bx/.pbtn/.nm/#pt 가 border-image(9조각)+image-rendering:pixelated, 도트 크기 --px 는 resize() 에서 화면 폭/186(최소 2px). 대화창·설정·안내 창 안은 양피지라 --ink 등 글자색 변수를 짙은 색으로 덮어씀.
- v0.45: 이야기 3편 「브란의 가을 수프 대회」(퀘스트 id `soup`). 2편을 끝낸 **다음 날**부터(S.bellDay) 선술집 브란 메뉴 첫 줄로 시작 → 재료 3개(상점 herb, 웰라 redleaf, 마법스승 moonshroom) → 브란에게 건네고 불꽃 미니게임(cook) → 저녁(phase 2)에 브란에게 말 걸면 대회(judge), 보상 수프 2·50G, S.autumnSoup. 선택지 버튼은 나타난 뒤 0.3초 안의 클릭 무시(chShownT) — 봇도 선택지 클릭 전 0.35초 기다림. 시작 화면 로고는 코드로 그린 도트 로고(drawPixLogo/pixText: Galmuri 22px 글자를 칸 단위로 금빛 띠·외곽선 칠해 8배 확대, '빌리지' 빨간 리본, '마법학교 이야기'), 타이틀 버튼은 assets/ui/btn_title(_on).png. build.py 가 그림을 WebP 로 내장(배경 손실 92, 투명 그림 무손실) → game.html 약 3.9MB.
- v0.46: 이야기 4편 「웰라의 구름 소동」(퀘스트 id `cloud`, 3편 다음 날부터 S.soupDay). 광장 웰라 → 상점 알레센도/올빼미(ask) → 광장 분수 바람결(gather) → 분수 물결(rain) → 웰라·시나 마무리(wella), 보상 rainbowdrop·45G. 광장 그림은 plazaWeather(): pixCloud·pixRain·pixRainbow(단풍나무 fg poly 로 잘라 나무 뒤에 걸림). 날짜별 소소한 일 DAYEV('월-일' 키, wake 문구 + l{npc:한마디} + rain), tellLore 맨 앞에서 그날 한 번(S.evHeard). 마을 이야기 46편.
- v0.47: 말투 3단계 bond()(0=1~3일차 처음 본 사이, 1=4~7일차 얼굴 익힘, 2=8일차~ 다정). LORE 항목의 `b`=꺼낼 수 있는 최소 단계(못 미치면 건너뛰고 다음 이야기), `c0`/`c1`=그 단계 대사. 오르가 인사·브란 인사·알레센도 잡담(ALES_B)도 단계별. 첫 화면 바 = barTex() 가 만든 도트 그라데이션(6색 가로 단계 + 2x2 바둑판 디더링, 윗줄 밝게·아랫줄 어둡게), 폭은 6칸 단위로 차오름. 'AUTUMN TERM' 글자 삭제. 제목은 사용자 선택으로 예전 그림 로고 title_logo.png 로 복귀(build.py: title_logo_final.png > title_logo.png > 코드 도트 로고). 설정 '정보' 탭 업데이트 기록 = 한 장에 한 버전(renderLog, ◀ 이전 버전 / 다음 버전 ▶, 밀어 넘기기). 알레센도 초상화 목 정리(원본 `portrait_alesendo_cut_old.png`). 초상화 틀 #pt z-index 로 아래 테두리 보이게. 광장 상점 앞 물약·상자 solids+fg. 광장 가로등 lampFlame(도트 불꽃, 아멜리아가 앞을 가리면 안 그림).
- v0.48: 이야기 5편 「첫 등불의 약속」(퀘스트 id `promise`, 4편 다음 날부터 S.cloudDay). 그날 아침 꿈 귀띔(S.prHint) → 낮 알레센도가 전함(visit) 또는 밤 올빼미에게 바로 → 꾸러미 '아델라인'(seat) → 브란 메뉴 '구석 자리'(cards) → 오르가 가장 오래된 엽서 "— A."(record) → 마법스승 입학 명부, 빛 모으기 미니게임으로 바랜 글씨(back) → 밤 올빼미가 꼬리표 뒷면 "내가 돌아오지 못하면, 이 등불을 다시 켤 학생에게" + oldlamp(light) → 선술집 tableBR(구석 자리)에서 불꽃 미니게임, 브란의 나무 숟가락 spoon·50G, S.promiseLamp(탁자 위 도트 등불 tavernLamp, pre/post 로 탁자 뒤 가림 처리). 설정: 아델라인 = 마법학교 첫 입학생, 광장 첫 등불을 켬, 마을 이름의 주인, 졸업 뒤 먼 곳으로 떠난 선배(사용자 선택, 아멜리아와 혈연 없음).
- v0.49: 이야기 6편 「스승의 첫 초」(퀘스트 id `firstcandle`, 5편 다음 날부터 S.promiseDay): 광장 웰라(fcStart) → 마법스승(ask) → 상점 알레센도가 실패의 공책 failnote(note) → **저녁(phase 2)** 학교 서가 그림자 미니게임으로 첫 초 fcandle(shadow) → 마법스승 앞 불꽃 미니게임(light), 스승이 처음 웃음, S.fcDone(다음에 웰라가 콧노래 이야기 한 번). 웃는 초상화는 아직 없어서 평소 초상화 사용. 작은 부탁(smallReady: 9일차~, 1편 끝, 진행 중이거나 막 시작할 이야기 없을 때): milk(오르가 → 여관 벽난로 불꽃, warmmilk·15G), ink(알레센도 → 광장 단풍잎 아무거나 → 알레센도, 별빛 차·20G), thanks(속삭임 배운 뒤 낮 시나 → 웰라에게 속삭임 미니게임 → 시나, starpebble). 여관 엽서 벽 CARDS/drawPostcards(inn1 pre, 첫 장=아델라인 엽서, promise record 단계에선 비어 있음, 사물 inn1.cards). 테스트 탭 devStory(n): 앞 이야기 끝낸 상태 + 마법 6종 + 시작 장소로. 다듬기: npc_magiccat 스티커 테두리 제거(원본 npc_magiccat_old.png), 일지 small/note 줄간격 1.75·글자간격·keep-all, drawLights 에 l/c/f 심지 빛(g2) 일렁임, 상점 수정구슬 'g' 추가·옛 네온 'n' 삭제, 선술집 칸막이 들보 fg(base 1440), pixCloud 4px 외곽선·명암, 무지개 plazaRainbow(plaza pre, 분수 위 r140), 단풍잎 반짝이 4px 별. 인물(objs _n)에게 말 걸면 planPath 가 NPC 왼쪽/오른쪽 중 가까운 빈자리로 감(겹침 방지). 광장 웰라 spots 0/2 x640·1 x160, 시나 0/2 x790·1 x400(분수 서는 자리 455,1205 를 막지 않게).
- v0.50: 글자 크기 설정 textSize: UIZOOM small 1(=예전 보통 크기)·normal 1.12(기본)·large 1.26 (resize() 가 stage font-size 에 곱함, 기준값은 --fs0). #dlg/#set/#guide 에 -webkit-text-stroke .45px 로 살짝 굵게(Galmuri11 은 굵은 글꼴이 없어 가짜 굵게). 초상화 #pt 폭은 --fs0*8.6 이라 글자 설정과 무관. 양피지 tex_parch.png 는 tools/make_ui.py 가 만드는 64x64(타일 노이즈 3단계 + 바둑판 디더링, 섬유 선, 잔점), head.html 에서 background-size px*64 + 안쪽 계단식 inset box-shadow. 알림(#toast)은 줄바꿈 허용, 설정 .row 는 flex-wrap.
- v0.51: `.pbtn.sel` 의 padding 을 좌우 같게(1.5em) 해서 선택 버튼 글자 가운데 정렬(◀ 는 ::after 로 오른쪽 여백에 따로 놓임). 버튼 글자 중심 측정법: Range.getBoundingClientRect 로 글자 영역 중심과 버튼 중심 차이(dx,dy) 계산(이번에 모든 화면 0±1px 확인).
- 완료된 최근 수정: 계단 오를 땐 왼쪽·내려갈 땐 오른쪽을 봄, 알레센도 초상화 배경 제거, 상점 NPC 카운터 겹침 수정, 첫 실행(터치 대기) 화면 꾸밈.
- 임시 이미지(그림 생기면 교체): 시작 화면 배경 title_bg.jpg / 로고(지금은 예전 그림 로고 title_logo.png, 새 그림을 받으면 assets/title_logo_final.png 로 넣으면 자동 사용), 다락방 배경(attic_bg), 마법스승 웃는 초상화(6편 결말에서 쓰면 좋음), 올빼미.

## 다음 할 일 (우선순위)
1. 이야기 1편·마법서 미니게임 손맛 확인(봇은 성공 처리만 함, 사람이 직접 해 봐야 함). 약초 부탁의 상점 구매 화면은 봇이 건너뜀.
2. 이야기 7편 이후 작성(후보 미정, 사용자와 정하기). 2~6편·작은 부탁 미니게임 손맛도 사람이 확인(설정 → 테스트 → 이야기 n편 시작 지점).
3. 오디오·아이폰 실기기 확인(미검증, 홈 화면 앱으로), 앱 아이콘 그림 교체(지금은 임시), 릴리스 전 일지의 "테스트" 탭 숨기기.
4. 그림 교체(위 임시 이미지 목록). 새 그림을 넣으면 반드시 겹침/크기/외곽선을 기존 캐릭터와 맞춰 스크린샷으로 확인(NPC 높이 기준: 아멜리아=100 대비 orga87, bran106, master104, alesendo106(새 도트 기준 sc1.16), wella91).

## 알려진 한계
- 마스터/오르가/브란 스프라이트의 픽셀 밀도가 서로 달라 완전히 통일하려면 다시 그려야 함.
- 계단 주변 아주 희미한 얼룩이 남아 있을 수 있음(사용자가 거슬려하면 추가 정리).
