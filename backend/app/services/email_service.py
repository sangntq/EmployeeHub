"""
メール送信サービス

SMTP_HOST が未設定の場合はコンソールログのみ出力する（開発環境向け）。
"""
import asyncio
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_email_sync(to: str, subject: str, body: str) -> None:
    """smtplib を使って同期的にメールを送信する（asyncio.to_thread から呼ぶ）。"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER or "noreply@employeehub.local"
    msg["To"] = to
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)


async def send_email(to: str, subject: str, body: str) -> None:
    """メールを非同期送信する。SMTP_HOST 未設定時はログ出力のみ。"""
    if not settings.SMTP_HOST:
        logger.info("[MAIL] To=%s | Subject=%s | Body=%s", to, subject, body[:100])
        return

    try:
        await asyncio.to_thread(_send_email_sync, to, subject, body)
        logger.info("[MAIL] Sent to %s: %s", to, subject)
    except Exception as exc:
        logger.error("[MAIL] Failed to send to %s: %s", to, exc)
