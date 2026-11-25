#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Патч веб-интерфейса CraftBeerPi4 (пакет cbpi4gui, файл main.*.js).

Команды (обычно запускаются как `sudo cbpi4-ui-patch <команда>`):
  apply      применить патч (сначала сохраняется копия оригинала main.*.js.orig)
  restore    вернуть оригинальный файл
  status     показать, где лежит файл и применён ли патч
  uninstall  вернуть оригинал и удалить сам патчер

Параметр --file ПУТЬ позволяет указать файл main.*.js вручную.
Настройки лежат в settings.py рядом со скриптом (шаблон: settings_default.py).
"""
import os, re, sys, glob, shutil, runpy, subprocess, argparse

HERE = os.path.dirname(os.path.realpath(__file__))
MARK = "/* cbpi4-ui-patch applied */"


# ---------------------------------------------------------------- настройки
def load_settings():
    base = runpy.run_path(os.path.join(HERE, "settings_default.py"))
    sizes = dict(base["SIZES"])
    user_file = os.path.join(HERE, "settings.py")
    if os.path.exists(user_file):
        user = runpy.run_path(user_file)
        for name in ("COLORS", "FONTS"):
            if name in user:
                print(f"Внимание: {name} в settings.py больше не используется. Цвета и шрифты теперь "
                      "настраиваются в Settings CraftBeerPi4 (плагин cbpi4-UITheme), вкладка UI Theme.")
        for k, v in user.get("SIZES", {}).items():
            if k not in sizes:
                print(f"Предупреждение: неизвестный параметр SIZES[{k!r}] в settings.py, пропущен")
            else:
                sizes[k] = v
    return sizes


# ---------------------------------------------------------------- патч текста
def apply_patches(s, Z):
    """Возвращает пропатченный текст main.js. При несовпадении кода завершает работу с ошибкой."""

    def rep(old, new, count=1):
        nonlocal s
        n = s.count(old)
        if n != count:
            fail(f"ожидалось {count} вхождений, найдено {n}:\n  {old[:90]}")
        s = s.replace(old, new)

    def crep(pattern, repl, count=1):
        """Замена по регулярному выражению (для цветов: подходит любой исходный цвет)."""
        nonlocal s
        s, n = re.subn(pattern, repl, s)
        if n != count:
            fail(f"ожидалось {count} вхождений, найдено {n}:\n  {pattern[:90]}")

    def fail(msg):
        sys.exit("ОШИБКА: этот файл интерфейса отличается от того, для которого сделан патч "
                 "(протестировано: cbpi4gui 0.5.0, main.65b608fc.js).\n" + msg +
                 "\nФайл не изменён.")

    def px(v): return f"{v}px"
    def rem(v): return f"{v}rem"

    # ---------- 1. Кнопка Actor: фиксированная ширина группы ----------
    rep('(0,s.jsxs)(Zt.A,{children:[', '(0,s.jsxs)(GRP,{fullWidth:!0,pm:PMP,children:[', 4)
    EXTRA = 'fontVariantNumeric:"tabular-nums",whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis"'
    rep('{fontSize:h.props.size+"px",fontWeight:h.props.fontweight||"normal"}',
        '{fontSize:h.props.size+"px",fontWeight:h.props.fontweight||"normal",' + EXTRA + '}')
    rep('{fontSize:"12px",fontWeight:"normal"}',
        '{fontSize:"12px",fontWeight:"normal",' + EXTRA + '}')

    # ---------- 2. Диалоги мощности (Power и Output) ----------
    rep('(0,s.jsxs)(et.A,{fullWidth:!0,onClose:k,',
        '(0,s.jsxs)(et.A,{fullWidth:!0,sx:{"& .MuiDialog-paper":{width:"min(%s,96vw)",maxWidth:"96vw"}},onClose:k,'
        % px(Z["power_dlg_width_px"]), 2)
    NUM = 'sx:{fontSize:"%s",lineHeight:1.2},' % rem(Z["power_value_rem"])
    rep('variant:"h2",component:"h2",gutterBottom:!0,children:[a,"%"]',
        'variant:"h2",component:"h2",' + NUM + 'gutterBottom:!0,children:[a,"%"]')
    rep('variant:"h2",component:"h2",gutterBottom:!0,children:m',
        'variant:"h2",component:"h2",' + NUM + 'gutterBottom:!0,children:m')
    _th = Z["power_slider_thick_px"]; _tb = Z["power_slider_thumb_px"]
    SL = ('sx:{mt:3,mb:6,mx:"%dpx",width:"calc(100%% - %dpx)",height:%d,'
          '"& .MuiSlider-rail":{height:%d},"& .MuiSlider-track":{height:%d},'
          '"& .MuiSlider-thumb":{width:%d,height:%d},'
          '"& .MuiSlider-mark":{height:%d,width:3},'
          '"& .MuiSlider-markLabel":{fontSize:"%s",top:%d}},'
          % (_tb // 2, _tb, _th, _th, _th, _tb, _tb, _th, rem(Z["power_slider_marks_rem"]), _tb - 8))
    rep('Wt,{min:l,max:u,marks:p,step:1,value:a,', 'Wt,{' + SL + 'min:l,max:u,marks:p,step:1,value:a,')
    rep('Wt,{min:v,max:x,marks:_,step:1,value:m,', 'Wt,{' + SL + 'min:v,max:x,marks:_,step:1,value:m,')
    BTN = 'size:"large",sx:{fontSize:"%s",m:2,px:%s,py:%s},' % (rem(Z["power_btn_font_rem"]), Z["power_btn_pad_x"], Z["power_btn_pad_y"])
    rep('variant:"contained",onClick:k,color:"secondary",autoFocus:!0,children:"Cancel"',
        'variant:"contained",' + BTN + 'onClick:k,color:"secondary",autoFocus:!0,children:"Cancel"', 2)
    for fn in ("T", "S"):
        rep('variant:"contained",onClick:%s,color:"primary",autoFocus:!0,children:"Set"' % fn,
            'variant:"contained",' + BTN + 'onClick:%s,color:"primary",autoFocus:!0,children:"Set"' % fn)
    TT = 'sx:{fontSize:"%s"},' % rem(Z["power_dlg_title_rem"])
    rep('children:["Set Power ",r.name," "]', TT + 'children:["Set Power ",r.name," "]')
    rep('children:["Set Output ",r.name," "]', TT + 'children:["Set Output ",r.name," "]')

    # ---------- 3. Уведомления без кнопок ----------
    _f = rem(Z["toast_font_rem"])
    rep('style:{position:"absolute",bottom:10,right:30},severity:e.type||"info"',
        'style:{position:"fixed",bottom:%d,right:%d,zIndex:2000,minWidth:%d,maxWidth:"90vw",'
        'padding:"14px 24px",boxShadow:"0 4px 20px rgba(0,0,0,.5)"},'
        'sx:{fontSize:"%s","& .MuiAlert-icon":{fontSize:"%s",alignItems:"center"},'
        '"& .MuiAlert-message, & .MuiAlert-message *":{fontSize:"%s"}},'
        'severity:e.type||"info"'
        % (Z["toast_bottom_px"], Z["toast_right_px"], Z["toast_min_width_px"], _f, rem(Z["toast_icon_rem"]), _f))
    rep('setTimeout(()=>{o(e)},r)', 'setTimeout(()=>{o(e)},Math.max(r,%d))' % (Z["toast_time_sec"] * 1000))

    # ---------- 4. Уведомления с кнопками (центральный диалог) ----------
    _h = ',minHeight:"%s"' % px(Z["alert_height_px"]) if Z["alert_height_px"] else ''
    rep('(0,_.jsxs)(j.A,{open:!0,"aria-labelledby":"alert-dialog-title"',
        '(0,_.jsxs)(j.A,{open:!0,fullWidth:!0,sx:{"& .MuiDialog-paper":{width:"min(%s,96vw)",maxWidth:"96vw",maxHeight:"96vh",padding:"%s"%s}},"aria-labelledby":"alert-dialog-title"'
        % (px(Z["alert_width_px"]), px(Z["alert_pad_px"]), _h))
    rep('(0,_.jsx)(B.A,{id:"alert-dialog-title",children:t.title})',
        '(0,_.jsx)(B.A,{id:"alert-dialog-title",sx:{fontSize:"%s"},children:t.title})' % rem(Z["alert_title_rem"]))
    rep('(0,_.jsx)(F.A,{id:"alert-dialog-description",children:(n=t.message',
        '(0,_.jsx)(F.A,{id:"alert-dialog-description",sx:{fontSize:"%s","& *":{fontSize:"inherit"}},children:(n=t.message' % rem(Z["alert_text_rem"]))
    rep('(0,_.jsx)(D.A,{onClick:()=>{return n=t.id,i=e.id',
        '(0,_.jsx)(D.A,{size:"large",variant:"contained",sx:{fontSize:"%s",px:5,py:1.5,m:1},onClick:()=>{return n=t.id,i=e.id' % rem(Z["alert_btn_font_rem"]))

    # ---------- 5. Кнопки -/+ внутри существующего элемента Actor ----------
    # Новые свойства элемента: plusminus (yes/no) и step (шаг, %)
    rep('{name:"powerslider",options:["Power","Output","No"],default:"No",type:"select"}]},{name:"Led"',
        '{name:"powerslider",options:["Power","Output","No"],default:"No",type:"select"},'
        '{name:"plusminus",options:["yes","no"],default:"no",type:"select"},'
        '{name:"step",default:"1",type:"number",unit:"%"}]},{name:"Led"')
    rep('[k,T]=(0,d.useState)("N/V");return(0,d.useMemo)(()=>{var e;let t={width:h.width',
        '[k,T]=(0,d.useState)("N/V"),'
        'PMR=(0,d.useRef)(null),PMT=(0,d.useRef)(null),'
        'PMA=e=>{if(!f||p)return;const t=Math.max(1,Number(h.props&&h.props.step)||1);'
        'let r=null!==PMR.current?PMR.current:(f.power>=0?f.power:0);'
        'r=Math.min(100,Math.max(0,r+e*t));PMR.current=r;u.actions.set_actor_power(f.id,r);'
        'clearTimeout(PMT.current);PMT.current=setTimeout(()=>{PMR.current=null},3e3)},'
        'GRP=(0,d.useMemo)(()=>function(e){let{pm:q,bare:z,children:c,...r}=e;'
        'const H=(0,d.useRef)({t:null,i:null}).current,'
        'X=()=>{clearTimeout(H.t);clearInterval(H.i);H.t=H.i=null},'
        'B=n=>({onPointerDown:e=>{e.preventDefault();X();n();H.t=setTimeout(()=>{H.i=setInterval(n,'
        + str(Z["pm_hold_repeat_ms"]) + ')},' + str(Z["pm_hold_delay_ms"]) + ')},'
        'onPointerUp:X,onPointerLeave:X,onPointerCancel:X,onContextMenu:e=>e.preventDefault()}),'
        'S={minWidth:0,width:"' + str(Z["pm_button_width_pct"]) + '%",flex:"0 0 ' + str(Z["pm_button_width_pct"]) + '%",'
        'fontSize:"' + str(Z["pm_symbol_size_em"]) + 'em",'
        'fontWeight:"bold",touchAction:"none",userSelect:"none"},'
        'A={"&:active":{backgroundColor:"primary.main",color:"primary.contrastText"}};'
        '(0,d.useEffect)(()=>X,[]);'
        'const i=Array.isArray(c)?c:[c];'
        'if(!q||!q.on)return z?i[0]:(0,s.jsxs)(Zt.A,{...r,children:i});'
        'return(0,s.jsxs)(Zt.A,{...r,children:[(0,s.jsx)(Xt.A,{key:"pmm",disabled:q.dis,...B(q.dec),color:"primary",'
        'variant:"outlined",style:S,sx:A,children:"\\u2212"}),'
        '...i,(0,s.jsx)(Xt.A,{key:"pmp",disabled:q.dis,...B(q.inc),color:"primary",'
        'variant:"outlined",style:S,sx:A,children:"+"})]})},[]);'
        'return(0,d.useMemo)(()=>{var e;const PMP={on:"yes"===(h.props&&h.props.plusminus),dis:p||!f,'
        'dec:()=>PMA(-1),inc:()=>PMA(1)};let t={width:h.width')
    # ---------- 1б. Кнопки молнии (Set Power) и трёх точек (Actions): узкие, как в оригинале ----------
    _w = '%s%%' % Z["side_button_width_pct"]
    _sb = 'style:{minWidth:0,width:"%s",flex:"0 0 %s",padding:0},' % (_w, _w)
    rep('onClick:L,color:"primary",startIcon:(0,s.jsx)(er,{}),size:"small",',
        'onClick:L,color:"primary",startIcon:(0,s.jsx)(er,{}),size:"small",' + _sb +
        'sx:{"& .MuiButton-startIcon":{m:0},"& .MuiButton-startIcon > *":{fontSize:(+(h.props.size)||12)*%s+"px !important"}},' % Z["icon_size_ratio"], 2)
    _dots = '(0,s.jsx)(i.A,{title:"Actions",children:(0,s.jsx)(Xt.A,{disabled:p,onClick:E,color:"primary",size:"small",'
    if Z["hide_actions_button"]:
        # убираем кнопку с тремя точками целиком (null в списке детей ButtonGroup игнорируется)
        s, n = re.subn(re.escape(_dots) + r'"aria-label":"select merge strategy","aria-haspopup":"menu",children:\(0,s\.jsx\)\(Kt,\{\}\)\}\)\}\)', 'null', s)
        if n != 3:
            fail(f"ожидалось 3 вхождений кнопки Actions, найдено {n}")
    else:
        rep(_dots, _dots + _sb + 'sx:{"& svg":{fontSize:(+(h.props.size)||12)*%s+"px"}},' % Z["icon_size_ratio"], 3)

    rep('(0,s.jsx)("div",{style:t,children:(0,s.jsx)(Xt.A,{disabled:p,onClick:o,fullWidth:!0,variant:n,color:r,children:(0,s.jsxs)("div",{style:M(),children:[" ",l()," "]})})})',
        '(0,s.jsx)("div",{style:t,children:(0,s.jsx)(GRP,{fullWidth:!0,bare:!0,pm:PMP,children:(0,s.jsx)(Xt.A,{disabled:p,onClick:o,fullWidth:!0,variant:n,color:r,children:(0,s.jsxs)("div",{style:M(),children:[" ",l()," "]})})})})')
    rep('(0,s.jsxs)("div",{style:t,children:[(0,s.jsx)(i.A,{title:f?f.name:"",children:(0,s.jsx)(Xt.A,{disabled:p,onClick:o,fullWidth:!0,variant:n,color:r,children:(0,s.jsxs)("div",{style:M(),children:[" ",l()," (",k,") "]})})}),(0,s.jsx)(Ar,',
        '(0,s.jsxs)("div",{style:t,children:[(0,s.jsx)(GRP,{fullWidth:!0,bare:!0,pm:PMP,children:(0,s.jsx)(i.A,{title:f?f.name:"",children:(0,s.jsx)(Xt.A,{disabled:p,onClick:o,fullWidth:!0,variant:n,color:r,children:(0,s.jsxs)("div",{style:M(),children:[" ",l()," (",k,") "]})})})}),(0,s.jsx)(Ar,')
    rep('},[null===(r=h.props)||void 0===r?void 0:r.actor,null===(n=h.props)||void 0===n?void 0:n.size,',
        '},[h.props&&h.props.plusminus,h.props&&h.props.step,null===(r=h.props)||void 0===r?void 0:r.actor,null===(n=h.props)||void 0===n?void 0:n.size,')


    return MARK + "\n" + s


# ---------------------------------------------------------------- поиск файла
def find_targets():
    """Ищет main.*.js интерфейса CraftBeerPi4 во всей системе (виртуальные окружения тоже)."""
    cache = os.path.join(HERE, ".target")
    if os.path.exists(cache):
        paths = [p for p in open(cache).read().split("\n") if p and os.path.exists(p)]
        if paths:
            return paths
    cmd = ["find", "/", "(", "-path", "/proc", "-o", "-path", "/sys", "-o", "-path", "/dev", ")", "-prune",
           "-o", "-type", "f", "-name", "main.*.js", "-print"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()
    found = []
    for p in out:
        if "/static/js/" in p and ("cbpi4gui" in p or "cbpi4ui" in p):
            try:
                if "ActorButton" in open(p, encoding="utf-8", errors="ignore").read():
                    found.append(p)
            except OSError:
                pass
    if found:
        try:
            open(cache, "w").write("\n".join(found))
        except OSError:
            pass
    return found


def targets(args):
    if args.file:
        return [args.file]
    found = find_targets()
    if not found:
        sys.exit("Файл интерфейса не найден. Укажите его вручную: --file /путь/к/main.XXXX.js")
    return found


# ---------------------------------------------------------------- команды
def read(p):
    return open(p, encoding="utf-8").read()


def write(p, text):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    shutil.copymode(p, tmp)
    os.replace(tmp, p)


def io_guard(fn, *a):
    try:
        return fn(*a)
    except PermissionError:
        sys.exit("Нет прав на запись. Запустите команду с sudo.")


def cmd_apply(args):
    Z = load_settings()
    for p in targets(args):
        orig = p + ".orig"
        cur = read(p)
        if cur.startswith(MARK):
            if not os.path.exists(orig):
                sys.exit(f"{p}: патч уже применён, но копии оригинала (.orig) нет. "
                         "Переустановите интерфейс: pip install --force-reinstall cbpi4gui")
            base = read(orig)
        else:
            base = cur
            io_guard(shutil.copy2, p, orig)      # свежий оригинал (в т.ч. после переустановки пакета)
        io_guard(write, p, apply_patches(base, Z))
        gz = p + ".gz"
        print(f"Патч применён: {p}")
        if os.path.exists(gz):
            print(f"Внимание: рядом есть {gz}, удалите его, иначе сервер может отдавать старую версию.")
    print("Обновите страницу в браузере с очисткой кеша (Ctrl+F5). Перезапуск CraftBeerPi не нужен.")


def cmd_restore(args, quiet=False):
    ok = False
    for p in targets(args):
        orig = p + ".orig"
        if not os.path.exists(orig):
            print(f"{p}: копии оригинала нет, " + ("патч, похоже, не применялся." if not read(p).startswith(MARK)
                  else "восстановите вручную: pip install --force-reinstall cbpi4gui"))
            continue
        io_guard(shutil.copy2, orig, p)
        io_guard(os.remove, orig)
        print(f"Оригинал восстановлен: {p}")
        ok = True
    if ok and not quiet:
        print("Обновите страницу в браузере с очисткой кеша (Ctrl+F5).")


def cmd_status(args):
    for p in targets(args):
        applied = read(p).startswith(MARK)
        print(p)
        print("  патч:", "применён" if applied else "не применён")
        print("  копия оригинала:", "есть" if os.path.exists(p + ".orig") else "нет")


def cmd_uninstall(args):
    cmd_restore(args, quiet=True)
    if HERE == "/opt/cbpi4-ui-patch":
        launcher = "/usr/local/bin/cbpi4-ui-patch"
        io_guard(shutil.rmtree, HERE)
        if os.path.exists(launcher):
            io_guard(os.remove, launcher)
        print("Патчер удалён. Оригинальный интерфейс восстановлен. Обновите страницу (Ctrl+F5).")
    else:
        print("Оригинал восстановлен. Сам скрипт лежит не в /opt/cbpi4-ui-patch, удалите его вручную.")


def main():
    ap = argparse.ArgumentParser(description="Патч интерфейса CraftBeerPi4")
    ap.add_argument("command", choices=["apply", "restore", "status", "uninstall"])
    ap.add_argument("--file", help="путь к main.*.js (по умолчанию ищется автоматически)")
    args = ap.parse_args()
    {"apply": cmd_apply, "restore": cmd_restore, "status": cmd_status, "uninstall": cmd_uninstall}[args.command](args)


if __name__ == "__main__":
    main()
