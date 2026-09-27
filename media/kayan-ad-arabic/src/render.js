const puppeteer=require('puppeteer-core'),fs=require('fs'),path=require('path');
const W=__dirname+'/';const mode=process.argv[2]||'all';
(async()=>{
 const b=await puppeteer.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',headless:true,
   args:['--allow-file-access-from-files','--no-sandbox','--disable-web-security']});
 const p=await b.newPage();await p.setViewport({width:1080,height:1920});
 p.on('console',m=>console.log('PAGE',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+W+'compose.html');
 await p.evaluate(()=>Promise.all([document.fonts.load("700 70px 'IBM Plex Sans Arabic'",'إدارة'),document.fonts.load('700 26px Inter','12')]));
 await p.evaluate(()=>new Promise(r=>{const l=document.getElementById('LOGO');l.complete?r():l.onload=r;}));
 console.log('fontok',await p.evaluate(()=>document.fonts.check("700 70px 'IBM Plex Sans Arabic'",'إدارة')));
 const FPS=30,TOTAL=9.6,N=Math.round(TOTAL*FPS);
 let times=mode==='all'?[...Array(N).keys()].map(i=>i/FPS):process.argv.slice(3).map(Number);
 const od=W+(mode==='all'?'out/':'prev/');fs.mkdirSync(od,{recursive:true});
 for(const [k,t] of times.entries()){
   const fi=Math.min(240,Math.floor(t*FPS+1e-6)+1);
   await p.evaluate(s=>window.setFrame(s),'file://'+W+'vfr/'+String(fi).padStart(5,'0')+'.jpg');
   const d=await p.evaluate(t=>{window.draw(t);return window.shot(0.93);},t);
   fs.writeFileSync(od+(mode==='all'?String(k+1).padStart(5,'0'):'p'+t.toFixed(2))+'.jpg',Buffer.from(d.split(',')[1],'base64'));
 }
 await b.close();
})();
