"""Jolly Roll Instagram post generator (1080x1350, 'Sıcak Ev Akşamı' style).
Usage: python3 make_posts.py <posts.json> <out_dir>
"""
import json, sys, pathlib, asyncio

FONT_DIR = pathlib.Path(__file__).parent / "fonts/node_modules/@fontsource-variable"
F = lambda n: (FONT_DIR / n).as_uri()
LAT = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
EXT = "U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF"
def face(fam, base, style, w):
    return "".join(f"@font-face{{font-family:{fam};src:url({F(base.format(r))}) format('woff2');font-weight:{w};font-style:{style};unicode-range:{u}}}" for r,u in (("latin",LAT),("latin-ext",EXT)))
FACES = face("Fraunces","fraunces/files/fraunces-{}-wght-normal.woff2","normal","100 900") + face("Fraunces","fraunces/files/fraunces-{}-wght-italic.woff2","italic","100 900") + face("Manrope","manrope/files/manrope-{}-wght-normal.woff2","normal","200 800")

ACC = {"amber": "#E8A63E", "coral": "#E07A6A", "lilac": "#C9B6F0", "sage": "#9DB08A", "sky": "#A9D2F2", "mint": "#7FD0BE"}

CSS = FACES + f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;background:#1F1712;color:#F6EEDF;font-family:Manrope,sans-serif;overflow:hidden;position:relative}}
.glow{{position:absolute;border-radius:50%}}
.wrap{{position:absolute;inset:0;padding:92px 84px 0;display:flex;flex-direction:column}}
.kicker{{font-weight:800;font-size:30px;letter-spacing:6px;text-transform:uppercase}}
h1{{font-family:Fraunces,serif;font-weight:900;font-size:104px;line-height:1.0;margin-top:26px;letter-spacing:-1px}}
h1 em{{font-style:italic;font-weight:800}}
.sub{{font-size:36px;line-height:1.38;color:#E6D8C2;margin-top:28px;max-width:860px}}
.stack{{position:relative;margin-top:58px;height:520px}}
.card{{position:absolute;left:40px;right:40px;top:30px;height:440px;border-radius:44px;background:#F6EEDF;color:#1F1712;padding:48px 52px;display:flex;flex-direction:column;box-shadow:0 30px 60px rgba(0,0,0,.45)}}
.back1,.back2{{position:absolute;left:80px;right:80px;top:10px;height:440px;border-radius:44px}}
.back1{{transform:rotate(5deg)}} .back2{{transform:rotate(-4deg);left:60px;right:60px;top:20px}}
.tag{{align-self:flex-start;font-weight:800;font-size:24px;letter-spacing:3px;padding:12px 22px;border-radius:99px;text-transform:uppercase;color:#1F1712}}
.q{{font-family:Fraunces,serif;font-weight:800;font-size:58px;line-height:1.12;margin-top:34px}}
.foot{{margin-top:auto;font-size:26px;font-weight:600;color:#7A6A5A}}
.list{{margin-top:54px;display:flex;flex-direction:column;gap:22px}}
.row{{display:flex;align-items:center;gap:26px;background:#2A211C;border-radius:30px;padding:26px 30px;box-shadow:inset 0 0 0 2px #3E342D}}
.dot{{width:64px;height:64px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-family:Fraunces,serif;font-weight:900;font-size:32px;color:#1F1712}}
.rt{{font-size:36px;font-weight:700;line-height:1.25}} .rt small{{display:block;font-size:26px;font-weight:600;color:#BFAE98;margin-top:4px}}
.brand{{position:absolute;left:84px;right:84px;bottom:64px;display:flex;align-items:center;justify-content:space-between}}
.logo{{display:flex;align-items:center;gap:18px}}
.mark{{width:76px;height:76px;border-radius:22px;background:#F6EEDF;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:.95;font-family:Fraunces,serif;font-weight:900;font-size:21px;color:#1F1712}}
.mark b{{color:#E07A6A}}
.bn{{font-family:Fraunces,serif;font-weight:900;font-size:40px}} .bs{{font-size:24px;color:#BFAE98;font-weight:600}}
.cta{{font-weight:800;font-size:28px;padding:20px 32px;border-radius:99px;background:#F6EEDF;color:#1F1712}}
.chip{{position:absolute;display:flex;align-items:center;gap:14px;padding:16px 28px 16px 16px;border-radius:99px;background:#F6EEDF;color:#1F1712;font-weight:800;font-size:28px;box-shadow:0 20px 40px rgba(0,0,0,.45);z-index:3}}
.chip i{{width:48px;height:48px;border-radius:50%;display:inline-block}}
.compact .row{{padding:16px 28px}} .compact{{gap:14px!important;margin-top:40px!important}} .compact .rt{{font-size:32px}} .compact .rt small{{font-size:24px}} .compact .dot{{width:54px;height:54px;font-size:28px}}
.big{{font-family:Fraunces,serif;font-weight:900;font-size:300px;line-height:.9;letter-spacing:-6px}}
"""

def deco(a):
    return (f'<div class="glow" style="right:-260px;top:-260px;width:820px;height:820px;background:radial-gradient(circle,{a}33 0,{a}00 70%)"></div>'
            '<div class="glow" style="left:-200px;bottom:120px;width:520px;height:520px;background:#261C16"></div>'
            f'<svg style="position:absolute;left:0;top:0" width="1080" height="1350"><path d="M-40 1010 C220 930 420 1120 640 1040 S960 900 1140 980" stroke="{a}" stroke-opacity=".45" stroke-width="5" stroke-dasharray="4 20" stroke-linecap="round" fill="none"/></svg>')

def brand(cta):
    return ('<div class="brand"><div class="logo"><div class="mark"><b>JOLLY</b>ROLL</div>'
            '<div><div class="bn">Jolly Roll</div><div class="bs">App Store\'da ücretsiz indir</div></div></div>'
            f'<div class="cta">{cta}</div></div>')

def render_card(p):
    a = ACC[p["accent"]]
    body = f'''<p class="kicker" style="color:{a}">{p["kicker"]}</p><h1>{p["title"]}</h1>'''
    if p.get("sub"): body += f'<p class="sub">{p["sub"]}</p>'
    if p["layout"] == "card":
        b1 = ACC[p.get("back1", "sage")]; b2 = ACC[p.get("back2", "lilac")]
        chip = ""
        if p.get("chip"):
            chip = f'<div class="chip" style="right:0;top:-6px;transform:rotate(6deg)"><i style="background:{ACC[p["chip"][1]]}"></i>{p["chip"][0]}</div>'
        body += f'''<div class="stack">{chip}<div class="back1" style="background:{b1}"></div><div class="back2" style="background:{b2}"></div>
        <div class="card"><span class="tag" style="background:{a}">{p["tag"]}</span><p class="q">{p["q"]}</p><p class="foot">{p["foot"]}</p></div></div>'''
    elif p["layout"] == "list":
        rows = "".join(f'<div class="row"><div class="dot" style="background:{ACC[c]}">{i+1}</div><div class="rt">{t}<small>{s}</small></div></div>'
                       for i, (t, s, c) in enumerate(p["rows"]))
        body += f'<div class="list{" compact" if len(p["rows"])>=5 else ""}">{rows}</div>'
    elif p["layout"] == "big":
        body += f'<div style="margin-top:40px;display:flex;align-items:flex-end;gap:30px"><span class="big" style="color:{a}">{p["big"]}</span><span class="sub" style="margin:0 0 40px;font-size:40px">{p["bigtext"]}</span></div>'
        if p.get("rows"):
            rows = "".join(f'<div class="row"><div class="dot" style="background:{ACC[c]}">{i+1}</div><div class="rt">{t}<small>{s}</small></div></div>' for i, (t, s, c) in enumerate(p["rows"]))
            body += f'<div class="list" style="margin-top:20px">{rows}</div>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{deco(a)}<div class="wrap">{body}</div>{brand(p["cta"])}</body></html>'

async def main(spec, out):
    from playwright.async_api import async_playwright
    posts = json.load(open(spec))
    out = pathlib.Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for p in posts:
            html = out / f'{p["id"]}.html'; html.write_text(render_card(p))
            await pg.goto(html.as_uri()); await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(out / f'{p["id"]}.png'))
            html.unlink()
        await b.close()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))
