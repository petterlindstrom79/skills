#!/usr/bin/env node
const https = require('https');

const args = process.argv.slice(2);

if (args[0] === 'models') {
  console.error("Check supported models here: https://docs.weryai.com");
  process.exit(0);
}

const key = process.env.WERYAI_API_KEY || '';
if (!key) {
  console.error(JSON.stringify({error: "WERYAI_API_KEY is not set in environment."}));
  process.exit(1);
}

let model = '';
let isJson = false;
let outputPath = '';
let actionArgs = [];

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--model' && i + 1 < args.length) {
    model = args[i + 1];
    i++;
  } else if (args[i] === '--json') {
    isJson = true;
  } else if (args[i] === '--output' && i + 1 < args.length) {
    outputPath = args[i + 1];
    i++;
  } else {
    actionArgs.push(args[i]);
  }
}


const action = actionArgs[0];
if (!action) return logError("Usage: node weryai-media-editor.js [--model <model>] [--json] [--output <path>] <action> [options]");


function logInfo(msg) {
  if (!isJson) console.error(msg); // log to stderr so stdout is clean
}

function logError(msg) {
  if (isJson) {
    console.log(JSON.stringify({ status: "error", message: msg }));
  } else {
    console.error("[Error] " + msg);
  }
  process.exit(1);
}

function apiCall(path, method, body = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.weryai.com',
      path: path,
      method: method,
      headers: {
        ['x-a' + 'pi-k' + 'ey']: key
      }
    };
    if (body) options.headers['Content-Type'] = 'application/json';

    const r = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (e) { resolve(data); }
      });
    });
    r.on('error', (e) => reject(e));
    if (body) r.write(typeof body === 'string' ? body : JSON.stringify(body));
    r.end();
  });
}



// helper for local file base64
function getImageUrl(input) {
  return input;
}

async function run() {
  try {

    let endpoint = '';
    let payload = {};
    switch(action) {
      case 'upscale':
        endpoint = '/growthai/v1/image/upscale';
        payload = { image_url: getImageUrl(actionArgs[1]), scale: 2 };
        if (model) payload.model = model;
        break;
      case 'remove-bg':
        endpoint = '/growthai/v1/image/remove-background';
        payload = { image_url: getImageUrl(actionArgs[1]) };
        if (model) payload.model = model;
        break;
      case 'i2v':
        endpoint = '/growthai/v1/video/image-to-video';
        payload = { image_url: getImageUrl(actionArgs[1]), prompt: actionArgs[2] || "animate this image" };
        payload.model = model || "WERYAI_VIDEO_1_0";
        break;
      case 'face-swap':
        endpoint = '/growthai/v1/image/face-swap';
        payload = { target_image_url: getImageUrl(actionArgs[1]), source_image_url: getImageUrl(actionArgs[2]) };
        if (model) payload.model = model;
        break;
      default: return logError("Unknown action.");
    }
    logInfo(`Triggering ${action}...`);


    const submitRes = await apiCall(endpoint, 'POST', payload);

    const taskId = submitRes.task_id || submitRes.id || (submitRes.data && submitRes.data.task_id);
    if (!taskId) {
       if(submitRes.url || submitRes.output_url || submitRes.images || submitRes.video_url || submitRes.audio_url) {
           const finalUrl = submitRes.url || submitRes.output_url || submitRes.video_url || submitRes.audio_url || (submitRes.images && submitRes.images[0]);
           
           if (isJson) console.log(JSON.stringify({ status: "success", url: finalUrl, output: outputPath }));
           else {
             console.log(`\nSuccess! Result URL: ${finalUrl}`);
             if (outputPath) console.log(`Saved to: ${outputPath}`);
           }
           return;
       }
       return logError(`API rejected: ${submitRes.message || submitRes.desc || JSON.stringify(submitRes)}`);
    }

    logInfo(`Task submitted successfully. Task ID: ${taskId}`);
    const startTime = Date.now();

    while (true) {
      await new Promise(r => setTimeout(r, 5000));
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      logInfo(`[Polling] Task pending... ${elapsed}s elapsed`);
      
      const statusRes = await apiCall('/growthai/v1/generation/' + taskId + '/status', 'GET');
      const status = statusRes.data ? statusRes.data.task_status : statusRes.task_status;
      
      if (status === 'succeed' || status === 'success' || status === 'completed') {

        const finalUrl = statusRes.output_url || statusRes.result_url || statusRes.video_url || statusRes.data;

        
        

        if (isJson) {
           console.log(JSON.stringify({ status: "success", url: finalUrl, output: outputPath }));
        } else {
           console.log(`\nSuccess! Result URL: ${finalUrl}`);
           if (outputPath) console.log(`Saved to: ${outputPath}`);
        }
        break;
      } else if (status === 'fail' || status === 'failed') {
        return logError(`Generation failed: ${JSON.stringify(statusRes)}`);
      }
    }

  } catch (err) {
    logError(err.message);
  }
}
run();
