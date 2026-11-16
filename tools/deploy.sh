#!/usr/bin/env bash
# 저장소가 준비된 뒤 한 번에 배포하는 스크립트
#   사용법: bash tools/deploy.sh [owner/repo]
# 예) bash tools/deploy.sh aragitan123/geomdan-ara
set -euo pipefail
cd "$(dirname "$0")/.."

REPO="${1:-aragitan123/Ara}"

if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "https://github.com/${REPO}.git"
else
  git remote set-url origin "https://github.com/${REPO}.git"
fi

git -c user.name="aragitan123" -c user.email="aragitan123@users.noreply.github.com" \
    branch -M main 2>/dev/null || true
git push -u origin main

# GitHub Pages: main 브랜치 루트에서 배포
# (Pickle의 GitHub 연결에는 Pages 권한이 없어 403이 납니다.
#  저장소 Settings → Pages → Source: Deploy from a branch → main / (root) → Save 로 한 번만 켜 주세요.)
gh api -X POST "repos/${REPO}/pages" \
  -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 || \
gh api -X PUT "repos/${REPO}/pages" \
  -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 || \
echo "ℹ️  Pages 자동 켜기는 권한이 없어 건너뜁니다. Settings → Pages 에서 main /(root) 를 선택해 주세요."

OWNER="${REPO%%/*}"
NAME="${REPO##*/}"
echo "✅ 푸시 완료"
echo "🌐 주소: https://${OWNER}.github.io/${NAME}/"
echo "   (Pages 최초 반영까지 1~3분 걸릴 수 있습니다)"
