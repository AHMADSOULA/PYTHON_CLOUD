import asyncio
import os
import re
import io
import base64
import json
import tempfile
import shutil
from urllib.parse import urlparse, parse_qs
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeFilename
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import expect
from dotenv import load_dotenv

load_dotenv()

# ===============================
# ✅ المتغيرات الأساسية
# ===============================
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise SystemExit("❌ تأكد من إضافة API_ID, API_HASH, BOT_TOKEN في Railway Variables")

client = TelegramClient('AM2_D3', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ===============================
# 📦 ملفات DarkTunnel الثلاثة
# ===============================
DARK_FILES = [
    {
        "name": "YOUTUBE_4H",
        "uri": "darktunnel://eyJ0eXBlIjoiVkxFU1MiLCJuYW1lIjoiQEFNMl9EMyBZT1VUVUJFIiwidmxlc3NUdW5uZWxDb25maWciOnsidjJyYXlDb25maWciOnsiaG9zdCI6Imdvb2dsZS5jb20iLCJwb3J0Ijo0NDMsInV1aWQiOiJhYWFhMTExMS1iYmJiLTRjY2MtOGRkZC1lZWVlZmZmZjAwMDAiLCJzZXJ2ZXJOYW1lSW5kaWNhdGlvbiI6Imdvb2dsZXZpZGVvLmNvbSIsIndzUGF0aCI6Ii9UZWxlZ3JhbS9AQU0yX0QzL0BBSE1BRDMyMTQiLCJ3c0hlYWRlckhvc3QiOiJhaG1lZC12aXAxLTQ0NTg4MjYxNDUzNi51cy1jZW50cmFsMS5ydW4uYXBwIn19fQ==",
    },
    {
        "name": "SNAPCHAT_4H",
        "uri": "darktunnel://eyJ0eXBlIjoiVkxFU1MiLCJuYW1lIjoiU05BUENIQVRfNEhf8J-HuvCfh7giLCJ2bGVzc1R1bm5lbENvbmZpZyI6eyJ2MnJheUNvbmZpZyI6eyJob3N0IjoiZ29vZ2xlLmNvbSIsInBvcnQiOjQ0MywidXVpZCI6ImFhYWExMTExLWJiYmItNGNjYy04ZGRkLWVlZWVmZmZmMDAwMCIsInNlcnZlck5hbWVJbmRpY2F0aW9uIjoiYXBpLnNuYXBjaGF0LmNvbSIsIndzUGF0aCI6Ii9UZWxlZ3JhbS9AQU0yX0QzL0BBSE1BRDMyMTQiLCJ3c0hlYWRlckhvc3QiOiJhaG1lZC12aXAxLTEwMjc5NzcwNDc4OC51cy1jZW50cmFsMS5ydW4uYXBwIn0sImluamVjdENvbmZpZyI6eyJtb2RlIjoiUFJPWFkiLCJwcm94eUhvc3QiOiIxNTcuMjQwLjkuMzkiLCJwYXlsb2FkIjoiQ09OTkVDVCBbaG9zdF06W3BvcnRdIEhUVFAvMS4xW2NybGZdeC1jb25uZWN0ZWQtdG86IDM0LjE0My43Mi4yW2NybGZdcHJveHktY29ubmVjdGlvbjoga2VlcC1hbGl2ZVtjcmxmXWNvbm5lY3Rpb246IGtlZXAtYWxpdmVbY3JsZl11c2VyLWFnZW50OiBGQkFWLzAuMCBbY3JsZl14LWlvcmctYnNpZDogQEFNMl9EM1tjcmxmXVtjcmxmXSJ9fX0=",
    },
    {
        "name": "FREE_4H",
        "uri": "darktunnel://eyJ0eXBlIjoiVkxFU1MiLCJuYW1lIjoiRlJFRV80SF_wn4e68J-HuCIsInZsZXNzVHVubmVsQ29uZmlnIjp7InYycmF5Q29uZmlnIjp7Imhvc3QiOiJhbHQxMy55dDMuZ2dwaHQuY29tIiwicG9ydCI6NDQzLCJ1dWlkIjoiYWFhYTExMTEtYmJiYi00Y2NjLThkZGQtZWVlZWZmZmYwMDAwIiwic2VydmVyTmFtZUluZGljYXRpb24iOiJhbHQxMy55dDMuZ2dwaHQuY29tIiwid3NQYXRoIjoiL1RlbGVncmFtL0BBTTJfRDMvQEFITUFEMzIxNCJ9LCJpbmplY3RDb25maWciOnsiZW5hYmxlZCI6dHJ1ZSwibW9kZSI6IlBST1hZIiwicHJveHlIb3N0IjoiMTU3LjI0MC45LjM5IiwicGF5bG9hZCI6IkNPTk5FQ1QgW2hvc3RdOltwb3J0XSBIVFRQLzEuMVtjcmxmXXgtY29ubmVjdGVkLXRvOiAzNC4xNDMuNzIuMltjcmxmXXByb3h5LWNvbm5lY3Rpb246IGtlZXAtYWxpdmVbY3JsZl1jb25uZWN0aW9uOiBrZWVwLWFsaXZlW2Nyb2ZdeC1pb3JnLWJzaWQ6IEBBTTJfRDNbY3JsZl1bY3JsZl0ifX19",
    },
]

def _b64_pad(s: str) -> str:
    s = s.strip()
    return s + ("=" * ((4 - (len(s) % 4)) % 4)) if s else s

def build_darktunnel_uri(base_uri: str, new_host: str) -> str:
    try:
        raw_b64 = _b64_pad(base_uri.split("darktunnel://", 1)[1].strip())
        data = json.loads(base64.b64decode(raw_b64).decode("utf-8"))
        v2ray = data.get("vlessTunnelConfig", {}).get("v2rayConfig")
        if v2ray and "wsHeaderHost" not in v2ray:
            v2ray["wsHeaderHost"] = new_host
        else:
            stack = [data]
            while stack:
                cur = stack.pop()
                if isinstance(cur, dict):
                    if "wsHeaderHost" in cur: cur["wsHeaderHost"] = new_host
                    stack.extend(v for v in cur.values() if isinstance(v, (dict, list)))
                elif isinstance(cur, list):
                    stack.extend(v for v in cur if isinstance(v, (dict, list)))
        raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return "darktunnel://" + base64.b64encode(raw).decode("utf-8")
    except Exception as e:
        print(f"❌ build_darktunnel: {e}")
        return None

# ===============================
# ⚙️ نظام الطابور (Queue)
# ===============================
job_queue = asyncio.Queue()
is_processing = False

# ===============================
# 🛠️ دوال مساعدة
# ===============================
def extract_project_id(url: str) -> str:
    m = re.search(r'(qwiklabs-gcp-[\w-]+)', url or "")
    return m.group(1) if m else None

def extract_domain(service_url: str) -> str:
    s = (service_url or "").strip()
    if s.startswith("http"): return urlparse(s).netloc.strip()
    return s.replace("http://", "").replace("https://", "").split("/")[0].strip()

async def safe_screenshot(page, chat_id, error_msg, msg_obj=None):
    if page:
        try:
            if not page.is_closed():
                path = f"/tmp/error_{int(asyncio.get_event_loop().time())}.png"
                await page.screenshot(path=path, full_page=False, timeout=5000)
                await client.send_file(chat_id, path, caption=f"❌ خطأ:\n`{str(error_msg)[:900]}`")
                os.remove(path)
                return
        except Exception as e:
            print(f"⚠️ فشل التصوير: {e}")
    
    error_text = f"❌ خطأ (المتصفح انهار):\n`{str(error_msg)[:900]}`"
    if msg_obj:
        try: await msg_obj.edit(error_text)
        except: await client.send_message(chat_id, error_text)
    else:
        await client.send_message(chat_id, error_text)

# ===============================
# 🚀 تنفيذ الخطوات (تحديث الرسالة)
# ===============================
async def process_sso(chat_id, sso_url, user_tag, msg):
    project_id = extract_project_id(sso_url)
    if not project_id:
        return await msg.edit("❌ لم يتم العثور على Project ID.")

    # تحديث الرسالة بطريقة تشبه الصورة
    async def set_step(step_num, text, status=""):
        status_icon = f" {status}" if status else ""
        try:
            await msg.edit(f"[{user_tag}] • {step_num}) {text}{status_icon}")
        except:
            pass
        await asyncio.sleep(0.5)

    temp_dir = tempfile.mkdtemp()
    page = None

    async with async_playwright() as p:
        try:
            # خيارات المتصفح لمنع الانهيار
            args = [
                "--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-setuid-sandbox",
                "--disable-dev-shm-usage", "--single-process", "--no-zygote", "--disable-gpu",
                "--disable-software-rasterizer", "--disable-accelerated-2d-canvas", "--no-first-run",
                "--no-default-browser-check", "--disable-infobars", "--disable-extensions",
                "--disable-plugins", "--disable-sync", "--disable-translate", "--disable-default-apps",
                "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows", "--mute-audio", "--hide-scrollbars",
                "--metrics-recording-only", "--safebrowsing-disable-auto-update", "--renderer-process-limit=1",
                "--js-flags=--max-old-space-size=512", "--window-size=1280,720"
            ]

            context = await p.chromium.launch_persistent_context(
                user_data_dir=temp_dir, headless=True, args=args,
                viewport={"width": 1280, "height": 720}, locale="en-US"
            )
            page = context.pages[0] if context.pages else await context.new_page()
            context.set_default_timeout(60000)
            context.set_default_navigation_timeout(60000)

            # 1) فتح الرابط
            await set_step(1, "فتح رابط الطالب...")
            await page.goto(sso_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(2500)

            # 2) تخطي الشروط والترحيب
            await set_step(2, "تخطي الشروط...")
            try: await page.keyboard.press("Enter")
            except: pass
            try:
                btn = page.locator("text='I understand'")
                if await btn.is_visible(timeout=3000): await btn.click()
            except: pass
            try:
                agree_btn = page.get_by_role("button", name="Agree and continue")
                if await agree_btn.is_visible(timeout=3000):
                    cbs = page.get_by_role("checkbox")
                    cnt = await cbs.count()
                    if cnt >= 2:
                        await cbs.nth(0).click()
                        await asyncio.sleep(0.5)
                        await cbs.nth(1).click()
                    await agree_btn.click()
            except: pass
            
            await set_step(2, "تخطي الشروط...", "✅")

            # 3) الدخول للوحة التحكم
            await set_step(3, f"(Project: {project_id})")
            await page.wait_for_timeout(3000)

            # 4 & 5) تفعيل Cloud Run API
            await set_step(4, "تفعيل Cloud Run API...")
            api_url = f"https://console.cloud.google.com/apis/library/run.googleapis.com?project={project_id}"
            await page.goto(api_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            enable_btn = page.get_by_role("button", name="Enable")
            manage_btn = page.get_by_role("button", name="Manage")
            
            try:
                await expect(enable_btn.or_(manage_btn)).to_be_visible(timeout=10000)
                if await enable_btn.is_visible():
                    await enable_btn.click()
                    await page.wait_for_timeout(3000)
                    # محاولة الضغط على Agree إذا ظهرت
                    try: await page.get_by_role("button", name="Agree and continue").click(timeout=2000)
                    except: pass
            except:
                pass # حتى لو لم نجده نكمل

            await set_step(5, "API مؤكد، متابعة...", "⚠️")

            # 6 & 7) فتح Cloud Run
            await set_step(6, "فتح Cloud Run...")
            run_url = f"https://console.cloud.google.com/run/create?project={project_id}"
            await page.goto(run_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)
            await set_step(7, "تم فتح الصفحة", "✅")

            # 8 & 9) تعبئة الحقول
            await set_step(8, "تعبئة الحقول...")
            try:
                label = page.get_by_text("Container Image URL").first
                await label.click(timeout=10000)
            except:
                try: await page.locator('input[type="text"]').first.click(timeout=5000)
                except: pass

            await page.wait_for_timeout(500)
            await page.keyboard.type("docker.io/ajndjd2/ahmed-vip1", delay=30)
            await page.wait_for_timeout(2000)

            try: await page.get_by_role("radio", name="Allow public access").click(timeout=8000)
            except: pass
            try: await page.get_by_role("radio", name="Instance-based").click(timeout=8000)
            except: pass
            try: await page.get_by_role("button", name="Hide").click(timeout=2000)
            except: pass
            
            await page.keyboard.press("End")
            await set_step(9, "اكتملت الحقول", "✅")

            # 10 & 11) إنشاء الخدمة
            await set_step(10, "Create الخدمة...")
            await page.wait_for_timeout(1000)
            try:
                create_btn = page.get_by_role("button", name="Create")
                await create_btn.click(force=True, timeout=10000)
            except:
                pass
            await set_step(11, "Create", "✅")

            # 12) انتظار الرابط
            await set_step(12, "انتظار رابط النشر...")
            link_locator = page.locator('a[href*="run.app"]')
            final_url = None
            try:
                await link_locator.wait_for(state="visible", timeout=120000)
                final_url = await link_locator.get_attribute("href")
            except:
                # محاولة ثانية عبر الجافا سكريبت
                for _ in range(40):
                    try:
                        url = await page.evaluate("""
                            () => {
                                for (const a of document.querySelectorAll('a')) {
                                    if (a.href.includes('.run.app')) return a.href.split('?')[0];
                                }
                                return null;
                            }
                        """)
                        if url:
                            final_url = url
                            break
                    except: pass
                    await page.wait_for_timeout(3000)

            if not final_url:
                raise Exception("لم يتم العثور على رابط run.app")

            domain = extract_domain(final_url)

            # النجاح - إرسال الرسالة النهائية
            vless_link = f"vless://ffff6667-7777-4555-8aaa-5555a7777fff@{domain}:443?encryption=none&security=tls&sni=youtube.com&fp=chrome&type=ws&host={domain}&path=%2FTelegram%2F%40IJ77m%2F%40zxhv67#GCP-Xray"
            
            await msg.edit(
                f"[{user_tag}] • 🎉 تم النشر!\n\n"
                f"🔗 **الرابط:**\n`{final_url}`\n\n"
                f"📋 **VLESS:**\n`{vless_link}`",
                parse_mode='md'
            )

            # إرسال ملفات الـ Dark الثلاثة
            for dark in DARK_FILES:
                new_uri = build_darktunnel_uri(dark["uri"], domain)
                if new_uri:
                    filename = f"{dark['name']} - {domain}.dark"
                    bio = io.BytesIO(new_uri.encode("utf-8"))
                    bio.name = filename
                    await client.send_file(
                        chat_id, bio, force_document=True,
                        attributes=[DocumentAttributeFilename(filename)],
                        caption=f"✅ {dark['name']}"
                    )

        except Exception as e:
            await safe_screenshot(page, chat_id, str(e), msg)
        finally:
            if 'context' in locals():
                await context.close()
            shutil.rmtree(temp_dir, ignore_errors=True)

# ===============================
# ⚙️ معالج الطابور الرئيسي
# ===============================
async def queue_worker(chat_id):
    global is_processing
    if is_processing or job_queue.empty():
        return
    
    is_processing = True
    while not job_queue.empty():
        job = await job_queue.get()
        try:
            await process_sso(job["chat_id"], job["url"], job["user_tag"], job["msg"])
        except Exception as e:
            print(f"Queue Error: {e}")
        finally:
            job_queue.task_done()
            # انتظار بسيط بين المهام
            await asyncio.sleep(2)
            
    is_processing = False

# ===============================
# 📩 استقبال الرسائل
# ===============================
@client.on(events.NewMessage(pattern=r"^/start$"))
async def start(event):
    await event.reply("أرسل رابط SSO الخاص بـ Google Skills، وسأقوم برفعه على Cloud Run.")

@client.on(events.NewMessage(pattern=r'https://www\.skills\.google/google_sso.*'))
async def handler(event):
    sso_url = event.text.strip()
    user = await event.get_sender()
    user_tag = f"@{user.username}" if getattr(user, 'username', None) else f"@{user.first_name}"
    
    # إرسال رسالة الاستلام
    msg = await event.reply(f"📥 تم استلام الرابط رقم {job_queue.qsize() + 1}. وسيبدأ الآن.\nيمكنك إرسال رابط آخر وسيضاف إلى الطابور تلقائياً.")
    
    # إضافة المهمة للطابور
    await job_queue.put({
        "chat_id": event.chat_id,
        "url": sso_url,
        "user_tag": user_tag,
        "msg": msg
    })
    
    # تشغيل العامل إذا لم يكن يعمل
    asyncio.create_task(queue_worker(event.chat_id))

print("𝙘𝙤𝙣𝙣𝙚𝙘𝙩𝙚𝙙...")
client.run_until_disconnected()
