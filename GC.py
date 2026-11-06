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
from dotenv import load_dotenv

load_dotenv()

# ===============================
# ✅ قراءة المتغيرات من البيئة
# ===============================
required_vars = ["API_ID", "API_HASH", "BOT_TOKEN"]
missing = [v for v in required_vars if not os.environ.get(v)]
if missing:
    raise SystemExit(f"❌ متغيرات مفقودة: {', '.join(missing)}")

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

client = TelegramClient('AM2_D3', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ==========================================
# 🛡️ إعدادات التمويه (Stealth JS)
# ==========================================
STEALTH_JS = r"""
// 1. webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// 2. languages + platform
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 0 });
Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });

// 3. plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const plugins = [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
            { name: 'Native Client', filename: 'internal-nacl-plugin' },
        ];
        plugins.refresh = () => {};
        plugins.item = (i) => plugins[i];
        plugins.namedItem = (n) => plugins.find(p => p.name === n);
        return plugins;
    }
});

// 4. WebGL
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) return 'Intel Inc.';
    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
    return getParameter.call(this, parameter);
};

// 5. chrome runtime
window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: { isInstalled: false } };

// 6. screen
Object.defineProperty(screen, 'width', { get: () => 1920 });
Object.defineProperty(screen, 'height', { get: () => 1080 });
"""

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

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

DARKTUNNEL_BASE_URI = "darktunnel://eyJ0eXBlIjoiVkxFU1MiLCJuYW1lIjoi2YXYrNin2YbZiiDYp9iz2YrYpyDZiCDYp9ir2YrYsSAiLCJ2bGVzc1R1bm5lbENvbmZpZyI6eyJ2MnJheUNvbmZpZyI6eyJob3N0IjoiYWx0MTMueXQzLmdncGh0LmNvbSIsInBvcnQiOjQ0MywidXVpZCI6ImFhYWExMTExLWJiYmItNGNjYy04ZGRkLWVlZWVmZmZmMDAwMCIsInNlcnZlck5hbWVJbmRpY2F0aW9uIjoiYWx0MTMueXQzLmdncGh0LmNvbSIsIndzUGF0aCI6Ii9UZWxlZ3JhbS9AQU0yX0QzL0BBSE1BRDMyMTQiLCJ3c0hlYWRlckhvc3QiOiJhaG1lZC12aXAxLTQxNDAwODYxMjEyMy5ldXJvcGUtd2VzdDEucnVuLmFwcCJ9LCJpbmplY3RDb25maWciOnsiZW5hYmxlZCI6dHJ1ZSwibW9kZSI6IlBST1hZIiwicHJveHlIb3N0IjoiMTU3LjI0MC45LjM5IiwicGF5bG9hZCI6IkNPTk5FQ1QgW2hvc3RdOltwb3J0XSBIVFRQLzEuMVtjcmxmXXgtY29ubmVjdGVkLXRvOiAzNC4xNDMuNzIuMltjcmxmXXByb3h5LWNvbm5lY3Rpb246IGtlZXAtYWxpdmVbY3JsZl1jb25uZWN0aW9uOiBrZWVwLWFsaXZlW2NybGZddXNlci1hZ2VudDogRkJBVi8wLjAgW2NybGZdeC1pb3JnLWJzaWQ6IEBBTTJfRDNbY3JsZl1bY3JsZl0ifX19"

# ==========================================
# 🔔 أداة الإشعار المركزية
# ==========================================
async def notify(chat_id, msg):
    try:
        await client.send_message(chat_id, msg)
    except Exception as e:
        print(f"⚠️ notify failed: {e}")
    await asyncio.sleep(0.25)


async def handle_error(page, chat_id, step_name, error_msg):
    print(f"Error at {step_name}: {error_msg}")
    safe_error_msg = str(error_msg)[:900] + "\n... (تم تقصير الرسالة)" if len(str(error_msg)) > 800 else str(error_msg)
    
    if page:
        try:
            screenshot_path = f"error_{step_name}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            await client.send_file(
                chat_id, 
                file=screenshot_path, 
                caption=f"❌ حدث خطأ في مرحلة:\n**{step_name}**\n\nتفاصيل الخطأ:\n`{safe_error_msg}`"
            )
            os.remove(screenshot_path)
            return
        except Exception as e:
            pass
    
    # في حال فشل المتصفح من الأساس ولم نتمكن من أخذ سكرين شوت
    await client.send_message(chat_id, f"❌ حدث خطأ في مرحلة **{step_name}**:\n`{safe_error_msg}`")

# ==========================================
def extract_domain_from_service_url(service_url: str) -> str:
    s = (service_url or "").strip()
    if s.startswith("http://") or s.startswith("https://"):
        return urlparse(s).netloc.strip()
    return s.replace("http://", "").replace("https://", "").split("/")[0].strip()

def _b64_pad(s: str) -> str:
    return s + ("=" * ((4 - (len(s) % 4)) % 4)) if s else s

def darktunnel_decode(uri: str) -> dict:
    b64 = _b64_pad(uri.split("darktunnel://", 1)[1].strip())
    return json.loads(base64.b64decode(b64.encode("utf-8")).decode("utf-8"))

def darktunnel_encode(data: dict) -> str:
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return "darktunnel://" + base64.b64encode(raw).decode("utf-8")

def build_darktunnel_uri_with_host(new_host: str) -> str:
    data = darktunnel_decode(DARKTUNNEL_BASE_URI)
    stack = [data]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            if "wsHeaderHost" in cur:
                cur["wsHeaderHost"] = new_host
            stack.extend(v for v in cur.values() if isinstance(v, (dict, list)))
        elif isinstance(cur, list):
            stack.extend(v for v in cur if isinstance(v, (dict, list)))
    return darktunnel_encode(data)

async def generate_and_send_dark_file(chat_id: int, domain: str):
    new_uri = build_darktunnel_uri_with_host(domain)
    safe_domain = re.sub(r"[^a-z0-9\.\-]+", "_", domain.lower()).strip("_")
    tg_fname = f"زين و اسيا مجاني - {safe_domain}.dark"
    bio = io.BytesIO(new_uri.encode("utf-8"))
    bio.name = tg_fname 
    await client.send_file(
        chat_id,
        bio,
        force_document=True,
        attributes=[DocumentAttributeFilename(tg_fname)],
        caption=f"✅ ملف DarkTunnel جاهز:\n`{domain}`"
    )

# ==========================================
def extract_project_id(url):
    match = re.search(r'(qwiklabs-gcp-[\w-]+)', url)
    if match:
        return match.group(1)
    return None

# ==========================================
# 🔔 خطوات التنفيذ
# ==========================================
async def step1_welcome_screen(page, chat_id):
    await notify(chat_id, "1️⃣ [1/5] بدء شاشة الترحيب: انتظار تحميل الصفحة...")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    
    await notify(chat_id, "⌨️ ضغط زر Enter لتخطي شاشة الترحيب...")
    await page.keyboard.press("Enter")
    
    try:
        button = page.locator("text='I understand'")
        if await button.is_visible(timeout=3000):
            await notify(chat_id, "✅ الضغط على زر 'I understand'...")
            await button.click()
        else:
            await notify(chat_id, "ℹ️ زر 'I understand' غير موجود — تخطي.")
    except:
        await notify(chat_id, "ℹ️ لم يظهر زر 'I understand' — تخطي.")
    await page.wait_for_load_state("networkidle")
    await notify(chat_id, "✅ [1/5] انتهت شاشة الترحيب بنجاح.")

async def step2_tos_and_country(page, chat_id):
    agree_btn = page.get_by_role("button", name="Agree and continue")
    try:
        await notify(chat_id, "2️⃣ [2/5] بحث عن زر 'Agree and continue'...")
        await agree_btn.wait_for(state="visible", timeout=10000)
        
        await notify(chat_id, "☑️ الضغط على مربع الموافقة الأول...")
        checkboxes = page.get_by_role("checkbox")
        await checkboxes.nth(0).click()
        await asyncio.sleep(1)
        
        await notify(chat_id, "☑️ الضغط على مربع الموافقة الثاني...")
        await checkboxes.nth(1).click()
        
        await notify(chat_id, "✅ الضغط على 'Agree and continue'...")
        await agree_btn.click()
        await page.wait_for_load_state("domcontentloaded")
        await notify(chat_id, "✅ [2/5] تمت الموافقة على الشروط.")
    except Exception:
        print("رسالة الشروط لم تظهر، تم التخطي تلقائياً.")
        await notify(chat_id, "ℹ️ [2/5] لم تظهر رسالة الشروط — تخطي تلقائي.")

async def step3_enable_api(page, project_id, authuser, chat_id):
    api_url = f"https://console.cloud.google.com/apis/library/run.googleapis.com?project={project_id}&authuser={authuser}"
    await notify(chat_id, f"3️⃣ [3/5] فتح صفحة Cloud Run API...\n📍 Project: `{project_id}`")
    await page.goto(api_url, wait_until="domcontentloaded")
    
    enable_btn = page.get_by_role("button", name="Enable")
    manage_btn = page.get_by_role("button", name="Manage")
    disable_btn = page.get_by_text("Disable API") 
    
    try:
        await notify(chat_id, "🔍 التحقق من حالة الـ API (Enable / Manage)...")
        await expect(enable_btn.or_(manage_btn)).to_be_visible(timeout=15000)
        
        if await enable_btn.is_visible():
            await notify(chat_id, "🔘 الـ API غير مفعّل — الضغط على 'Enable'...")
            await enable_btn.click()
            await notify(chat_id, "⏳ انتظار اكتمال التفعيل (حتى 60 ثانية)...")
            await expect(manage_btn.or_(disable_btn)).to_be_visible(timeout=60000)
            await notify(chat_id, "✅ [3/5] تم تفعيل Cloud Run API.")
        elif await manage_btn.is_visible():
            await notify(chat_id, "✅ [3/5] الـ API مفعّل مسبقاً — لا حاجة للتفعيل.")
    except Exception as e:
         raise Exception(f"عطل في إيجاد زر تفعيل الـ API: {str(e)}")

async def step4_create_cloud_run(page, project_id, authuser, chat_id):
    run_url = f"https://console.cloud.google.com/run/create?project={project_id}&authuser={authuser}"
    await notify(chat_id, "4️⃣ [4/5] فتح صفحة إنشاء خدمة Cloud Run...")
    await page.goto(run_url, wait_until="domcontentloaded")
    
    await notify(chat_id, "⏳ انتظار تحميل صفحة الإنشاء (5 ثوانٍ)...")
    await page.wait_for_timeout(5000)
    
    try:
        await notify(chat_id, "🖱️ اختيار حقل 'Container Image URL'...")
        label = page.get_by_text("Container Image URL").first
        await label.click()
        await page.wait_for_timeout(500)
        
        await notify(chat_id, "⌨️ كتابة رابط صورة Docker...")
        await page.keyboard.type("docker.io/ajndjd2/ahmed-vip1", delay=50)
    except Exception as e:
        raise Exception(f"فشل في الضغط وكتابة الرابط: {str(e)}")
    
    await notify(chat_id, "⏳ انتظار ظهور الخيارات (3 ثوانٍ)...")
    await page.wait_for_timeout(3000)
    
    try:
        await notify(chat_id, "🌐 اختيار 'Allow public access'...")
        await page.get_by_role("radio", name="Allow public access").click()
        await notify(chat_id, "⚙️ اختيار 'Instance-based'...")
        await page.get_by_role("radio", name="Instance-based").click()
        
        try:
            await page.get_by_role("button", name="Hide").click(timeout=2000)
            await notify(chat_id, "🙈 طي لوحة الإعدادات الإضافية...")
        except:
            pass
            
        await page.keyboard.press("End")
        await page.wait_for_timeout(1000)
        
        await notify(chat_id, "🚀 الضغط على 'Create' لبدء النشر...")
        create_btn = page.get_by_role("button", name="Create")
        await create_btn.click(force=True)
        await notify(chat_id, "✅ [4/5] تم إرسال طلب إنشاء الخدمة.")
    except Exception as e:
        raise Exception(f"فشل في اختيار الإعدادات أو ضغط Create: {str(e)}")

async def step5_get_deployed_url(page, chat_id):
    await notify(chat_id, "5️⃣ [5/5] انتظار ظهور رابط الخدمة (حتى دقيقتين)...")
    link_locator = page.locator('a[href*="run.app"]')
    await link_locator.wait_for(state="visible", timeout=120000) 
    final_url = await link_locator.get_attribute("href")
    await notify(chat_id, f"✅ [5/5] تم استخراج الرابط:\n`{final_url}`")
    return final_url

# ==========================================
# 🔔 المعالج الرئيسي
# ==========================================
async def process_sso_link(chat_id, sso_url):
    project_id = extract_project_id(sso_url)
    if not project_id:
        await client.send_message(chat_id, "❌ لم يتم العثور على Project ID في الرابط.")
        return

    await notify(chat_id, f"🎯 تم استخراج Project ID:\n`{project_id}`")
    await notify(chat_id, "⏳ 𝙡𝙚𝙩 𝙢𝙚 𝙨𝙚𝙚 𝙬𝙝𝙖𝙩 𝙄 𝙘𝙖𝙣 𝙙𝙤...")

    temp_dir = tempfile.mkdtemp()
    page = None

    async with async_playwright() as p:
        try:
            await notify(chat_id, "🌐 إطلاق متصفح Chromium (headless) مع إعدادات الحماية...")
            
            args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-infobars",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-sync",
                "--disable-translate",
                "--disable-default-apps",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--mute-audio",
                "--hide-scrollbars",
                "--metrics-recording-only",
                "--safebrowsing-disable-auto-update",
                "--renderer-process-limit=1",
                "--js-flags=--max-old-space-size=256",
                "--window-size=1920,1080",
                f"--user-agent={USER_AGENT}",
            ]

            context = await p.chromium.launch_persistent_context(
                user_data_dir=temp_dir,
                headless=True,
                args=args,
                viewport={"width": 1920, "height": 1080},
                user_agent=USER_AGENT,
                locale="en-US",
                timezone_id="America/New_York",
                color_scheme="light",
                java_script_enabled=True,
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                },
            )
            
            await context.add_init_script(STEALTH_JS)
            context.set_default_timeout(60000)
            context.set_default_navigation_timeout(60000)

            page = context.pages[0] if context.pages else await context.new_page()
            await notify(chat_id, "✅ المتصفح جاهز ومموه بالكامل.")
            
            await notify(chat_id, "🔗 فتح رابط SSO...")
            await page.goto(sso_url, wait_until="domcontentloaded", timeout=60000)
            await notify(chat_id, "✅ تم تحميل صفحة SSO.")
            
            await step1_welcome_screen(page, chat_id)
            
            await notify(chat_id, "⏳ 𝙩𝙖𝙠𝙞𝙣𝙜 𝙖 𝙘𝙞𝙜𝙖𝙧𝙚𝙩𝙩𝙚 𝙛𝙞𝙧𝙨𝙩...")
            await notify(chat_id, "⏳ انتظار الوصول إلى لوحة التحكم (dashboard)...")
            await page.wait_for_url("**/home/dashboard**", timeout=45000)
            await notify(chat_id, "✅ وصلنا إلى لوحة التحكم.")
            
            current_qs = parse_qs(urlparse(page.url).query)
            authuser = current_qs.get('authuser', ['1'])[0]
            await notify(chat_id, f"🔑 authuser = `{authuser}`")
            
            await step2_tos_and_country(page, chat_id)
            await step3_enable_api(page, project_id, authuser, chat_id)
            await step4_create_cloud_run(page, project_id, authuser, chat_id)
            
            await notify(chat_id, "⏳ 𝙬𝙖𝙞𝙩, 𝙟𝙪𝙨𝙩 𝙤𝙣𝙚 𝙘𝙞𝙜𝙖𝙧𝙚𝙩𝙩𝙚...")
            final_url = await step5_get_deployed_url(page, chat_id)        
            domain = extract_domain_from_service_url(final_url)
            
            await notify(chat_id, f"✅ **𝙃𝙚𝙧𝙚 𝙮𝙤𝙪 𝙜𝙤 𝙗𝙧𝙤**\n\n 𝙙𝙤𝙢𝙖𝙞𝙣 :\n {domain}")
            
            await notify(chat_id, "📤 إرسال رابط VLESS...")
            vless_result = VLESS_TEMPLATE.format(domain=domain)
            await client.send_message(
                chat_id, 
                f"🔗 <pre><code class=\"language-java\">{vless_result}</code></pre>", 
                parse_mode='html'
            )
            
            await notify(chat_id, "📤 إرسال ملف JSON...")
            json_result = JSON_TEMPLATE.replace("__DOMAIN__", domain)
            await client.send_message(
                chat_id, 
                f"📄<pre><code class=\"language-json\">{json_result}</code></pre>", 
                parse_mode='html'
            )
            
            await notify(chat_id, "📤 إرسال ملف DarkTunnel...")
            await generate_and_send_dark_file(chat_id, domain)
            
            await notify(chat_id, "🎉 اكتملت جميع الخطوات بنجاح!")
            
        except PlaywrightTimeoutError as e:
            await handle_error(page, chat_id, "انتهى وقت الانتظار (Timeout)", str(e))
        except Exception as e:
            await handle_error(page, chat_id, "خطأ عام", str(e))
        finally:
            if 'context' in locals():
                await context.close()
            shutil.rmtree(temp_dir, ignore_errors=True)


# ==========================================
@client.on(events.NewMessage(pattern=r"^/start$"))
async def start(event):
    welcome_msg = (
        "**إذا غامَرْتَ في شَرَفٍ مَرُومِ  ***  فَلا تَقنَعْ بما دونَ النّجومِ** ☁️✨\n\n"
        "⏳ **الوقت:** 4 ساعات و 30 دقيقة (4:30 hours)\n"
        "🔗 **الرابط:**\n"
        "https://www.cloudskillsboost.google/focuses/20774?parent=catalog\n\n"
        "⏳ **الوقت:** 3 ساعات (3:00 hours)\n"
        "🔗 **الرابط:**\n"
        "https://www.skills.google/focuses/82384?parent=catalog\n\n"
        "@AM2_D3"
    )
    await event.reply(welcome_msg)

# ==========================================
@client.on(events.NewMessage(pattern=r'https://www\.skills\.google/google_sso.*'))
async def handler(event):
    sso_url = event.text
    asyncio.create_task(process_sso_link(event.chat_id, sso_url))

print("𝙘𝙤𝙣𝙣𝙚𝙘𝙩𝙚𝙙...")
client.run_until_disconnected()
