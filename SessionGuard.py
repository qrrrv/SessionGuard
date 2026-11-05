"""
⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀
⡀⢠⠋⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢷⡀⡀
⢀⡟⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⡀⡀⡀⡀⡀⡀⡀⢀⣤⠶⡀⡀⣷⡀
⢸⠁⡀⡀⡀⡀⡀⡀⣿⡇⡀⡀⡀⡀⡀⡀⢀⡿⠁⣠⡀⡀⣿⡀⡀⡀⣀⡴⠛⠁⡀⡀⡀⡀⢹⡀
⢸⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣿⡀⡀⣿⡀⡀⣿⡀⡀⡀⠉⠳⣤⡀⡀⡀⡀⡀⢸⡀
⠘⣇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⡀⡀⢿⣤⣶⠹⣦⣴⠏⡀⡀⡀⡀⡀⡀⠈⠛⠦⡀⡀⣿⡀
⡀⠻⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣰⠃⡀
⡀⡀⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀

                                   Made by @JavaScript_XD
                                   Channel: https://t.me/plugin_XD
                                   Created: 05.11.2026
                                   Updated: Initial release
"""

# meta developer: @JavaScript_XD
# meta version: 1.0.1

import html
import importlib
import logging
from datetime import datetime, timedelta, timezone

from .. import loader, utils

__version__ = (1, 0, 1)

logger = logging.getLogger(__name__)

MSK = timezone(timedelta(hours=3))


def _account_tl():
    """TL-модуль Telethon-форка: herokutl у Heroku, hikkatl у Hikka, telethon как запасной."""
    for root in ("herokutl", "hikkatl", "telethon"):
        try:
            return importlib.import_module(f"{root}.tl.functions.account")
        except ImportError:
            continue
    return None


_account = _account_tl()
GetAuthorizationsRequest = getattr(_account, "GetAuthorizationsRequest", None)
ResetAuthorizationRequest = getattr(_account, "ResetAuthorizationRequest", None)


def _dt(value) -> str:
    """datetime или unix -> «05.11.2026 14:32» по Москве.

    В Telethon-форке Heroku поля дат приходят как datetime, а не как int.
    """
    try:
        if isinstance(value, datetime):
            moment = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
            return moment.astimezone(MSK).strftime("%d.%m.%Y %H:%M")
        return datetime.fromtimestamp(int(value), tz=MSK).strftime("%d.%m.%Y %H:%M")
    except (TypeError, ValueError, OSError):
        return "—"


def _ts(value) -> float:
    """datetime | int | None -> unix-время для сортировки."""
    if isinstance(value, datetime):
        return value.timestamp()
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


PLATFORM_ICONS = (
    ("android", "🤖"),
    ("ios", "🍎"),
    ("iphone", "🍎"),
    ("ipad", "🍎"),
    ("macos", "🍏"),
    ("mac", "🍏"),
    ("windows", "🪟"),
    ("win", "🪟"),
    ("linux", "🐧"),
    ("web", "🌐"),
    ("chrome", "🌐"),
    ("firefox", "🌐"),
    ("safari", "🌐"),
)


def _platform_icon(platform: str) -> str:
    low = (platform or "").lower()
    for needle, icon in PLATFORM_ICONS:
        if needle in low:
            return icon
    return "📱"


def _esc(value) -> str:
    return html.escape(str(value or "—"))


@loader.tds
class SessionGuardMod(loader.Module):
    """Показывает, где ещё открыт твой аккаунт, и завершает чужие сессии"""

    strings = {
        "name": "SessionGuard",
        "_cls_doc": "Аудит активных сессий Telegram: устройства, IP, время входа",
        "_cmd_doc_devices": (
            "[kill <номер|all>] — список активных сессий аккаунта "
            "или завершение чужих (по номеру из списка либо всех сразу)"
        ),
        "no_tl": "❌ <b>Не нашёл TL-модуль Telethon</b> — фреймворк нестандартный.",
        "error": "❌ <b>Не получилось:</b> <code>{}</code>",
        "header": "🛡 <b>Активные сессии</b>\n<i>всего {total} · чужих {others}</i>\n",
        "session": (
            "\n<b>{i}.</b> <b>{device}</b>{current}\n"
            "<blockquote>{icon} {platform} · {app}{official}\n"
            "📍 {place}\n"
            "🕓 вход {created} · был {active}</blockquote>"
        ),
        "official": " ✅",
        "unofficial": " ⚠️",
        "hint": (
            "\n\n<i>🔻 <code>.devices kill 2</code> — завершить одну\n"
            "🔻 <code>.devices kill all</code> — завершить все чужие</i>"
        ),
        "tail": "\n<i>…и ещё {n} — список обрезан</i>",
        "bad_num": "❌ <b>Сессии с номером {}</b> нет в списке.",
        "current": " ⬅ <i>это ты</i>",
        "self_kill": "🤔 <b>Это текущая сессия.</b> Если её завершить — выкинет прямо сейчас.",
        "killed": "✅ <b>Сессия завершена</b>\n{device} · <code>{ip}</code>",
        "killed_many": "✅ <b>Завершено чужих сессий:</b> <b>{}</b>",
        "nothing": "🤷 <b>Чужих сессий нет</b> — аккаунт открыт только у тебя.",
        "no_args": "❌ <b>Укажи номер:</b> <code>.devices kill 2</code> или <code>.devices kill all</code>",
    }

    @loader.command()
    async def devices(self, message):
        """[kill <номер|all>] — активные сессии аккаунта"""
        if GetAuthorizationsRequest is None or ResetAuthorizationRequest is None:
            await utils.answer(message, self.strings["no_tl"])
            return

        args = utils.get_args_raw(message).split()
        client = message.client

        try:
            result = await client(GetAuthorizationsRequest())
            auths = list(result.authorizations)
        except Exception as exc:  # noqa: BLE001
            logger.debug("SessionGuard: не удалось получить сессии", exc_info=True)
            await utils.answer(message, self.strings["error"].format(_esc(exc)))
            return

        auths.sort(
            key=lambda a: (
                not getattr(a, "current", False),
                -_ts(getattr(a, "date_active", None)),
            )
        )

        if args and args[0].lower() == "kill":
            await self._kill(message, client, auths, args[1:])
            return

        await utils.answer(message, self._render(auths))

    async def _kill(self, message, client, auths, rest):
        if not rest:
            await utils.answer(message, self.strings["no_args"])
            return

        target = rest[0].lower()

        if target == "all":
            victims = [a for a in auths if not getattr(a, "current", False)]
            if not victims:
                await utils.answer(message, self.strings["nothing"])
                return
            done = 0
            for auth in victims:
                try:
                    await client(ResetAuthorizationRequest(hash=auth.hash))
                    done += 1
                except Exception:  # noqa: BLE001
                    logger.debug("SessionGuard: kill all", exc_info=True)
            await utils.answer(message, self.strings["killed_many"].format(done))
            return

        try:
            index = int(target)
        except ValueError:
            await utils.answer(message, self.strings["bad_num"].format(_esc(target)))
            return

        if index < 1 or index > len(auths):
            await utils.answer(message, self.strings["bad_num"].format(index))
            return

        auth = auths[index - 1]
        if getattr(auth, "current", False):
            await utils.answer(message, self.strings["self_kill"])
            return

        try:
            await client(ResetAuthorizationRequest(hash=auth.hash))
        except Exception as exc:  # noqa: BLE001
            await utils.answer(message, self.strings["error"].format(_esc(exc)))
            return

        await utils.answer(
            message,
            self.strings["killed"].format(
                device=_esc(getattr(auth, "device_model", None)),
                ip=_esc(getattr(auth, "ip", None)),
            ),
        )

    def _render(self, auths) -> str:
        others = sum(1 for a in auths if not getattr(a, "current", False))
        out = [self.strings["header"].format(total=len(auths), others=others)]

        limit = 10
        for i, auth in enumerate(auths[:limit], start=1):
            platform = " ".join(
                part
                for part in (
                    getattr(auth, "platform", None),
                    getattr(auth, "system_version", None),
                )
                if part
            ) or "неизвестно"
            app = (
                getattr(auth, "app_name", None)
                or getattr(auth, "app_version", None)
                or "?"
            )
            official = (
                self.strings["official"]
                if getattr(auth, "official_app", False)
                else self.strings["unofficial"]
            )
            place = (
                getattr(auth, "country", None)
                or getattr(auth, "region", None)
                or "неизвестно"
            )
            ip = getattr(auth, "ip", None)
            place_line = (
                f"<code>{_esc(ip)}</code> · {_esc(place)}" if ip else _esc(place)
            )

            out.append(
                self.strings["session"].format(
                    i=i,
                    device=_esc(getattr(auth, "device_model", None) or "Неизвестное устройство"),
                    current=self.strings["current"] if getattr(auth, "current", False) else "",
                    icon=_platform_icon(platform),
                    platform=_esc(platform),
                    app=_esc(app),
                    official=official,
                    place=place_line,
                    created=_dt(getattr(auth, "date_created", None)),
                    active=_dt(getattr(auth, "date_active", None)),
                )
            )

        if len(auths) > limit:
            out.append(self.strings["tail"].format(n=len(auths) - limit))

        out.append(self.strings["hint"])
        return "".join(out)
