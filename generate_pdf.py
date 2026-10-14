import os
import subprocess

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>HTML Web Development Lab Manual</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@400;500;600;700;800&display=swap');

  @page {
    size: A4;
    margin: 15mm;
    @bottom-right {
      content: counter(page);
    }
  }

  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1e293b;
    line-height: 1.5;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
  }

  .cover-page {
    height: 98vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    color: white;
    padding: 40px;
    border-radius: 12px;
    page-break-after: always;
  }

  .cover-title {
    font-size: 32pt;
    font-weight: 800;
    margin-bottom: 15px;
    letter-spacing: -0.5px;
    color: #f8fafc;
  }

  .cover-subtitle {
    font-size: 16pt;
    font-weight: 400;
    color: #93c5fd;
    margin-bottom: 40px;
  }

  .cover-badge {
    background-color: rgba(255, 255, 255, 0.15);
    padding: 8px 20px;
    border-radius: 20px;
    font-size: 11pt;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .cover-footer {
    margin-top: auto;
    font-size: 11pt;
    color: #cbd5e1;
    border-top: 1px solid rgba(255,255,255,0.2);
    padding-top: 20px;
    width: 100%;
  }

  .experiment-card {
    page-break-after: always;
    padding-top: 10px;
  }

  .experiment-card:last-child {
    page-break-after: avoid;
  }

  .exp-header {
    display: flex;
    align-items: center;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 8px;
    margin-bottom: 20px;
  }

  .exp-number {
    background-color: #2563eb;
    color: white;
    font-size: 12pt;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 6px;
    margin-right: 12px;
  }

  .exp-title {
    font-size: 16pt;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
  }

  .section-label {
    font-size: 11pt;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 15px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
  }

  .section-label::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #3b82f6;
    border-radius: 50%;
    margin-right: 8px;
  }

  /* Code Block Styling */
  .code-container {
    background-color: #0f172a;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    border: 1px solid #334155;
  }

  .code-header {
    background-color: #1e293b;
    padding: 8px 16px;
    font-family: 'Fira Code', monospace;
    font-size: 9pt;
    color: #94a3b8;
    border-bottom: 1px solid #334155;
    display: flex;
    justify-content: space-between;
  }

  pre.code-block {
    margin: 0;
    padding: 16px;
    font-family: 'Fira Code', 'Cascadia Code', monospace;
    font-size: 10pt;
    line-height: 1.5;
    color: #f8fafc;
    white-space: pre-wrap;
    word-break: break-all;
  }

  /* Syntax Highlighting Classes */
  .tag { color: #38bdf8; font-weight: 600; }
  .attr { color: #f472b6; }
  .val { color: #34d399; }
  .comm { color: #64748b; font-style: italic; }

  /* Browser Real-Time Preview Mockup */
  .browser-window {
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    background-color: #ffffff;
    margin-top: 10px;
  }

  .browser-header {
    background-color: #f1f5f9;
    padding: 8px 14px;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
  }

  .browser-dots {
    display: flex;
    gap: 6px;
    margin-right: 14px;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }
  .dot-red { background-color: #ef4444; }
  .dot-yellow { background-color: #f59e0b; }
  .dot-green { background-color: #10b981; }

  .browser-address-bar {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 3px 12px;
    font-size: 8.5pt;
    color: #64748b;
    flex-grow: 1;
    font-family: 'Inter', sans-serif;
  }

  .browser-content {
    padding: 20px;
    min-height: 150px;
    background-color: #ffffff;
  }

  /* Demo Table styling in preview */
  .preview-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }
  .preview-table th, .preview-table td {
    border: 1px solid #000000;
    padding: 6px 12px;
    text-align: left;
  }
  .preview-table th {
    background-color: #f8fafc;
  }

  /* Demo Form Styling in preview */
  .preview-form {
    font-size: 10pt;
  }
  .preview-form input[type="text"],
  .preview-form input[type="email"],
  .preview-form input[type="password"],
  .preview-form select,
  .preview-form textarea {
    border: 1px solid #767676;
    border-radius: 2px;
    padding: 3px 6px;
    margin-top: 2px;
    margin-bottom: 8px;
    font-size: 10pt;
  }

  .page-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 8pt;
    color: #94a3b8;
  }
</style>
</head>
<body>

<!-- Cover Page -->
<div class="cover-page">
  <div class="cover-badge">Lab Reference Manual</div>
  <h1 class="cover-title">HTML5 Practical Guide</h1>
  <p class="cover-subtitle">Step-by-Step HTML Examples with Code & Real-Time Live Browser Previews</p>
  
  <div style="margin-top: 40px; text-align: left; background: rgba(255,255,255,0.1); padding: 20px 30px; border-radius: 8px; width: 80%; border: 1px solid rgba(255,255,255,0.2);">
    <p style="margin: 5px 0;"><strong>Subject:</strong> Web Development / HTML Basics</p>
    <p style="margin: 5px 0;"><strong>Format:</strong> Source Code + Live Browser Output</p>
    <p style="margin: 5px 0;"><strong>Typography:</strong> Modern Sans-Serif & Fira Code Monospace</p>
  </div>

  <div class="cover-footer">
    <p>Computer Science & Information Technology Department</p>
  </div>
</div>

<!-- Experiment 1 -->
<div class="experiment-card">
  <div class="exp-header">
    <span class="exp-number">EXP 01</span>
    <h2 class="exp-title">Create a Simple HTML Page Displaying "Hello Friends!"</h2>
  </div>

  <div class="section-label">Source Code (HTML)</div>
  <div class="code-container">
    <div class="code-header">
      <span>1st.html</span>
      <span>HTML5</span>
    </div>
    <pre class="code-block">&lt;<span class="tag">html</span>&gt;
&lt;<span class="tag">head</span>&gt;
  &lt;<span class="tag">title</span>&gt;Hello Friends&lt;/<span class="tag">title</span>&gt;
&lt;/<span class="tag">head</span>&gt;
&lt;<span class="tag">body</span>&gt;
  &lt;<span class="tag">h1</span>&gt;Hello Friends!&lt;/<span class="tag">h1</span>&gt;
  &lt;<span class="tag">p</span>&gt;Welcome to my first HTML webpage.&lt;/<span class="tag">p</span>&gt;
&lt;/<span class="tag">body</span>&gt;
&lt;/<span class="tag">html</span>&gt;</pre>
  </div>

  <div class="section-label">Real-Time Live Browser Preview</div>
  <div class="browser-window">
    <div class="browser-header">
      <div class="browser-dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="browser-address-bar">file:///C:/Users/asus/OneDrive/Desktop/HTML/1st.html</div>
    </div>
    <div class="browser-content" style="font-family: 'Times New Roman', Times, serif;">
      <h1 style="font-size: 2em; margin-top: 0; font-weight: bold; color: black;">Hello Friends!</h1>
      <p style="font-size: 1em; color: black;">Welcome to my first HTML webpage.</p>
    </div>
  </div>
</div>

<!-- Experiment 2 -->
<div class="experiment-card">
  <div class="exp-header">
    <span class="exp-number">EXP 02</span>
    <h2 class="exp-title">Text Formatting Tags (&lt;b&gt;, &lt;i&gt;, &lt;u&gt;, &lt;strong&gt;, &lt;em&gt;)</h2>
  </div>

  <div class="section-label">Source Code (HTML)</div>
  <div class="code-container">
    <div class="code-header">
      <span>text_formatting.html</span>
      <span>HTML5</span>
    </div>
    <pre class="code-block">&lt;<span class="tag">html</span>&gt;
&lt;<span class="tag">head</span>&gt;
  &lt;<span class="tag">title</span>&gt;Text Formatting Tags&lt;/<span class="tag">title</span>&gt;
&lt;/<span class="tag">head</span>&gt;
&lt;<span class="tag">body</span>&gt;
  &lt;<span class="tag">h1</span>&gt;Text Formatting Example&lt;/<span class="tag">h1</span>&gt;
  &lt;<span class="tag">p</span>&gt;&lt;<span class="tag">b</span>&gt;This text is Bold.&lt;/<span class="tag">b</span>&gt;&lt;/<span class="tag">p</span>&gt;
  &lt;<span class="tag">p</span>&gt;&lt;<span class="tag">i</span>&gt;This text is Italic.&lt;/<span class="tag">i</span>&gt;&lt;/<span class="tag">p</span>&gt;
  &lt;<span class="tag">p</span>&gt;&lt;<span class="tag">u</span>&gt;This text is Underlined.&lt;/<span class="tag">u</span>&gt;&lt;/<span class="tag">p</span>&gt;
  &lt;<span class="tag">p</span>&gt;&lt;<span class="tag">strong</span>&gt;This text is Strong (Important).&lt;/<span class="tag">strong</span>&gt;&lt;/<span class="tag">p</span>&gt;
  &lt;<span class="tag">p</span>&gt;&lt;<span class="tag">em</span>&gt;This text is Emphasized.&lt;/<span class="tag">em</span>&gt;&lt;/<span class="tag">p</span>&gt;
  &lt;<span class="tag">p</span>&gt;
    &lt;<span class="tag">b</span>&gt;&lt;<span class="tag">i</span>&gt;&lt;<span class="tag">u</span>&gt;Bold + Italic + Underlined&lt;/<span class="tag">u</span>&gt;&lt;/<span class="tag">i</span>&gt;&lt;/<span class="tag">b</span>&gt;
  &lt;/<span class="tag">p</span>&gt;
&lt;/<span class="tag">body</span>&gt;
&lt;/<span class="tag">html</span>&gt;</pre>
  </div>

  <div class="section-label">Real-Time Live Browser Preview</div>
  <div class="browser-window">
    <div class="browser-header">
      <div class="browser-dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="browser-address-bar">file:///C:/Users/asus/OneDrive/Desktop/HTML/text_formatting.html</div>
    </div>
    <div class="browser-content" style="font-family: 'Times New Roman', Times, serif;">
      <h1 style="font-size: 2em; margin-top: 0; font-weight: bold; color: black;">Text Formatting Example</h1>
      <p style="margin: 8px 0;"><b>This text is Bold.</b></p>
      <p style="margin: 8px 0;"><i>This text is Italic.</i></p>
      <p style="margin: 8px 0;"><u>This text is Underlined.</u></p>
      <p style="margin: 8px 0;"><strong>This text is Strong (Important).</strong></p>
      <p style="margin: 8px 0;"><em>This text is Emphasized.</em></p>
      <p style="margin: 8px 0;"><b><i><u>Bold + Italic + Underlined</u></i></b></p>
    </div>
  </div>
</div>

<!-- Experiment 3 -->
<div class="experiment-card">
  <div class="exp-header">
    <span class="exp-number">EXP 03</span>
    <h2 class="exp-title">Ordered and Unordered Lists (Different Types)</h2>
  </div>

  <div class="section-label">Source Code (HTML)</div>
  <div class="code-container">
    <div class="code-header">
      <span>lists.html</span>
      <span>HTML5</span>
    </div>
    <pre class="code-block">&lt;<span class="tag">html</span>&gt;
&lt;<span class="tag">head</span>&gt;
  &lt;<span class="tag">title</span>&gt;Different Types of Lists&lt;/<span class="tag">title</span>&gt;
&lt;/<span class="tag">head</span>&gt;
&lt;<span class="tag">body</span>&gt;
  &lt;<span class="tag">h1</span>&gt;Different Types of Lists&lt;/<span class="tag">h1</span>&gt;
  &lt;<span class="tag">h2</span>&gt;Ordered List (Number)&lt;/<span class="tag">h2</span>&gt;
  &lt;<span class="tag">ol</span> <span class="attr">type</span>=<span class="val">"1"</span>&gt;
    &lt;<span class="tag">li</span>&gt;HTML&lt;/<span class="tag">li</span>&gt;
    &lt;<span class="tag">li</span>&gt;CSS&lt;/<span class="tag">li</span>&gt;
    &lt;<span class="tag">li</span>&gt;JavaScript&lt;/<span class="tag">li</span>&gt;
  &lt;/<span class="tag">ol</span>&gt;

  &lt;<span class="tag">h2</span>&gt;Ordered List (Uppercase Letters)&lt;/<span class="tag">h2</span>&gt;
  &lt;<span class="tag">ol</span> <span class="attr">type</span>=<span class="val">"A"</span>&gt;
    &lt;<span class="tag">li</span>&gt;Python&lt;/<span class="tag">li</span>&gt;
    &lt;<span class="tag">li</span>&gt;Java&lt;/<span class="tag">li</span>&gt;
    &lt;<span class="tag">li</span>&gt;C++&lt;/<span class="tag">li</span>&gt;
  &lt;/<span class="tag">ol</span>&gt;

  &lt;<span class="tag">h2</span>&gt;Unordered List (Disc)&lt;/<span class="tag">h2</span>&gt;
  &lt;<span class="tag">ul</span> <span class="attr">type</span>=<span class="val">"disc"</span>&gt;
    &lt;<span class="tag">li</span>&gt;Apple&lt;/<span class="tag">li</span>&gt;
    &lt;<span class="tag">li</span>&gt;Banana&lt;/<span class="tag">li</span>&gt;
    &lt;<span class="tag">li</span>&gt;Mango&lt;/<span class="tag">li</span>&gt;
  &lt;/<span class="tag">ul</span>&gt;

  &lt;<span class="tag">h2</span>&gt;Unordered List (Square)&lt;/<span class="tag">h2</span>&gt;
  &lt;<span class="tag">ul</span> <span class="attr">type</span>=<span class="val">"square"</span>&gt;
    &lt;<span class="tag">li</span>&gt;Red&lt;/<span class="tag">li</span>&gt;
    &lt;<span class="tag">li</span>&gt;Blue&lt;/<span class="tag">li</span>&gt;
    &lt;<span class="tag">li</span>&gt;Green&lt;/<span class="tag">li</span>&gt;
  &lt;/<span class="tag">ul</span>&gt;
&lt;/<span class="tag">body</span>&gt;
&lt;/<span class="tag">html</span>&gt;</pre>
  </div>

  <div class="section-label">Real-Time Live Browser Preview</div>
  <div class="browser-window">
    <div class="browser-header">
      <div class="browser-dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="browser-address-bar">file:///C:/Users/asus/OneDrive/Desktop/HTML/lists.html</div>
    </div>
    <div class="browser-content" style="font-family: 'Times New Roman', Times, serif;">
      <h1 style="font-size: 1.8em; margin-top: 0;">Different Types of Lists</h1>
      <h2 style="font-size: 1.3em; margin: 10px 0 5px 0;">Ordered List (Number)</h2>
      <ol type="1" style="margin-top: 0; padding-left: 25px;">
        <li>HTML</li>
        <li>CSS</li>
        <li>JavaScript</li>
      </ol>

      <h2 style="font-size: 1.3em; margin: 10px 0 5px 0;">Ordered List (Uppercase Letters)</h2>
      <ol type="A" style="margin-top: 0; padding-left: 25px;">
        <li>Python</li>
        <li>Java</li>
        <li>C++</li>
      </ol>

      <h2 style="font-size: 1.3em; margin: 10px 0 5px 0;">Unordered List (Disc)</h2>
      <ul style="list-style-type: disc; margin-top: 0; padding-left: 25px;">
        <li>Apple</li>
        <li>Banana</li>
        <li>Mango</li>
      </ul>

      <h2 style="font-size: 1.3em; margin: 10px 0 5px 0;">Unordered List (Square)</h2>
      <ul style="list-style-type: square; margin-top: 0; padding-left: 25px;">
        <li>Red</li>
        <li>Blue</li>
        <li>Green</li>
      </ul>
    </div>
  </div>
</div>

<!-- Experiment 4 -->
<div class="experiment-card">
  <div class="exp-header">
    <span class="exp-number">EXP 04</span>
    <h2 class="exp-title">Hyperlinks (Navigating External & Internal Pages)</h2>
  </div>

  <div class="section-label">Source Code (HTML)</div>
  <div class="code-container">
    <div class="code-header">
      <span>hyperlinks.html</span>
      <span>HTML5</span>
    </div>
    <pre class="code-block">&lt;<span class="tag">html</span>&gt;
&lt;<span class="tag">head</span>&gt;
  &lt;<span class="tag">title</span>&gt;Home&lt;/<span class="tag">title</span>&gt;
&lt;/<span class="tag">head</span>&gt;
&lt;<span class="tag">body</span>&gt;
  &lt;<span class="tag">h1</span>&gt;Google Page&lt;/<span class="tag">h1</span>&gt;
  &lt;<span class="tag">a</span> <span class="attr">href</span>=<span class="val">"https://www.google.com"</span>&gt;Google&lt;/<span class="tag">a</span>&gt;
&lt;/<span class="tag">body</span>&gt;
&lt;/<span class="tag">html</span>&gt;</pre>
  </div>

  <div class="section-label">Real-Time Live Browser Preview</div>
  <div class="browser-window">
    <div class="browser-header">
      <div class="browser-dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="browser-address-bar">file:///C:/Users/asus/OneDrive/Desktop/HTML/hyperlinks.html</div>
    </div>
    <div class="browser-content" style="font-family: 'Times New Roman', Times, serif;">
      <h1 style="font-size: 2em; margin-top: 0;">Google Page</h1>
      <p><a href="https://www.google.com" style="color: blue; text-decoration: underline;">Google</a></p>
    </div>
  </div>
</div>

<!-- Experiment 5 -->
<div class="experiment-card">
  <div class="exp-header">
    <span class="exp-number">EXP 05</span>
    <h2 class="exp-title">Display Images using &lt;img&gt; Tag with Attributes</h2>
  </div>

  <div class="section-label">Source Code (HTML)</div>
  <div class="code-container">
    <div class="code-header">
      <span>images.html</span>
      <span>HTML5</span>
    </div>
    <pre class="code-block">&lt;<span class="tag">html</span>&gt;
&lt;<span class="tag">head</span>&gt;
  &lt;<span class="tag">title</span>&gt;Image Example&lt;/<span class="tag">title</span>&gt;
&lt;/<span class="tag">head</span>&gt;
&lt;<span class="tag">body</span>&gt;
  &lt;<span class="tag">h1</span>&gt;BMW CAR&lt;/<span class="tag">h1</span>&gt;
  &lt;<span class="tag">img</span> <span class="attr">src</span>=<span class="val">"https://images.unsplash.com/photo-1607853554439..."</span> 
       <span class="attr">width</span>=<span class="val">"300"</span> 
       <span class="attr">height</span>=<span class="val">"200"</span> 
       <span class="attr">alt</span>=<span class="val">"BMW Sports Car"</span>&gt;
&lt;/<span class="tag">body</span>&gt;
&lt;/<span class="tag">html</span>&gt;</pre>
  </div>

  <div class="section-label">Real-Time Live Browser Preview</div>
  <div class="browser-window">
    <div class="browser-header">
      <div class="browser-dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="browser-address-bar">file:///C:/Users/asus/OneDrive/Desktop/HTML/images.html</div>
    </div>
    <div class="browser-content" style="font-family: 'Times New Roman', Times, serif;">
      <h1 style="font-size: 2em; margin-top: 0;">BMW CAR</h1>
      <img src="https://images.unsplash.com/photo-1607853554439-0069ec0f29b6?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8Ym13JTIwd2FsbHBhcGVyfGVufDB8fDB8fHww" width="300" height="200" style="border: 1px solid #ccc; display: block;" alt="BMW Car">
    </div>
  </div>
</div>

<!-- Experiment 6 -->
<div class="experiment-card">
  <div class="exp-header">
    <span class="exp-number">EXP 06</span>
    <h2 class="exp-title">Student Information Table (&lt;table&gt;, &lt;tr&gt;, &lt;th&gt;, &lt;td&gt;)</h2>
  </div>

  <div class="section-label">Source Code (HTML)</div>
  <div class="code-container">
    <div class="code-header">
      <span>student_table.html</span>
      <span>HTML5</span>
    </div>
    <pre class="code-block">&lt;<span class="tag">html</span>&gt;
&lt;<span class="tag">head</span>&gt;
  &lt;<span class="tag">title</span>&gt;Student Information&lt;/<span class="tag">title</span>&gt;
&lt;/<span class="tag">head</span>&gt;
&lt;<span class="tag">body</span>&gt;
  &lt;<span class="tag">h2</span>&gt;Student Information Table&lt;/<span class="tag">h2</span>&gt;
  &lt;<span class="tag">table</span> <span class="attr">border</span>=<span class="val">"1"</span>&gt;
    &lt;<span class="tag">tr</span>&gt;
      &lt;<span class="tag">th</span>&gt;Roll No&lt;/<span class="tag">th</span>&gt;
      &lt;<span class="tag">th</span>&gt;Name&lt;/<span class="tag">th</span>&gt;
      &lt;<span class="tag">th</span>&gt;Course&lt;/<span class="tag">th</span>&gt;
      &lt;<span class="tag">th</span>&gt;Marks&lt;/<span class="tag">th</span>&gt;
    &lt;/<span class="tag">tr</span>&gt;
    &lt;<span class="tag">tr</span>&gt;
      &lt;<span class="tag">td</span>&gt;101&lt;/<span class="tag">td</span>&gt;
      &lt;<span class="tag">td</span>&gt;Aditya&lt;/<span class="tag">td</span>&gt;
      &lt;<span class="tag">td</span>&gt;CSE Cyber&lt;/<span class="tag">td</span>&gt;
      &lt;<span class="tag">td</span>&gt;89&lt;/<span class="tag">td</span>&gt;
    &lt;/<span class="tag">tr</span>&gt;
    &lt;<span class="tag">tr</span>&gt;
      &lt;<span class="tag">td</span>&gt;102&lt;/<span class="tag">td</span>&gt;
      &lt;<span class="tag">td</span>&gt;Rahul&lt;/<span class="tag">td</span>&gt;
      &lt;<span class="tag">td</span>&gt;CSE&lt;/<span class="tag">td</span>&gt;
      &lt;<span class="tag">td</span>&gt;92&lt;/<span class="tag">td</span>&gt;
    &lt;/<span class="tag">tr</span>&gt;
    &lt;<span class="tag">tr</span>&gt;
      &lt;<span class="tag">td</span>&gt;103&lt;/<span class="tag">td</span>&gt;
      &lt;<span class="tag">td</span>&gt;Priya&lt;/<span class="tag">td</span>&gt;
      &lt;<span class="tag">td</span>&gt;IT&lt;/<span class="tag">td</span>&gt;
      &lt;<span class="tag">td</span>&gt;85&lt;/<span class="tag">td</span>&gt;
    &lt;/<span class="tag">tr</span>&gt;
  &lt;/<span class="tag">table</span>&gt;
&lt;/<span class="tag">body</span>&gt;
&lt;/<span class="tag">html</span>&gt;</pre>
  </div>

  <div class="section-label">Real-Time Live Browser Preview</div>
  <div class="browser-window">
    <div class="browser-header">
      <div class="browser-dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="browser-address-bar">file:///C:/Users/asus/OneDrive/Desktop/HTML/student_table.html</div>
    </div>
    <div class="browser-content" style="font-family: 'Times New Roman', Times, serif;">
      <h2 style="font-size: 1.5em; margin-top: 0;">Student Information Table</h2>
      <table class="preview-table">
        <tr>
          <th>Roll No</th>
          <th>Name</th>
          <th>Course</th>
          <th>Marks</th>
        </tr>
        <tr>
          <td>101</td>
          <td>Aditya</td>
          <td>CSE Cyber</td>
          <td>89</td>
        </tr>
        <tr>
          <td>102</td>
          <td>Rahul</td>
          <td>CSE</td>
          <td>92</td>
        </tr>
        <tr>
          <td>103</td>
          <td>Priya</td>
          <td>IT</td>
          <td>85</td>
        </tr>
      </table>
    </div>
  </div>
</div>

<!-- Experiment 7 -->
<div class="experiment-card">
  <div class="exp-header">
    <span class="exp-number">EXP 07</span>
    <h2 class="exp-title">Student Registration Form (&lt;input&gt;, &lt;select&gt;, &lt;textarea&gt;)</h2>
  </div>

  <div class="section-label">Source Code (HTML)</div>
  <div class="code-container">
    <div class="code-header">
      <span>registration_form.html</span>
      <span>HTML5</span>
    </div>
    <pre class="code-block">&lt;<span class="tag">html</span>&gt;
&lt;<span class="tag">head</span>&gt;
  &lt;<span class="tag">title</span>&gt;Student Registration Form&lt;/<span class="tag">title</span>&gt;
&lt;/<span class="tag">head</span>&gt;
&lt;<span class="tag">body</span>&gt;
  &lt;<span class="tag">h2</span>&gt;Student Registration Form&lt;/<span class="tag">h2</span>&gt;
  &lt;<span class="tag">form</span>&gt;
    Name:&lt;<span class="tag">br</span>&gt;
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"text"</span>&gt;&lt;<span class="tag">br</span>&gt;&lt;<span class="tag">br</span>&gt;
    Email:&lt;<span class="tag">br</span>&gt;
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"email"</span>&gt;&lt;<span class="tag">br</span>&gt;&lt;<span class="tag">br</span>&gt;
    Password:&lt;<span class="tag">br</span>&gt;
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"password"</span>&gt;&lt;<span class="tag">br</span>&gt;&lt;<span class="tag">br</span>&gt;
    Gender:
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"radio"</span> <span class="attr">name</span>=<span class="val">"g"</span>&gt; Male
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"radio"</span> <span class="attr">name</span>=<span class="val">"g"</span>&gt; Female&lt;<span class="tag">br</span>&gt;&lt;<span class="tag">br</span>&gt;
    Course:
    &lt;<span class="tag">select</span>&gt;
      &lt;<span class="tag">option</span>&gt;CSE&lt;/<span class="tag">option</span>&gt;
      &lt;<span class="tag">option</span>&gt;IT&lt;/<span class="tag">option</span>&gt;
      &lt;<span class="tag">option</span>&gt;ECE&lt;/<span class="tag">option</span>&gt;
    &lt;/<span class="tag">select</span>&gt;&lt;<span class="tag">br</span>&gt;&lt;<span class="tag">br</span>&gt;
    Address:&lt;<span class="tag">br</span>&gt;
    &lt;<span class="tag">textarea</span> <span class="attr">rows</span>=<span class="val">"4"</span> <span class="attr">cols</span>=<span class="val">"25"</span>&gt;&lt;/<span class="tag">textarea</span>&gt;&lt;<span class="tag">br</span>&gt;&lt;<span class="tag">br</span>&gt;
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"submit"</span> <span class="attr">value</span>=<span class="val">"Register"</span>&gt;
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"reset"</span> <span class="attr">value</span>=<span class="val">"Clear"</span>&gt;
  &lt;/<span class="tag">form</span>&gt;
&lt;/<span class="tag">body</span>&gt;
&lt;/<span class="tag">html</span>&gt;</pre>
  </div>

  <div class="section-label">Real-Time Live Browser Preview</div>
  <div class="browser-window">
    <div class="browser-header">
      <div class="browser-dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="browser-address-bar">file:///C:/Users/asus/OneDrive/Desktop/HTML/registration_form.html</div>
    </div>
    <div class="browser-content preview-form" style="font-family: 'Times New Roman', Times, serif;">
      <h2 style="font-size: 1.4em; margin-top: 0;">Student Registration Form</h2>
      <form>
        Name: <br><input type="text"><br><br>
        Email: <br><input type="email"><br><br>
        Password: <br><input type="password"><br><br>
        Gender: <input type="radio" name="g"> Male <input type="radio" name="g"> Female<br><br>
        Course: 
        <select>
          <option>CSE</option>
          <option>IT</option>
          <option>ECE</option>
        </select><br><br>
        Address:<br>
        <textarea rows="4" cols="25"></textarea><br><br>
        <input type="submit" value="Register" style="padding: 2px 8px;">
        <input type="reset" value="Clear" style="padding: 2px 8px;">
      </form>
    </div>
  </div>
</div>

<!-- Experiment 8 -->
<div class="experiment-card">
  <div class="exp-header">
    <span class="exp-number">EXP 08</span>
    <h2 class="exp-title">User Form (Radio Buttons, Checkboxes & Drop-down Lists)</h2>
  </div>

  <div class="section-label">Source Code (HTML)</div>
  <div class="code-container">
    <div class="code-header">
      <span>user_info_form.html</span>
      <span>HTML5</span>
    </div>
    <pre class="code-block">&lt;<span class="tag">html</span>&gt;
&lt;<span class="tag">head</span>&gt;
  &lt;<span class="tag">title</span>&gt;User Form&lt;/<span class="tag">title</span>&gt;
&lt;/<span class="tag">head</span>&gt;
&lt;<span class="tag">body</span>&gt;
  &lt;<span class="tag">h2</span>&gt;User Information&lt;/<span class="tag">h2</span>&gt;
  &lt;<span class="tag">form</span>&gt;
    Name:
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"text"</span>&gt;&lt;<span class="tag">br</span>&gt;&lt;<span class="tag">br</span>&gt;
    Gender:
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"radio"</span> <span class="attr">name</span>=<span class="val">"gender"</span>&gt; Male
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"radio"</span> <span class="attr">name</span>=<span class="val">"gender"</span>&gt; Female&lt;<span class="tag">br</span>&gt;&lt;<span class="tag">br</span>&gt;
    Hobbies:
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"checkbox"</span>&gt; Reading
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"checkbox"</span>&gt; Music
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"checkbox"</span>&gt; Sports&lt;<span class="tag">br</span>&gt;&lt;<span class="tag">br</span>&gt;
    Course:
    &lt;<span class="tag">select</span>&gt;
      &lt;<span class="tag">option</span>&gt;Select&lt;/<span class="tag">option</span>&gt;
      &lt;<span class="tag">option</span>&gt;CSE&lt;/<span class="tag">option</span>&gt;
      &lt;<span class="tag">option</span>&gt;IT&lt;/<span class="tag">option</span>&gt;
      &lt;<span class="tag">option</span>&gt;ECE&lt;/<span class="tag">option</span>&gt;
    &lt;/<span class="tag">select</span>&gt;&lt;<span class="tag">br</span>&gt;&lt;<span class="tag">br</span>&gt;
    &lt;<span class="tag">input</span> <span class="attr">type</span>=<span class="val">"submit"</span> <span class="attr">value</span>=<span class="val">"Submit"</span>&gt;
  &lt;/<span class="tag">form</span>&gt;
&lt;/<span class="tag">body</span>&gt;
&lt;/<span class="tag">html</span>&gt;</pre>
  </div>

  <div class="section-label">Real-Time Live Browser Preview</div>
  <div class="browser-window">
    <div class="browser-header">
      <div class="browser-dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="browser-address-bar">file:///C:/Users/asus/OneDrive/Desktop/HTML/user_info_form.html</div>
    </div>
    <div class="browser-content preview-form" style="font-family: 'Times New Roman', Times, serif;">
      <h2 style="font-size: 1.4em; margin-top: 0;">User Information</h2>
      <form>
        Name: <input type="text" value="VANIYA ADITYA"><br><br>
        Gender: <input type="radio" name="gender" checked> Male <input type="radio" name="gender"> Female<br><br>
        Hobbies: <input type="checkbox"> Reading <input type="checkbox"> Music <input type="checkbox" checked> Sports<br><br>
        Course: 
        <select>
          <option>Select</option>
          <option>CSE</option>
          <option>IT</option>
          <option>ECE</option>
        </select><br><br>
        <input type="submit" value="Submit" style="padding: 2px 8px;">
      </form>
    </div>
  </div>
</div>

</body>
</html>
"""

with open("HTML_Lab_Manual.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML template written to HTML_Lab_Manual.html")
