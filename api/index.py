"""
TRADEFLOW AI — FULL STACK v3.0
FastAPI + Frontend HTML intégré + Claude + PDF
"""

import anthropic
import json
import datetime
import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

ANTHROPIC_KEY   = os.getenv("ANTHROPIC_API_KEY", "")
TWILIO_SID      = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM     = os.getenv("TWILIO_FROM_NUMBER", "")
RESEND_KEY      = os.getenv("RESEND_API_KEY", "")
MAKE_WEBHOOK    = os.getenv("MAKE_WEBHOOK_URL", "")
ARTISAN_PHONE   = os.getenv("ARTISAN_PHONE", "")
ARTISAN_EMAIL   = os.getenv("ARTISAN_EMAIL", "")
ARTISAN_NAME    = os.getenv("ARTISAN_NAME", "Votre Entreprise")
ARTISAN_SIRET   = os.getenv("ARTISAN_SIRET", "123 456 789 00010")
ARTISAN_TVA     = os.getenv("ARTISAN_TVA_INTRA", "FR12345678900")
ARTISAN_ADDRESS = os.getenv("ARTISAN_ADDRESS", "Paris, France")

claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

app = FastAPI(title="TradeFlow AI", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ═════════════════════════════════════════════════
# HTML FRONTEND
# ═════════════════════════════════════════════════

HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TradeFlow AI — L'assistant des artisans</title>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a08;--s1:#121210;--s2:#1a1a17;--s3:#222220;
  --border:rgba(255,255,255,0.07);--border2:rgba(255,255,255,0.13);
  --amber:#f5a623;--amber-d:rgba(245,166,35,0.10);--amber-g:rgba(245,166,35,0.22);
  --green:#4ade80;--green-d:rgba(74,222,128,0.10);
  --red:#f87171;--red-d:rgba(248,113,113,0.10);
  --blue:#60a5fa;--blue-d:rgba(96,165,250,0.10);
  --text:#f0ede8;--text-m:rgba(240,237,232,0.6);--text-d:rgba(240,237,232,0.3);
  --font:'Bricolage Grotesque',sans-serif;--mono:'JetBrains Mono',monospace;
}
html{background:var(--bg);color:var(--text);font-family:var(--font);scroll-behavior:smooth}
body{
  min-height:100vh;
  background:
    radial-gradient(ellipse 80% 50% at 15% -10%,rgba(245,166,35,0.07) 0%,transparent 60%),
    radial-gradient(ellipse 60% 40% at 85% 110%,rgba(245,166,35,0.04) 0%,transparent 50%),
    var(--bg);
}

/* NAV */
nav{
  position:fixed;top:0;left:0;right:0;z-index:100;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 48px;height:64px;
  background:rgba(10,10,8,0.8);backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
}
.logo{display:flex;align-items:center;gap:10px;font-size:18px;font-weight:800;letter-spacing:-0.5px;cursor:pointer}
.logo-icon{width:32px;height:32px;background:var(--amber);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px}
.logo em{color:var(--amber);font-style:normal}
.nav-r{display:flex;align-items:center;gap:8px}
.nav-link{padding:8px 16px;border-radius:8px;font-size:14px;font-weight:500;color:var(--text-m);cursor:pointer;transition:all .15s;border:none;background:none;font-family:var(--font)}
.nav-link:hover{color:var(--text);background:var(--s2)}
.nav-cta{padding:9px 20px;background:var(--amber);color:#000;border:none;border-radius:8px;font-family:var(--font);font-size:14px;font-weight:700;cursor:pointer;transition:all .15s}
.nav-cta:hover{opacity:.9;transform:translateY(-1px)}

/* PAGES */
.page{display:none;min-height:100vh;padding-top:64px}
.page.active{display:block}

/* ─── LANDING ─── */
.hero{
  max-width:1100px;margin:0 auto;
  padding:96px 48px 80px;
  display:grid;grid-template-columns:1fr 460px;gap:80px;align-items:center;
}
.hero-badge{
  display:inline-flex;align-items:center;gap:8px;
  padding:5px 14px;background:var(--amber-d);border:1px solid rgba(245,166,35,0.22);
  border-radius:100px;margin-bottom:24px;
  font-size:11px;font-weight:600;color:var(--amber);font-family:var(--mono);letter-spacing:.5px;
}
.dot{width:6px;height:6px;border-radius:50%;background:var(--amber);animation:blink 2s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
h1{font-size:clamp(34px,4.2vw,54px);font-weight:800;letter-spacing:-2.5px;line-height:1.06;margin-bottom:20px}
h1 em{font-style:normal;color:var(--amber)}
.hero p{font-size:17px;color:var(--text-m);line-height:1.65;margin-bottom:36px;max-width:460px}
.hero-btns{display:flex;gap:12px;flex-wrap:wrap}
.btn-p{padding:14px 28px;background:var(--amber);color:#000;border:none;border-radius:10px;font-family:var(--font);font-size:15px;font-weight:700;cursor:pointer;transition:all .15s}
.btn-p:hover{opacity:.9;transform:translateY(-2px);box-shadow:0 8px 25px rgba(245,166,35,.3)}
.btn-s{padding:14px 28px;background:var(--s2);color:var(--text);border:1px solid var(--border2);border-radius:10px;font-family:var(--font);font-size:15px;font-weight:600;cursor:pointer;transition:all .15s}
.btn-s:hover{background:var(--s3)}
.hero-stats{display:flex;gap:32px;margin-top:48px;padding-top:32px;border-top:1px solid var(--border)}
.stat-v{font-size:28px;font-weight:800;letter-spacing:-1px;color:var(--amber)}
.stat-l{font-size:13px;color:var(--text-d);margin-top:2px}

/* DEMO CARD */
.demo-card{background:var(--s1);border:1px solid var(--border2);border-radius:20px;overflow:hidden;box-shadow:0 40px 80px rgba(0,0,0,.6)}
.demo-hdr{padding:14px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:7px;background:var(--s2)}
.dd{width:10px;height:10px;border-radius:50%}
.demo-call{padding:18px;border-bottom:1px solid var(--border)}
.call-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.live-badge{display:flex;align-items:center;gap:5px;padding:4px 10px;background:var(--green-d);border:1px solid rgba(74,222,128,.2);border-radius:100px;font-size:11px;font-weight:600;color:var(--green);font-family:var(--mono)}
.waves{display:flex;align-items:center;gap:3px;height:34px;padding:0 14px;background:var(--s2);border-radius:10px}
.wb{width:3px;border-radius:2px;background:var(--amber);animation:wave 1.2s ease-in-out infinite}
.wb:nth-child(1){height:8px;animation-delay:0s}.wb:nth-child(2){height:20px;animation-delay:.1s}
.wb:nth-child(3){height:13px;animation-delay:.2s}.wb:nth-child(4){height:24px;animation-delay:.3s}
.wb:nth-child(5){height:16px;animation-delay:.4s}.wb:nth-child(6){height:20px;animation-delay:.5s}
.wb:nth-child(7){height:10px;animation-delay:.6s}.wb:nth-child(8){height:18px;animation-delay:.7s}
@keyframes wave{0%,100%{transform:scaleY(1);opacity:.7}50%{transform:scaleY(.4);opacity:1}}
.msgs{margin-top:12px;display:flex;flex-direction:column;gap:8px}
.msg{padding:8px 12px;border-radius:10px;font-size:12px;line-height:1.45;max-width:85%}
.msg-ai{background:var(--amber-d);border:1px solid rgba(245,166,35,.15);align-self:flex-start}
.msg-cl{background:var(--s3);color:var(--text-m);align-self:flex-end}
.demo-acts{padding:14px 18px;display:flex;flex-direction:column;gap:7px}
.act-row{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:10px;background:var(--s2);border:1px solid var(--border);font-size:13px}
.act-ico{width:28px;height:28px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.ic-a{background:var(--amber-d)}.ic-g{background:var(--green-d)}.ic-b{background:var(--blue-d)}
.act-ttl{font-weight:600;font-size:13px}.act-sub{font-size:11px;color:var(--text-d);font-family:var(--mono)}
.ck{color:var(--green);font-weight:700;margin-left:auto}

/* FEATURES */
.section{max-width:1100px;margin:0 auto;padding:80px 48px}
.sec-lbl{font-size:11px;font-family:var(--mono);letter-spacing:2px;text-transform:uppercase;color:var(--amber);margin-bottom:14px}
.sec-ttl{font-size:clamp(26px,3vw,38px);font-weight:800;letter-spacing:-1.5px;line-height:1.1;margin-bottom:48px}
.feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.feat-card{background:var(--s1);border:1px solid var(--border);border-radius:16px;padding:26px;transition:all .2s}
.feat-card:hover{border-color:rgba(245,166,35,.2);transform:translateY(-3px)}
.feat-ico{width:42px;height:42px;border-radius:11px;background:var(--amber-d);border:1px solid rgba(245,166,35,.2);display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:14px}
.feat-ttl{font-size:15px;font-weight:700;margin-bottom:7px}
.feat-desc{font-size:13px;color:var(--text-m);line-height:1.6}

/* DEVIS DEMO */
.devis-demo{max-width:1100px;margin:0 auto;padding:0 48px 80px}
.devis-box{background:var(--s1);border:1px solid var(--border2);border-radius:20px;overflow:hidden}
.devis-hdr{padding:20px 28px;background:var(--s2);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.devis-hdr h3{font-size:16px;font-weight:700}
.devis-body{display:grid;grid-template-columns:1fr 1fr;gap:0}
.devis-left{padding:28px;border-right:1px solid var(--border)}
.devis-right{padding:28px}
.flabel{font-size:11px;font-family:var(--mono);letter-spacing:1px;color:var(--text-d);margin-bottom:6px;display:block}
.finput{width:100%;padding:11px 14px;background:var(--s2);border:1px solid var(--border2);border-radius:9px;color:var(--text);font-family:var(--font);font-size:14px;outline:none;transition:border-color .2s;margin-bottom:14px}
.finput:focus{border-color:var(--amber)}
.finput::placeholder{color:var(--text-d)}
textarea.finput{resize:vertical;min-height:80px}
.result-box{background:var(--s2);border-radius:12px;padding:20px;min-height:200px}
.result-loading{display:flex;flex-direction:column;align-items:center;justify-content:center;height:180px;color:var(--text-d)}
.spin{width:32px;height:32px;border:2px solid var(--border2);border-top-color:var(--amber);border-radius:50%;animation:spin .8s linear infinite;margin-bottom:12px}
@keyframes spin{to{transform:rotate(360deg)}}
.result-item{padding:10px 0;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;font-size:13px}
.result-item:last-child{border:none}
.result-total{display:flex;justify-content:space-between;padding:12px 0 0;font-size:18px;font-weight:800;color:var(--amber)}

/* PRICING */
.plans{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:48px}
.plan{background:var(--s1);border:1px solid var(--border);border-radius:18px;padding:30px;position:relative;transition:all .2s}
.plan:hover{transform:translateY(-4px)}
.plan.feat{border-color:rgba(245,166,35,.3);background:linear-gradient(135deg,#16140c 0%,var(--s1) 100%)}
.plan-badge{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--amber);color:#000;padding:4px 16px;border-radius:100px;font-size:10px;font-weight:800;letter-spacing:.5px;white-space:nowrap}
.plan-name{font-size:11px;font-family:var(--mono);letter-spacing:2px;text-transform:uppercase;color:var(--text-d);margin-bottom:14px}
.plan-price{font-size:46px;font-weight:800;letter-spacing:-2px;line-height:1;margin-bottom:4px}
.plan.feat .plan-price{color:var(--amber)}
.plan-period{font-size:13px;color:var(--text-d);margin-bottom:22px}
.plan-feats{list-style:none;margin-bottom:24px}
.plan-feats li{display:flex;gap:9px;align-items:flex-start;padding:7px 0;border-bottom:1px solid var(--border);font-size:13px;color:var(--text-m)}
.plan-feats li:last-child{border:none}
.plan-feats li::before{content:'✓';color:var(--amber);font-weight:700;flex-shrink:0}
.plan-btn{display:block;width:100%;padding:12px;border:none;border-radius:9px;font-family:var(--font);font-size:14px;font-weight:700;cursor:pointer;transition:all .15s;text-align:center}
.plan.feat .plan-btn{background:var(--amber);color:#000}
.plan:not(.feat) .plan-btn{background:var(--s2);color:var(--text);border:1px solid var(--border2)}
.plan:not(.feat) .plan-btn:hover{background:var(--s3)}
.plan.feat .plan-btn:hover{opacity:.9}

/* FOOTER */
footer{background:var(--s1);border-top:1px solid var(--border);padding:40px 48px;display:flex;align-items:center;justify-content:space-between;margin-top:40px}
.footer-logo{font-size:16px;font-weight:800;letter-spacing:-.5px}
.footer-logo em{color:var(--amber);font-style:normal}
.footer-links{display:flex;gap:24px}
.footer-link{font-size:13px;color:var(--text-d);cursor:pointer;transition:color .15s}
.footer-link:hover{color:var(--text)}
.footer-copy{font-size:12px;color:var(--text-d);font-family:var(--mono)}

/* ─── ONBOARDING ─── */
#page-onboard{display:none;align-items:center;justify-content:center;min-height:100vh;padding:100px 20px 40px}
#page-onboard.active{display:flex}
.ob-card{width:100%;max-width:500px;background:var(--s1);border:1px solid var(--border2);border-radius:22px;overflow:hidden}
.ob-prog{height:3px;background:var(--s3)}
.ob-bar{height:100%;background:var(--amber);transition:width .4s ease}
.ob-body{padding:38px}
.ob-step{display:none}.ob-step.active{display:block}
.step-n{font-size:11px;font-family:var(--mono);color:var(--amber);letter-spacing:1px;margin-bottom:8px}
.ob-body h2{font-size:24px;font-weight:800;letter-spacing:-1px;margin-bottom:8px}
.ob-body p{font-size:14px;color:var(--text-m);margin-bottom:26px;line-height:1.6}
.type-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-bottom:22px}
.type-opt{padding:14px;border-radius:11px;border:1px solid var(--border2);background:var(--s2);cursor:pointer;transition:all .15s;text-align:center}
.type-opt:hover{border-color:rgba(245,166,35,.3)}
.type-opt.sel{border-color:var(--amber);background:var(--amber-d)}
.type-em{font-size:26px;margin-bottom:5px}
.type-nm{font-size:12px;font-weight:600}
.lang-grid{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:22px}
.lang-opt{padding:7px 14px;border-radius:8px;border:1px solid var(--border2);background:var(--s2);cursor:pointer;font-size:12px;font-weight:600;transition:all .15s}
.lang-opt:hover{border-color:rgba(245,166,35,.3)}
.lang-opt.sel{border-color:var(--amber);background:var(--amber-d);color:var(--amber)}
.ob-acts{display:flex;gap:9px;margin-top:22px}
.btn-next{flex:1;padding:12px;background:var(--amber);color:#000;border:none;border-radius:9px;font-family:var(--font);font-size:14px;font-weight:700;cursor:pointer;transition:all .15s}
.btn-next:hover{opacity:.9}
.btn-back{padding:12px 18px;background:var(--s2);color:var(--text-m);border:1px solid var(--border);border-radius:9px;font-family:var(--font);font-size:14px;font-weight:600;cursor:pointer;transition:all .15s}
.btn-back:hover{background:var(--s3)}

/* ─── DASHBOARD ─── */
#page-dash{display:none;padding-top:64px}
#page-dash.active{display:block}
.dash-layout{display:grid;grid-template-columns:220px 1fr;min-height:calc(100vh - 64px)}
.sidebar{background:var(--s1);border-right:1px solid var(--border);padding:20px 14px;position:sticky;top:64px;height:calc(100vh - 64px);overflow-y:auto}
.sb-lbl{font-size:10px;font-family:var(--mono);letter-spacing:2px;text-transform:uppercase;color:var(--text-d);padding:0 10px;margin-bottom:5px;margin-top:16px}
.sb-item{display:flex;align-items:center;gap:9px;padding:9px 10px;border-radius:9px;font-size:13px;font-weight:500;color:var(--text-m);cursor:pointer;transition:all .15s;margin-bottom:1px}
.sb-item:hover{background:var(--s2);color:var(--text)}
.sb-item.active{background:var(--amber-d);color:var(--amber)}
.main{padding:28px}
.pg-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px}
.pg-ttl{font-size:22px;font-weight:800;letter-spacing:-.8px}
.pg-sub{font-size:13px;color:var(--text-d);margin-top:2px}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}
.mc{background:var(--s1);border:1px solid var(--border);border-radius:14px;padding:18px;position:relative;overflow:hidden;transition:all .2s}
.mc:hover{border-color:var(--border2);transform:translateY(-2px)}
.mc::after{content:'';position:absolute;top:0;left:0;right:0;height:2px}
.mc.a::after{background:var(--amber)}.mc.g::after{background:var(--green)}
.mc.b::after{background:var(--blue)}.mc.r::after{background:var(--red)}
.mc-lbl{font-size:10px;font-family:var(--mono);letter-spacing:1px;text-transform:uppercase;color:var(--text-d);margin-bottom:9px}
.mc-val{font-size:30px;font-weight:800;letter-spacing:-1.5px;line-height:1;margin-bottom:5px}
.mc.a .mc-val{color:var(--amber)}.mc.g .mc-val{color:var(--green)}
.mc.b .mc-val{color:var(--blue)}.mc.r .mc-val{color:var(--red)}
.mc-chg{display:inline-flex;align-items:center;gap:3px;font-size:11px;font-family:var(--mono);padding:2px 7px;border-radius:100px}
.up{background:var(--green-d);color:var(--green)}.dn{background:var(--red-d);color:var(--red)}
.two{display:grid;grid-template-columns:1fr 300px;gap:14px;margin-bottom:20px}
.panel{background:var(--s1);border:1px solid var(--border);border-radius:14px;overflow:hidden}
.panel-hdr{padding:16px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.panel-ttl{font-size:13px;font-weight:700;letter-spacing:-.3px}
.panel-act{font-size:12px;color:var(--amber);cursor:pointer;font-weight:600;background:none;border:none;font-family:var(--font)}
.call-item{display:grid;grid-template-columns:36px 1fr auto;gap:10px;align-items:center;padding:11px 18px;border-bottom:1px solid var(--border);cursor:pointer;transition:background .1s}
.call-item:hover{background:rgba(255,255,255,.02)}
.call-item:last-child{border:none}
.call-av{width:34px;height:34px;border-radius:9px;background:var(--s3);display:flex;align-items:center;justify-content:center;font-size:14px}
.call-nm{font-size:13px;font-weight:600;margin-bottom:2px}
.call-ds{font-size:11px;color:var(--text-d);font-family:var(--mono)}
.call-tm{font-size:11px;color:var(--text-d);font-family:var(--mono);text-align:right}
.status{display:inline-block;padding:2px 7px;border-radius:5px;font-size:9px;font-weight:700;font-family:var(--mono);letter-spacing:.5px;margin-top:3px}
.st-ok{background:var(--green-d);color:var(--green)}.st-pend{background:var(--amber-d);color:var(--amber)}.st-miss{background:var(--red-d);color:var(--red)}
.qa{padding:14px;display:flex;flex-direction:column;gap:7px}
.qa-item{display:flex;align-items:center;gap:10px;padding:11px 12px;border-radius:10px;background:var(--s2);border:1px solid var(--border);cursor:pointer;transition:all .15s}
.qa-item:hover{border-color:rgba(245,166,35,.2);background:var(--s3)}
.qa-ico{width:34px;height:34px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0}
.qa-ttl{font-size:13px;font-weight:600}.qa-sub{font-size:11px;color:var(--text-d)}
.qa-arr{margin-left:auto;color:var(--text-d);font-size:16px}

/* DASH TABS */
.dash-tab{display:none}.dash-tab.active{display:block}

/* VOICE */
.voice-box{background:var(--s1);border:1px solid var(--border);border-radius:14px;padding:24px}
.voice-stat{display:flex;align-items:center;gap:10px;padding:14px;border-radius:10px;background:var(--s2);margin-bottom:18px}
.v-ind{width:40px;height:40px;border-radius:50%;background:var(--green-d);border:2px solid var(--green);display:flex;align-items:center;justify-content:center;font-size:18px;position:relative}
.v-pulse{position:absolute;inset:-5px;border-radius:50%;border:2px solid var(--green);opacity:.3;animation:pulse 2s infinite}
@keyframes pulse{0%{transform:scale(1);opacity:.3}100%{transform:scale(1.5);opacity:0}}
.tbox{background:var(--s2);border-radius:10px;padding:14px;min-height:180px;display:flex;flex-direction:column;gap:9px;margin-bottom:14px;overflow-y:auto;max-height:240px}
.tm{padding:9px 12px;border-radius:9px;max-width:85%;font-size:12px;line-height:1.5}
.tm-ai{background:var(--amber-d);border-left:2px solid var(--amber);align-self:flex-start}
.tm-cl{background:var(--s3);border-left:2px solid var(--border2);color:var(--text-m);align-self:flex-end}
.tm-lbl{font-size:9px;font-family:var(--mono);letter-spacing:1px;margin-bottom:3px;font-weight:600}
.tm-ai .tm-lbl{color:var(--amber)}.tm-cl .tm-lbl{color:var(--text-d)}
.call-res{padding:12px 14px;border-radius:10px;background:var(--green-d);border:1px solid rgba(74,222,128,.2);display:flex;align-items:center;gap:10px}
.cr-txt{font-size:12px;color:var(--green)}.cr-txt strong{display:block;font-size:13px;margin-bottom:2px}

/* DEVIS FORM */
.dform{background:var(--s1);border:1px solid var(--border);border-radius:14px;padding:24px;margin-bottom:16px}
.dform h3{font-size:15px;font-weight:700;margin-bottom:18px}
.frow{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.items-tbl{width:100%;border-collapse:collapse;margin:16px 0}
.items-tbl th{text-align:left;font-size:10px;font-family:var(--mono);letter-spacing:1px;text-transform:uppercase;color:var(--text-d);padding:0 0 9px;border-bottom:1px solid var(--border)}
.items-tbl td{padding:9px 0;border-bottom:1px solid var(--border);font-size:13px}
.ti{width:100%;padding:7px 9px;background:var(--s2);border:1px solid var(--border);border-radius:7px;color:var(--text);font-family:var(--font);font-size:12px;outline:none}
.ti:focus{border-color:var(--amber)}
.total-row{display:flex;justify-content:flex-end;gap:40px;padding-top:14px}
.tl{font-size:12px;color:var(--text-d)}.tv{font-size:18px;font-weight:800;color:var(--amber);font-family:var(--mono)}
.add-btn{display:flex;align-items:center;gap:7px;padding:9px 14px;background:none;border:1px dashed var(--border2);border-radius:7px;color:var(--text-d);font-family:var(--font);font-size:12px;cursor:pointer;transition:all .15s}
.add-btn:hover{border-color:var(--amber);color:var(--amber)}
.dlist{display:flex;flex-direction:column;gap:9px}
.di{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;background:var(--s1);border:1px solid var(--border);border-radius:11px;cursor:pointer;transition:all .15s}
.di:hover{border-color:rgba(245,166,35,.2)}
.di-cl{font-size:13px;font-weight:600;margin-bottom:2px}
.di-ds{font-size:11px;color:var(--text-d);font-family:var(--mono)}
.di-am{font-size:17px;font-weight:800;color:var(--amber);font-family:var(--mono);margin-right:14px}

/* TOAST */
.toast{position:fixed;bottom:22px;right:22px;z-index:999;padding:12px 18px;border-radius:10px;background:var(--s1);border:1px solid var(--border2);box-shadow:0 20px 40px rgba(0,0,0,.5);display:flex;align-items:center;gap:9px;font-size:13px;font-weight:600;transform:translateY(80px);opacity:0;transition:all .3s cubic-bezier(.34,1.56,.64,1)}
.toast.show{transform:translateY(0);opacity:1}
.toast.success{border-color:rgba(74,222,128,.3)}
.toast.success .ti-ico{color:var(--green)}

/* ANIMATIONS */
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
.an{animation:fadeUp .5s ease both}
.d1{animation-delay:.1s}.d2{animation-delay:.2s}.d3{animation-delay:.3s}.d4{animation-delay:.4s}

@media(max-width:900px){
  .hero{grid-template-columns:1fr;padding:60px 20px}
  .demo-card{display:none}
  .feat-grid{grid-template-columns:1fr}
  .plans{grid-template-columns:1fr}
  .metrics{grid-template-columns:1fr 1fr}
  .two{grid-template-columns:1fr}
  .dash-layout{grid-template-columns:1fr}
  .sidebar{display:none}
  nav{padding:0 20px}
  .devis-body{grid-template-columns:1fr}
  .devis-left{border-right:none;border-bottom:1px solid var(--border)}
}
</style>
</head>
<body>

<nav>
  <div class="logo" onclick="showPage('home')">
    <div class="logo-icon">⚡</div>
    Trade<em>Flow</em> AI
  </div>
  <div class="nav-r">
    <button class="nav-link" onclick="scrollToId('features')">Fonctionnalités</button>
    <button class="nav-link" onclick="scrollToId('pricing')">Tarifs</button>
    <button class="nav-link" onclick="showPage('dash')">Dashboard</button>
    <button class="nav-cta" onclick="showPage('onboard')">Essai gratuit →</button>
  </div>
</nav>

<!-- ═════════ LANDING ═══════════ -->
<div id="page-home" class="page active">

  <section class="hero">
    <div>
      <div class="hero-badge an"><span class="dot"></span>DISPONIBLE EN FR · DE · ES · IT · NL</div>
      <h1 class="an d1">L'IA qui gère<br>votre <em>admin</em><br>à votre place</h1>
      <p class="an d2">TradeFlow répond à vos appels, crée vos devis et envoie vos factures automatiquement. Concentrez-vous sur votre métier.</p>
      <div class="hero-btns an d3">
        <button class="btn-p" onclick="showPage('onboard')">Essai gratuit 14 jours →</button>
        <button class="btn-s" onclick="showPage('dash')">Voir la démo</button>
      </div>
      <div class="hero-stats an d4">
        <div><div class="stat-v">1.6M</div><div class="stat-l">artisans en Europe</div></div>
        <div><div class="stat-v">3h</div><div class="stat-l">économisées/jour</div></div>
        <div><div class="stat-v">97%</div><div class="stat-l">satisfaction</div></div>
      </div>
    </div>
    <div class="demo-card an d2">
      <div class="demo-hdr">
        <div class="dd" style="background:#ff5f57"></div>
        <div class="dd" style="background:#febc2e"></div>
        <div class="dd" style="background:#28c840"></div>
        <span style="flex:1;text-align:center;font-size:11px;color:var(--text-d);font-family:var(--mono)">Appel en cours</span>
      </div>
      <div class="demo-call">
        <div class="call-top">
          <div style="font-size:13px;font-weight:700">📞 +33 6 12 34 56 78</div>
          <div class="live-badge"><span class="dot"></span>EN DIRECT</div>
        </div>
        <div class="waves">
          <div class="wb"></div><div class="wb"></div><div class="wb"></div><div class="wb"></div>
          <div class="wb"></div><div class="wb"></div><div class="wb"></div><div class="wb"></div>
        </div>
        <div class="msgs">
          <div class="msg msg-ai">Bonjour, Martin Électricité, comment puis-je vous aider ?</div>
          <div class="msg msg-cl">J'ai une panne électrique dans ma cuisine...</div>
          <div class="msg msg-ai">Pas de problème ! Je vous propose demain à 9h. Ça vous convient ?</div>
          <div class="msg msg-cl">Oui parfait, merci !</div>
        </div>
      </div>
      <div class="demo-acts">
        <div class="act-row"><div class="act-ico ic-a">📅</div><div><div class="act-ttl">RDV créé automatiquement</div><div class="act-sub">Demain 09:00 — Dupont Jean</div></div><div class="ck">✓</div></div>
        <div class="act-row"><div class="act-ico ic-g">💬</div><div><div class="act-ttl">SMS de confirmation envoyé</div><div class="act-sub">+33 6 12 34 56 78</div></div><div class="ck">✓</div></div>
        <div class="act-row"><div class="act-ico ic-b">📋</div><div><div class="act-ttl">Devis généré en 30 secondes</div><div class="act-sub">PDF envoyé au client</div></div><div class="ck">→</div></div>
      </div>
    </div>
  </section>

  <!-- FEATURES -->
  <section id="features" class="section">
    <div class="sec-lbl">Fonctionnalités</div>
    <div class="sec-ttl">Tout en un seul outil</div>
    <div class="feat-grid">
      <div class="feat-card"><div class="feat-ico">📞</div><div class="feat-ttl">IA Réceptionniste 24/7</div><div class="feat-desc">Répond à vos appels en votre nom, dans votre langue. Prend les messages et planifie les rendez-vous.</div></div>
      <div class="feat-card"><div class="feat-ico">📋</div><div class="feat-ttl">Devis en 2 minutes</div><div class="feat-desc">Parlez dans votre téléphone après l'intervention. L'IA génère un devis professionnel et l'envoie par email.</div></div>
      <div class="feat-card"><div class="feat-ico">💶</div><div class="feat-ttl">Facturation automatique</div><div class="feat-desc">Le devis accepté devient une facture en un clic. L'IA relance automatiquement les factures impayées.</div></div>
      <div class="feat-card"><div class="feat-ico">📅</div><div class="feat-ttl">Agenda intelligent</div><div class="feat-desc">Vos rendez-vous sont organisés selon votre disponibilité. Plus jamais de double réservation.</div></div>
      <div class="feat-card"><div class="feat-ico">💬</div><div class="feat-ttl">SMS & WhatsApp</div><div class="feat-desc">Confirmations, rappels, suivi de factures — tout automatique dans la langue du client.</div></div>
      <div class="feat-card"><div class="feat-ico">📊</div><div class="feat-ttl">Tableau de bord</div><div class="feat-desc">Suivez vos revenus, appels récupérés, devis envoyés et taux d'encaissement en temps réel.</div></div>
    </div>
  </section>

  <!-- DEVIS DEMO -->
  <section class="devis-demo">
    <div class="sec-lbl">Démo live</div>
    <div class="sec-ttl">Testez la génération de devis</div>
    <div class="devis-box">
      <div class="devis-hdr">
        <h3>⚡ Générer un devis depuis une note vocale</h3>
        <span style="font-size:12px;color:var(--text-d);font-family:var(--mono)">PROPULSÉ PAR CLAUDE AI</span>
      </div>
      <div class="devis-body">
        <div class="devis-left">
          <label class="flabel">NOTE VOCALE OU TEXTE</label>
          <textarea class="finput" id="demo-transcript" placeholder="Ex: Pour Monsieur Dupont au 12 rue de Rivoli Metz, remplacement tableau électrique 500 euros et 4 heures de main d'oeuvre à 65 euros...">Pour Monsieur Dupont au 12 rue de Rivoli Metz, remplacement tableau électrique 500 euros et 4 heures de main d'oeuvre à 65 euros l'heure</textarea>
          <button class="btn-p" style="width:100%;margin-top:4px" onclick="generateLiveDevis()">⚡ Générer le devis →</button>
          <div style="margin-top:16px">
            <div class="flabel">ESSAYEZ AUSSI:</div>
            <div style="display:flex;flex-direction:column;gap:6px;margin-top:6px">
              <button onclick="setTranscript('Pour Madame Schmidt à Berlin, installation de 3 prises murales, 2 heures de travail à 70 euros et matériel 80 euros')" style="padding:7px 12px;background:var(--s2);border:1px solid var(--border);border-radius:7px;font-size:11px;cursor:pointer;color:var(--text-m);text-align:left;font-family:var(--font)">🇩🇪 Exemple allemand</button>
              <button onclick="setTranscript('Pour García Carlos, réparation fuite salle de bain urgence, 3 heures plombier à 80 euros et pièces 120 euros')" style="padding:7px 12px;background:var(--s2);border:1px solid var(--border);border-radius:7px;font-size:11px;cursor:pointer;color:var(--text-m);text-align:left;font-family:var(--font)">🔧 Urgence plomberie</button>
              <button onclick="setTranscript('Pour Monsieur Leclerc, peinture salon 40m2, 2 jours de travail à 350 euros par jour et fournitures 200 euros')" style="padding:7px 12px;background:var(--s2);border:1px solid var(--border);border-radius:7px;font-size:11px;cursor:pointer;color:var(--text-m);text-align:left;font-family:var(--font)">🎨 Peinture</button>
            </div>
          </div>
        </div>
        <div class="devis-right">
          <label class="flabel">RÉSULTAT</label>
          <div class="result-box" id="result-box">
            <div class="result-loading" id="result-placeholder">
              <div style="font-size:32px;margin-bottom:12px">📋</div>
              <div style="font-size:13px;color:var(--text-d)">Votre devis apparaîtra ici</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- PRICING -->
  <section id="pricing" class="section">
    <div class="sec-lbl">Tarifs</div>
    <div class="sec-ttl">Simple et transparent</div>
    <div class="plans">
      <div class="plan">
        <div class="plan-name">Starter</div>
        <div class="plan-price">€39</div>
        <div class="plan-period">par mois</div>
        <ul class="plan-feats">
          <li>100 appels/mois</li><li>IA Réceptionniste FR/DE/ES</li>
          <li>Devis & Factures illimités</li><li>Agenda en ligne</li><li>Support email</li>
        </ul>
        <button class="plan-btn" onclick="showPage('onboard')">Commencer gratuitement</button>
      </div>
      <div class="plan feat">
        <div class="plan-badge">LE PLUS POPULAIRE</div>
        <div class="plan-name">Pro</div>
        <div class="plan-price">€79</div>
        <div class="plan-period">par mois</div>
        <ul class="plan-feats">
          <li>Appels illimités</li><li>Toutes les langues EU</li>
          <li>SMS & WhatsApp auto</li><li>Relances impayés</li>
          <li>Rapports mensuels</li><li>Support prioritaire</li>
        </ul>
        <button class="plan-btn" onclick="showPage('onboard')">Commencer gratuitement →</button>
      </div>
      <div class="plan">
        <div class="plan-name">Business</div>
        <div class="plan-price">€149</div>
        <div class="plan-period">par mois</div>
        <ul class="plan-feats">
          <li>Multi-utilisateurs</li><li>API & intégrations</li>
          <li>Personnalisation avancée</li><li>Onboarding dédié</li>
          <li>Account manager</li><li>SLA garanti</li>
        </ul>
        <button class="plan-btn" onclick="showPage('onboard')">Contacter les ventes</button>
      </div>
    </div>
    <p style="text-align:center;margin-top:20px;font-size:13px;color:var(--text-d)">🔒 14 jours gratuits · Sans carte de crédit · Annulation à tout moment</p>
  </section>

  <footer>
    <div class="footer-logo">Trade<em>Flow</em> AI</div>
    <div class="footer-links">
      <span class="footer-link">Mentions légales</span>
      <span class="footer-link">Confidentialité</span>
      <span class="footer-link">Contact</span>
    </div>
    <div class="footer-copy">© 2026 TradeFlow AI · Made in France 🇫🇷</div>
  </footer>
</div>

<!-- ═════════ ONBOARDING ═══════════ -->
<div id="page-onboard" class="page">
  <div class="ob-card">
    <div class="ob-prog"><div class="ob-bar" id="ob-bar" style="width:33%"></div></div>
    <div class="ob-body">
      <div class="ob-step active" id="ob-1">
        <div class="step-n">ÉTAPE 1 / 3</div>
        <h2>Votre entreprise</h2>
        <p>Quelques infos pour configurer votre IA personnalisée.</p>
        <label class="flabel">NOM DE L'ENTREPRISE</label>
        <input class="finput" type="text" placeholder="Martin Électricité">
        <label class="flabel">VOTRE NOM</label>
        <input class="finput" type="text" placeholder="Jean Martin">
        <label class="flabel">TÉLÉPHONE</label>
        <input class="finput" type="tel" placeholder="+33 6 12 34 56 78">
        <div class="ob-acts"><button class="btn-next" onclick="obStep(2)">Continuer →</button></div>
      </div>
      <div class="ob-step" id="ob-2">
        <div class="step-n">ÉTAPE 2 / 3</div>
        <h2>Votre métier</h2>
        <p>L'IA sera formée spécifiquement pour votre secteur.</p>
        <div class="type-grid">
          <div class="type-opt sel" onclick="selType(this)"><div class="type-em">⚡</div><div class="type-nm">Électricien</div></div>
          <div class="type-opt" onclick="selType(this)"><div class="type-em">🔧</div><div class="type-nm">Plombier</div></div>
          <div class="type-opt" onclick="selType(this)"><div class="type-em">🏗️</div><div class="type-nm">Maçon</div></div>
          <div class="type-opt" onclick="selType(this)"><div class="type-em">🪟</div><div class="type-nm">Menuisier</div></div>
          <div class="type-opt" onclick="selType(this)"><div class="type-em">🎨</div><div class="type-nm">Peintre</div></div>
          <div class="type-opt" onclick="selType(this)"><div class="type-em">🔩</div><div class="type-nm">Autre</div></div>
        </div>
        <div class="lang-grid">
          <div class="lang-opt sel" onclick="selLang(this)">🇫🇷 Français</div>
          <div class="lang-opt" onclick="selLang(this)">🇩🇪 Deutsch</div>
          <div class="lang-opt" onclick="selLang(this)">🇪🇸 Español</div>
          <div class="lang-opt" onclick="selLang(this)">🇮🇹 Italiano</div>
          <div class="lang-opt" onclick="selLang(this)">🇳🇱 Nederlands</div>
        </div>
        <div class="ob-acts"><button class="btn-back" onclick="obStep(1)">← Retour</button><button class="btn-next" onclick="obStep(3)">Continuer →</button></div>
      </div>
      <div class="ob-step" id="ob-3">
        <div class="step-n">ÉTAPE 3 / 3</div>
        <h2>Votre compte</h2>
        <p>Créez votre compte et commencez votre essai gratuit de 14 jours.</p>
        <label class="flabel">EMAIL</label>
        <input class="finput" type="email" placeholder="jean@martin-electricite.fr">
        <label class="flabel">MOT DE PASSE</label>
        <input class="finput" type="password" placeholder="•••••••">
        <div class="ob-acts"><button class="btn-back" onclick="obStep(2)">← Retour</button><button class="btn-next" onclick="obDone()">Lancer mon IA ⚡</button></div>
      </div>
    </div>
  </div>
</div>

<!-- ═════════ DASHBOARD ═══════════ -->
<div id="page-dash" class="page">
  <div class="dash-layout">
    <aside class="sidebar">
      <div class="sb-lbl">Principal</div>
      <div class="sb-item active" onclick="showTab('overview',this)"><span>📊</span> Vue d'ensemble</div>
      <div class="sb-item" onclick="showTab('calls',this)"><span>📞</span> Appels IA</div>
      <div class="sb-item" onclick="showTab('devis',this)"><span>📋</span> Devis</div>
      <div class="sb-item" onclick="showTab('factures',this)"><span>💶</span> Factures</div>
      <div class="sb-lbl">Config</div>
      <div class="sb-item" onclick="showTab('settings',this)"><span>⚙️</span> Paramètres</div>
      <div style="margin-top:20px;padding:14px;background:var(--amber-d);border:1px solid rgba(245,166,35,.2);border-radius:10px">
        <div style="font-size:10px;font-family:var(--mono);color:var(--amber);margin-bottom:3px">PLAN PRO · ESSAI</div>
        <div style="font-size:11px;color:var(--text-d)">11 jours restants</div>
      </div>
    </aside>
    <main class="main">

      <!-- OVERVIEW -->
      <div id="tab-overview" class="dash-tab active">
        <div class="pg-hdr">
          <div><div class="pg-ttl">Bonjour, Jean 👋</div><div class="pg-sub">Voici ce qui s'est passé aujourd'hui</div></div>
          <button class="btn-p" onclick="showTab('devis',document.querySelector('[onclick*=devis]'))">+ Nouveau devis</button>
        </div>
        <div class="metrics">
          <div class="mc a"><div class="mc-lbl">Revenus ce mois</div><div class="mc-val">€8,240</div><div class="mc-chg up">↑ +23%</div></div>
          <div class="mc g"><div class="mc-lbl">Appels récupérés</div><div class="mc-val">34</div><div class="mc-chg up">↑ +8</div></div>
          <div class="mc b"><div class="mc-lbl">Devis envoyés</div><div class="mc-val">12</div><div class="mc-chg up">↑ 8 acceptés</div></div>
          <div class="mc r"><div class="mc-lbl">Factures impayées</div><div class="mc-val">3</div><div class="mc-chg dn">€1,240</div></div>
        </div>
        <div class="two">
          <div class="panel">
            <div class="panel-hdr"><span class="panel-ttl">Appels récents</span><button class="panel-act" onclick="showTab('calls',document.querySelectorAll('.sb-item')[1])">Voir tout →</button></div>
            <div class="call-item"><div class="call-av">👤</div><div><div class="call-nm">Dupont Jean</div><div class="call-ds">Panne électrique — 09:15</div></div><div><div class="call-tm">Il y a 2h</div><div class="status st-ok">RÉSERVÉ</div></div></div>
            <div class="call-item"><div class="call-av">👤</div><div><div class="call-nm">Schmidt Maria</div><div class="call-ds">Installation tableau</div></div><div><div class="call-tm">Il y a 4h</div><div class="status st-pend">EN ATTENTE</div></div></div>
            <div class="call-item"><div class="call-av">👤</div><div><div class="call-nm">García Carlos</div><div class="call-ds">Urgence prise murale</div></div><div><div class="call-tm">Hier</div><div class="status st-miss">MANQUÉ</div></div></div>
          </div>
          <div class="panel">
            <div class="panel-hdr"><span class="panel-ttl">Actions rapides</span></div>
            <div class="qa">
              <div class="qa-item" onclick="showTab('devis',document.querySelectorAll('.sb-item')[2])"><div class="qa-ico ic-a">📋</div><div><div class="qa-ttl">Créer un devis</div><div class="qa-sub">Parlez ou tapez</div></div><div class="qa-arr">›</div></div>
              <div class="qa-item" onclick="showTab('factures',document.querySelectorAll('.sb-item')[3])"><div class="qa-ico ic-g">💶</div><div><div class="qa-ttl">Envoyer une facture</div><div class="qa-sub">3 en attente</div></div><div class="qa-arr">›</div></div>
              <div class="qa-item" onclick="showTab('calls',document.querySelectorAll('.sb-item')[1])"><div class="qa-ico ic-b">📞</div><div><div class="qa-ttl">Configurer l'IA</div><div class="qa-sub">Script d'accueil</div></div><div class="qa-arr">›</div></div>
            </div>
          </div>
        </div>
      </div>

      <!-- CALLS -->
      <div id="tab-calls" class="dash-tab">
        <div class="pg-hdr"><div><div class="pg-ttl">Appels IA</div><div class="pg-sub">Votre réceptionniste virtuelle</div></div></div>
        <div class="two">
          <div class="voice-box">
            <div style="font-size:15px;font-weight:700;margin-bottom:14px">🎙️ Simulation d'appel IA</div>
            <div class="voice-stat">
              <div class="v-ind">📞<div class="v-pulse"></div></div>
              <div style="flex:1"><div style="font-size:13px;font-weight:600">IA active — Martin Électricité</div><div style="font-size:11px;color:var(--text-d);font-family:var(--mono)">Répond 24h/24, 7j/7</div></div>
              <div style="background:var(--green-d);border:1px solid rgba(74,222,128,.2);padding:5px 10px;border-radius:7px;font-size:11px;color:var(--green);font-family:var(--mono)">EN LIGNE</div>
            </div>
            <div class="tbox" id="tbox">
              <div class="tm tm-ai"><div class="tm-lbl">TRADEFLOW IA</div>Bonjour, Martin Électricité, comment puis-je vous aider ?</div>
            </div>
            <div style="display:flex;gap:9px;margin-bottom:12px">
              <input class="finput" id="chat-in" placeholder="Tapez un message client..." style="flex:1;margin-bottom:0" onkeypress="if(event.key==='Enter')sendChat()">
              <button class="btn-p" onclick="sendChat()" style="padding:11px 18px;white-space:nowrap">Envoyer</button>
            </div>
            <div style="display:flex;gap:6px;flex-wrap:wrap">
              <button onclick="setChatMsg('J\\'ai une fuite urgente')" style="padding:5px 10px;background:var(--s2);border:1px solid var(--border);border-radius:7px;font-size:11px;cursor:pointer;color:var(--text-m);font-family:var(--font)">Fuite urgente</button>
              <button onclick="setChatMsg('Je voudrais un devis')" style="padding:5px 10px;background:var(--s2);border:1px solid var(--border);border-radius:7px;font-size:11px;cursor:pointer;color:var(--text-m);font-family:var(--font)">Demander devis</button>
              <button onclick="setChatMsg('Quels sont vos horaires ?')" style="padding:5px 10px;background:var(--s2);border:1px solid var(--border);border-radius:7px;font-size:11px;cursor:pointer;color:var(--text-m);font-family:var(--font)">Horaires ?</button>
            </div>
          </div>
          <div class="panel">
            <div class="panel-hdr"><span class="panel-ttl">Stats appels</span></div>
            <div style="padding:18px;display:flex;flex-direction:column;gap:12px">
              <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:12px;border-bottom:1px solid var(--border)"><span style="font-size:12px;color:var(--text-d)">Appels ce mois</span><span style="font-size:20px;font-weight:800;color:var(--amber)">87</span></div>
              <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:12px;border-bottom:1px solid var(--border)"><span style="font-size:12px;color:var(--text-d)">RDV pris par IA</span><span style="font-size:20px;font-weight:800;color:var(--green)">34</span></div>
              <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:12px;border-bottom:1px solid var(--border)"><span style="font-size:12px;color:var(--text-d)">Taux conversion</span><span style="font-size:20px;font-weight:800;color:var(--blue)">79%</span></div>
              <div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:12px;color:var(--text-d)">CA via IA</span><span style="font-size:20px;font-weight:800;color:var(--amber)">€4,200</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- DEVIS -->
      <div id="tab-devis" class="dash-tab">
        <div class="pg-hdr"><div><div class="pg-ttl">Devis</div><div class="pg-sub">Créez des devis professionnels</div></div></div>
        <div class="two">
          <div class="dform">
            <h3>✏️ Nouveau devis</h3>
            <div class="frow">
              <div><label class="flabel">CLIENT</label><input class="finput" type="text" placeholder="Dupont Jean"></div>
              <div><label class="flabel">EMAIL</label><input class="finput" type="email" placeholder="jean@email.com"></div>
            </div>
            <label class="flabel">DESCRIPTION</label>
            <input class="finput" type="text" placeholder="Remplacement tableau électrique...">
            <table class="items-tbl">
              <thead><tr><th style="width:40%">Description</th><th style="width:15%">Qté</th><th style="width:20%">Prix HT</th><th style="width:20%">Total</th></tr></thead>
              <tbody id="items-body">
                <tr><td><input class="ti" value="Main d'œuvre électricien" oninput="calcTot()"></td><td><input class="ti" type="number" value="4" style="width:55px" oninput="calcTot()"></td><td><input class="ti" type="number" value="65" style="width:70px" oninput="calcTot()">€</td><td style="font-weight:700;font-family:var(--mono)" class="rt">260€</td></tr>
                <tr><td><input class="ti" value="Matériel électrique" oninput="calcTot()"></td><td><input class="ti" type="number" value="1" style="width:55px" oninput="calcTot()"></td><td><input class="ti" type="number" value="200" style="width:70px" oninput="calcTot()">€</td><td style="font-weight:700;font-family:var(--mono)" class="rt">200€</td></tr>
              </tbody>
            </table>
            <button class="add-btn" onclick="addItem()">+ Ajouter une ligne</button>
            <div class="total-row">
              <div><div class="tl">Total HT</div><div class="tv" id="t-ht">460€</div></div>
              <div><div class="tl">TVA 20%</div><div class="tv" id="t-tva" style="color:var(--text-m)">92€</div></div>
              <div><div class="tl">Total TTC</div><div class="tv" id="t-ttc">552€</div></div>
            </div>
            <div style="display:flex;gap:9px;margin-top:18px">
              <button class="btn-p" style="flex:1" onclick="showToast('Devis envoyé par email ✓','success')">📤 Envoyer</button>
              <button class="btn-s" onclick="showToast('PDF généré ✓','success')">📄 PDF</button>
            </div>
          </div>
          <div>
            <div style="font-size:13px;font-weight:700;margin-bottom:12px">Devis récents</div>
            <div class="dlist">
              <div class="di"><div class="di-info"><div class="di-cl">Dupont Jean</div><div class="di-ds">DEV-2026-042</div></div><div class="di-am">€1,240</div><div class="status st-ok">ACCEPTÉ</div></div>
              <div class="di"><div class="di-info"><div class="di-cl">Schmidt Maria</div><div class="di-ds">DEV-2026-041</div></div><div class="di-am">€3,800</div><div class="status st-pend">EN ATTENTE</div></div>
              <div class="di"><div class="di-info"><div class="di-cl">García Carlos</div><div class="di-ds">DEV-2026-040</div></div><div class="di-am">€680</div><div class="status st-ok">ACCEPTÉ</div></div>
            </div>
          </div>
        </div>
      </div>

      <!-- FACTURES -->
      <div id="tab-factures" class="dash-tab">
        <div class="pg-hdr"><div><div class="pg-ttl">Factures</div><div class="pg-sub">Suivi des paiements automatique</div></div><button class="btn-p" onclick="showToast('Relances envoyées ✓','success')">📤 Relancer impayés</button></div>
        <div class="metrics" style="grid-template-columns:repeat(3,1fr)">
          <div class="mc g"><div class="mc-lbl">Encaissé</div><div class="mc-val">€7,000</div></div>
          <div class="mc a"><div class="mc-lbl">En attente</div><div class="mc-val">€1,240</div></div>
          <div class="mc r"><div class="mc-lbl">En retard</div><div class="mc-val">€580</div></div>
        </div>
        <div class="panel">
          <div class="panel-hdr"><span class="panel-ttl">Toutes les factures</span></div>
          <div class="call-item"><div class="call-av">💶</div><div><div class="call-nm">FAC-2026-042 — Dupont Jean</div><div class="call-ds">Tableau électrique · Échéance 15/03</div></div><div><div class="call-tm" style="font-size:14px;font-weight:800;color:var(--amber)">€1,240</div><div class="status st-pend">IMPAYÉ</div></div></div>
          <div class="call-item"><div class="call-av">💶</div><div><div class="call-nm">FAC-2026-041 — García Carlos</div><div class="call-ds">Prise murale · Payé le 01/03</div></div><div><div class="call-tm" style="font-size:14px;font-weight:800;color:var(--green)">€680</div><div class="status st-ok">PAYÉ</div></div></div>
          <div class="call-item"><div class="call-av">💶</div><div><div class="call-nm">FAC-2026-040 — Müller Hans</div><div class="call-ds">Rénovation · En retard 12 jours</div></div><div><div class="call-tm" style="font-size:14px;font-weight:800;color:var(--red)">€580</div><div class="status st-miss">EN RETARD</div></div></div>
        </div>
      </div>

      <!-- SETTINGS -->
      <div id="tab-settings" class="dash-tab">
        <div class="pg-hdr"><div><div class="pg-ttl">Paramètres</div><div class="pg-sub">Configurez votre IA</div></div></div>
        <div style="max-width:560px;display:flex;flex-direction:column;gap:14px">
          <div class="panel">
            <div class="panel-hdr"><span class="panel-ttl">🎙️ Script d'accueil</span></div>
            <div style="padding:18px">
              <label class="flabel">MESSAGE D'ACCUEIL</label>
              <textarea class="finput" style="resize:vertical;min-height:70px">Bonjour, Martin Électricité, comment puis-je vous aider ?</textarea>
              <label class="flabel">HORAIRES</label>
              <input class="finput" value="Lundi–Vendredi 8h–18h">
              <button class="btn-p" onclick="showToast('Sauvegardé ✓','success')">Sauvegarder</button>
            </div>
          </div>
          <div class="panel">
            <div class="panel-hdr"><span class="panel-ttl">💶 Facturation</span></div>
            <div style="padding:18px">
              <div class="frow">
                <div><label class="flabel">SIRET</label><input class="finput" placeholder="123 456 789 00010"></div>
                <div><label class="flabel">TVA INTRA</label><input class="finput" placeholder="FR12345678900"></div>
              </div>
              <button class="btn-p" onclick="showToast('Sauvegardé ✓','success')">Sauvegarder</button>
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>
</div>

<div class="toast" id="toast"><span class="ti-ico">✓</span><span id="toast-txt">Action effectuée</span></div>

<script>
const API = window.location.origin;

function showPage(p){
  document.querySelectorAll('.page').forEach(x=>x.classList.remove('active'));
  document.getElementById('page-'+p).classList.add('active');
  window.scrollTo(0,0);
}
function scrollToId(id){document.getElementById(id)?.scrollIntoView({behavior:'smooth'})}

// ONBOARDING
function obStep(n){
  document.querySelectorAll('.ob-step').forEach(s=>s.classList.remove('active'));
  document.getElementById('ob-'+n).classList.add('active');
  document.getElementById('ob-bar').style.width={1:'33%',2:'66%',3:'100%'}[n];
}
function selType(el){document.querySelectorAll('.type-opt').forEach(o=>o.classList.remove('sel'));el.classList.add('sel')}
function selLang(el){document.querySelectorAll('.lang-opt').forEach(o=>o.classList.remove('sel'));el.classList.add('sel')}
function obDone(){showToast('Bienvenue ! 🎉','success');setTimeout(()=>showPage('dash'),700)}

// DASHBOARD TABS
function showTab(t,el){
  document.querySelectorAll('.dash-tab').forEach(x=>x.classList.remove('active'));
  document.getElementById('tab-'+t).classList.add('active');
  document.querySelectorAll('.sb-item').forEach(i=>i.classList.remove('active'));
  if(el)el.classList.add('active');
}

// LIVE DEVIS GENERATION
async function generateLiveDevis(){
  const transcript = document.getElementById('demo-transcript').value.trim();
  if(!transcript)return;
  const box = document.getElementById('result-box');
  box.innerHTML='<div class="result-loading"><div class="spin"></div><div style="font-size:12px;color:var(--text-d)">Claude analyse...</div></div>';
  try{
    const r = await fetch(API+'/api/devis/generate',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({transcript})
    });
    const d = await r.json();
    if(d.success){
      const data = d.data;
      let itemsHtml = data.items.map(i=>`
        <div class="result-item">
          <span>${i.description}</span>
          <span style="font-family:var(--mono);color:var(--text-m)">${i.quantite} × ${i.prix_unitaire_ht}€</span>
        </div>`).join('');
      box.innerHTML=`
        <div style="margin-bottom:12px">
          <div style="font-size:11px;font-family:var(--mono);color:var(--amber);margin-bottom:4px">CLIENT DÉTECTÉ</div>
          <div style="font-size:15px;font-weight:700">${data.client_name}</div>
          ${data.client_address?`<div style="font-size:12px;color:var(--text-d)">${data.client_address}</div>`:''}
        </div>
        ${itemsHtml}
        <div class="result-total">
          <span>TOTAL TTC</span>
          <span>${data.total_ttc.toFixed(2)} €</span>
        </div>
        <div style="margin-top:14px;display:flex;gap:8px">
          <a href="${d.pdf_url}" target="_blank" style="flex:1;display:block;padding:10px;background:var(--amber);color:#000;border-radius:8px;text-align:center;font-weight:700;font-size:13px;text-decoration:none">📄 Télécharger PDF</a>
        </div>
        <div style="margin-top:10px;padding:10px;background:var(--green-d);border:1px solid rgba(74,222,128,.2);border-radius:8px;font-size:12px;color:var(--green)">
          ✅ Devis N° ${d.numero} généré avec succès
        </div>`;
    }else{
      box.innerHTML='<div style="color:var(--red);font-size:13px;padding:20px">❌ Erreur: '+JSON.stringify(d)+'</div>';
    }
  }catch(e){
    box.innerHTML='<div style="color:var(--red);font-size:13px;padding:20px">❌ Erreur serveur: '+e.message+'</div>';
  }
}

function setTranscript(t){document.getElementById('demo-transcript').value=t}

// AI CHAT
const aiR={
  urgence:"Pas de panique ! Je comprends l'urgence. M. Martin peut intervenir aujourd'hui. Je vous propose 15h00 — ça vous convient ? Je vous envoie un SMS de confirmation.",
  devis:"Bien sûr ! Pour établir un devis précis, pouvez-vous décrire les travaux ? M. Martin peut aussi passer faire un état des lieux gratuit cette semaine.",
  horaires:"Nous intervenons du lundi au vendredi de 8h à 18h. En cas d'urgence M. Martin est disponible. Puis-je vous proposer un rendez-vous ?",
  default:"Je comprends votre demande. M. Martin sera ravi de vous aider. Puis-je vous proposer un rendez-vous cette semaine ?"
};
function setChatMsg(m){document.getElementById('chat-in').value=m}
function sendChat(){
  const inp=document.getElementById('chat-in');
  const msg=inp.value.trim();if(!msg)return;
  const box=document.getElementById('tbox');
  const ce=document.createElement('div');ce.className='tm tm-cl';
  ce.innerHTML='<div class="tm-lbl">CLIENT</div>'+msg;
  box.appendChild(ce);inp.value='';
  const te=document.createElement('div');te.className='tm tm-ai';
  te.innerHTML='<div class="tm-lbl">TRADEFLOW IA</div><span style="color:var(--text-d)">...</span>';
  box.appendChild(te);box.scrollTop=box.scrollHeight;
  setTimeout(()=>{
    const l=msg.toLowerCase();
    let r=aiR.default;
    if(l.includes('fuite')||l.includes('urgence')||l.includes('panne'))r=aiR.urgence;
    else if(l.includes('devis')||l.includes('install')||l.includes('travaux'))r=aiR.devis;
    else if(l.includes('horaire')||l.includes('heure')||l.includes('ouvert'))r=aiR.horaires;
    te.innerHTML='<div class="tm-lbl">TRADEFLOW IA</div>'+r;
    box.scrollTop=box.scrollHeight;
    if(l.includes('fuite')||l.includes('devis')||l.includes('urgence')){
      setTimeout(()=>{
        const re=document.createElement('div');re.className='call-res';
        re.innerHTML='<div style="font-size:22px">✅</div><div class="cr-txt"><strong>RDV créé automatiquement</strong>SMS de confirmation envoyé</div>';
        box.appendChild(re);box.scrollTop=box.scrollHeight;
      },800);
    }
  },1000);
}

// DEVIS CALCULATOR
function calcTot(){
  const rows=document.querySelectorAll('#items-body tr');
  let tot=0;
  rows.forEach(r=>{
    const ins=r.querySelectorAll('input[type=number]');
    if(ins.length>=2){
      const t=parseFloat(ins[0].value)||0,p=parseFloat(ins[1].value)||0,rl=t*p;
      tot+=rl;r.querySelector('.rt').textContent=rl+'€';
    }
  });
  const tva=Math.round(tot*.2);
  document.getElementById('t-ht').textContent=tot+'€';
  document.getElementById('t-tva').textContent=tva+'€';
  document.getElementById('t-ttc').textContent=(tot+tva)+'€';
}
function addItem(){
  const tb=document.getElementById('items-body');
  const r=document.createElement('tr');
  r.innerHTML='<td><input class="ti" placeholder="Description..." oninput="calcTot()"></td><td><input class="ti" type="number" value="1" style="width:55px" oninput="calcTot()"></td><td><input class="ti" type="number" value="0" style="width:70px" oninput="calcTot()">€</td><td style="font-weight:700;font-family:var(--mono)" class="rt">0€</td>';
  tb.appendChild(r);
}

// TOAST
function showToast(msg,type){
  const t=document.getElementById('toast');
  document.getElementById('toast-txt').textContent=msg;
  t.className='toast show '+(type||'');
  setTimeout(()=>t.classList.remove('show'),3000);
}
</script>
</body>
</html>"""

# ═════════════════════════════════════════════════
# SERVE FRONTEND
# ═══════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def frontend():
    return HTMLResponse(content=HTML)

@app.get("/health")
async def health():
    return {"status": "ok"}

# ═════════════════════════════════════════════════
# CLAUDE EXTRACT
# ═════════════════════════════════════════════════

def extract_devis(transcript: str) -> dict:
    prompt = f"""
Tu es un comptable professionnel français spécialisé dans l'artisanat.
Analyse cette transcription: "{transcript}"
Retourne UNIQUEMENT du JSON valide:
{{
  "client_name": "Nom du client",
  "client_email": null,
  "client_address": null,
  "artisan_name": "{ARTISAN_NAME}",
  "description_travaux": "Description générale",
  "items": [{{"description": "Prestation", "quantite": 1, "unite": "forfait", "prix_unitaire_ht": 0.0}}],
  "tva_rate": 10,
  "total_ht": 0.0,
  "tva_montant": 0.0,
  "total_ttc": 0.0,
  "validite_jours": 30,
  "notes": null,
  "urgence": false
}}"""

    r = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    text = r.content[0].text.strip().replace("```json","").replace("```","").strip()
    start = text.find("{"); end = text.rfind("}") + 1
    if start != -1: text = text[start:end]
    data = json.loads(text)

    items = []
    for i in data.get("items", []):
        items.append({
            "description": i.get("description") or i.get("desc", "Prestation"),
            "quantite": float(i.get("quantite") or i.get("qty", 1)),
            "unite": i.get("unite", "forfait"),
            "prix_unitaire_ht": float(i.get("prix_unitaire_ht") or i.get("unit_price", 0))
        })
    data["items"] = items

    tva_rate = float(data.get("tva_rate", 10))
    total_ht = sum(i["quantite"] * i["prix_unitaire_ht"] for i in items)
    tva = round(total_ht * tva_rate / 100, 2)
    data["total_ht"] = round(total_ht, 2)
    data["tva_rate"] = tva_rate
    data["tva_montant"] = tva
    data["total_ttc"] = round(total_ht + tva, 2)
    return data


def make_pdf(data: dict, numero: str) -> str:
    return f"/tmp/devis_{numero}.pdf"


def make_numero(seed=""):
    return f"DEV-{datetime.date.today().strftime('%Y%m')}-{str(abs(hash(seed+str(datetime.datetime.now()))))[-4:]}"


# ═════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════

@app.post("/api/devis/generate")
async def generate_devis(request: Request):
    body = await request.json()
    transcript = body.get("transcript", "").strip()
    if not transcript:
        raise HTTPException(400, "transcript requis")
    try:
        data = extract_devis(transcript)
        numero = make_numero(transcript)
        make_pdf(data, numero)
        return JSONResponse({
            "success": True,
            "numero": numero,
            "client": data["client_name"],
            "total_ttc": data["total_ttc"],
            "total_ht": data["total_ht"],
            "items_count": len(data["items"]),
            "pdf_url": f"/api/devis/pdf/{numero}",
            "data": data
        })
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/devis/pdf/{numero}")
async def get_pdf(numero: str):
    path = f"/tmp/devis_{numero}.pdf"
    if not os.path.exists(path):
        raise HTTPException(404, "PDF non trouvé")
    return FileResponse(path, media_type="application/pdf", filename=f"devis_{numero}.pdf")


@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    payload = await request.json()
    if payload.get("type") == "end-of-call-report":
        transcript = payload.get("transcript") or payload.get("summary", "")
        customer = payload.get("customer", {}).get("number", "")
        if transcript:
            try:
                data = extract_devis(transcript)
                numero = make_numero(transcript + customer)
                make_pdf(data, numero)
                return {"status": "success", "numero": numero, "total_ttc": data["total_ttc"]}
            except Exception as e:
                return {"status": "error", "message": str(e)}
    return {"status": "received"}


@app.get("/api/stats")
async def stats():
    return {"mrr": 3950, "clients": 50, "devis": 187, "appels": 342, "ca": 48200}


handler = Mangum(app)
pythonhandler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
"""
