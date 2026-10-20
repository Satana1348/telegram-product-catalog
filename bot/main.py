import asyncio,os,httpx
from aiogram import Bot,Dispatcher,F
from aiogram.filters import CommandStart
from aiogram.types import Message,WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
dp=Dispatcher(); admin=int(os.environ["ADMIN_TELEGRAM_ID"])
def kb():
 b=InlineKeyboardBuilder(); b.button(text="Открыть каталог",web_app=WebAppInfo(url=os.environ["WEB_APP_URL"])); return b.as_markup()
@dp.message(CommandStart())
async def start(m:Message): await m.answer("У меня есть товар",reply_markup=kb())
@dp.message(F.photo)
async def add(m:Message,bot:Bot):
 if not m.from_user or m.from_user.id!=admin: return
 if not (name:=(m.caption or '').strip()): await m.answer("Добавьте название в подпись к фото."); return
 f=await bot.get_file(m.photo[-1].file_id); raw=await bot.download_file(f.file_path)
 try:
  async with httpx.AsyncClient(timeout=20) as c: r=await c.post(os.environ.get("API_BASE_URL","http://localhost:8000")+"/api/internal/products",params={"name":name},headers={"X-Internal-Token":os.environ["INTERNAL_API_TOKEN"]},files={"image":("product.jpg",raw.read(),"image/jpeg")}); r.raise_for_status()
 except httpx.HTTPError: await m.answer("Не удалось сохранить товар."); return
 await m.answer(f"Товар «{name}» добавлен.")
async def main(): await dp.start_polling(Bot(os.environ["BOT_TOKEN"]))
asyncio.run(main())
