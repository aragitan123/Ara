# 기탄사고력교실 검단아라학원 · 홈페이지

12월 겨울방학 특강 안내 페이지입니다. 서버 없이 파일만으로 동작하는 정적 사이트라
GitHub Pages·Netlify·Vercel 어디에 올려도 그대로 열립니다.

## 화면 구성
| 주소 | 내용 |
| --- | --- |
| `/` (홈) | 특강 소개, 네 가지 공부 방향, 초등 1학년 특강 상세 |
| `#grades` | 학년별 공부 이야기, 인스타그램·릴스 갤러리 |
| `#library` | 특강 연습 학습지 PDF 내려받기·미리보기 |
| `#notice` | 공지사항, 운영·보강·퇴원 규정, 교육비 |
| `#contact` | 결석·보강 신청, 학부모 소통 게시판, 연락처 |

## 원장님이 직접 고치는 곳
### 1) 공지사항 — `data/notices.json`
```json
{ "date": "11.16", "title": "제목", "body": "내용", "isNew": true }
```
`isNew`가 `true`이면 제목 옆에 NEW 표시가 붙습니다.

### 2) 소통 게시판 — `data/feedback.json`
구글 폼으로 받은 이야기 중 **게시를 허락하신 것만** 옮겨 적습니다.
`answer`에 답변을 적으면 게시판에 바로 반영되고, 비워 두면 "확인하고 있습니다"로 표시됩니다.
```json
{
  "kind": "수업·학습", "who": "초1 학부모", "asked_at": "2026.11.16",
  "title": "제목", "question": "학부모님이 남긴 내용",
  "answer": "원장님 답변", "answered_at": "원장 · 2026.11.17"
}
```

### 3) 릴스·영상 — `data/videos.json`
`items`에 주소만 넣으면 사이트에서 바로 재생됩니다. (인스타 릴스·게시물, 유튜브 영상·쇼츠)
```json
{ "url": "https://www.instagram.com/reel/ABC123/", "title": "12월 특강 소개", "caption": "짧은 설명" }
```

### 4) 구글 폼
- 결석·보강 신청 : `1gFx-GEo0GdCqWFchixcecoe5IaaJeKU-6nDLeELv9Og`
- 학부모 소통·피드백 : `1BAJODW8XoyDxmPCmi5mffA4OxyYEZXH-Cz1bffVNbE4`
링크를 바꾸려면 `index.html`에서 `viewform` 주소 두 곳과 `assets/js/app.js`의 `wireEmbed(...)` 두 곳을 함께 고쳐 주세요.

## 학습지 PDF 다시 만들기
```bash
pip install reportlab fonttools otf2ttf
python3 tools/prepare_fonts.py      # 시스템 OTF → TTF 변환 (tools/pdfkit.py가 사용)
python3 tools/build_pdfs_kids.py    # 유치 6~7세용 워크북 4종 → downloads/
```
- `tools/kidkit.py` : 큰 글씨·큰 칸·별/구름/깜짝 놀이 도구 모음
- `tools/pdfkit.py` : 폰트 등록, 기본 도형(선·산·해·달) 그리기
- `tools/build_pdfs.py` : (예전) 초등용 버전 — 지금 배포본은 `build_pdfs_kids.py`

## 배포
GitHub Pages 기준: 저장소 `Settings → Pages → Branch: main / (root)`.
`index.html`이 저장소 루트에 있어야 그대로 열립니다.

## 문구 기준 (학부모 안내)
- 정원·명수 숫자, '개편', '선착순' 같은 표현은 쓰지 않습니다.
- 맞벌이 가정이 배제되어 보일 만한 표현은 쓰지 않습니다.
- 짧고 정중하며 따뜻하게 씁니다.
