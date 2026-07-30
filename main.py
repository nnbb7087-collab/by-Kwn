import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app.mount("/downloads", StaticFiles(directory=DOWNLOAD_DIR), name="downloads")

html_content = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>فيديو تنزيل - by Kwn</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl text-center">
        
        <!-- عنوان الموقع -->
        <div class="mb-3">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-red-600/20 text-red-400 rounded-2xl mb-2 text-2xl font-bold">🎬</div>
            <h1 class="text-2xl font-bold text-white">فيديو تنزيل</h1>
        </div>

        <!-- اسمك لوحده في المنتصف -->
        <div class="mb-6">
            <span class="inline-block px-5 py-1.5 bg-red-600/10 border border-red-500/30 text-red-400 text-sm font-bold rounded-full tracking-wider uppercase shadow-inner">
                by Kwn
            </span>
        </div>

        <p class="text-slate-400 text-xs mb-6">حمل مقاطعك من جميع البرامج بدون علامة مائية (تيك توك، سناب، إنستا، تويتر...)</p>

        <form action="/download" method="POST" class="space-y-4 text-right">
            <div>
                <input type="url" name="url" placeholder="الصق الرابط هنا..." required
                    class="w-full px-4 py-3.5 bg-slate-800 border border-slate-700 rounded-2xl focus:outline-none focus:border-red-500 text-white placeholder-slate-500 text-sm text-right">
            </div>
            <button type="submit" 
                class="w-full py-3.5 bg-red-600 hover:bg-red-500 text-white font-medium rounded-2xl transition duration-200 shadow-lg shadow-red-600/30 text-sm">
                تحميل المقطع الآن 📥
            </button>
        </form>

        {% if message %}
            <div class="mt-4 p-3 bg-slate-800 border border-slate-700 rounded-xl text-center text-sm text-emerald-400">
                {{ message | safe }}
            </div>
        {% endif %}
        
        {% if error %}
            <div class="mt-4 p-3 bg-slate-800 border border-slate-700 rounded-xl text-center text-sm text-rose-400">
                {{ error }}
            </div>
        {% endif %}

        <div class="text-center mt-6 text-xs text-slate-500 border-t border-slate-800 pt-4">
            جميع الحقوق محفوظة © 2026
        </div>
    </div>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
  return HTMLResponse(
      content=html_content.replace("{% if message %}", "")
      .replace("{% endif %}", "")
      .replace("{% if error %}", "")
      .replace("{% endif %}", "")
  )


@app.post("/download", response_class=HTMLResponse)
async def download_media(url: str = Form(...)):
  try:
    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "format": "best",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      filename = ydl.prepare_filename(info)
      file_url = f"/{filename}"

    success_msg = f'✅ تم التحميل بنجاح! <br><a href="{file_url}" download class="text-red-400 underline font-bold mt-2 inline-block">اضغط هنا لحفظ المقطع بجوالك</a>'

    rendered = (
        html_content.replace("{% if message %}", "")
        .replace("{% endif %}", "")
        .replace("{{ message | safe }}", success_msg)
        .replace("{% if error %}", "<!--")
        .replace("{% endif %}", "-->")
    )
    return HTMLResponse(content=rendered)

  except Exception as e:
    error_msg = "❌ حدث خطأ، تأكد من صحة الرابط أو حماية المنصة"
    rendered = (
        html_content.replace("{% if error %}", "")
        .replace("{% endif %}", "")
        .replace("{{ error }}", error_msg)
        .replace("{% if message %}", "<!--")
        .replace("{% endif %}", "-->")
    )
    return HTMLResponse(content=rendered)
