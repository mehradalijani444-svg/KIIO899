import os,json,secrets,html
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from http.server import BaseHTTPRequestHandler,HTTPServer
PORT=int(os.getenv("PORT","8080")); PASS=os.getenv("ADMIN_PASSWORD","change-this-password"); TG=os.getenv("TELEGRAM_URL","https://t.me/KIIOVPN"); DATA=Path(os.getenv("DATA_DIR","/data"))/"subs.json"
def read():
 try:return json.loads(DATA.read_text())
 except:return {}
def write(d):
 DATA.parent.mkdir(parents=True,exist_ok=True); DATA.write_text(json.dumps(d,ensure_ascii=False))
def page(title,body):
 css="""*{box-sizing:border-box}body{margin:0;background:#080a0e;color:#f4f7fb;font-family:Tahoma,Arial}.wrap{max-width:740px;margin:auto;padding:24px 16px}.brand{display:flex;align-items:center;gap:12px;margin:12px 0 24px}.logo{width:52px;height:52px;border-radius:16px;background:#111923;border:1px solid #2c4c48;display:grid;place-items:center;color:#a6f5dc;font-size:25px}.muted{color:#9aa5b4;font-size:13px;line-height:1.8}.card{background:#10141b;border:1px solid #252d38;border-radius:18px;padding:20px;margin:14px 0}h1{font-size:22px;margin:0}h2{font-size:17px}.row{padding:12px 0;border-bottom:1px solid #242a33;display:flex;justify-content:space-between;gap:10px}a,button{color:#07110e;background:#a6f5dc;text-decoration:none;border:0;border-radius:12px;padding:13px 16px;font-weight:bold;display:inline-block;cursor:pointer}input{width:100%;padding:13px;background:#090c11;color:white;border:1px solid #303946;border-radius:10px;margin:8px 0 14px}.pill{color:#a6f5dc;background:#142722;border-radius:99px;padding:6px 10px;font-size:12px}code{word-break:break-all;color:#a6f5dc}.notice{padding:12px;background:#201b12;color:#f5d9a6;border-radius:10px;font-size:13px;line-height:1.8}.footer{text-align:center;color:#7f8997;font-size:12px;margin-top:28px}"""
 return "<!doctype html><html lang='fa' dir='rtl'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>"+html.escape(title)+"</title><style>"+css+"</style><main class='wrap'>"+body+"</main></html>"
def brand():return "<header class='brand'><div class='logo'>K</div><div><h1>KIIO PANEL</h1><div class='muted'>KIIO VPN · Subscription Portal</div></div></header>"
class H(BaseHTTPRequestHandler):
 def out(self,s,status=200):
  b=s.encode();self.send_response(status);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path)
  if u.path=="/health":self.send_response(200);self.end_headers();self.wfile.write(b"ok");return
  if u.path=="/":self.out(page("KIIO Panel",brand()+"<section class='card'><span class='pill'>WELCOME</span><h2>به KIIO VPN خوش آمدید</h2><p class='muted'>درگاه اشتراک KIIO با ظاهر مشکی و سازگار با موبایل.</p><a href='"+html.escape(TG,quote=True)+"'>پشتیبانی تلگرام</a> <a href='/admin'>ورود مدیریت</a></section><div class='footer'>KIIO PANEL</div>"));return
  if u.path=="/admin":self.out(page("ورود مدیریت",brand()+"<section class='card'><h2>ورود مدیریت</h2><form method='post'><input type='password' name='password' placeholder='رمز مدیریت' required><button>ورود</button></form><p class='muted'>رمز را در متغیر ADMIN_PASSWORD تعیین کنید.</p></section>"));return
  if u.path=="/dashboard":
   token=parse_qs(u.query).get("s",[""])[0]
   if not secrets.compare_digest(token,PASS):self.out(page("خطا","دسترسی غیرمجاز"),403);return
   d=read();rows="".join("<div class='row'>"+html.escape(v["name"])+" <code>/sub/"+k+"</code></div>" for k,v in d.items()) or "<p class='muted'>هنوز اشتراکی نساخته‌اید.</p>"
   self.out(page("KIIO Dashboard",brand()+"<section class='card'><h2>مدیریت اشتراک‌ها</h2><form method='post' action='/create?s="+html.escape(token,quote=True)+"'><input name='name' value='KIIO VPN' required><button>ساخت لینک اشتراک</button></form>"+rows+"<p class='notice'>این نسخه فقط نمونه‌ی اولیه است؛ لینک‌ها هنوز کانفیگ واقعی Xray تولید نمی‌کنند.</p><a href='"+html.escape(TG,quote=True)+"'>پشتیبانی</a></section>"));return
  if u.path.startswith("/sub/"):
   k=u.path.split("/",2)[2];d=read()
   if k not in d:self.out(page("یافت نشد",brand()+"<section class='card'>اشتراک پیدا نشد.</section>"),404);return
   self.out(page("KIIO VPN",brand()+"<section class='card'><span class='pill'>SUBSCRIPTION</span><h2>"+html.escape(d[k]["name"])+"</h2><div class='row'>برند <b>KIIO VPN</b></div><div class='row'>وضعیت <span class='pill'>نسخه اولیه</span></div><p class='muted'>برای حجم، انقضا و کانفیگ واقعی باید هسته Xray متصل شود.</p><a href='"+html.escape(TG,quote=True)+"'>پشتیبانی تلگرام</a></section>"));return
  self.out(page("404","صفحه پیدا نشد"),404)
 def do_POST(self):
  u=urlparse(self.path);n=int(self.headers.get("Content-Length","0"));f=parse_qs(self.rfile.read(n).decode())
  if u.path=="/admin":
   if secrets.compare_digest(f.get("password",[""])[0],PASS):
    self.send_response(303);self.send_header("Location","/dashboard?s="+PASS);self.end_headers()
   else:self.out(page("خطا","رمز اشتباه است"),401)
   return
  if u.path=="/create":
   s=parse_qs(u.query).get("s",[""])[0]
   if not secrets.compare_digest(s,PASS):self.out(page("خطا","دسترسی غیرمجاز"),403);return
   d=read();k=secrets.token_urlsafe(18);d[k]={"name":f.get("name",["KIIO VPN"])[0][:80]};write(d)
   self.out(page("ساخته شد",brand()+"<section class='card'><h2>لینک ساخته شد</h2><code>/sub/"+k+"</code><p class='muted'>دامنه Railway را قبل از این مسیر قرار دهید.</p><a href='/dashboard?s="+html.escape(s,quote=True)+"'>بازگشت</a></section>"));return
  self.out(page("404","یافت نشد"),404)
 def log_message(self,*args):pass
HTTPServer(("0.0.0.0",PORT),H).serve_forever()
