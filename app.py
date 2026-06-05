import os, re, tempfile, threading, time, uuid
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), 'vidgrab')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def fmt_size(b):
    if not b: return None
    if b >= 1e9: return f"{b/1e9:.1f} GB"
    if b >= 1e6: return f"{b/1e6:.1f} MB"
    if b >= 1e3: return f"{b/1e3:.1f} KB"
    return f"{b} B"

# =============================================
#  FRONTEND — POORA HTML YAHI SE SERVE HOGA
# =============================================
@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>VidGrab Pro — Free Video Downloader</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎬</text></svg>">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--p:#6C63FF;--s:#FF6584;--a:#43E97B;--bg:#f0f2f5;--gl:rgba(255,255,255,.48);--gb:rgba(255,255,255,.62);--gs:0 8px 32px rgba(108,99,255,.12);--t:#1a1a2e;--m:#6b7280;--g1:linear-gradient(135deg,#6C63FF,#FF6584,#43E97B);--g2:linear-gradient(135deg,#667eea,#764ba2);--g3:linear-gradient(135deg,#f093fb,#f5576c);--g4:linear-gradient(135deg,#4facfe,#00f2fe);--r:20px;--rs:12px;--e:all .4s cubic-bezier(.25,.46,.45,.94)}
html{scroll-behavior:smooth}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--t);min-height:100vh;overflow-x:hidden}

.bg-w{position:fixed;inset:0;z-index:0;overflow:hidden;background:linear-gradient(135deg,#e0e5ec,#f0f2f5,#e8ecf1)}
.orb{position:absolute;border-radius:50%;filter:blur(90px);opacity:.35;will-change:transform;animation:fo 22s ease-in-out infinite}
.orb:nth-child(1){width:520px;height:520px;background:linear-gradient(135deg,#6C63FF,#a78bfa);top:-12%;left:-6%;animation-duration:26s}
.orb:nth-child(2){width:420px;height:420px;background:linear-gradient(135deg,#FF6584,#fca5a5);top:58%;right:-10%;animation-delay:-6s;animation-duration:21s}
.orb:nth-child(3){width:360px;height:360px;background:linear-gradient(135deg,#43E97B,#38bdf8);bottom:-12%;left:28%;animation-delay:-11s;animation-duration:24s}
.orb:nth-child(4){width:260px;height:260px;background:linear-gradient(135deg,#f59e0b,#f97316);top:28%;left:62%;animation-delay:-8s;animation-duration:19s}
@keyframes fo{0%,100%{transform:translate(0,0) scale(1)}25%{transform:translate(55px,-45px) scale(1.08)}50%{transform:translate(-35px,55px) scale(.94)}75%{transform:translate(45px,35px) scale(1.06)}}
.bg-d{position:fixed;inset:0;background-image:radial-gradient(rgba(108,99,255,.05) 1px,transparent 1px);background-size:32px 32px;z-index:0;pointer-events:none}
.main{position:relative;z-index:1}

.nav{position:fixed;top:0;width:100%;z-index:1000;padding:14px 0;transition:var(--e)}
.nav.sc{background:rgba(255,255,255,.72);backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px);border-bottom:1px solid rgba(255,255,255,.5);box-shadow:0 4px 30px rgba(0,0,0,.06);padding:10px 0}
.nav-in{max-width:1100px;margin:0 auto;padding:0 20px;display:flex;align-items:center;justify-content:space-between}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;font-family:'Space Grotesk',sans-serif;font-weight:800;font-size:1.45rem}
.logo-b{width:40px;height:40px;background:var(--g1);border-radius:12px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:1rem;box-shadow:0 4px 16px rgba(108,99,255,.3);animation:pg 3s ease-in-out infinite}
@keyframes pg{0%,100%{box-shadow:0 4px 16px rgba(108,99,255,.3)}50%{box-shadow:0 4px 28px rgba(108,99,255,.55)}}
.gt{background:var(--g1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;background-size:200% 200%;animation:gss 5s ease infinite}
@keyframes gss{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.nls{display:flex;align-items:center;gap:26px;list-style:none}
.nls a{text-decoration:none;color:var(--t);font-weight:500;font-size:.88rem;position:relative;transition:var(--e)}
.nls a::after{content:'';position:absolute;bottom:-4px;left:0;width:0;height:2px;background:var(--g1);border-radius:2px;transition:var(--e)}
.nls a:hover{color:var(--p)}.nls a:hover::after{width:100%}
.ncta{background:var(--g2)!important;color:#fff!important;padding:9px 20px;border-radius:50px;font-weight:600!important;box-shadow:0 4px 15px rgba(102,126,234,.3)}
.ncta:hover{transform:translateY(-2px);box-shadow:0 6px 24px rgba(102,126,234,.4)!important}.ncta::after{display:none!important}
.mtg{display:none;background:none;border:none;font-size:1.4rem;color:var(--t);cursor:pointer}
.mm{display:none;position:fixed;inset:0;background:rgba(255,255,255,.96);backdrop-filter:blur(30px);z-index:999;flex-direction:column;align-items:center;justify-content:center;gap:26px}
.mm.op{display:flex}
.mm a{text-decoration:none;font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:700;color:var(--t);transition:var(--e)}.mm a:hover{color:var(--p)}
.mm .cb{position:absolute;top:18px;right:20px;background:none;border:none;font-size:1.8rem;cursor:pointer;color:var(--t)}

.hero{padding:145px 20px 65px;text-align:center;max-width:860px;margin:0 auto}
.bdg{display:inline-flex;align-items:center;gap:8px;background:rgba(108,99,255,.08);border:1px solid rgba(108,99,255,.15);padding:7px 18px;border-radius:50px;font-size:.8rem;font-weight:600;color:var(--p);margin-bottom:22px;animation:fu .6s ease-out}
.bdg i{animation:sk 2s ease-in-out infinite}
@keyframes sk{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.3)}}
.hero h1{font-family:'Space Grotesk',sans-serif;font-size:clamp(2.1rem,6vw,3.8rem);font-weight:800;line-height:1.08;margin-bottom:16px;animation:fu .6s ease-out .1s both}
.hero>p{font-size:1.02rem;color:var(--m);max-width:540px;margin:0 auto 34px;line-height:1.7;animation:fu .6s ease-out .2s both}
@keyframes fu{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}

.dlb{max-width:700px;margin:0 auto 20px;animation:fu .6s ease-out .3s both}
.iw{display:flex;align-items:center;background:var(--gl);backdrop-filter:blur(25px);-webkit-backdrop-filter:blur(25px);border:1.5px solid var(--gb);border-radius:60px;padding:7px 7px 7px 24px;box-shadow:var(--gs);transition:var(--e)}
.iw:focus-within{border-color:rgba(108,99,255,.4);box-shadow:var(--gs),0 0 0 4px rgba(108,99,255,.08);transform:translateY(-2px)}
.iw .ic{color:var(--p);font-size:1.1rem;margin-right:10px;opacity:.65;flex-shrink:0}
.iw input{flex:1;border:none;outline:none;background:transparent;font-size:.93rem;font-family:'Inter',sans-serif;color:var(--t);padding:12px 0;min-width:0}
.iw input::placeholder{color:#9ca3af}
.bg0{display:inline-flex;align-items:center;gap:8px;background:var(--g1);background-size:200% 200%;color:#fff;border:none;padding:14px 30px;border-radius:50px;font-size:.92rem;font-weight:700;font-family:'Inter',sans-serif;cursor:pointer;transition:var(--e);white-space:nowrap;box-shadow:0 6px 24px rgba(108,99,255,.3);animation:gss 5s ease infinite;flex-shrink:0}
.bg0:hover{transform:translateY(-2px) scale(1.02);box-shadow:0 10px 32px rgba(108,99,255,.4)}
.bg0:active{transform:translateY(0) scale(.98)}
.bg0.ld{pointer-events:none;opacity:.82}
.bg0 .sp{display:none;width:20px;height:20px;border:3px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spp .7s linear infinite}
.bg0.ld .sp{display:block}.bg0.ld .bt{display:none}
@keyframes spp{to{transform:rotate(360deg)}}
.stt{font-size:.8rem;color:var(--m);margin-top:12px;animation:fu .6s ease-out .4s both}
.stt i{color:var(--a);margin-right:4px}

.pls{display:flex;align-items:center;justify-content:center;gap:10px;margin-top:30px;flex-wrap:wrap;animation:fu .6s ease-out .5s both}
.ch{display:flex;align-items:center;gap:6px;background:var(--gl);backdrop-filter:blur(15px);border:1px solid var(--gb);padding:8px 16px;border-radius:50px;font-size:.78rem;font-weight:600;color:var(--t);transition:var(--e);cursor:default}
.ch:hover{transform:translateY(-3px);box-shadow:0 8px 22px rgba(0,0,0,.07)}
.ch i{font-size:.95rem}
.ch.yt i{color:#FF0000}.ch.ig i{color:#E4405F}.ch.fb i{color:#1877F2}.ch.tw i{color:#1DA1F2}.ch.tk i{color:#010101}.ch.vi i{color:#1AB7EA}.ch.rd i{color:#FF4500}

.sts{display:none;padding:12px 18px;border-radius:var(--rs);font-size:.86rem;font-weight:500;margin:14px auto 0;max-width:700px;animation:su .4s ease-out;align-items:center;gap:8px}
.sts.sh{display:flex}.sts.err{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);color:#dc2626}.sts.ok{background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);color:#059669}.sts.inf{background:rgba(108,99,255,.08);border:1px solid rgba(108,99,255,.15);color:var(--p)}
@keyframes su{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.pw{display:none;max-width:700px;margin:16px auto 0;padding:0 20px}
.pw.sh{display:block}
.pbg{height:6px;background:rgba(108,99,255,.1);border-radius:10px;overflow:hidden}
.pf{height:100%;width:0;background:var(--g1);background-size:200% 200%;border-radius:10px;transition:width .3s;animation:gss 3s ease infinite}
.pt{font-size:.76rem;color:var(--m);margin-top:6px;text-align:center}

.ra{max-width:700px;margin:0 auto;padding:0 20px}
.rc{display:none;background:var(--gl);backdrop-filter:blur(30px);-webkit-backdrop-filter:blur(30px);border:1.5px solid var(--gb);border-radius:var(--r);padding:24px;box-shadow:var(--gs);animation:su .5s ease-out;margin-top:22px}
.rc.sh{display:block}
.rh{display:flex;gap:16px;margin-bottom:20px}
.rt{width:168px;height:100px;border-radius:var(--rs);object-fit:cover;flex-shrink:0;background:linear-gradient(135deg,#e5e7eb,#f3f4f6)}
.ri{flex:1;min-width:0}
.ri h3{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;margin-bottom:4px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:1.35}
.rm{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}
.rm span{font-size:.75rem;color:var(--m);display:flex;align-items:center;gap:4px}
.rm i{color:var(--p);font-size:.7rem}
.sl{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--m);margin:18px 0 10px;display:flex;align-items:center;gap:7px}
.sl i{color:var(--p)}
.fg{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:9px}
.fb{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:rgba(255,255,255,.55);border:1.5px solid rgba(108,99,255,.08);border-radius:var(--rs);cursor:pointer;transition:var(--e);text-decoration:none;color:var(--t);position:relative;overflow:hidden}
.fb::before{content:'';position:absolute;inset:0;background:var(--g1);opacity:0;transition:opacity .3s;z-index:0}
.fb:hover{border-color:var(--p);transform:translateY(-2px);box-shadow:0 6px 20px rgba(108,99,255,.12)}
.fb:hover::before{opacity:.04}
.fb:active{transform:translateY(0) scale(.98)}
.fl{display:flex;align-items:center;gap:8px;z-index:1}
.fi{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.78rem;color:#fff;flex-shrink:0}
.fi.v{background:var(--g2)}.fi.a{background:var(--g3)}
.fd{display:flex;flex-direction:column}
.fq{font-weight:700;font-size:.84rem}
.fss{font-size:.7rem;color:var(--m)}
.di{color:var(--p);font-size:.9rem;transition:var(--e);z-index:1}
.fb:hover .di{transform:translateY(2px);color:var(--s)}
.fb.dling{pointer-events:none;opacity:.65}
.fb.dling .di{animation:spp .7s linear infinite}

.fs-sec{padding:85px 20px;max-width:1100px;margin:0 auto}
.shd{text-align:center;margin-bottom:48px}
.shd h2{font-family:'Space Grotesk',sans-serif;font-size:clamp(1.7rem,4vw,2.5rem);font-weight:800;margin-bottom:10px}
.shd p{color:var(--m);font-size:.98rem;max-width:460px;margin:0 auto}
.fgd{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}
.fc{background:var(--gl);backdrop-filter:blur(20px);border:1.5px solid var(--gb);border-radius:var(--r);padding:28px 22px;transition:var(--e);position:relative;overflow:hidden}
.fc::before{content:'';position:absolute;top:0;left:0;width:100%;height:3px;background:var(--g1);opacity:0;transition:var(--e)}
.fc:hover{transform:translateY(-6px);box-shadow:0 18px 45px rgba(108,99,255,.11)}
.fc:hover::before{opacity:1}
.fci{width:48px;height:48px;border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;color:#fff;margin-bottom:16px}
.fc:nth-child(1) .fci{background:var(--g2)}.fc:nth-child(2) .fci{background:var(--g3)}.fc:nth-child(3) .fci{background:var(--g4)}
.fc:nth-child(4) .fci{background:linear-gradient(135deg,#f59e0b,#ef4444)}.fc:nth-child(5) .fci{background:linear-gradient(135deg,#10b981,#3b82f6)}.fc:nth-child(6) .fci{background:linear-gradient(135deg,#8b5cf6,#ec4899)}
.fc h3{font-family:'Space Grotesk',sans-serif;font-size:1.02rem;font-weight:700;margin-bottom:7px}
.fc p{color:var(--m);font-size:.85rem;line-height:1.6}

.hw{padding:45px 20px 85px;max-width:860px;margin:0 auto}
.stp{display:flex;gap:20px;flex-wrap:wrap;justify-content:center}
.st-c{flex:1;min-width:200px;max-width:250px;text-align:center;padding:26px 18px;background:var(--gl);backdrop-filter:blur(20px);border:1.5px solid var(--gb);border-radius:var(--r);transition:var(--e)}
.st-c:hover{transform:translateY(-5px);box-shadow:0 14px 36px rgba(108,99,255,.1)}
.sn{width:42px;height:42px;border-radius:50%;background:var(--g1);color:#fff;font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:800;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;box-shadow:0 6px 18px rgba(108,99,255,.25)}
.st-c h3{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:.95rem;margin-bottom:5px}
.st-c p{color:var(--m);font-size:.82rem;line-height:1.5}

.ftr{padding:40px 20px 24px;text-align:center;border-top:1px solid rgba(108,99,255,.08);margin-top:28px}
.ftr-b{font-family:'Space Grotesk',sans-serif;font-weight:800;font-size:1.15rem;margin-bottom:6px}
.ftr p{color:var(--m);font-size:.8rem;margin-bottom:12px}
.ftr-l{display:flex;justify-content:center;gap:18px;flex-wrap:wrap}
.ftr-l a{color:var(--m);text-decoration:none;font-size:.8rem;transition:var(--e)}
.ftr-l a:hover{color:var(--p)}
.ftr-bt{margin-top:20px;padding-top:14px;border-top:1px solid rgba(0,0,0,.05);font-size:.75rem;color:#9ca3af}

.rv{opacity:0;transform:translateY(35px);transition:all .7s cubic-bezier(.25,.46,.45,.94)}
.rv.vi{opacity:1;transform:translateY(0)}

.tc{position:fixed;top:78px;right:18px;z-index:9999;display:flex;flex-direction:column;gap:8px;pointer-events:none}
.tt{background:rgba(255,255,255,.9);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.6);padding:12px 18px;border-radius:var(--rs);box-shadow:0 10px 38px rgba(0,0,0,.1);font-size:.84rem;font-weight:500;display:flex;align-items:center;gap:8px;animation:ti .4s ease-out;max-width:320px;pointer-events:all}
.tt.lv{animation:too .3s ease-in forwards}
@keyframes ti{from{opacity:0;transform:translateX(50px)}to{opacity:1;transform:translateX(0)}}
@keyframes too{from{opacity:1;transform:translateX(0)}to{opacity:0;transform:translateX(50px)}}

@media(max-width:768px){
.nls{display:none}.mtg{display:block}
.hero{padding:120px 16px 45px}
.iw{flex-direction:column;border-radius:var(--r);padding:6px}
.iw .ic{display:none}
.iw input{width:100%;padding:13px 16px;text-align:center}
.bg0{width:100%;justify-content:center;border-radius:14px}
.rh{flex-direction:column;align-items:center;text-align:center}
.rt{width:100%;height:165px}
.fg{grid-template-columns:1fr}
.pls{gap:7px}.ch{padding:6px 11px;font-size:.74rem}
.fgd{grid-template-columns:1fr}
.stp{flex-direction:column;align-items:center}.st-c{max-width:100%}
}
@media(max-width:480px){.hero h1{font-size:1.85rem}.hero>p{font-size:.93rem}.rc{padding:16px}}
</style>
</head>
<body>
<div class="bg-w"><div class="orb"></div><div class="orb"></div><div class="orb"></div><div class="orb"></div></div>
<div class="bg-d"></div>
<div class="main">

<nav class="nav" id="nav">
<div class="nav-in">
<a href="#" class="logo"><div class="logo-b"><i class="fas fa-play"></i></div><span class="gt">VidGrab</span></a>
<ul class="nls">
<li><a href="#feat"><i class="fas fa-sparkles"></i> Features</a></li>
<li><a href="#howw"><i class="fas fa-circle-info"></i> How it Works</a></li>
<li><a href="https://github.com/yt-dlp/yt-dlp" target="_blank" class="ncta"><i class="fab fa-github"></i> yt-dlp</a></li>
</ul>
<button class="mtg" onclick="document.getElementById('mmm').classList.toggle('op')"><i class="fas fa-bars"></i></button>
</div>
</nav>

<div class="mm" id="mmm">
<button class="cb" onclick="document.getElementById('mmm').classList.remove('op')"><i class="fas fa-xmark"></i></button>
<a href="#feat" onclick="document.getElementById('mmm').classList.remove('op')">Features</a>
<a href="#howw" onclick="document.getElementById('mmm').classList.remove('op')">How it Works</a>
</div>

<section class="hero">
<div class="bdg"><i class="fas fa-bolt"></i> 100% Free — Seedha Download — No Redirect</div>
<h1>Video Download Karo<br><span class="gt">Seedha Yahi Par</span></h1>
<p>Kisi bhi video ka link paste karo — video <strong>seedha yahi se download</strong> hoga. YouTube, Instagram, Facebook, Twitter, TikTok — sab supported hai.</p>
<div class="dlb"><div class="iw">
<i class="fas fa-link ic"></i>
<input type="url" id="urlInp" placeholder="Video ka link yahan paste karo..." autocomplete="off" spellcheck="false">
<button class="bg0" id="goBtn" onclick="go()"><span class="bt"><i class="fas fa-magnifying-glass"></i> Fetch Video</span><span class="sp"></span></button>
</div></div>
<p class="stt"><i class="fas fa-circle-check"></i> Phone & Desktop dono par kaam karta hai</p>
<div class="pls">
<div class="ch yt"><i class="fab fa-youtube"></i> YouTube</div>
<div class="ch ig"><i class="fab fa-instagram"></i> Instagram</div>
<div class="ch fb"><i class="fab fa-facebook"></i> Facebook</div>
<div class="ch tw"><i class="fab fa-x-twitter"></i> Twitter</div>
<div class="ch tk"><i class="fab fa-tiktok"></i> TikTok</div>
<div class="ch vi"><i class="fab fa-vimeo-v"></i> Vimeo</div>
<div class="ch rd"><i class="fab fa-reddit-alien"></i> Reddit</div>
</div>
</section>

<div class="sts" id="stsEl"><i class="fas fa-circle-info"></i><span id="stsTxt"></span></div>
<div class="pw" id="pw"><div class="pbg"><div class="pf" id="pf"></div></div><p class="pt" id="ptxt">Video dhundh raha hai...</p></div>

<div class="ra"><div class="rc" id="resCard">
<div class="rh">
<img class="rt" id="resThumb" src="" alt="Thumbnail">
<div class="ri"><h3 id="resTitle">Video Title</h3>
<div class="rm">
<span><i class="fas fa-clock"></i> <span id="resDur">0:00</span></span>
<span><i class="fas fa-eye"></i> <span id="resViews">-</span></span>
<span><i class="fas fa-user"></i> <span id="resUp">Unknown</span></span>
</div></div></div>
<div class="sl"><i class="fas fa-video"></i> VIDEO — Quality Chuno aur Download Karo</div>
<div class="fg" id="vFmts"></div>
<div class="sl" style="margin-top:16px"><i class="fas fa-music"></i> AUDIO — MP3 Download</div>
<div class="fg" id="aFmts"></div>
</div></div>

<section class="fs-sec" id="feat">
<div class="shd rv"><h2>Kyun Hai <span class="gt">VidGrab</span> Best?</h2><p>Simple, Fast, Free — Koi bakwaas nahi.</p></div>
<div class="fgd">
<div class="fc rv"><div class="fci"><i class="fas fa-download"></i></div><h3>Seedha Download</h3><p>Video seedha aapke phone/PC me save hota hai. Koi redirect nahi.</p></div>
<div class="fc rv"><div class="fci"><i class="fas fa-shield-halved"></i></div><h3>Safe & Private</h3><p>Koi login nahi, koi tracking nahi. 100% private.</p></div>
<div class="fc rv"><div class="fci"><i class="fas fa-globe"></i></div><h3>1000+ Sites</h3><p>YouTube, Instagram, TikTok, Twitter, Facebook, Vimeo, Reddit supported.</p></div>
<div class="fc rv"><div class="fci"><i class="fas fa-film"></i></div><h3>Best Quality</h3><p>360p se lekar 4K tak — jo chahiye wo quality chuno.</p></div>
<div class="fc rv"><div class="fci"><i class="fas fa-mobile-screen"></i></div><h3>Phone Friendly</h3><p>Mobile browser me kholo aur download karo. App nahi chahiye.</p></div>
<div class="fc rv"><div class="fci"><i class="fas fa-music"></i></div><h3>Audio / MP3</h3><p>Sirf gaana chahiye? MP3 me directly download karo.</p></div>
</div></section>

<section class="hw" id="howw">
<div class="shd rv"><h2>Kaise <span class="gt">Kaam</span> Karta Hai?</h2><p>Bus 3 simple steps.</p></div>
<div class="stp">
<div class="st-c rv"><div class="sn">1</div><h3>Link Copy Karo</h3><p>YouTube/Instagram se video ka link copy karo.</p></div>
<div class="st-c rv"><div class="sn">2</div><h3>Paste & Fetch</h3><p>Upar box me paste karo, Fetch Video dabao.</p></div>
<div class="st-c rv"><div class="sn">3</div><h3>Download!</h3><p>Quality chuno, download button dabao — done!</p></div>
</div></section>

<footer class="ftr">
<div class="ftr-b"><span class="gt">VidGrab Pro</span></div>
<p>Free video downloader — powered by yt-dlp</p>
<div class="ftr-l"><a href="#feat">Features</a><a href="#howw">How it Works</a></div>
<div class="ftr-bt">&copy; 2026 VidGrab Pro. Personal use only.</div>
</footer>
</div>
<div class="tc" id="tc"></div>

<script>
window.addEventListener('scroll',()=>document.getElementById('nav').classList.toggle('sc',scrollY>30));
const rObs=new IntersectionObserver(e=>{e.forEach(el=>{if(el.isIntersecting)el.target.classList.add('vi')})},{threshold:.12});
document.querySelectorAll('.rv').forEach(el=>rObs.observe(el));
function toast(m,t='info'){const c=document.getElementById('tc'),d=document.createElement('div');d.className='tt';const ic={info:'fa-circle-info',success:'fa-circle-check',error:'fa-circle-exclamation',warning:'fa-triangle-exclamation'};const co={info:'var(--p)',success:'#10b981',error:'#ef4444',warning:'#f59e0b'};d.innerHTML='<i class="fas '+ic[t]+'" style="color:'+co[t]+'"></i> '+m;c.appendChild(d);setTimeout(()=>{d.classList.add('lv');setTimeout(()=>d.remove(),300)},3500)}
function showSts(m,t='inf'){const e=document.getElementById('stsEl'),x=document.getElementById('stsTxt');e.className='sts sh '+t;const i={inf:'fa-circle-info',err:'fa-circle-exclamation',ok:'fa-circle-check'};e.querySelector('i').className='fas '+i[t];x.textContent=m}
function hideSts(){document.getElementById('stsEl').classList.remove('sh')}
let pInt;
function showProg(t){document.getElementById('pw').classList.add('sh');document.getElementById('ptxt').textContent=t||'Video dhundh raha hai...';const f=document.getElementById('pf');f.style.width='0%';let w=0;pInt=setInterval(()=>{w+=Math.random()*10;if(w>85){clearInterval(pInt);w=85}f.style.width=w+'%'},220)}
function hideProg(){clearInterval(pInt);const f=document.getElementById('pf');f.style.width='100%';setTimeout(()=>{document.getElementById('pw').classList.remove('sh');f.style.width='0%'},400)}
function fmtDur(s){if(!s)return'N/A';const h=Math.floor(s/3600),m=Math.floor(s%3600/60),ss=Math.floor(s%60);return h>0?h+':'+String(m).padStart(2,'0')+':'+String(ss).padStart(2,'0'):m+':'+String(ss).padStart(2,'0')}
function fmtViews(n){if(!n)return'-';if(n>=1e9)return(n/1e9).toFixed(1)+'B';if(n>=1e6)return(n/1e6).toFixed(1)+'M';if(n>=1e3)return(n/1e3).toFixed(1)+'K';return n+''}
async function go(){const inp=document.getElementById('urlInp');const url=inp.value.trim();const btn=document.getElementById('goBtn');const card=document.getElementById('resCard');if(!url){showSts('Pehle video ka link paste karo!','err');toast('Link paste karo','warning');inp.focus();return}try{new URL(url)}catch(e){showSts('Ye valid URL nahi lag raha.','err');toast('URL check karo','error');return}btn.classList.add('ld');card.classList.remove('sh');hideSts();showProg('Video ki info dhundh raha hai...');try{const r=await fetch('/api/info',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})});if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.error||'Video fetch nahi ho paya')}const data=await r.json();hideProg();renderResult(data,url);toast('Video mil gaya! Ab download karo 🎉','success')}catch(e){hideProg();showSts(e.message,'err');toast(e.message,'error')}finally{btn.classList.remove('ld')}}
function renderResult(d,url){const card=document.getElementById('resCard');const th=document.getElementById('resThumb');th.src=d.thumbnail||'';th.style.display='block';th.onerror=()=>th.style.display='none';document.getElementById('resTitle').textContent=d.title||'Untitled';document.getElementById('resDur').textContent=fmtDur(d.duration);document.getElementById('resViews').textContent=fmtViews(d.view_count);document.getElementById('resUp').textContent=d.uploader||'Unknown';const vf=document.getElementById('vFmts');vf.innerHTML='';if(d.videos&&d.videos.length>0){d.videos.forEach(f=>{vf.innerHTML+=fmtBtn(url,f.format_id,f.quality,f.ext,f.filesize,'video')})}else{vf.innerHTML+=fmtBtn(url,'best','Best Quality','mp4',null,'video')}const af=document.getElementById('aFmts');af.innerHTML='';if(d.audios&&d.audios.length>0){d.audios.forEach(f=>{af.innerHTML+=fmtBtn(url,f.format_id,f.quality,f.ext,f.filesize,'audio')})}else{af.innerHTML+=fmtBtn(url,'bestaudio','Best Audio','mp3',null,'audio')}card.classList.add('sh');card.scrollIntoView({behavior:'smooth',block:'center'})}
function fmtBtn(url,fid,quality,ext,size,type){const encUrl=encodeURIComponent(url);const dlLink='/api/download?url='+encUrl+'&format='+fid+'&type='+type;const icon=type==='audio'?'fa-music':'fa-play';const cls=type==='audio'?'a':'v';const sizeText=size?' \\u00b7 '+size:'';const extU=ext.toUpperCase();const id='dl_'+Math.random().toString(36).substr(2,6);return '<a class="fb" id="'+id+'" href="'+dlLink+'" onclick="startDl(event,\\''+id+'\\')" download><div class="fl"><div class="fi '+cls+'"><i class="fas '+icon+'"></i></div><div class="fd"><span class="fq">'+quality+'</span><span class="fss">'+extU+sizeText+'</span></div></div><i class="fas fa-download di"></i></a>'}
function startDl(e,id){const btn=document.getElementById(id);btn.classList.add('dling');toast('Download shuru ho raha hai... 📥','info');setTimeout(()=>btn.classList.remove('dling'),8000)}
document.getElementById('urlInp').addEventListener('keydown',e=>{if(e.key==='Enter')go()});
document.getElementById('urlInp').addEventListener('paste',()=>{setTimeout(()=>toast('Link paste ho gaya — Fetch Video dabao!','info'),100)});
</script>
</body></html>'''


# =============================================
#  API: VIDEO INFO
# =============================================
@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    if not data or not data.get('url'):
        return jsonify({'error': 'URL daalo pehle!'}), 400

    url = data['url'].strip()
    ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True, 'socket_timeout': 30}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return jsonify({'error': 'Video info nahi mila'}), 400

        if info.get('_type') == 'playlist':
            entries = info.get('entries', [])
            info = next((e for e in entries if e), None) if entries else None
            if not info:
                return jsonify({'error': 'Playlist empty hai'}), 400

        raw = info.get('formats', [])
        videos, audios = [], []
        seen_v, seen_a = set(), set()

        for f in raw:
            vc = f.get('vcodec', 'none')
            ac = f.get('acodec', 'none')
            h = f.get('height')
            abr = f.get('abr')
            fid = f.get('format_id', '')
            ext = f.get('ext', 'mp4')
            fs = f.get('filesize') or f.get('filesize_approx')

            if vc and vc != 'none' and h:
                fps = f.get('fps') or 30
                label = f"{h}p" + (f" {fps}fps" if fps > 30 else "")
                key = f"{h}_{fps}"
                if key not in seen_v:
                    seen_v.add(key)
                    videos.append({'format_id': fid, 'quality': label, 'ext': ext, 'filesize': fmt_size(fs), 'height': h, 'fps': fps, 'type': 'video'})

            elif ac and ac != 'none' and (not vc or vc == 'none'):
                br = int(abr) if abr else 0
                if br > 0:
                    label = f"{br}kbps"
                    key = f"{br}_{ext}"
                    if key not in seen_a:
                        seen_a.add(key)
                        audios.append({'format_id': fid, 'quality': label, 'ext': ext, 'filesize': fmt_size(fs), 'abr': br, 'type': 'audio'})

        videos.sort(key=lambda x: (x['height'], x['fps']), reverse=True)
        audios.sort(key=lambda x: x['abr'], reverse=True)

        # Unique heights only
        final_v, sh2 = [], set()
        for v in videos:
            if v['height'] not in sh2:
                sh2.add(v['height'])
                final_v.append(v)
            if len(final_v) >= 8: break

        return jsonify({
            'title': info.get('title', 'Untitled'),
            'thumbnail': info.get('thumbnail', ''),
            'duration': info.get('duration'),
            'view_count': info.get('view_count'),
            'uploader': info.get('uploader') or info.get('channel', 'Unknown'),
            'videos': final_v,
            'audios': audios[:5],
        })

    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if 'Unsupported URL' in msg: msg = 'Ye URL supported nahi hai'
        elif 'Private' in msg: msg = 'Ye video private hai'
        elif 'unavailable' in msg: msg = 'Ye video available nahi hai'
        else: msg = 'Video fetch nahi ho paya. URL check karo.'
        return jsonify({'error': msg}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


# =============================================
#  API: DOWNLOAD
# =============================================
@app.route('/api/download')
def download():
    url = request.args.get('url', '').strip()
    fmt = request.args.get('format', 'best').strip()
    dtype = request.args.get('type', 'video').strip()

    if not url:
        return jsonify({'error': 'URL nahi mila'}), 400

    uid = str(uuid.uuid4())[:8]
    out_dir = os.path.join(DOWNLOAD_DIR, uid)
    os.makedirs(out_dir, exist_ok=True)
    out_tpl = os.path.join(out_dir, '%(title).80s.%(ext)s')

    if dtype == 'audio':
        ydl_opts = {
            'format': f'{fmt}/bestaudio/best', 'outtmpl': out_tpl, 'quiet': True, 'no_warnings': True, 'socket_timeout': 60,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        }
    else:
        format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best' if fmt == 'best' else f'{fmt}+bestaudio/{fmt}/best'
        ydl_opts = {'format': format_str, 'outtmpl': out_tpl, 'quiet': True, 'no_warnings': True, 'merge_output_format': 'mp4', 'socket_timeout': 60}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        if not info:
            return jsonify({'error': 'Download fail ho gaya'}), 500

        if info.get('_type') == 'playlist':
            entries = [e for e in info.get('entries', []) if e]
            if entries: info = entries[0]

        filepath = None
        for root, dirs, files in os.walk(out_dir):
            for f in files:
                fp = os.path.join(root, f)
                if os.path.getsize(fp) > 0:
                    filepath = fp
                    break

        if not filepath:
            return jsonify({'error': 'File nahi mili'}), 500

        title = info.get('title', 'download')
        safe_title = re.sub(r'[^\w\s\-.]', '', title)[:80].strip() or 'download'
        ext = os.path.splitext(filepath)[1] or ('.mp3' if dtype == 'audio' else '.mp4')
        filename = f"{safe_title}{ext}"

        def generate():
            try:
                with open(filepath, 'rb') as f:
                    while True:
                        chunk = f.read(524288)
                        if not chunk: break
                        yield chunk
            finally:
                def cleanup():
                    time.sleep(10)
                    try:
                        import shutil; shutil.rmtree(out_dir, ignore_errors=True)
                    except: pass
                threading.Thread(target=cleanup, daemon=True).start()

        fsize = os.path.getsize(filepath)
        response = Response(stream_with_context(generate()), content_type='application/octet-stream')
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length'] = str(fsize)
        response.headers['Cache-Control'] = 'no-cache'
        return response

    except yt_dlp.utils.DownloadError:
        return jsonify({'error': 'Download fail: URL check karo'}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'version': yt_dlp.version.__version__})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
