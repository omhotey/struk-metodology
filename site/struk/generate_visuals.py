from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64, json, math, hashlib, html
ROOT=Path(__file__).resolve().parent
A=ROOT/'assets'
P={'ink':'#040037','blue':'#2173ea','violet':'#404bff','muted':'#514d7c','line':'#deddeb','soft':'#efeff5','paper':'#f8f9fa'}
class Figure:
 def __init__(self,w,h):
  self.w,self.h=w,h;self.s=2;self.im=Image.new('RGB',(w*2,h*2),P['paper']);self.d=ImageDraw.Draw(self.im);self.svg=[];self.labels=[]
 def font(self,z,bold=False):return ImageFont.truetype(str(A/'fonts'/('Play-Bold.ttf' if bold else 'Play-Regular.ttf')),int(z*self.s))
 def line(self,pts,color=None,width=2,dash=False,arrow=False):
  color=color or P['blue'];scaled=[(x*2,y*2) for x,y in pts]
  if dash:
   for (x1,y1),(x2,y2) in zip(scaled,scaled[1:]):
    length=math.hypot(x2-x1,y2-y1)
    for start in range(0,int(length),22):
     stop=min(start+12,length);self.d.line([(x1+(x2-x1)*start/length,y1+(y2-y1)*start/length),(x1+(x2-x1)*stop/length,y1+(y2-y1)*stop/length)],fill=color,width=width*2)
  else:self.d.line(scaled,fill=color,width=width*2,joint='curve')
  self.svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="6 5"' if dash else '')+'/>')
  if arrow:
   x,y=pts[-1];xp,yp=pts[-2];angle=math.atan2(y-yp,x-xp);size=10
   triangle=[(x,y),(x-size*math.cos(angle-.5),y-size*math.sin(angle-.5)),(x-size*math.cos(angle+.5),y-size*math.sin(angle+.5))]
   self.d.polygon([(a*2,b*2) for a,b in triangle],fill=color);self.svg.append('<polygon points="'+' '.join(f'{a},{b}' for a,b in triangle)+f'" fill="{color}"/>')
 def circle(self,x,y,r,fill):
  self.d.ellipse(((x-r)*2,(y-r)*2,(x+r)*2,(y+r)*2),fill=fill);self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>')
 def rect(self,x,y,w,h,fill):
  self.d.rectangle((x*2,y*2,(x+w)*2,(y+h)*2),fill=fill);self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>')
 def text(self,x,y,t,size=26,bold=False,color=None,align='left',maxw=None):
  f=self.font(size,bold);width=self.d.textlength(t,font=f)/2
  if maxw is not None:assert width<=maxw,(t,width,maxw)
  left=x-width/2 if align=='center' else x
  assert left>=0 and left+width<=self.w,(t,left,width,self.w)
  self.d.text((left*2,y*2),t,font=f,fill=color or P['ink'])
  asc=f.getmetrics()[0]/2;anchor='middle' if align=='center' else 'start'
  self.svg.append(f'<text x="{x}" y="{y+asc}" text-anchor="{anchor}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color or P["ink"]}">{html.escape(t)}</text>')
  self.labels.append({'text':t,'font_size':size,'bounds':[round(left,2),y,round(width,2)]})
 def save(self,name):
  css=''
  for weight,font in [(400,'Play-Regular.ttf'),(700,'Play-Bold.ttf')]:
   data=base64.b64encode((A/'fonts'/font).read_bytes()).decode();css+=f'@font-face{{font-family:Play;src:url(data:font/ttf;base64,{data});font-weight:{weight}}}'
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img"><title>Пять связанных функций СТРУК</title><desc>Основной ход и выборочные возвраты при изменениях, с ориентиром на нужный результат.</desc><style>{css}text{{font-family:Play,sans-serif}}</style><rect width="100%" height="100%" fill="{P["paper"]}"/>'+''.join(self.svg)+'</svg>'
  (A/(name+'.svg')).write_text(svg,encoding='utf-8')
  self.im.save(A/(name+'.webp'),'WEBP',quality=94,method=6)
  return {'file':name+'.webp','width':self.im.width,'height':self.im.height,'source':name+'.svg','logical_width':self.w,'logical_height':self.h,'min_font_size':min(x['font_size'] for x in self.labels),'labels':self.labels}
wide=Figure(1120,760)
wide.text(48,28,'С.Т.Р.У.К.',48,True,color=P['blue'])
wide.text(48,93,'Пять связанных функций',32)
centers=[144,352,560,768,976]
names=['Ситуация','Требования','Решение','Управление','Контроль']
letters=['С','Т','Р','У','К']
questions=[['Что происходит','на самом деле?'],['Что должно','получиться?'],['Как действовать','и почему так?'],['Выполнить','выбранное'],['Сопоставить','с требованиями']]
for i,x in enumerate(centers):
 if i<4:wide.line([(x+53,220),(centers[i+1]-53,220)],width=2,arrow=True)
 wide.circle(x,220,44,P['soft']);wide.text(x,182,letters[i],62,True,color=P['blue'],align='center')
 wide.text(x,283,names[i],28,True,align='center',maxw=202)
 for j,t in enumerate(questions[i]):wide.text(x,327+j*34,t,26,align='center',maxw=202)
for source,target,yy in [(768,144,430),(976,352,474),(976,560,518)]:wide.line([(source,390),(source,yy),(target,yy),(target,397)],color=P['violet'],width=2,dash=True,arrow=True)
for y,left,right in [(554,'Новое обстоятельство','Ситуация'),(592,'Изменились требования','Требования'),(630,'Способ не подошёл','Решение')]:
 wide.text(48,y,left,26,color=P['muted'],maxw=405);wide.line([(466,y+22),(508,y+22)],color=P['violet'],arrow=True);wide.text(530,y,right,26,color=P['muted'])
wide.rect(48,692,1024,48,P['ink']);wide.text(560,697,'Ориентир — нужный результат',28,True,color='#ffffff',align='center')
wm=wide.save('functions-map-wide')
m=Figure(400,1150);m.text(22,23,'С.Т.Р.У.К.',34,True,color=P['blue']);m.text(22,70,'Пять связанных функций',24)
for i,y in enumerate([162,292,422,552,682]):
 if i<4:m.line([(57,y+43),(57,y+90)],arrow=True)
 m.circle(57,y,33,P['soft']);m.text(57,y-29,letters[i],46,True,color=P['blue'],align='center')
 m.text(108,y-32,names[i],27,True,maxw=272)
 for j,t in enumerate(questions[i]):m.text(108,y+8+j*29,t,23,maxw=272)
m.text(22,803,'Если условия изменились',25,True,maxw=360)
for y,left,right in [(856,'Новое обстоятельство','С'),(900,'Изменились требования','Т'),(944,'Способ не подошёл','Р')]:
 m.text(22,y,left,23,color=P['muted'],maxw=300);m.line([(330,y+19),(350,y+19)],color=P['violet'],arrow=True);m.text(370,y,right,23,True,color=P['blue'],align='center')
m.rect(20,1024,360,96,P['ink']);m.text(200,1034,'Ориентир —',27,True,color='#ffffff',align='center');m.text(200,1071,'нужный результат',27,True,color='#ffffff',align='center')
mm=m.save('functions-map-mobile')
for original,output,maxsize in [('release-story-original.png','release-story.webp',(1254,1254)),('product-stories-original.png','product-stories-wide.webp',(1536,1024)),('product-stories-mobile-original.png','product-stories-mobile.webp',(1024,1536))]:
 im=Image.open(A/original).convert('RGB');im.thumbnail(maxsize,Image.Resampling.LANCZOS);im.save(A/output,'WEBP',quality=90,method=6)
figures=[
 {'id':'functions-map','wide':'functions-map-wide.webp','mobile':'functions-map-mobile.webp','alt':'Пять функций СТРУК: ситуация, требования, решение, управление и контроль. При изменениях возможны выборочные возвраты к затронутым функциям.','caption':'При новых обстоятельствах можно вернуться к затронутой функции и пересмотреть дальнейшее действие.'},
 {'id':'goal-check','wide':'release-story.webp','mobile':None,'alt':'Иллюстрация: машина выпустила продукт с праздничным флажком, но разрыв на пути мешает доставить его ожидающему пользователю.','caption':'Релиз состоялся, а путь пользователя всё ещё прерван.'},
 {'id':'product-routes','wide':'product-stories-wide.webp','mobile':'product-stories-mobile.webp','alt':'Три продуктовые ситуации: изучение механизма через лупу, сборка нового продукта и восстановление связей в существующем.','caption':'Диагностика, создание и работа с проблемным продуктом требуют разных действий и результатов.'}
]
files={}
for f in figures:
 for file in [f['wide'],f['mobile']]:
  if file and file not in files:
   im=Image.open(A/file);files[file]={'width':im.width,'height':im.height,'sha256':hashlib.sha256((A/file).read_bytes()).hexdigest(),'bytes':(A/file).stat().st_size}
manifest={'edition':'visuals-1','site_style_source':'https://yuriystruk.ru/','palette':P,'font':'Play','font_source':'https://github.com/google/fonts/tree/main/ofl/play','font_license':'fonts/OFL.txt','figures':figures,'files':files,'diagram_metrics':{'wide':wm,'mobile':mm},'viewport_breakpoint_px':767,'browser_page_visual_checked':False}
previous_path=A/'manifest.json'
if previous_path.exists():
 previous=json.loads(previous_path.read_text(encoding='utf-8'))
 if previous.get('files')==files:
  manifest={**previous,**manifest}
(A/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'figures':len(figures),'files':files,'diagram_smallest_text_css_at_320px':23*320/400},ensure_ascii=False,indent=2))
