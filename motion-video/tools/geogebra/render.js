const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:960,height:540}});
await p.goto('file://'+process.argv[2]);await p.waitForFunction('window.done===true',{timeout:120000});await p.waitForTimeout(4000);
await p.screenshot({path:process.argv[3]});await b.close();console.log('ok');})().catch(e=>{console.error(e.message);process.exit(1)});
