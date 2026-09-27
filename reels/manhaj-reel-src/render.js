const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
  const mode=process.argv[2]||'stills';
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
  const pg=await b.newPage({viewport:{width:1080,height:1920}});
  pg.on('pageerror',e=>console.log('ERR',e.message));
  await pg.goto('file://'+__dirname+'/reel.html');
  await pg.waitForFunction('window.ready===true');
  if(mode==='stills'){
    const ts=process.argv.slice(3).map(Number);
    fs.mkdirSync('stills',{recursive:true});
    for(const t of ts){await pg.evaluate(t=>render(t),t);await pg.screenshot({path:`stills/t${t.toFixed(2)}.jpg`,type:'jpeg',quality:80});}
  } else {
    fs.mkdirSync('out',{recursive:true});
    const dur=await pg.evaluate('DURATION');const fps=30;const n=Math.round(dur*fps);
    for(let i=0;i<n;i++){await pg.evaluate(t=>render(t),i/fps);await pg.screenshot({path:`out/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});if(i%60==0)console.log(i,'/',n);}
  }
  await b.close();
})();
