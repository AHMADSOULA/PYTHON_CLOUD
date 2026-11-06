import asyncio
import os
import re
from urllib.parse import urlparse, parse_qs
from telethon import TelegramClient, events
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import expect
import io
import base64
import json
from telethon.tl.types import DocumentAttributeFilename
import tempfile
import shutil

#===============================
# 🚨 تحذير: قم بتغيير التوكن من BotFather فوراً لأنه تسرب
API_ID = 35339972  
API_HASH = 'fcbb29c0cdd4fbeb66ba017020e721cc' 
BOT_TOKEN = '9276555712:AAFArpLu5l1pomVLQ9zE54YjMfna1Z0NEys' 

client = TelegramClient('DDarkNetConfigs_1', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ==========================================
VLESS_TEMPLATE = (
    "vless://aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000@google.com:443"
    "?path=%2FTelegram%2F%40AM2_D3%2F%40AHMAD3214&security=tls&encryption=none"
    "&host={domain}&type=ws&sni={domain}#%40AHMAD3214"
)

JSON_TEMPLATE = r'''{
  "dns": {
    "fallbackStrategy": "disabledIfAnyMatch",
    "hosts": {},
    "servers": [
      {
        "address": "tcp://8.8.8.8",
        "fakedns": [
          {
            "ipPool": "198.18.0.0/15",
            "poolSize": 65535
          }
        ],
        "queryStrategy": "UseIPv4"
      }
    ]
  },
  "inbounds": [
    {
      "listen": "0.0.0.0",
      "port": "1080",
      "protocol": "dokodemo-door",
      "settings": {
        "network": "tcp,udp",
        "followRedirect": true
      },
      "tag": "tun-inbound"
    },
    {
      "listen": "127.0.0.1",
      "port": "10808",
      "protocol": "socks",
      "settings": {
        "auth": "noauth",
        "udp": true
      },
      "tag": "socks-inbound"
    }
  ],
  "log": {
    "loglevel": "warning"
  },
  "outbounds": [
    {
      "mux": {
        "enabled": false
      },
      "protocol": "vless",
      "proxySettings": {
        "tag": "AhMed",
        "transportLayer": true
      },
      "settings": {
        "vnext": [
          {
            "address": "yt3.ggpht.com",
            "port": 443,
            "users": [
              {
                "encryption": "none",
                "flow": "",
                "id": "aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000",
                "level": 8
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "tlsSettings": {
          "allowInsecure": true,
          "serverName": "yt3.ggpht.com"
        },
        "wsSettings": {
          "headers": {
            "Host": "__DOMAIN__"
          },
          "path": "/Telegram/@AM2_D3/@AHMAD3214"
        }
      },
      "tag": "VLESS"
    },
    {
      "domainStrategy": "AsIs",
      "protocol": "http",
      "settings": {
        "servers": [
          {
            "address": "57.144.120.4",
            "port": 8080
          }
        ],
        "headers": {
          "Host": "yt3.ggpht.com:443",
          "Proxy-Connection": "keep-alive",
          "User-Agent": "FBAV/0.0",
          "X-iorg-bsid": "@AM2_D3"
        }
      },
      "tag": "@AM2_D3"
    },
    {
      "protocol": "freedom",
      "tag": "direct"
    },
    {
      "protocol": "blackhole",
      "tag": "block"
    }
  ],
  "policy": {
    "levels": {
      "8": {
        "connIdle": 300,
        "downlinkOnly": 1,
        "handshake": 4,
        "uplinkOnly": 1
      }
    }
  },
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {
        "outboundTag": "direct",
        "protocol": [
          "dns"
        ],
        "type": "field"
      },
      {
        "inboundTag": [
          "tun-inbound",
          "socks-inbound"
        ],
        "outboundTag": "VLESS",
        "type": "field"
      }
    ]
  }
}'''

# ==========================================
# 📦 3 ملفات DarkTunnel
# ==========================================
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

def build_darktunnel_uri_with_host(base_uri: str, new_host: str) -> str:
    try:
        raw_b64 = _b64_pad(base_uri.split("darktunnel://", 1)[1].strip())
        data = json.loads(base64.b64decode(raw_b64).decode("utf-8"))
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

# ==========================================
# 🛠️ دوال مساعدة ومعالجة الأخطاء
# ==========================================
async def handle_error(page, chat_id, step_name, error_msg):
    print(f"Error at {step_name}: {error_msg}")
    safe_error_msg = str(error_msg)[:900] + "\n... (تم تقصير الرسالة)" if len(str(error_msg)) > 800 else str(error_msg)
    
    screenshot_sent = False
    if page:
        try:
            if not page.is_closed():
                screenshot_path = f"error_{step_name}.png"
                await page.screenshot(path=screenshot_path, full_page=False, timeout=5000)
                await client.send_file(
                    chat_id, 
                    file=screenshot_path, 
                    caption=f"❌ حدث خطأ في مرحلة:\n**{step_name}**\n\nتفاصيل الخطأ:\n`{safe_error_msg}`"
                )
                os.remove(screenshot_path)
                screenshot_sent = True
        except Exception as e:
            print(f"⚠️ تعذر التقاط صورة: {e}")
            
    if not screenshot_sent:
        await client.send_message(
            chat_id, 
            f"❌ حدث خطأ في مرحلة **{step_name}**:\n`{safe_error_msg}`\n\n⚠️ (تعذر التقاط صورة للشاشة)."
        )

def extract_domain_from_service_url(service_url: str) -> str:
    s = (service_url or "").strip()
    if s.startswith("http://") or s.startswith("https://"):
        return urlparse(s).netloc.strip()
    return s.replace("http://", "").replace("https://", "").split("/")[0].strip()

def extract_project_id(url):
    match = re.search(r'(qwiklabs-gcp-[\w-]+)', url)
    return match.group(1) if match else None

async def handle_tos_dialog(page):
    agree_btn = page.get_by_role("button", name="Agree and continue")
    try:
        if await agree_btn.is_visible(timeout=4000):
            checkboxes = page.get_by_role("checkbox")
            count = await checkboxes.count()
            if count >= 2:
                await checkboxes.nth(0).click()
                await asyncio.sleep(0.5)
                await checkboxes.nth(1).click()
            elif count == 1:
                await checkboxes.nth(0).click()
            await agree_btn.click()
            await page.wait_for_timeout(2000)
            return True
    except Exception:
        pass
    return False

# ==========================================
# 🚀 خطوات التنفيذ
# ==========================================
async def step1_welcome_screen(page):
    try: await page.wait_for_load_state("networkidle", timeout=10000)
    except: pass
    await page.wait_for_timeout(2000)    
    try: await page.keyboard.press("Enter")
    except: pass
    try:
        button = page.locator("text='I understand'")
        if await button.is_visible(timeout=3000):
            await button.click()
    except: pass
    await handle_tos_dialog(page)

async def step2_tos_and_country(page):
    await handle_tos_dialog(page)

async def step3_enable_api(page, project_id, authuser):
    api_url = f"https://console.cloud.google.com/apis/library/run.googleapis.com?project={project_id}&authuser={authuser}"
    await page.goto(api_url, wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    await handle_tos_dialog(page)
    
    enable_btn = page.get_by_role("button", name="Enable")
    manage_btn = page.get_by_role("button", name="Manage")
    disable_btn = page.get_by_text("Disable API") 
    
    try:
        await expect(enable_btn.or_(manage_btn)).to_be_visible(timeout=15000)
        if await enable_btn.is_visible():
            await enable_btn.click()
            await page.wait_for_timeout(2500)
            await handle_tos_dialog(page)
            try:
                await expect(manage_btn.or_(disable_btn)).to_be_visible(timeout=45000)
            except Exception:
                await handle_tos_dialog(page)
                await expect(manage_btn.or_(disable_btn)).to_be_visible(timeout=20000)
        elif await manage_btn.is_visible():
            pass 
    except Exception as e:
         raise Exception(f"عطل في إيجاد زر تفعيل الـ API: {str(e)}")

async def step4_create_cloud_run(page, project_id, authuser):
    run_url = f"https://console.cloud.google.com/run/create?project={project_id}&authuser={authuser}"
    await page.goto(run_url, wait_until="domcontentloaded")
    await page.wait_for_timeout(5000)
    
    try:
        label = page.get_by_text("Container Image URL").first
        await label.click()
        await page.wait_for_timeout(500)
        await page.keyboard.type("docker.io/ajndjd2/ahmed-vip1", delay=50)
    except Exception as e:
        raise Exception(f"فشل في الضغط وكتابة الرابط: {str(e)}")
    
    await page.wait_for_timeout(3000)
    await handle_tos_dialog(page)
    
    try:
        await page.get_by_role("radio", name="Allow public access").click()
        await page.get_by_role("radio", name="Instance-based").click()
        try: await page.get_by_role("button", name="Hide").click(timeout=2000)
        except: pass
            
        await page.keyboard.press("End")
        await page.wait_for_timeout(1000)
        
        create_btn = page.get_by_role("button", name="Create")
        await create_btn.click(force=True)
    except Exception as e:
        raise Exception(f"فشل في اختيار الإعدادات أو ضغط Create: {str(e)}")

async def step5_get_deployed_url(page):
    link_locator = page.locator('a[href*="run.app"]')
    await link_locator.wait_for(state="visible", timeout=120000) 
    final_url = await link_locator.get_attribute("href")
    return final_url

# ==========================================
# 🎯 المعالج الرئيسي
# ==========================================
async def process_sso_link(chat_id, sso_url):
    project_id = extract_project_id(sso_url)
    if not project_id:
        await client.send_message(chat_id, "❌ لم يتم العثور على Project ID في الرابط.")
        return

    await client.send_message(chat_id, "⏳ **جاري تجهيز المتصفح وفتح الرابط...**", parse_mode='md')

    temp_dir = tempfile.mkdtemp()
    page = None
    
    async with async_playwright() as p:
        try:
            # ✅ تم تعديل headless إلى True لحل المشكلة
            context = await p.chromium.launch_persistent_context(
                user_data_dir=temp_dir,
                headless=True, 
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--window-size=1920,1080'
                ],
                viewport={'width': 1920, 'height': 1080},
                locale='en-US'
            )
            
            page = context.pages[0] if context.pages else await context.new_page()
            
            await page.goto(sso_url, wait_until="domcontentloaded", timeout=60000)
            
            await client.send_message(chat_id, "🔄 **[1/5] جاري تخطي شاشة الترحيب...**", parse_mode='md')
            await step1_welcome_screen(page)
            
            await client.send_message(chat_id, "⏳ **[2/5] انتظار الدخول إلى لوحة التحكم...**", parse_mode='md')
            await page.wait_for_url("**/home/dashboard**", timeout=45000)
            
            current_qs = parse_qs(urlparse(page.url).query)
            authuser = current_qs.get('authuser', ['1'])[0]
            
            await client.send_message(chat_id, f"🔄 **[3/5] معالجة الشروط...**", parse_mode='md')
            await step2_tos_and_country(page)
            
            await client.send_message(chat_id, "🔄 **[4/5] جاري تفعيل Cloud Run API...**", parse_mode='md')
            await step3_enable_api(page, project_id, authuser)
            
            await client.send_message(chat_id, "🔄 **[5/5] جاري إنشاء خدمة Cloud Run...**", parse_mode='md')
            await step4_create_cloud_run(page, project_id, authuser)
            
            await client.send_message(chat_id, "⏳ **انتظار استخراج رابط run.app (قد يستغرق دقيقة)...**", parse_mode='md')
            final_url = await step5_get_deployed_url(page)        
            domain = extract_domain_from_service_url(final_url)
            
            await client.send_message(chat_id, f"✅ **تم النشر بنجاح!**\n\n🌐 **الرابط:**\n`{final_url}`", parse_mode='md')
            
            # إرسال VLESS و JSON
            vless_result = VLESS_TEMPLATE.format(domain=domain)
            await client.send_message(
                chat_id, 
                f"🔗 **VLESS:**\n<pre><code class=\"language-java\">{vless_result}</code></pre>", 
                parse_mode='html'
            )
            
            json_result = JSON_TEMPLATE.replace("__DOMAIN__", domain)
            await client.send_message(
                chat_id, 
                f"📄 **JSON:**\n<pre><code class=\"language-json\">{json_result}</code></pre>", 
                parse_mode='html'
            )
            
            # إرسال الملفات الثلاثة
            await client.send_message(chat_id, "📤 **جاري إرسال ملفات DarkTunnel الثلاثة...**", parse_mode='md')
            for dark in DARK_FILES:
                new_uri = build_darktunnel_uri_with_host(dark["uri"], domain)
                if new_uri:
                    safe_domain = "".join(c for c in domain.lower() if c.isalnum() or c in ".-_")[:40]
                    tg_fname = f"{dark['name']} - {safe_domain}.dark"
                    bio = io.BytesIO(new_uri.encode("utf-8"))
                    bio.name = tg_fname 
                    await client.send_file(
                        chat_id,
                        bio,
                        force_document=True,
                        attributes=[DocumentAttributeFilename(tg_fname)],
                        caption=f"✅ **{dark['name']}** جاهز."
                    )
            
            await client.send_message(chat_id, "🎉 **اكتملت جميع الخطوات بنجاح!**", parse_mode='md')
            
        except PlaywrightTimeoutError as e:
            await handle_error(page, chat_id, "انتهى وقت الانتظار (Timeout)", str(e))
        except Exception as e:
            await handle_error(page, chat_id, "خطأ عام", str(e))
        finally:
            if 'context' in locals():
                await context.close()
            shutil.rmtree(temp_dir, ignore_errors=True)

# ==========================================
# 📩 استقبال الرسائل
# ==========================================
@client.on(events.NewMessage(pattern=r"^/start$"))
async def start(event):
    welcome_msg = (
        "**إذا غامَرْتَ في شَرَفٍ مَرُومِ  ***  فَلا تَقنَعْ بما دونَ النّجومِ** ☁️✨\n\n"
        "⏳ **الوقت:** 4 ساعات و 30 دقيقة\n"
        "🔗 **الرابط:**\n"
        "https://www.cloudskillsboost.google/focuses/20774?parent=catalog\n\n"
        "⏳ **الوقت:** 3 ساعات\n"
        "🔗 **الرابط:**\n"
        "https://www.skills.google/focuses/82384?parent=catalog\n\n"
        "@DDarkNetConfigs_1"
    )
    await event.reply(welcome_msg)

@client.on(events.NewMessage(pattern=r'https://www\.skills\.google/google_sso.*'))
async def handler(event):
    sso_url = event.text
    asyncio.create_task(process_sso_link(event.chat_id, sso_url))

print("𝙘𝙤𝙣𝙣𝙚𝙘𝙩𝙚𝙙...")
client.run_until_disconnected()
