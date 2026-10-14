"""
=============================================================================
PRO BACKGROUND REMOVER WEB STUDIO (FastAPI - Render Deployment Ready)
=============================================================================
Description: Interactive Web Studio Server built with FastAPI.
Fully configured for Render deployment using environment variables.

Usage:
  python bg_remover_server.py
  Render Deployment: uvicorn bg_remover_server:app --host 0.0.0.0 --port $PORT
=============================================================================
"""

import os
import sys
import io
from typing import Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import uvicorn

from bg_remover import remove_background

PORT = int(os.getenv("PORT", 8080))

app = FastAPI(title="AI Background Remover Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_UI = """<!DOCTYPE html>
<html lang="hi" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>✨ AI Background Remover Studio</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 500: '#6366f1', 600: '#4f46e5', 700: '#4338ca' }
          }
        }
      }
    }
  </script>
  <style>
    .checkerboard {
      background-color: #0f172a;
      background-image: linear-gradient(45deg, #1e293b 25%, transparent 25%),
                        linear-gradient(-45deg, #1e293b 25%, transparent 25%),
                        linear-gradient(45deg, transparent 75%, #1e293b 75%),
                        linear-gradient(-45deg, transparent 75%, #1e293b 75%);
      background-size: 20px 20px;
      background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
    }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans selection:bg-brand-500 selection:text-white">

  <!-- Header Bar -->
  <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3.5 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <i class="fa-solid fa-wand-magic-sparkles text-white text-lg"></i>
        </div>
        <div>
          <h1 class="text-lg font-bold bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
            AI Background Remover Studio
          </h1>
          <p class="text-[11px] text-slate-400">Pro Grade Image Cutout & Background Changer</p>
        </div>
      </div>
      <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        <span class="w-2 h-2 rounded-full bg-emerald-400 mr-2 animate-pulse"></span> Render Cloud Ready
      </span>
    </div>
  </header>

  <!-- Main Grid Layout -->
  <main class="flex-1 max-w-7xl w-full mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
    
    <!-- Left Control Panel -->
    <div class="lg:col-span-4 space-y-6">
      
      <!-- Upload Box -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h2 class="text-sm font-semibold mb-4 flex items-center gap-2 text-slate-200">
          <i class="fa-solid fa-cloud-arrow-up text-indigo-400"></i> Step 1: Upload Photo
        </h2>
        
        <div 
          id="dropzone"
          onclick="document.getElementById('imageInput').click()"
          class="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-8 text-center cursor-pointer transition-all duration-200 bg-slate-950/50 hover:bg-indigo-950/20 group"
        >
          <input type="file" id="imageInput" accept="image/*" class="hidden" onchange="handleFileSelect(event)" />
          <div class="w-12 h-12 rounded-full bg-slate-800 group-hover:bg-indigo-600/20 text-slate-400 group-hover:text-indigo-400 flex items-center justify-center mx-auto mb-3 transition-colors">
            <i class="fa-solid fa-image text-xl"></i>
          </div>
          <p class="text-xs font-medium text-slate-300 group-hover:text-indigo-300">Click to upload or Drag & Drop</p>
          <p class="text-[10px] text-slate-500 mt-1">PNG, JPG, WEBP, BMP</p>
        </div>

        <div id="fileInfo" class="hidden mt-4 p-3 bg-slate-800/60 rounded-lg flex items-center justify-between border border-slate-700">
          <div class="flex items-center gap-2 overflow-hidden">
            <i class="fa-solid fa-file-image text-indigo-400"></i>
            <span id="fileName" class="text-xs font-mono text-slate-300 truncate">photo.jpg</span>
          </div>
          <button onclick="resetImage()" class="text-slate-400 hover:text-rose-400 text-xs px-2 py-1">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
      </div>

      <!-- Settings Box -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
        <h2 class="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <i class="fa-solid fa-sliders text-indigo-400"></i> Step 2: Background Settings
        </h2>

        <!-- Mode Select -->
        <div>
          <label class="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Background Mode</label>
          <div class="grid grid-cols-2 gap-2">
            <button type="button" id="btnModeTransparent" onclick="setBgMode('transparent')" class="py-2 px-3 rounded-xl border text-xs font-medium flex items-center justify-center gap-2 border-indigo-500 bg-indigo-500/10 text-indigo-300">
              <i class="fa-solid fa-border-none"></i> Transparent
            </button>
            <button type="button" id="btnModeColor" onclick="setBgMode('color')" class="py-2 px-3 rounded-xl border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-medium flex items-center justify-center gap-2">
              <i class="fa-solid fa-palette"></i> Solid Color
            </button>
          </div>
        </div>

        <!-- Color Palette Options -->
        <div id="colorOptions" class="hidden space-y-3 pt-2 border-t border-slate-800">
          <label class="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Choose Background Color</label>
          <div class="flex items-center gap-2">
            <input type="color" id="bgColorPicker" value="#ffffff" onchange="updateColorHex(this.value)" class="w-9 h-9 rounded-lg cursor-pointer bg-slate-800 border border-slate-700 p-1" />
            <input type="text" id="bgColorHex" value="#FFFFFF" oninput="updateColorPicker(this.value)" class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500" />
          </div>
          <div class="flex gap-2 pt-1">
            <button onclick="setColorPreset('#FFFFFF')" title="White" class="w-6 h-6 rounded-full bg-white border border-slate-600 shadow-sm"></button>
            <button onclick="setColorPreset('#000000')" title="Black" class="w-6 h-6 rounded-full bg-black border border-slate-600 shadow-sm"></button>
            <button onclick="setColorPreset('#00FF00')" title="Green Screen" class="w-6 h-6 rounded-full bg-green-500 border border-slate-600 shadow-sm"></button>
            <button onclick="setColorPreset('#0055FF')" title="Blue" class="w-6 h-6 rounded-full bg-blue-600 border border-slate-600 shadow-sm"></button>
            <button onclick="setColorPreset('#FF0055')" title="Red" class="w-6 h-6 rounded-full bg-rose-600 border border-slate-600 shadow-sm"></button>
          </div>
        </div>

        <!-- Process Button -->
        <button 
          id="processBtn"
          onclick="processImage()"
          disabled
          class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-xs shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-2 transition-all active:scale-[0.99]"
        >
          <i class="fa-solid fa-wand-magic-sparkles"></i> Remove Background Now
        </button>

      </div>
    </div>

    <!-- Right Panel: Side-by-Side Comparison -->
    <div class="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
      
      <div>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <i class="fa-solid fa-eye text-indigo-400"></i> Step 3: Live Side-by-Side Preview
          </h2>
          <span id="statusBadge" class="text-xs text-slate-500">Upload photo to start</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 min-h-[340px]">
          
          <!-- Original Image Preview -->
          <div class="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
            <div class="px-3 py-2 bg-slate-900/80 border-b border-slate-800 text-[11px] text-slate-400 font-medium flex justify-between">
              <span>Original Photo</span>
              <span id="origDimensions" class="font-mono">--</span>
            </div>
            <div class="flex-1 flex items-center justify-center p-4 min-h-[260px]">
              <img id="origPreview" class="max-h-[280px] w-auto max-w-full object-contain rounded hidden" />
              <div id="origPlaceholder" class="text-center text-slate-600 text-xs">
                <i class="fa-solid fa-image text-3xl mb-2 block text-slate-700"></i>
                Select photo on the left
              </div>
            </div>
          </div>

          <!-- Processed Result Preview -->
          <div class="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden flex flex-col relative">
            <div class="px-3 py-2 bg-slate-900/80 border-b border-slate-800 text-[11px] text-slate-400 font-medium flex justify-between">
              <span>Background Removed</span>
              <span id="resDimensions" class="font-mono text-emerald-400">--</span>
            </div>
            <div id="resultCanvas" class="flex-1 checkerboard flex items-center justify-center p-4 min-h-[260px] relative">
              
              <img id="resPreview" class="max-h-[280px] w-auto max-w-full object-contain rounded hidden z-10" />
              
              <div id="resPlaceholder" class="text-center text-slate-600 text-xs z-10">
                <i class="fa-solid fa-wand-magic-sparkles text-3xl mb-2 block text-slate-700"></i>
                Cutout result will appear here
              </div>

              <!-- Loading Spinner -->
              <div id="loadingSpinner" class="hidden absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center z-20">
                <div class="w-9 h-9 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mb-3"></div>
                <p class="text-xs font-semibold text-indigo-300 animate-pulse">Removing background with AI...</p>
              </div>

            </div>
          </div>

        </div>
      </div>

      <!-- Download Button -->
      <div class="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
        <p class="text-xs text-slate-500">
          <i class="fa-solid fa-shield-halved text-indigo-400 mr-1"></i> Full Resolution PNG Output
        </p>
        <a 
          id="downloadBtn" 
          href="#" 
          download="nobg_photo.png"
          class="hidden py-2.5 px-5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/20 flex items-center gap-2 transition-all active:scale-[0.98]"
        >
          <i class="fa-solid fa-download"></i> Download High-Res Result
        </a>
      </div>

    </div>

  </main>

  <script>
    let selectedFile = null;
    let bgMode = 'transparent';

    function setBgMode(mode) {
      bgMode = mode;
      const btnTrans = document.getElementById('btnModeTransparent');
      const btnColor = document.getElementById('btnModeColor');
      const colorOpts = document.getElementById('colorOptions');

      if (mode === 'transparent') {
        btnTrans.className = 'py-2 px-3 rounded-xl border text-xs font-medium flex items-center justify-center gap-2 border-indigo-500 bg-indigo-500/10 text-indigo-300';
        btnColor.className = 'py-2 px-3 rounded-xl border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-medium flex items-center justify-center gap-2';
        colorOpts.classList.add('hidden');
      } else {
        btnColor.className = 'py-2 px-3 rounded-xl border text-xs font-medium flex items-center justify-center gap-2 border-indigo-500 bg-indigo-500/10 text-indigo-300';
        btnTrans.className = 'py-2 px-3 rounded-xl border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-medium flex items-center justify-center gap-2';
        colorOpts.classList.remove('hidden');
      }
    }

    function setColorPreset(hex) {
      document.getElementById('bgColorPicker').value = hex;
      document.getElementById('bgColorHex').value = hex.toUpperCase();
    }

    function updateColorHex(hex) {
      document.getElementById('bgColorHex').value = hex.toUpperCase();
    }

    function updateColorPicker(hex) {
      if (/^#[0-9A-F]{6}$/i.test(hex)) {
        document.getElementById('bgColorPicker').value = hex;
      }
    }

    function handleFileSelect(e) {
      const file = e.target.files[0];
      if (file) loadFile(file);
    }

    function loadFile(file) {
      selectedFile = file;
      document.getElementById('fileName').innerText = file.name;
      document.getElementById('fileInfo').classList.remove('hidden');
      document.getElementById('processBtn').disabled = false;
      document.getElementById('statusBadge').innerText = 'Ready to process';

      const reader = new FileReader();
      reader.onload = function(evt) {
        const img = document.getElementById('origPreview');
        img.src = evt.target.result;
        img.classList.remove('hidden');
        document.getElementById('origPlaceholder').classList.add('hidden');
        
        img.onload = () => {
          document.getElementById('origDimensions').innerText = `${img.naturalWidth} × ${img.naturalHeight}`;
        };
      };
      reader.readAsDataURL(file);
    }

    function resetImage() {
      selectedFile = null;
      document.getElementById('imageInput').value = '';
      document.getElementById('fileInfo').classList.add('hidden');
      document.getElementById('processBtn').disabled = true;
      document.getElementById('origPreview').classList.add('hidden');
      document.getElementById('origPlaceholder').classList.remove('hidden');
      document.getElementById('resPreview').classList.add('hidden');
      document.getElementById('resPlaceholder').classList.remove('hidden');
      document.getElementById('downloadBtn').classList.add('hidden');
      document.getElementById('statusBadge').innerText = 'No photo loaded';
      document.getElementById('origDimensions').innerText = '--';
      document.getElementById('resDimensions').innerText = '--';
    }

    // Drag & Drop
    const dropzone = document.getElementById('dropzone');
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('border-indigo-500', 'bg-indigo-950/30'); });
    dropzone.addEventListener('dragleave', (e) => { e.preventDefault(); dropzone.classList.remove('border-indigo-500', 'bg-indigo-950/30'); });
    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('border-indigo-500', 'bg-indigo-950/30');
      if (e.dataTransfer.files.length > 0) loadFile(e.dataTransfer.files[0]);
    });

    async function processImage() {
      if (!selectedFile) return;

      const spinner = document.getElementById('loadingSpinner');
      const processBtn = document.getElementById('processBtn');
      spinner.classList.remove('hidden');
      processBtn.disabled = true;
      document.getElementById('statusBadge').innerText = 'Processing with AI...';

      const formData = new FormData();
      formData.append('file', selectedFile);
      if (bgMode === 'color') {
        formData.append('bg_color', document.getElementById('bgColorHex').value);
      }

      try {
        const response = await fetch('/api/remove-bg', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          const errJson = await response.json().catch(() => ({ detail: 'Server Error' }));
          throw new Error(errJson.detail || 'Failed to process');
        }

        const blob = await response.blob();
        const outputUrl = URL.createObjectURL(blob);

        const resImg = document.getElementById('resPreview');
        resImg.src = outputUrl;
        resImg.classList.remove('hidden');
        document.getElementById('resPlaceholder').classList.add('hidden');

        resImg.onload = () => {
          document.getElementById('resDimensions').innerText = `${resImg.naturalWidth} × ${resImg.naturalHeight}`;
        };

        const downloadBtn = document.getElementById('downloadBtn');
        downloadBtn.href = outputUrl;
        downloadBtn.download = `nobg_${selectedFile.name.split('.')[0]}.png`;
        downloadBtn.classList.remove('hidden');

        document.getElementById('statusBadge').innerText = '✅ Background Removed!';
      } catch (err) {
        alert('Error: ' + err.message);
        document.getElementById('statusBadge').innerText = '❌ Failed to process';
      } finally {
        spinner.classList.add('hidden');
        processBtn.disabled = false;
      }
    }
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serves the background remover Web UI."""
    return HTML_UI

@app.post("/api/remove-bg")
async def api_remove_bg(request: Request):
    """
    API endpoint for background removal.
    Uses REMOVE_BG_API_KEY environment variable.
    """
    try:
        form = await request.form()
        file_obj = form.get("file")
        if not file_obj:
            raise HTTPException(status_code=400, detail="No image file provided in upload")

        contents = await file_obj.read()
        bg_color = form.get("bg_color")

        processed_img = remove_background(
            input_image=contents,
            bg_color=bg_color if bg_color else None
        )

        buf = io.BytesIO()
        output_format = "PNG" if processed_img.mode == "RGBA" else "JPEG"
        processed_img.save(buf, format=output_format)
        img_bytes = buf.getvalue()

        media_type = "image/png" if output_format == "PNG" else "image/jpeg"
        return Response(content=img_bytes, media_type=media_type)

    except Exception as e:
        print(f"❌ Server Error during /api/remove-bg: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"\n==================================================")
    print(f"🚀 AI Background Remover Studio Live on Port {PORT}")
    print(f"👉 Open in browser: http://localhost:{PORT}")
    print(f"==================================================\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
