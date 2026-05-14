"""Blogger publisher (Google Blogger API v3 기반).

인증 흐름:
  첫 1회: 브라우저 OAuth2 → credentials/blogger_token.json 저장
  이후: 자동 토큰 갱신

필요 설정 (.env):
  BLOGGER_CLIENT_SECRETS  = credentials/blogger_client_secrets.json 경로
  BLOGGER_BLOG_ID         = 블로그 숫자 ID (URL에서 확인)
"""

from __future__ import annotations

import json
from pathlib import Path

import markdown as md_lib
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from blog_auto import config
from blog_auto.publishers.base import BasePublisher, PublishRequest, PublishResult

_SCOPES = ["https://www.googleapis.com/auth/blogger"]
_MD_EXTENSIONS = ["tables", "fenced_code", "nl2br"]


def _get_credentials() -> Credentials:
    token_path = config.SESSIONS_DIR / "blogger_token.json"
    secrets_path = Path(config.BLOGGER_CLIENT_SECRETS)

    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), _SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), _SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return creds


class BloggerPublisher(BasePublisher):
    platform = "blogger"

    def publish(self, req: PublishRequest) -> PublishResult:
        if not config.BLOGGER_BLOG_ID:
            return PublishResult(url=None, ok=False, note="BLOGGER_BLOG_ID 미설정.")
        if not config.BLOGGER_CLIENT_SECRETS:
            return PublishResult(url=None, ok=False, note="BLOGGER_CLIENT_SECRETS 미설정.")

        try:
            creds = _get_credentials()
        except Exception as e:
            return PublishResult(url=None, ok=False, note=f"인증 실패: {e}")

        html_body = md_lib.markdown(req.body_md, extensions=_MD_EXTENSIONS)
        service = build("blogger", "v3", credentials=creds)

        body: dict = {
            "title": req.title,
            "content": html_body,
            "labels": req.tags,
        }

        if req.mode == "schedule":
            if not req.schedule_at:
                return PublishResult(url=None, ok=False, note="schedule 모드는 --at RFC3339 시간 필요.")
            body["published"] = req.schedule_at

        try:
            if req.mode == "draft":
                resp = (
                    service.posts()
                    .insert(blogId=config.BLOGGER_BLOG_ID, body=body, isDraft=True)
                    .execute()
                )
            else:
                resp = (
                    service.posts()
                    .insert(blogId=config.BLOGGER_BLOG_ID, body=body, isDraft=False)
                    .execute()
                )
        except Exception as e:
            return PublishResult(url=None, ok=False, note=f"API 오류: {e}")

        url = resp.get("url")
        status = resp.get("status", "")
        label = {"draft": "임시저장", "schedule": f"예약 ({req.schedule_at})", "publish": "발행"}.get(req.mode, "발행")
        return PublishResult(url=url, ok=True, note=f"{label} 완료 (status={status})")
