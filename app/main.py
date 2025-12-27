import logging
import sys
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app import bot as tg_bot
from app import routers as fast_router
from app.admin import setup_admin
from app.bot import middlewares as bot_middleware
from app.core.configs import settings
from app.core.rate_limiter import limiter
from app.utils import rate_limit_handler

load_dotenv()

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

logger = logging.getLogger(__name__)

# ------- Bot ------- #
bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ------- Bot Routers ------- #
dp.include_router(tg_bot.auth_router)
dp.include_router(tg_bot.role_router)
dp.include_router(tg_bot.command_router)
dp.include_router(tg_bot.balance_router)
dp.include_router(tg_bot.group_chat_router)
dp.include_router(tg_bot.lang_router)

# ------- Bot Middlewares ------- #
dp.update.middleware(bot_middleware.RepositoryMiddleware())

dp.message.outer_middleware(bot_middleware.GroupValidationMiddleware())
dp.callback_query.outer_middleware(bot_middleware.GroupValidationMiddleware())

dp.message.outer_middleware(bot_middleware.AdminCacheMiddleware())
dp.callback_query.outer_middleware(bot_middleware.AdminCacheMiddleware())


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Application startup...", )

    try:
        await bot.set_webhook(url=settings.WEBHOOK_URL)
        logger.info(f"✅ Webhook set to: {settings.WEBHOOK_URL}")
        from app.utils.translations import initialize_translator, MESSAGES
        initialize_translator(MESSAGES)
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}", exc_info=True)

    yield

    await bot.session.close()


# ------- FastAPI ------- #
app = FastAPI(lifespan=lifespan)

# ------- Slowapi ------- #
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


# ------- CORS ------- #

class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get('x-forwarded-proto') == 'https':
            request.scope['scheme'] = 'https'
        if request.headers.get('x-forwarded-host'):
            request.scope['server'] = (request.headers.get('x-forwarded-host'), 443)
        return await call_next(request)


app.add_middleware(ProxyHeadersMiddleware)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["aibot.grossbook.uz", "localhost", "127.0.0.1", "aiadmin.grossbook.uz",
                   "excommunicable-frowstily-ayako.ngrok-free.dev"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------- Admin ------- #
setup_admin(app)

# ------- FastAPI Routers ------- #
app.include_router(fast_router.group_router)
app.include_router(fast_router.fetch_router)
app.include_router(fast_router.company_router)
app.include_router(fast_router.kapital_router)
app.include_router(fast_router.gnk_api_router)
app.include_router(fast_router.certificates_router)
app.include_router(fast_router.company_group_router)
app.include_router(fast_router.telegram_auth_router)
app.include_router(fast_router.audit_log_router)


@app.post("/tg/webhook")
async def bot_webhook(request: Request):
    """Receive updates from Telegram."""
    try:
        update_data = await request.json()
        telegram_update = types.Update(**update_data)
        await dp.feed_webhook_update(bot=bot, update=telegram_update)
        return Response(status_code=200)
    except Exception as e:
        logging.error(f"Error processing update: {e}", exc_info=True)
        return Response(status_code=500)


@app.get("/")
async def root():
    """API status."""
    return {
        "status": "running",
        "bot_mode": "webhook",
        "webhook_url": settings.WEBHOOK_URL
    }
