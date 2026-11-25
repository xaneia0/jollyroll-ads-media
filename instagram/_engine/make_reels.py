"""Jolly Roll Reels generator (1080x1920, 30fps). Each reel = list of states (HTML snapshots) held for N seconds
with short crossfades, optional tick/boom audio. Usage: python3 make_reels.py <reels.json> <out_dir>"""
import json, sys, pathlib, asyncio, subprocess, shutil
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from make_posts import FACES, ACC

W, H, FPS = 1080, 1920, 30
BASE = FACES + """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1920px;background:#1F1712;color:#F6EEDF;font-family:Manrope,sans-serif;overflow:hidden;position:relative}
.wrap{position:absolute;inset:0;padding:200px 80px 0;display:flex;flex-direction:column}
.kicker{font-weight:800;font-size:34px;letter-spacing:6px;text-transform:uppercase}
.h{font-family:Fraunces,serif;font-weight:900;font-size:110px;line-height:1.0;margin-top:26px}
.h em{font-style:italic;font-weight:800}
.brand{position:absolute;left:80px;right:80px;bottom:330px;display:flex;align-items:center;justify-content:space-between}
.mark{width:96px;height:96px;border-radius:26px;background:#F6EEDF;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:.95;font-family:Fraunces,serif;font-weight:900;font-size:26px;color:#1F1712}
.mark b{color:#E07A6A}
.bn{font-family:Fraunces,serif;font-weight:900;font-size:48px}.bs{font-size:28px;color:#BFAE98;font-weight:600}
.cta{font-weight:800;font-size:32px;padding:24px 36px;border-radius:99px;background:#F6EEDF;color:#1F1712}
"""

def glow(a):
    return (f'<div style="position:absolute;right:-300px;top:-200px;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,{a}38 0,{a}00 70%)"></div>'
            '<div style="position:absolute;left:-220px;bottom:420px;width:600px;height:600px;border-radius:50%;background:#261C16"></div>')

def brand(cta):
    return ('<div class="brand"><div style="display:flex;align-items:center;gap:20px"><div class="mark"><b>JOLLY</b>ROLL</div>'
            '<div><div class="bn">Jolly Roll</div><div class="bs">App Store\'da ücretsiz indir</div></div></div>'
            f'<div class="cta">{cta}</div></div>')

def chat_state(r, n):
    a = ACC[r["accent"]]
    bub = ""
    for name, msg, side, c in r["msgs"][:n]:
        me = side == "r"
        bub += (f'<div style="display:flex;flex-direction:column;align-items:{"flex-end" if me else "flex-start"};margin-top:22px">'
                + ("" if me else f'<span style="font-size:28px;font-weight:800;color:{ACC[c]};margin:0 0 8px 20px">{name}</span>')
                + f'<div style="max-width:800px;padding:26px 34px;border-radius:38px;{"border-bottom-right-radius:12px" if me else "border-bottom-left-radius:12px"};font-size:44px;font-weight:600;line-height:1.28;background:{"#F6EEDF" if me else "#2E241E"};color:{"#1F1712" if me else "#F6EEDF"};box-shadow:inset 0 0 0 {"0" if me else "2"}px #3E342D">{msg}</div></div>')
    typing = ""
    if n < len(r["msgs"]):
        typing = '<div style="margin-top:22px;display:flex;gap:10px;padding:24px 30px;background:#2E241E;border-radius:38px;width:150px;justify-content:center">' + ''.join('<span style="width:16px;height:16px;border-radius:50%;background:#BFAE98"></span>' for _ in range(3)) + '</div>'
    seen = f'<div style="text-align:right;margin-top:14px;font-size:26px;color:#BFAE98">{r["seen"]}</div>' if r.get("seen") and n >= len(r["msgs"]) else ""
    return f'''<p class="kicker" style="color:{a}">{r["kicker"]}</p><div class="h" style="font-size:96px">{r["title"]}</div>
    <div style="margin-top:56px;background:#251C17;border-radius:48px;padding:34px 38px 44px;box-shadow:inset 0 0 0 2px #3A2E26">
    <div style="display:flex;align-items:center;gap:20px;padding-bottom:18px;border-bottom:2px solid #3A2E26"><span style="width:70px;height:70px;border-radius:50%;background:{a}"></span><div><div style="font-size:38px;font-weight:800">{r["group"]}</div><div style="font-size:26px;color:#BFAE98">{r.get("members","")}</div></div></div>{bub}{typing}{seen}</div>'''

def end_state(r):
    a = ACC[r["accent"]]
    return f'''<p class="kicker" style="color:{a}">{r.get("end_kicker","Bu akşam sizde")}</p><div class="h" style="margin-top:40px;font-size:130px">{r["end_title"]}</div>
    <p style="margin-top:44px;font-size:46px;line-height:1.4;color:#E6D8C2">{r["end_sub"]}</p>'''

def bomb_state(r, sec, holder, boom=False):
    a = ACC[r["accent"]]
    if boom:
        return f'''<p class="kicker" style="color:{a}">Saatli Bomba</p>
        <div style="margin-top:220px;text-align:center;font-family:Fraunces,serif;font-weight:900;font-size:240px;line-height:.9;color:#E07A6A">BOOM!</div>
        <div style="margin-top:60px;text-align:center;font-family:Fraunces,serif;font-weight:800;font-size:96px">Ceza <em style="color:#E8A63E">sende.</em></div>
        <div style="margin-top:40px;text-align:center;font-size:44px;color:#E6D8C2">{r["penalty"]}</div>'''
    names = r["names"]
    chips = "".join(f'<span style="padding:20px 34px;border-radius:99px;font-size:40px;font-weight:800;{"background:#E8A63E;color:#1F1712" if n == holder else "background:#2A211C;color:#BFAE98;box-shadow:inset 0 0 0 2px #3E342D"}">{n}</span>' for n in names)
    pct = sec / r["seconds"] * 360
    return f'''<p class="kicker" style="color:{a}">Saatli Bomba</p><div class="h">Kelimeyi söyle,<br><em style="color:{a}">bombayı pasla!</em></div>
    <div style="margin-top:70px;align-self:center;width:520px;height:520px;border-radius:50%;background:conic-gradient({"#E07A6A" if sec <= 3 else a} 0 {pct}deg,#2A211C {pct}deg 360deg);display:flex;align-items:center;justify-content:center">
    <div style="width:440px;height:440px;border-radius:50%;background:#1F1712;display:flex;flex-direction:column;align-items:center;justify-content:center">
    <span style="font-family:Fraunces,serif;font-weight:900;font-size:230px;line-height:1;color:{"#E07A6A" if sec <= 3 else "#F6EEDF"}">{sec}</span></div></div>
    <div style="margin-top:60px;text-align:center;font-size:40px;color:#E6D8C2">Kategori: <b style="color:#F6EEDF">{r["category"]}</b></div>
    <div style="margin-top:40px;display:flex;gap:18px;justify-content:center;flex-wrap:wrap">{chips}</div>'''

def pov_state(r, step):
    a = ACC[r["accent"]]
    lines = r["lines"][:step]
    body = "".join(f'<div style="margin-top:40px;font-family:Fraunces,serif;font-weight:800;font-size:76px;line-height:1.12">{l}</div>' for l in lines)
    return f'''<p class="kicker" style="color:{a}">{r["kicker"]}</p>
    <div style="margin-top:120px;font-family:Fraunces,serif;font-weight:900;font-size:220px;line-height:.9;color:{a}">POV:</div>{body}'''

def page(r, inner, show_brand=False):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE}</style></head><body>{glow(ACC[r["accent"]])}<div class="wrap">{inner}</div>{brand(r["cta"]) if show_brand else ""}</body></html>'

def states(r):
    """returns list of (html, seconds, sound) ; sound in {None,'tick','boom','pop'}"""
    out = []
    if r["type"] == "chat":
        for n in range(1, len(r["msgs"]) + 1):
            out.append((page(r, chat_state(r, n)), r.get("step", 1.3), "pop"))
        out[-1] = (out[-1][0], 2.4, "pop")
    elif r["type"] == "bomb":
        names = r["names"]
        for i, s in enumerate(range(r["seconds"], 0, -1)):
            out.append((page(r, bomb_state(r, s, names[min(i // 3, len(names) - 1)])), 0.75, "tick"))
        out.append((page(r, bomb_state(r, 0, None, boom=True)), 2.6, "boom"))
    elif r["type"] == "pov":
        for i in range(1, len(r["lines"]) + 1):
            out.append((page(r, pov_state(r, i)), r["holds"][i - 1], "pop"))
    out.append((page(r, end_state(r), True), 2.8, None))
    return out

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def sound_file(kind, path, dur):
    if kind == "tick":
        expr = "sin(2*PI*1400*t)*exp(-60*t)*0.6"
    elif kind == "pop":
        expr = "sin(2*PI*(500+900*t)*t)*exp(-30*t)*0.35"
    elif kind == "boom":
        expr = "(random(0)*2-1)*exp(-3*t)*0.8+sin(2*PI*55*t)*exp(-2.5*t)*0.6"
    else:
        expr = "0"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=44100:d={dur}", "-ac", "2", path])

async def main(spec, outdir):
    from playwright.async_api import async_playwright
    reels = json.load(open(spec)); outdir = pathlib.Path(outdir).resolve(); outdir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page(viewport={"width": W, "height": H})
        for r in reels:
            tmp = outdir / f'_{r["id"]}'; shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir()
            st = states(r); vids = []; auds = []
            for i, (html, sec, snd) in enumerate(st):
                hp = tmp / f's{i}.html'; hp.write_text(html)
                await pg.goto(hp.as_uri()); await pg.wait_for_timeout(250)
                png = tmp / f's{i}.png'; await pg.screenshot(path=str(png))
                v = tmp / f'v{i}.mp4'; fade = 0.12
                run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(png), "-vf",
                     f"format=yuv420p,loop=-1:1,trim=duration={sec},fade=t=in:st=0:d={fade}", "-r", str(FPS),
                     "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(v)])
                vids.append(v)
                a = tmp / f'a{i}.wav'; sound_file(snd, str(a), sec); auds.append(a)
            (tmp / "v.txt").write_text("".join(f"file '{v}'\n" for v in vids))
            (tmp / "a.txt").write_text("".join(f"file '{a}'\n" for a in auds))
            run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "v.txt"), "-c", "copy", str(tmp / "video.mp4")])
            run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "a.txt"), str(tmp / "audio.wav")])
            part = outdir / f'{r["id"]}.part.mp4'
            run(["ffmpeg", "-y", "-i", str(tmp / "video.mp4"), "-i", str(tmp / "audio.wav"), "-map", "0:v", "-map", "1:a",
                 "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(part)])
            part.rename(outdir / f'{r["id"]}.mp4')
            shutil.copy(tmp / "s0.png", outdir / f'{r["id"]}_cover.png')
            # keep frame previews for checking
            for i in (0, len(st) // 2, len(st) - 2, len(st) - 1):
                shutil.copy(tmp / f's{i}.png', outdir / f'{r["id"]}_f{i}.png')
            shutil.rmtree(tmp)
        await b.close()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))
