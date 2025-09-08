from __future__ import annotations

import smtplib
import socket
from email.mime.text import MIMEText
from email.utils import formatdate

from .config import settings


def _send_via_smtp_tls(host: str, port: int, user: str, password: str, sender: str, recipients: list[str], msg: MIMEText, timeout_seconds: float) -> None:
	with smtplib.SMTP(host, port, timeout=timeout_seconds) as smtp:
		smtp.set_debuglevel(1)
		smtp.starttls()
		smtp.login(user, password)
		smtp.sendmail(sender, recipients, msg.as_string())


def _send_via_smtp_ssl(host: str, port: int, user: str, password: str, sender: str, recipients: list[str], msg: MIMEText, timeout_seconds: float) -> None:
	with smtplib.SMTP_SSL(host, port, timeout=timeout_seconds) as smtp:
		smtp.set_debuglevel(1)
		smtp.login(user, password)
		smtp.sendmail(sender, recipients, msg.as_string())


async def send_alert_email(subject: str, body: str) -> None:
	msg = MIMEText(body, _charset="utf-8")
	msg["Subject"] = subject
	msg["From"] = settings.mail_sender
	msg["To"] = ", ".join(settings.mail_recipients)
	msg["Date"] = formatdate(localtime=True)

	# Slightly longer timeout and connection strategy with fallbacks
	timeout_seconds = 20

	# Build attempts based on explicit config first, then sensible fallbacks
	attempts: list[dict] = []
	if settings.smtp_use_ssl:
		attempts.append({"mode": "ssl", "host": settings.smtp_host, "port": settings.smtp_port})
	else:
		attempts.append({"mode": "tls", "host": settings.smtp_host, "port": settings.smtp_port})

	# Add common Gmail fallbacks to improve resiliency if the configured one times out
	if not any(a["mode"] == "tls" and a["port"] == 587 for a in attempts):
		attempts.append({"mode": "tls", "host": settings.smtp_host or "smtp.gmail.com", "port": 587})
	if not any(a["mode"] == "ssl" and a["port"] == 465 for a in attempts):
		attempts.append({"mode": "ssl", "host": settings.smtp_host or "smtp.gmail.com", "port": 465})

	last_error: Exception | None = None

	for attempt in attempts:
		mode = attempt["mode"]
		host = attempt["host"]
		port = attempt["port"]
		try:
			print(f"🔌 Trying SMTP {mode.upper()} {host}:{port} ...")
			if mode == "ssl":
				_send_via_smtp_ssl(host, port, settings.smtp_user, settings.smtp_password, settings.mail_sender, settings.mail_recipients, msg, timeout_seconds)
			else:
				_send_via_smtp_tls(host, port, settings.smtp_user, settings.smtp_password, settings.mail_sender, settings.mail_recipients, msg, timeout_seconds)
			print(f"✅ Email alert sent successfully to {settings.mail_recipients}")
			return
		except smtplib.SMTPAuthenticationError as e:
			error_msg = f"❌ Gmail authentication failed: {e}"
			print(error_msg)
			print("🔧 To fix this:")
			print("   1. Go to: https://myaccount.google.com/apppasswords")
			print("   2. Generate a new app password for 'Mail'")
			print("   3. Update SMTP_PASSWORD in your config.env file")
			print("   4. Make sure 2-Step Verification is enabled")
			raise Exception(error_msg)
		except (socket.timeout, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected) as e:
			# Save and try next attempt
			last_error = e
			print(f"⚠️ Connection attempt failed for {mode.upper()} {host}:{port}: {e}")
			continue
		except smtplib.SMTPException as e:
			last_error = e
			print(f"❌ SMTP error on {mode.upper()} {host}:{port}: {e}")
			continue
		except Exception as e:
			last_error = e
			print(f"❌ Email error on {mode.upper()} {host}:{port}: {e}")
			continue

	# If we reach here, all attempts failed
	detail = f"Last error: {last_error}" if last_error else "Unknown error"
	raise Exception(f"❌ SMTP connection failed for all attempts. {detail}")

