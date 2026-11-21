"""Version 3: a layered, engraved-print travel poster for Koravel."""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops


ROOT = Path(__file__).resolve().parent
S = 2
W = H = 1024
SIZE = (W*S, H*S)
random.seed(2026)


def p(x, y):
    return round(x*S), round(y*S)


def b(x0, y0, x1, y1):
    return round(x0*S), round(y0*S), round(x1*S), round(y1*S)


def curve_points(a, c1, c2, z, count=42):
    out = []
    for i in range(count+1):
        t = i/count
        q = 1-t
        out.append(p(q**3*a[0]+3*q*q*t*c1[0]+3*q*t*t*c2[0]+t**3*z[0],
                     q**3*a[1]+3*q*q*t*c1[1]+3*q*t*t*c2[1]+t**3*z[1]))
    return out


def stroke_curve(draw, a, c1, c2, z, color, width=2):
    draw.line(curve_points(a, c1, c2, z), fill=color, width=width*S, joint="curve")


def font(size, bold=False):
    face = "DejaVuSerifCondensed-Bold.ttf" if bold else "DejaVuSerifCondensed.ttf"
    candidates = (
        Path("/usr/share/fonts/truetype/dejavu") / face,
        Path("/usr/share/fonts/TTF") / face,
        Path("/data/data/com.termux/files/usr/share/fonts/TTF") / face,
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size*S)
    raise FileNotFoundError(f"Install the DejaVu font {face} to regenerate the poster")


def gradient():
    stops = [(0.00, (20, 24, 45)), (0.34, (39, 46, 69)), (0.64, (86, 73, 76)),
             (0.82, (120, 91, 75)), (1.00, (47, 53, 59))]
    im = Image.new("RGB", SIZE)
    px = im.load()
    for y in range(SIZE[1]):
        t = y/(SIZE[1]-1)
        for j in range(len(stops)-1):
            if stops[j][0] <= t <= stops[j+1][0]:
                ta, ca = stops[j]
                tb, cb = stops[j+1]
                u = (t-ta)/(tb-ta)
                color = tuple(round(ca[k]*(1-u)+cb[k]*u) for k in range(3))
                break
        for x in range(SIZE[0]):
            px[x,y] = color
    return im.convert("RGBA")


def light(center, radius, rgb, alpha):
    layer = Image.new("RGBA", SIZE, (0,0,0,0))
    x,y = p(*center)
    r = radius*S
    ImageDraw.Draw(layer).ellipse((x-r,y-r,x+r,y+r), fill=(*rgb,alpha))
    return layer.filter(ImageFilter.GaussianBlur(52*S))


def shape(points, draw, fill, outline=None, width=1):
    draw.polygon(points, fill=fill)
    if outline:
        draw.line(points+[points[0]], fill=outline, width=width*S, joint="curve")


def build(outfile):
    im = gradient()
    im.alpha_composite(light((512,585), 315, (235,126,77), 115))
    im.alpha_composite(light((540,440), 190, (76,124,139), 60))
    d = ImageDraw.Draw(im)

    # A cold moon, thin cloud folds and scattered mineral sparks.
    d.ellipse(b(790,86,870,166), fill=(231,205,164,255))
    d.ellipse(b(803,91,875,163), fill=(248,226,190,255))
    d.ellipse(b(813,107,831,124), fill=(223,199,159,255))
    for _ in range(52):
        x,y = random.randint(35,990),random.randint(45,390)
        r = random.choice((1,1,1,2))
        d.ellipse(b(x-r,y-r,x+r,y+r), fill=(244,218,175,random.randint(100,205)))
    for idx in range(3):
        y=393+idx*29
        stroke_curve(d,(-18,y+25),(75,y-57),(205,y-61),(282,y+2),(225,174,119,70-idx*14),3)
        stroke_curve(d,(742,y+1),(824,y-67),(943,y-54),(1040,y+17),(225,174,119,66-idx*13),3)

    # Wide mineral ledges frame an inland wind-basin without forming a generic mountain range.
    shape([p(0,594),p(73,579),p(151,585),p(220,563),p(285,584),p(284,710),p(0,790)],d,(35,49,64,255))
    shape([p(1024,590),p(948,574),p(876,585),p(807,562),p(744,583),p(739,713),p(1024,790)],d,(33,47,62,255))
    for i in range(6):
        y=620+i*20
        stroke_curve(d,(-10,y),(66,y-18),(169,y+13),(285,y-13),(169,147,133,39),2)
        stroke_curve(d,(741,y-11),(850,y+12),(950,y-20),(1035,y+4),(169,147,133,36),2)

    # A reflective salt-calcite forecourt, broken into broad plates and fine seams.
    shape([p(0,753),p(167,719),p(300,748),p(417,726),p(612,742),p(775,716),p(1024,765),p(1024,1024),p(0,1024)],d,(83,79,77,255))
    shape([p(0,839),p(205,793),p(369,822),p(538,790),p(758,821),p(1024,794),p(1024,1024),p(0,1024)],d,(102,89,82,255))
    # Concentric calcite shelves curve inward toward the bell and its entrance.
    for i in range(5):
        y=812+i*36
        depth=i*13
        stroke_curve(d,(-24,y+83),(102,y+11),(247,y-depth),(421,y-8),(221,184,143,44-i*4),3)
        stroke_curve(d,(603,y-8),(778,y-depth),(921,y+14),(1048,y+77),(221,184,143,42-i*4),3)
    for x,y in ((66,816),(952,829),(129,900),(895,907),(248,987),(778,972)):
        stroke_curve(d,(x,y),(x+26,y-13),(x+48,y+6),(x+74,y+2),(222,190,154,58),2)
    for x,y in ((104,875),(913,860),(183,958),(850,982),(675,911),(346,930)):
        d.polygon([p(x,y-7),p(x+6,y),p(x+1,y+10),p(x-5,y+3)],fill=(226,176,117,145))

    # The destination's flared wind-bell is a single monumental silhouette.
    outline=[]
    outline += curve_points((424,196),(455,161),(569,161),(600,196))
    outline += curve_points((600,196),(633,226),(650,283),(662,342))[1:]
    outline += curve_points((662,342),(676,420),(703,486),(751,553))[1:]
    outline += curve_points((751,553),(778,589),(809,617),(837,645))[1:]
    outline += curve_points((837,645),(806,683),(719,714),(512,722))[1:]
    outline += curve_points((512,722),(305,714),(218,683),(187,645))[1:]
    outline += curve_points((187,645),(215,617),(246,589),(273,553))[1:]
    outline += curve_points((273,553),(321,486),(348,420),(362,342))[1:]
    outline += curve_points((362,342),(374,283),(391,226),(424,196))[1:]
    mask=Image.new("L",SIZE,0)
    ImageDraw.Draw(mask).polygon(outline,fill=255)

    # A dimensional jade-to-copper skin, clipped to the bell's silhouette.
    skin=Image.new("RGBA",SIZE,(0,0,0,0))
    sd=ImageDraw.Draw(skin)
    for x in range(250*S,775*S):
        t=(x-250*S)/(525*S)
        c=(round(28+32*t),round(62+16*t),round(70+3*t),255)
        sd.line([(x,190*S),(x,730*S)],fill=c,width=1)
    shade=Image.new("RGBA",SIZE,(0,0,0,0))
    sh=ImageDraw.Draw(shade)
    sh.ellipse(b(218,285,518,804),fill=(7,18,29,92))
    sh.ellipse(b(538,235,828,735),fill=(220,128,70,49))
    skin=Image.alpha_composite(skin,shade.filter(ImageFilter.GaussianBlur(38*S)))
    skin.putalpha(ImageChops.multiply(skin.getchannel("A"),mask))
    im.alpha_composite(skin)
    d=ImageDraw.Draw(im)
    d.line(outline,fill=(225,167,104,255),width=4*S,joint="curve")

    # Fine lithographic marks make the jade shell feel weathered, not flat.
    body_mask=mask.load()
    stipple=Image.new("RGBA",SIZE,(0,0,0,0))
    td=ImageDraw.Draw(stipple)
    for _ in range(5200):
        x=random.randint(270*S,755*S)
        y=random.randint(250*S,700*S)
        if body_mask[x,y]<200 or (376*S<x<648*S and 382*S<y<493*S) or (298*S<x<727*S and y>525*S):
            continue
        length=random.randint(2,11)*S
        color=(226,174,117,random.randint(16,48)) if random.random()<0.57 else (5,20,29,random.randint(18,45))
        td.line([(x,y),(x+length,y-random.randint(0,2)*S)],fill=color,width=random.choice((1,2))*S)
    stipple.putalpha(ImageChops.multiply(stipple.getchannel("A"),mask))
    im.alpha_composite(stipple)
    d=ImageDraw.Draw(im)

    # Flutes and engraved ribs follow the body into its flared skirt.
    ribs=[(373,250,286),(392,240,303),(630,240,721),(651,250,738)]
    for x0,y0,x1 in ribs:
        stroke_curve(d,(x0,y0),(x0-9,y0+96),(x1+26,363),(x1,385),(222,158,94,144),3)
        stroke_curve(d,(x1,487),(x1+14,540),(x1+19,588),(x1+6,626),(222,158,94,118),3)
        stroke_curve(d,(x0+7,y0),(x0+4,y0+91),(x1+34,361),(x1+10,384),(10,25,34,145),2)
        stroke_curve(d,(x1+10,488),(x1+23,541),(x1+29,589),(x1+16,626),(10,25,34,135),2)
    stroke_curve(d,(390,246),(443,215),(577,215),(634,246),(240,191,126,185),4)
    stroke_curve(d,(313,550),(387,576),(632,576),(711,550),(218,152,93,104),3)

    # The bell crown is visible above the inscription; its clapper stays inside the hall.
    d.ellipse(b(406,180,618,230),fill=(41,69,75,255),outline=(220,163,102,255),width=4*S)
    d.ellipse(b(451,148,573,207),fill=(46,72,77,255),outline=(230,173,107,255),width=4*S)

    # The name is cut into the bell's curved jade face, with no separate sign or plaque.
    titlefont=font(68,True)
    label="KORAVEL"
    advances=[]
    measure=ImageDraw.Draw(Image.new("RGB",(2,2)))
    for ch in label:
        advances.append(measure.textlength(ch,font=titlefont)/S+2)
    total=sum(advances)
    cursor=512-total/2
    for ch,adv in zip(label,advances):
        cx=cursor+adv/2
        u=(cx-512)/280
        cy=455+14*u*u
        angle=math.degrees(math.atan(28*u/280))
        glyph=Image.new("RGBA",(round((adv+18)*S),100*S),(0,0,0,0))
        gd=ImageDraw.Draw(glyph)
        gd.text((8*S,0),ch,font=titlefont,fill=(246,208,145,255),stroke_width=2*S,stroke_fill=(28,43,48,255))
        glyph=glyph.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
        gx,gy=p(cx,cy)
        shadow=Image.new("RGBA",glyph.size,(37,30,29,0))
        shadow.putalpha(glyph.getchannel("A"))
        im.alpha_composite(shadow,(gx-glyph.width//2+2*S,gy-glyph.height//2+3*S))
        im.alpha_composite(glyph,(gx-glyph.width//2,gy-glyph.height//2))
        d=ImageDraw.Draw(im)
        cursor+=adv
    d=ImageDraw.Draw(im)

    # A deep arched opening exposes a real inner street of guest rooms and warm halls.
    aperture=[]
    aperture += curve_points((304,690),(305,638),(316,539),(512,528))
    aperture += curve_points((512,528),(708,539),(719,638),(720,690))[1:]
    aperture += [p(720,705),p(304,705)]
    aperture_mask=Image.new("L",SIZE,0)
    ImageDraw.Draw(aperture_mask).polygon(aperture,fill=255)
    inner=Image.new("RGBA",SIZE,(0,0,0,0))
    q=ImageDraw.Draw(inner)
    q.polygon(aperture,fill=(14,28,38,255))
    q.polygon([p(325,662),p(362,588),p(448,554),p(576,554),p(662,588),p(699,662),p(699,690),p(325,690)],
              fill=(44,52,51,255))
    q.line([p(329,661),p(695,661)],fill=(211,148,84,200),width=3*S)
    # Lodgings are carved into the inside curve; warm light dots every chamber.
    for row,(y,xs,w,h) in enumerate(((574,[371,411,451,491,533,573,613,653],23,30),
                                      (616,[344,386,428,470,554,596,638,680],19,24))):
        for x in xs:
            q.rounded_rectangle(b(x-w/2,y,x+w/2,y+h),radius=5*S,
                                fill=(224,143,78,255),outline=(19,32,40,255),width=3*S)
            q.rectangle(b(x-w/2+5,y+5,x+w/2-5,y+h-4),fill=(255,223,159,255))
            q.line([p(x,y+6),p(x,y+h-4)],fill=(150,92,56,255),width=2*S)
    q.polygon([p(463,688),p(463,622),p(480,591),p(544,591),p(561,622),p(561,688)],
              fill=(89,68,53,255),outline=(233,176,104,255))
    q.arc(b(472,584,552,673),180,360,fill=(246,199,126,255),width=4*S)
    q.rectangle(b(487,627,537,690),fill=(243,160,79,255))
    q.rectangle(b(494,632,530,690),fill=(255,230,172,255))
    q.ellipse(b(500,610,524,635),fill=(255,226,157,255))
    q.polygon([p(506,528),p(518,528),p(522,564),p(512,575),p(502,564)],fill=(169,104,61,255))
    q.ellipse(b(505,557,519,572),fill=(249,190,103,255))
    inner.putalpha(ImageChops.multiply(inner.getchannel("A"),aperture_mask))
    im.alpha_composite(inner)
    im.alpha_composite(light((512,646),145,(243,133,78),62))
    d=ImageDraw.Draw(im)
    d.line(aperture+[aperture[0]],fill=(225,168,103,255),width=5*S,joint="curve")
    # A broad flared stone lip is part of the bell, not a floating platform.
    stroke_curve(d,(210,652),(322,701),(699,701),(814,652),(225,166,101,255),7)
    stroke_curve(d,(219,670),(354,722),(670,722),(805,670),(17,31,40,230),5)

    # The visitor's lantern bridge crosses the lip and ends at the luminous guest hall.
    road=curve_points((513,1027),(463,914),(478,825),(512,745),58)
    road+=curve_points((512,745),(540,700),(518,674),(512,650),28)[1:]
    d.line(road,fill=(22,37,45,255),width=39*S,joint="curve")
    d.line(road,fill=(176,119,77,255),width=26*S,joint="curve")
    d.line(road,fill=(248,198,126,255),width=3*S,joint="curve")
    for idx in range(5,len(road),11):
        x,y=road[idx][0]/S,road[idx][1]/S
        d.ellipse(b(x-4,y-4,x+4,y+4),fill=(255,214,135,255))
    # Guardrail posts catch the same light as the lit windows.
    for idx in range(4,len(road)-4,16):
        x,y=road[idx][0]/S,road[idx][1]/S
        for side in (-1,1):
            d.line([p(x+side*17,y),p(x+side*20,y-17)],fill=(51,53,50,255),width=3*S)
            d.ellipse(b(x+side*17-3,y-21,x+side*17+3,y-15),fill=(255,199,112,255))

    # Silhouettes approach the warm rooms; the scale turns the monument into a visit.
    for x,y in ((469,867),(551,820),(530,754)):
        d.ellipse(b(x-4,y-19,x+4,y-11),fill=(19,30,38,255))
        d.line([p(x,y-11),p(x,y+11)],fill=(19,30,38,255),width=6*S)
        d.line([p(x,y-4),p(x-8,y+3)],fill=(19,30,38,255),width=4*S)
        d.line([p(x,y-4),p(x+8,y+3)],fill=(19,30,38,255),width=4*S)
        d.line([p(x,y+10),p(x-6,y+19)],fill=(19,30,38,255),width=4*S)
        d.line([p(x,y+10),p(x+6,y+19)],fill=(19,30,38,255),width=4*S)

    # Dry, fine grain gives the limited palette a tactile ink-on-paper finish.
    grain=Image.new("RGBA",SIZE,(0,0,0,0))
    gd=ImageDraw.Draw(grain)
    for _ in range(105000):
        x,y=random.randrange(SIZE[0]),random.randrange(SIZE[1])
        if random.random()<0.56:
            color=(244,217,174,random.randint(5,19))
        else:
            color=(7,16,29,random.randint(5,17))
        gd.point((x,y),fill=color)
    im=Image.alpha_composite(im,grain).convert("RGB").resize((W,H),Image.Resampling.LANCZOS)
    im=im.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.FLOYDSTEINBERG)
    im.save(ROOT/outfile,format="PNG",optimize=True)


if __name__=="__main__":
    build(sys.argv[1] if len(sys.argv)>1 else "poster.png")
