'use strict';
const fs=require('node:fs'), path=require('node:path'),crypto=require('node:crypto');
const {createNative}=require('D:/Project/YuriyStruk/YS Code/tools/editor-persistence-20261023/native-environment.cjs');
const base=__dirname, hash=s=>crypto.createHash('sha256').update(s).digest('hex');
(async()=>{
 const p=JSON.parse(fs.readFileSync(path.join(base,'production-draft.json'),'utf8'));
 const manifest=JSON.parse(fs.readFileSync(path.join(base,'assets/manifest.json'),'utf8'));
 const receipt=JSON.parse(fs.readFileSync(path.join(base,'production-admin-receipt.json'),'utf8'));
 const ids=[['functions-map',947,'functions-map-mobile.webp','400px'],['goal-check',948,'release-story.webp','640px'],['product-routes',950,'product-stories-mobile.webp','640px']];
 const config=ids.map(([key,id,file,width])=>{const f=manifest.figures.find(x=>x.id===key),upload=receipt.uploads.find(x=>x.id===id);return{key,id,url:upload.url,alt:f.alt,caption:f.caption,width,fixtureFile:file}});
 const n=await createNative();
 try{
  await n.page.route('**/*', async route=>{const match=config.find(x=>x.url===route.request().url());if(match)await route.fulfill({status:200,contentType:'image/webp',body:fs.readFileSync(path.join(base,'assets',match.fixtureFile))});else await route.abort();});
  await n.page.evaluate(()=>{wp.blockLibrary.registerCoreBlocks();wp.apiFetch.use(()=>Promise.resolve({}));});
  const result=await n.page.evaluate(async cfg=>{
   const blocks=cfg.map(x=>wp.blocks.createBlock('core/image',{id:x.id,url:x.url,alt:x.alt,caption:x.caption,sizeSlug:'full',linkDestination:'none',align:'center',width:x.width,height:'auto',style:{spacing:{margin:{top:'2em',bottom:'2em'}}},metadata:{name:'Иллюстрация СТРУК — '+x.key}}));
   const rows=blocks.map((b,i)=>{const saved=wp.blocks.serialize([b]),parsed=wp.blocks.parse(saved)[0];if(!parsed?.isValid||parsed.name!=='core/image'||parsed.attributes.id!==cfg[i].id||parsed.attributes.alt!==cfg[i].alt||String(parsed.attributes.caption)!==cfg[i].caption||wp.blocks.serialize([parsed])!==saved)throw Error(JSON.stringify({expected:cfg[i],parsedAttrs:parsed?.attributes,valid:parsed?.isValid,saved,reSaved:wp.blocks.serialize([parsed]),issues:parsed?.validationIssues}));return{key:cfg[i].key,id:cfg[i].id,url:cfg[i].url,alt:cfg[i].alt,caption:cfg[i].caption,block:saved,attrs:parsed.attributes,valid:true}});
   const before=wp.blocks.serialize(blocks);
   await wp.data.dispatch('core/editor').setupEditor({id:951,type:'post',status:'draft',title:'Isolated image-block verification',content:before,excerpt:'',meta:{}},{});
   const {createElement,useState,createRoot}=wp.element;
   window.__strukInitial=blocks;
   function App(){const [value,setValue]=useState(blocks);return createElement(wp.blockEditor.BlockEditorProvider,{value,onInput:setValue,onChange:setValue,useSubRegistry:false,settings:{allowedBlockTypes:true,hasUploadPermissions:true,canLockBlocks:false}},createElement(wp.blockEditor.BlockList));}
   createRoot(document.getElementById('native-editor')).render(createElement(App));
   return{rows,roundtrip:true,coreImageEdit:typeof wp.blocks.getBlockType('core/image').edit};
  },config);
  await n.page.waitForFunction(()=>document.querySelectorAll('[data-type="core/image"]').length>=3,{},{timeout:15000});
  await n.page.waitForFunction(()=>[...document.querySelectorAll('[data-type="core/image"] img')].length===3&&[...document.querySelectorAll('[data-type="core/image"] img')].every(i=>i.complete&&i.naturalWidth>0));
  for(let i=0;i<config.length;i++){const caption=n.page.locator('[data-type="core/image"] figcaption').nth(i);await caption.fill(config[i].caption+' [temporary native edit]');await n.page.waitForFunction(({i,text})=>String(wp.data.select('core/block-editor').getBlocks()[i].attributes.caption)===text,{i,text:config[i].caption+' [temporary native edit]'});await caption.fill(config[i].caption);await n.page.waitForFunction(({i,text})=>String(wp.data.select('core/block-editor').getBlocks()[i].attributes.caption)===text,{i,text:config[i].caption});}
  const ui=await n.page.evaluate(()=>{
   const rows=wp.data.select('core/block-editor').getBlocks().map(b=>({clientId:b.clientId,name:b.name,id:b.attributes.id,valid:b.isValid}));
   const resizable=document.querySelectorAll('.components-resizable-box__container,.block-library-image__resize-container').length;
   for(const first of wp.data.select('core/block-editor').getBlocks()){const width=first.attributes.width;wp.data.dispatch('core/block-editor').updateBlockAttributes(first.clientId,{width:'380px'});
   const updated=wp.data.select('core/block-editor').getBlock(first.clientId);const saved=wp.blocks.serialize([updated]);const parsed=wp.blocks.parse(saved)[0];
   if(parsed.attributes.width!=='380px'||!parsed.isValid)throw Error('EDIT_RESIZE_NOT_PERSISTED');
   wp.data.dispatch('core/block-editor').updateBlockAttributes(first.clientId,{width});}
   return{imageBlockDOM:document.querySelectorAll('[data-type="core/image"]').length,rows,resizable,resizeEditAndRoundtrip:true,allThreeCaptionsEditedThroughNativeDOMAndRestored:true,editableCaptions:document.querySelectorAll('figcaption[contenteditable="true"]').length};
  });
  const out={schema:'struk.native-images/1',targetPost:951,status:'ISOLATED_NATIVE_EDITOR_VERIFIED',source_sha256:p.source_sha256,production_baseline_sha256:receipt.content_sha256,rows:result.rows,checks:{roundtrip:result.roundtrip,editComponent:result.coreImageEdit,...ui},scope:'Isolated actual WordPress core block editor using existing local copies of public site JS; no production editor session, no network or site writes.',network:'No remote network: approved image URLs served from local fixtures, other requests blocked',mobilePolicy:'Use existing vertical compositions947/950 on all screens; no picture switch, no added runtime/plugin;946/949 remain in media library.',errors:n.errors.map(x=>x.message)};
  fs.writeFileSync(path.join(base,'native-images-r053.json'),JSON.stringify(out,null,2)+'\n');
  console.log(JSON.stringify({status:out.status,checks:out.checks,errors:out.errors,blocks:out.rows.length}));
 }finally{await n.browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
