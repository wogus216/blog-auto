from pathlib import Path
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

STYLE_DIR = ROOT / "style"
PROMPTS_DIR = ROOT / "prompts"
POSTS_DIR = ROOT / "posts"
SESSIONS_DIR = ROOT / "sessions"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-7")

TISTORY_BLOG_NAME = os.environ.get("TISTORY_BLOG_NAME", "")
NAVER_BLOG_ID = os.environ.get("NAVER_BLOG_ID", "")
BLOGGER_BLOG_ID = os.environ.get("BLOGGER_BLOG_ID", "6566918690057179781")
BLOGGER_STOCKS_BLOG_ID = os.environ.get("BLOGGER_STOCKS_BLOG_ID", "")
BLOGGER_CLIENT_SECRETS = os.environ.get("BLOGGER_CLIENT_SECRETS", "credentials/blogger_client_secrets.json")

PUBLISH_MODE = os.environ.get("PUBLISH_MODE", "draft")  # draft | publish

# Google Images 스크래핑 옵션 (utils/google_images.py)
GOOGLE_IMAGES_HEADLESS = os.environ.get("GOOGLE_IMAGES_HEADLESS", "true").lower() == "true"

MIN_DELAY = int(os.environ.get("MIN_DELAY_SECONDS", "90"))
MAX_DELAY = int(os.environ.get("MAX_DELAY_SECONDS", "180"))
