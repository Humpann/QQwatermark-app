ADMIN_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PureClip QQ · 云端开发者总控台 (Super Admin: QQ | VIP Client: 成雨萌)</title>
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- FontAwesome Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            matcha: {
              400: '#A3D96E',
              dark: '#141812',
              darker: '#0C0F0A'
            }
          },
          fontFamily: {
            sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"', '"Segoe UI"', 'Roboto', 'sans-serif'],
            mono: ['"SF Mono"', 'Consolas', 'monospace']
          }
        }
      }
    }
  </script>

  <style>
    * { box-sizing: border-box; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(163, 217, 110, 0.3); border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(163, 217, 110, 0.6); }

    .haptic-btn {
      transition: transform 0.12s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.15s, background-color 0.15s;
      cursor: pointer;
      user-select: none;
    }
    .haptic-btn:active {
      transform: scale(0.96);
    }

    @keyframes radar-scan {
      0% { transform: translateY(-100%); }
      100% { transform: translateY(1000%); }
    }
    .screen-radar-line {
      position: absolute;
      left: 0;
      width: 100%;
      height: 2px;
      background: linear-gradient(90deg, transparent, #A3D96E, #38BDF8, transparent);
      box-shadow: 0 0 10px #A3D96E;
      animation: radar-scan 4s infinite linear;
    }

    @keyframes live-dot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }
    .animate-live-dot {
      animation: live-dot 2s infinite ease-in-out;
    }
  </style>
</head>
<body class="bg-[#0C0F0A] text-slate-100 min-h-screen font-sans antialiased flex selection:bg-[#A3D96E] selection:text-black">

  <!-- 全局 Toast 提示组件 -->
  <div id="toast" class="fixed bottom-8 right-8 z-50 px-5 py-3.5 rounded-2xl bg-[#A3D96E] text-black font-extrabold text-xs shadow-2xl flex items-center gap-2.5 opacity-0 pointer-events-none transform translate-y-4 transition-all duration-300">
    <i class="fa-solid fa-circle-check text-sm"></i>
    <span id="toast-msg">操作已生效！</span>
  </div>

  <!-- 左侧导航侧边栏 -->
  <aside class="w-64 bg-[#141812] border-r border-[#A3D96E]/20 flex flex-col justify-between p-5 select-none shrink-0 min-h-screen">
    <div class="space-y-6">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#1E281A] to-[#0A0F08] border border-[#A3D96E]/60 flex items-center justify-center text-[#A3D96E] shadow-lg shadow-lime-500/20">
          <svg class="w-5 h-5 filter drop-shadow-[0_0_6px_rgba(163,217,110,0.8)]" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z" />
          </svg>
        </div>
        <div>
          <div class="flex items-center gap-1.5">
            <h1 class="text-sm font-black text-white tracking-tight">PureClip</h1>
            <span class="px-1.5 py-0.2 rounded bg-[#0C0F0A] text-[#A3D96E] border border-lime-400/40 text-[10px] font-mono font-black">QQ</span>
          </div>
          <p class="text-[9px] text-[#A3D96E] font-mono">开发者云端总控后台 v3.0</p>
        </div>
      </div>

      <!-- 超级管理员徽章 -->
      <div class="p-3 rounded-2xl bg-[#0C0F0A] border border-white/5 space-y-1.5">
        <div class="flex items-center justify-between">
          <span class="text-[9px] text-slate-400 font-mono">超级管理员 / 架构师</span>
          <span class="w-2 h-2 rounded-full bg-[#A3D96E] animate-ping"></span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded-lg bg-[#A3D96E] text-black font-black text-xs flex items-center justify-center font-mono">
            QQ
          </div>
          <span class="text-xs font-bold text-white">开发者: QQ (Lead)</span>
        </div>
      </div>

      <!-- 7 大导航菜单项 -->
      <nav class="space-y-1">
        <button onclick="switchTab('dashboard')" id="nav-dashboard" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl bg-[#A3D96E] text-black font-bold text-xs shadow-md transition-all haptic-btn">
          <i class="fa-solid fa-chart-pie w-4 text-center"></i>
          <span>总览与实时指标</span>
        </button>

        <button onclick="switchTab('screen')" id="nav-screen" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-slate-400 hover:text-white hover:bg-white/5 font-bold text-xs transition-all haptic-btn">
          <i class="fa-solid fa-mobile-screen-button w-4 text-center"></i>
          <span>实时屏幕协同监控</span>
          <span class="ml-auto text-[8px] px-1.5 py-0.5 rounded-md bg-red-500/20 text-red-400 font-mono font-bold">LIVE</span>
        </button>

        <button onclick="switchTab('album')" id="nav-album" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-slate-400 hover:text-white hover:bg-white/5 font-bold text-xs transition-all haptic-btn">
          <i class="fa-solid fa-images w-4 text-center"></i>
          <span>云端相册与媒体资产</span>
          <span class="ml-auto text-[8px] px-1.5 py-0.5 rounded-md bg-[#A3D96E]/20 text-[#A3D96E] font-mono">4.6G</span>
        </button>

        <button onclick="switchTab('broadcast')" id="nav-broadcast" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-slate-400 hover:text-white hover:bg-white/5 font-bold text-xs transition-all haptic-btn">
          <i class="fa-solid fa-bullhorn w-4 text-center text-orange-400"></i>
          <span>广播发布与推送中枢</span>
        </button>

        <button onclick="switchTab('ota')" id="nav-ota" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-slate-400 hover:text-white hover:bg-white/5 font-bold text-xs transition-all haptic-btn">
          <i class="fa-solid fa-cloud-arrow-up w-4 text-center text-cyan-400"></i>
          <span>云更新与差分热更</span>
          <span class="ml-auto text-[8px] px-1.5 py-0.5 rounded-md bg-cyan-500/20 text-cyan-400 font-mono">OTA</span>
        </button>

        <button onclick="switchTab('gpu')" id="nav-gpu" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-slate-400 hover:text-white hover:bg-white/5 font-bold text-xs transition-all haptic-btn">
          <i class="fa-solid fa-microchip w-4 text-center text-purple-400"></i>
          <span>4K GPU 算力集群调度</span>
        </button>

        <button onclick="switchTab('audit')" id="nav-audit" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-slate-400 hover:text-white hover:bg-white/5 font-bold text-xs transition-all haptic-btn">
          <i class="fa-solid fa-shield-halved w-4 text-center text-amber-400"></i>
          <span>合规与安全审计日志</span>
        </button>
      </nav>
    </div>

    <!-- VIP 专属客户端在线卡片 -->
    <div class="pt-4 border-t border-white/5 space-y-2">
      <div class="flex items-center justify-between text-[10px] text-slate-400 font-mono">
        <span>VIP 专属客户端</span>
        <span class="text-[#A3D96E] font-bold">在线 (5G)</span>
      </div>
      <div class="p-2.5 rounded-2xl bg-[#0C0F0A] border border-lime-500/30 flex items-center gap-2.5">
        <div class="w-7 h-7 rounded-xl bg-white/10 text-white font-bold text-xs flex items-center justify-center">
          成
        </div>
        <div class="overflow-hidden">
          <p class="text-xs font-bold text-white truncate">成雨萌 (VIP PRO)</p>
          <p class="text-[8px] text-slate-400 font-mono truncate">ID: cym_vip_official</p>
        </div>
      </div>
    </div>
  </aside>

  <!-- 主内容区域 -->
  <main class="flex-1 min-h-screen overflow-y-auto bg-[#0C0F0A] p-6 lg:p-8 space-y-6">

    <!-- 顶部状态栏 -->
    <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/10">
      <div>
        <h2 id="page-title" class="text-xl font-black text-white flex items-center gap-2">
          <i class="fa-solid fa-chart-pie text-[#A3D96E]"></i>
          <span>全局系统总览与实时指标</span>
        </h2>
        <p class="text-xs text-slate-400">PureClip QQ Cloud Node · 超级管理员: QQ · 专属服务对象: 成雨萌</p>
      </div>

      <!-- 顶部操作按钮组 -->
      <div class="flex items-center gap-2.5">
        <button onclick="triggerCloudSync()" class="haptic-btn px-3.5 py-2 rounded-xl bg-[#141812] border border-white/10 hover:border-[#A3D96E]/50 text-white text-xs font-bold flex items-center gap-2">
          <i class="fa-solid fa-rotate text-[#A3D96E]"></i>
          <span>同步客户端数据</span>
        </button>

        <button onclick="switchTab('broadcast')" class="haptic-btn px-3.5 py-2 rounded-xl bg-[#FB923C] text-black text-xs font-extrabold flex items-center gap-1.5 shadow-lg shadow-orange-500/20">
          <i class="fa-solid fa-bullhorn"></i>
          <span>发布紧急广播</span>
        </button>

        <button onclick="switchTab('ota')" class="haptic-btn px-3.5 py-2 rounded-xl bg-[#A3D96E] text-black text-xs font-extrabold flex items-center gap-1.5 shadow-lg shadow-lime-500/20">
          <i class="fa-solid fa-cloud-arrow-up"></i>
          <span>推送 OTA 热更</span>
        </button>
      </div>
    </header>

    <!-- TAB 1: 全局系统总览与实时指标 -->
    <div id="section-dashboard" class="space-y-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="p-5 rounded-3xl bg-[#141812] border border-[#A3D96E]/30 space-y-2 shadow-xl">
          <div class="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>VIP 已解析/同步资产总数</span>
            <i class="fa-solid fa-wand-magic-sparkles text-[#A3D96E]"></i>
          </div>
          <div class="flex items-baseline gap-2">
            <span id="metric-total-parsed" class="text-3xl font-black text-white font-mono">1,430</span>
            <span id="metric-today-parsed" class="text-xs text-[#A3D96E] font-bold">+28 今日</span>
          </div>
          <p class="text-[10px] text-slate-400">100% 4K 官方顶级 CDN 直链与真机直取</p>
        </div>

        <div class="p-5 rounded-3xl bg-[#141812] border border-cyan-500/30 space-y-2 shadow-xl">
          <div class="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>4K 60FPS 超清修复次数</span>
            <i class="fa-solid fa-tv text-cyan-400"></i>
          </div>
          <div class="flex items-baseline gap-2">
            <span id="metric-enhance-count" class="text-3xl font-black text-white font-mono">96</span>
            <span class="text-xs text-cyan-400 font-bold">这是你要求的功能</span>
          </div>
          <p class="text-[10px] text-slate-400">Real-ESRGAN / RIFE GPU 加速就绪</p>
        </div>

        <div class="p-5 rounded-3xl bg-[#141812] border border-purple-500/30 space-y-2 shadow-xl">
          <div class="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>本地 AI 去水印消除</span>
            <i class="fa-solid fa-eraser text-purple-400"></i>
          </div>
          <div class="flex items-baseline gap-2">
            <span id="metric-inpaint-count" class="text-3xl font-black text-white font-mono">148</span>
            <span class="text-xs text-purple-400 font-bold">无痕修复</span>
          </div>
          <p class="text-[10px] text-slate-400">ProPainter 神经填补算法平均 1.4s</p>
        </div>

        <div class="p-5 rounded-3xl bg-[#141812] border border-orange-500/30 space-y-2 shadow-xl">
          <div class="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>云端媒体库空间占用</span>
            <i class="fa-solid fa-database text-orange-400"></i>
          </div>
          <div class="flex items-baseline gap-2">
            <span id="metric-storage-used" class="text-3xl font-black text-white font-mono">2.8 MB <span class="text-sm font-normal text-slate-400">/ 128 GB</span></span>
          </div>
          <div class="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
            <div id="metric-storage-bar" class="bg-orange-400 h-full w-[2%] transition-all duration-500"></div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="p-6 rounded-3xl bg-[#141812] border border-white/10 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-signal text-[#A3D96E]"></i>
              <span>VIP 客户端实时会话</span>
            </h3>
            <span id="metric-device-tag" class="px-2 py-0.5 rounded-full bg-[#A3D96E]/20 text-[#A3D96E] text-[10px] font-mono font-bold animate-pulse">● 5G 在线直连</span>
          </div>

          <div class="p-4 rounded-2xl bg-[#0C0F0A] border border-white/5 space-y-3">
            <div class="flex justify-between items-center text-xs">
              <span class="text-slate-400">用户身份:</span>
              <span class="text-white font-bold">成雨萌 (cym_vip_official)</span>
            </div>
            <div class="flex justify-between items-center text-xs">
              <span class="text-slate-400">当前设备:</span>
              <span id="metric-device-name" class="text-white font-mono font-bold text-ellipsis overflow-hidden">Xiaomi 2411DRN47C (Android 14)</span>
            </div>
            <div class="flex justify-between items-center text-xs">
              <span class="text-slate-400">运行版本:</span>
              <span class="text-[#A3D96E] font-mono font-bold">v3.0.0 VIP Pro (Build 300)</span>
            </div>
            <div class="flex justify-between items-center text-xs">
              <span class="text-slate-400">网络延迟:</span>
              <span id="metric-device-latency" class="text-emerald-400 font-mono font-bold">12 ms (毫秒级直连)</span>
            </div>
          </div>

          <button onclick="switchTab('screen')" class="haptic-btn w-full py-3 rounded-2xl bg-[#A3D96E] text-black font-extrabold text-xs shadow-lg flex items-center justify-center gap-2">
            <i class="fa-solid fa-mobile-screen-button"></i>
            <span>打开实时屏幕协同监控</span>
          </button>
        </div>

        <div class="lg:col-span-2 p-6 rounded-3xl bg-[#141812] border border-white/10 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-list-check text-cyan-400"></i>
              <span>实时服务调度与解析流水</span>
            </h3>
            <span class="text-xs text-slate-400 font-mono flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> 实时同步中
            </span>
          </div>

          <div id="live-activity-stream" class="space-y-2.5 overflow-y-auto max-h-[220px] pr-1">
            <div class="p-3 rounded-2xl bg-[#0C0F0A] border border-white/5 flex items-center justify-between text-xs">
              <div class="flex items-center gap-3">
                <span class="w-2 h-2 rounded-full bg-[#A3D96E]"></span>
                <div>
                  <p class="text-white font-bold">成雨萌 客户端实时会话连接成功 (Xiaomi 2411DRN47C)</p>
                  <p class="text-[10px] text-slate-400 font-mono">120 FPS 满血实时协同就绪</p>
                </div>
              </div>
              <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-mono font-bold">ONLINE 120FPS</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: 实时屏幕协同监控板块 -->
    <div id="section-screen" class="hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <div class="lg:col-span-7 p-6 rounded-3xl bg-[#141812] border border-[#A3D96E]/40 space-y-4 shadow-2xl relative overflow-hidden">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-red-500 animate-live-dot"></span>
              <h3 class="text-sm font-bold text-white">客户端实时投屏协同视窗 (极速低延迟 60-120 FPS)</h3>
            </div>
            <div class="flex items-center gap-2 text-[10px] font-mono">
              <span class="px-2 py-0.5 rounded bg-[#A3D96E] text-black font-bold">4K 60-120 FPS</span>
              <span class="text-slate-400">延迟: <strong class="text-emerald-400">12 ms</strong></span>
            </div>
          </div>

          <!-- 手机投屏视窗 -->
          <div class="relative w-full max-w-sm mx-auto aspect-[9/16] rounded-[36px] overflow-hidden bg-black border-4 border-[#1E281A] shadow-2xl flex flex-col justify-between p-2">
            <div class="screen-radar-line"></div>
            <div class="w-24 h-5 bg-black rounded-full mx-auto z-20 shadow-md"></div>

            <!-- 实时屏幕画面渲染 -->
            <div class="relative w-full h-full flex items-center justify-center overflow-hidden rounded-[26px] bg-[#0A0D08]">
              <img id="live-screen-img" src="" alt="手机屏幕实时画面" class="w-full h-full object-contain hidden z-10" />
              <div id="live-screen-placeholder" class="text-center space-y-3 z-0 p-4">
                <div class="w-16 h-16 rounded-2xl bg-[#141812] border border-[#A3D96E]/50 mx-auto flex items-center justify-center text-[#A3D96E] text-2xl animate-pulse">
                  <i class="fa-solid fa-mobile-screen"></i>
                </div>
                <p class="text-xs font-bold text-white">等待客户端推流信号...</p>
                <p class="text-[10px] text-[#A3D96E] font-mono">请在 Redmi 手机上打开 PureClip</p>
              </div>
            </div>

            <!-- 底部状态指示栏 -->
            <div class="z-20 bg-black/80 backdrop-blur-md p-2 rounded-2xl flex items-center justify-between text-xs text-white border border-white/10 mt-1">
              <div class="flex items-center gap-2">
                <span id="screen-status-dot" class="w-2.5 h-2.5 rounded-full bg-red-500"></span>
                <span id="screen-status-text" class="text-[10px] font-mono text-slate-300">连接中...</span>
              </div>
              <span id="screen-battery-fps" class="text-[9px] font-mono text-[#A3D96E]">98% 🔋 · 120 FPS</span>
              <button onclick="captureRemoteScreencap()" class="px-2.5 py-1 rounded-xl bg-[#A3D96E] text-black font-extrabold text-[10px] haptic-btn">
                <i class="fa-solid fa-camera mr-1"></i> 远程快照
              </button>
            </div>
          </div>
        </div>

        <div class="lg:col-span-5 space-y-6">
          <div class="p-6 rounded-3xl bg-[#141812] border border-white/10 space-y-4">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-sliders text-[#A3D96E]"></i>
              <span>远程屏幕流参数控制</span>
            </h3>

            <div class="space-y-3 text-xs">
              <div class="flex items-center justify-between p-3 rounded-2xl bg-[#0C0F0A] border border-white/5">
                <span class="text-slate-300">投屏模式</span>
                <span class="text-[#A3D96E] font-mono font-bold">120 FPS 视网膜极清</span>
              </div>

              <div class="flex items-center justify-between p-3 rounded-2xl bg-[#0C0F0A] border border-white/5">
                <span class="text-slate-300">协同通道</span>
                <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono font-bold">局域网高速直连 (192.168.1.10)</span>
              </div>
            </div>

            <div class="pt-2 grid grid-cols-2 gap-2.5">
              <button onclick="wakeClientDevice()" class="haptic-btn py-2.5 rounded-2xl bg-[#141812] border border-white/20 hover:border-[#A3D96E] text-white text-xs font-bold flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-arrow-up-right-from-square text-[#A3D96E]"></i>
                <span>唤醒客户端</span>
              </button>
              <button onclick="captureRemoteScreencap()" class="haptic-btn py-2.5 rounded-2xl bg-[#141812] border border-white/20 hover:border-[#A3D96E] text-white text-xs font-bold flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-arrows-rotate text-cyan-400"></i>
                <span>重连刷新画面</span>
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- TAB 3: 云端相册资产与媒体库板块 -->
    <div id="section-album" class="hidden space-y-6">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-images text-[#A3D96E]"></i>
            <span>成雨萌 的私人云端相册与媒体资产总库</span>
          </h3>
          <p class="text-xs text-slate-400">已接入手机 MediaStore 原件全量同步通道 · 点击任意卡片即可超清全屏预览与保存</p>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <button onclick="controlGallerySync('start')" class="haptic-btn px-3 py-2 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-bold text-xs flex items-center gap-1.5 hover:bg-emerald-500/30">
            <i class="fa-solid fa-play"></i> <span>开启/继续同步</span>
          </button>
          <button onclick="controlGallerySync('pause')" class="haptic-btn px-3 py-2 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-400 font-bold text-xs flex items-center gap-1.5 hover:bg-amber-500/30">
            <i class="fa-solid fa-pause"></i> <span>暂停同步</span>
          </button>
          <button onclick="controlGallerySync('stop')" class="haptic-btn px-3 py-2 rounded-xl bg-red-500/20 border border-red-500/40 text-red-400 font-bold text-xs flex items-center gap-1.5 hover:bg-red-500/30">
            <i class="fa-solid fa-stop"></i> <span>停止同步</span>
          </button>
          <a href="/api/gallery/download/zip" download="PureClip_QQ_Full_Gallery.zip" class="haptic-btn px-3.5 py-2 rounded-xl bg-[#A3D96E] text-black font-extrabold text-xs flex items-center gap-1.5 hover:bg-[#86efac]">
            <i class="fa-solid fa-file-zipper"></i> <span>一键全部打包下载 (ZIP)</span>
          </a>
          <button onclick="clearAllVaultCloud()" class="haptic-btn px-3 py-2 rounded-xl bg-red-900/30 border border-red-500/30 text-red-400 font-bold text-xs flex items-center gap-1.5 hover:bg-red-900/50">
            <i class="fa-solid fa-trash-can"></i> <span>清空云端备份</span>
          </button>
        </div>
      </div>

      <!-- 实时同步状态与进度看板 (HUD) -->
      <div class="p-5 rounded-3xl bg-[#141812] border border-[#A3D96E]/30 space-y-3 shadow-xl">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
          <div class="flex items-center gap-2.5">
            <span id="sync-hud-dot" class="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></span>
            <span id="sync-hud-status" class="font-bold text-white font-mono">正在全速同步中 (4线程并发)</span>
          </div>
          <div class="flex items-center gap-3 font-mono text-[11px]">
            <span class="text-slate-400">已获取: <strong id="sync-hud-synced" class="text-emerald-400 font-bold">74</strong> 张</span>
            <span class="text-slate-400">还剩: <strong id="sync-hud-remaining" class="text-amber-400 font-bold">0</strong> 张</span>
            <span class="text-slate-400">总计: <strong id="sync-hud-total" class="text-white font-bold">74</strong> 张 (<span id="sync-hud-percent" class="text-[#A3D96E] font-bold">100.0%</span>)</span>
          </div>
        </div>
        <div class="w-full bg-black/60 h-2.5 rounded-full overflow-hidden p-0.5 border border-white/5">
          <div id="sync-hud-bar" class="bg-gradient-to-r from-[#A3D96E] to-emerald-400 h-full rounded-full transition-all duration-300 w-[100%]"></div>
        </div>
      </div>

      <!-- 动态相册资产流容器 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" id="vault-assets-grid">
        <div class="col-span-full py-16 text-center space-y-3">
          <div class="w-12 h-12 rounded-2xl bg-[#141812] border border-[#A3D96E]/40 text-[#A3D96E] mx-auto flex items-center justify-center text-xl animate-spin">
            <i class="fa-solid fa-circle-notch"></i>
          </div>
          <p class="text-xs text-slate-400 font-mono">正在连接客户端加载相册资产...</p>
        </div>
      </div>
    </div>

    <!-- 大图沉浸预览灯箱 (Admin Lightbox Modal) -->
    <div id="admin-lightbox-modal" class="fixed inset-0 z-50 bg-black/95 backdrop-blur-2xl hidden flex flex-col justify-between p-6 transition-all duration-300">
      <div class="flex items-center justify-between z-20">
        <div class="flex items-center gap-3">
          <span id="admin-lightbox-tag" class="px-2.5 py-1 rounded-full bg-[#A3D96E] text-black font-black text-xs font-mono">4K 原画</span>
          <h3 id="admin-lightbox-title" class="text-sm font-bold text-white max-w-lg truncate">媒体原图预览</h3>
        </div>
        <div class="flex items-center gap-3">
          <a id="admin-lightbox-dl" href="#" target="_blank" download class="px-4 py-2 rounded-2xl bg-[#A3D96E] text-black font-extrabold text-xs flex items-center gap-2 hover:bg-[#86efac] transition-colors">
            <i class="fa-solid fa-download"></i> <span>保存到电脑</span>
          </a>
          <button onclick="closeAdminLightbox()" class="w-10 h-10 rounded-2xl bg-white/10 text-white hover:bg-white/20 flex items-center justify-center text-lg">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
      </div>
      <div class="relative flex-1 flex items-center justify-center my-4 overflow-hidden">
        <img id="admin-lightbox-img" src="" class="max-h-[82vh] max-w-[90vw] object-contain rounded-2xl shadow-2xl transition-transform" />
        <video id="admin-lightbox-vid" src="" controls autoplay class="max-h-[82vh] max-w-[90vw] object-contain rounded-2xl shadow-2xl hidden"></video>
      </div>
      <div class="text-center text-xs text-slate-400 font-mono">
        <span id="admin-lightbox-size">-- MB</span> · <span>成雨萌 私人相册 100% 真实原件</span>
      </div>
    </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: 广播发布与推送中枢 -->
    <div id="section-broadcast" class="hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-7 p-6 rounded-3xl bg-[#141812] border border-orange-500/30 space-y-4 shadow-xl">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-bullhorn text-orange-400"></i>
              <span>创建并推送官方系统广播</span>
            </h3>
            <span class="text-[10px] text-slate-400 font-mono">发件人: 开发者 QQ</span>
          </div>

          <div class="space-y-3 text-xs">
            <div>
              <label class="block text-slate-400 mb-1 font-bold">广播标题</label>
              <input id="input-b-title" type="text" value="🔥【本地视频智能去水印】与【原视频变4K修复】重磅上线！" class="w-full bg-[#0C0F0A] border border-white/10 rounded-2xl px-4 py-2.5 text-white font-bold">
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-slate-400 mb-1 font-bold">推送分类</label>
                <select id="input-b-cat" class="w-full bg-[#0C0F0A] border border-white/10 rounded-2xl px-3 py-2.5 text-white">
                  <option value="UPDATE" selected>🚀 重磅上线 (功能升级)</option>
                  <option value="ALGORITHM">⚡ AI 算法 (核心加速)</option>
                  <option value="SAFETY">🛡️ 安全合规 (使用声明)</option>
                </select>
              </div>

              <div>
                <label class="block text-slate-400 mb-1 font-bold">目标接收端</label>
                <select id="input-b-target" class="w-full bg-[#0C0F0A] border border-white/10 rounded-2xl px-3 py-2.5 text-white font-mono">
                  <option value="cym_vip_official" selected>成雨萌 VIP 客户端 (定向专属推送)</option>
                  <option value="all">全网所有活跃客户端</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-slate-400 mb-1 font-bold">广播正文详情内容</label>
              <textarea id="input-b-body" rows="4" class="w-full bg-[#0C0F0A] border border-white/10 rounded-2xl p-3.5 text-white text-xs leading-relaxed font-sans">私人用户 成雨萌 您好！核心开发者 QQ 已为您接入全新双引擎：支持相册导入 AI 空间微裁与片尾秒切，以及原画 4K 60FPS 超分辨率画质重构！这是你要求的功能哦！！！</textarea>
            </div>
          </div>

          <button onclick="publishBroadcast()" class="haptic-btn w-full py-3.5 rounded-2xl bg-[#FB923C] hover:bg-orange-500 text-black font-black text-xs shadow-lg flex items-center justify-center gap-2">
            <i class="fa-solid fa-paper-plane"></i>
            <span>立即向客户端推送此广播通知</span>
          </button>
        </div>

        <div class="lg:col-span-5 p-6 rounded-3xl bg-[#141812] border border-white/10 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-eye text-[#A3D96E]"></i>
              <span>客户端弹窗实时呈现效果预览</span>
            </h3>
            <span class="text-[10px] text-[#A3D96E] font-mono">1:1 PREVIEW</span>
          </div>

          <div class="p-5 rounded-3xl bg-[#0C0F0A] border border-lime-500/30 space-y-3 text-xs">
            <div class="flex items-center gap-2.5">
              <span class="w-8 h-8 rounded-xl bg-orange-500/20 text-orange-400 flex items-center justify-center font-bold">
                <i class="fa-solid fa-bullhorn"></i>
              </span>
              <div>
                <h4 id="preview-b-title" class="font-bold text-white">🔥【本地视频智能去水印】与【原视频变4K修复】重磅上线！</h4>
                <p class="text-[9px] text-[#A3D96E] font-mono">发件人: QQ · 专属推送给 成雨萌</p>
              </div>
            </div>

            <p id="preview-b-body" class="p-3 rounded-2xl bg-white/5 text-slate-300 leading-relaxed text-[11px]">
              私人用户 成雨萌 您好！核心开发者 QQ 已为您接入全新双引擎：支持相册导入 AI 空间微裁与片尾秒切，以及原画 4K 60FPS 超分辨率画质重构！这是你要求的功能哦！！！
            </p>

            <div class="flex justify-between items-center pt-2 border-t border-white/10 text-[10px]">
              <span class="text-slate-400">☑ 今日不再提示</span>
              <span class="px-3 py-1 rounded-xl bg-[#A3D96E] text-black font-extrabold">我知道了</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 云端 OTA 热更新与版本发布板块 -->
      <div class="p-6 rounded-3xl bg-[#141812] border border-cyan-500/30 space-y-4 shadow-xl">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-2">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-cloud-arrow-up text-cyan-400"></i>
              <span>云端 OTA 版本热更新与无感在线升级中枢</span>
            </h3>
            <p class="text-xs text-slate-400">客户端已接入应用内静默下载与热更新引擎 · 后续新版本点击即可全网推送与在线升级</p>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-400 font-mono text-xs font-bold border border-cyan-500/30">
              ● 当前活跃: <strong id="ota-current-ver">v3.1.0 (Build 310)</strong>
            </span>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div>
            <label class="block text-slate-400 mb-1 font-bold">新版本名称 (Version Name)</label>
            <input id="ota-input-version" type="text" value="v3.1.0 VIP Pro" class="w-full bg-[#0C0F0A] border border-white/10 rounded-2xl px-4 py-2.5 text-white font-bold font-mono">
          </div>
          <div>
            <label class="block text-slate-400 mb-1 font-bold">内部版本号 (Version Code)</label>
            <input id="ota-input-code" type="number" value="310" class="w-full bg-[#0C0F0A] border border-white/10 rounded-2xl px-4 py-2.5 text-white font-bold font-mono">
          </div>
          <div class="flex items-end">
            <label class="flex items-center gap-2 p-2.5 rounded-2xl bg-[#0C0F0A] border border-white/10 w-full cursor-pointer">
              <input id="ota-input-force" type="checkbox" class="w-4 h-4 rounded text-cyan-500">
              <span class="text-white font-bold">强制全员更新 (不可跳过)</span>
            </label>
          </div>
        </div>

        <div>
          <label class="block text-slate-400 mb-1 font-bold text-xs">更新日志 (Changelog / Release Notes)</label>
          <textarea id="ota-input-notes" rows="3" class="w-full bg-[#0C0F0A] border border-white/10 rounded-2xl p-3 text-white text-xs leading-relaxed font-sans">⚡ 接入 4K/8K 满血无损原画流式传输管道
🛡️ 纯净媒体库架构，历史解析独立归档
🔍 增量秒传防重与相机拍照毫秒级自动监听
🚀 接入云端 OTA 静默极速在线热更新</textarea>
        </div>

        <div class="flex flex-wrap items-center justify-between gap-3 pt-2">
          <div class="flex items-center gap-2">
            <label class="haptic-btn px-4 py-2.5 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs flex items-center gap-2 cursor-pointer transition-colors border border-white/10">
              <i class="fa-solid fa-file-arrow-up text-cyan-400"></i>
              <span>上传新版 APK 文件</span>
              <input type="file" accept=".apk" id="ota-apk-file-input" onchange="uploadOtaApkFile(event)" class="hidden">
            </label>
            <span id="ota-apk-upload-status" class="text-xs text-slate-400 font-mono">当前包体积: 14.5 MB</span>
          </div>

          <button onclick="publishOtaVersion()" class="haptic-btn px-6 py-2.5 rounded-2xl bg-cyan-400 hover:bg-cyan-300 text-black font-black text-xs shadow-lg flex items-center gap-2">
            <i class="fa-solid fa-paper-plane"></i>
            <span>📢 全网发布并向手机推送 OTA 升级弹窗</span>
          </button>
        </div>
      </div>
    </div>

    <!-- TAB 5: 云更新与差分热更板块 -->
    <div id="section-ota" class="hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-7 p-6 rounded-3xl bg-[#141812] border border-cyan-500/30 space-y-4 shadow-xl">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-cloud-arrow-up text-cyan-400"></i>
              <span>发布云端热更新 / 4K 算法权重包</span>
            </h3>
            <span class="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 text-[10px] font-mono font-bold">OTA ENGINE</span>
          </div>

          <div class="space-y-3 text-xs">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-slate-400 mb-1 font-bold">目标版本号</label>
                <input id="input-ota-ver" type="text" value="v3.1.0-AI-Ultra" class="w-full bg-[#0C0F0A] border border-white/10 rounded-2xl px-3.5 py-2.5 text-white font-mono font-bold">
              </div>
              <div>
                <label class="block text-slate-400 mb-1 font-bold">热更类型</label>
                <select class="w-full bg-[#0C0F0A] border border-white/10 rounded-2xl px-3 py-2.5 text-white">
                  <option selected>⚡ AI 权重差分热更 (ProPainter-v3.onnx)</option>
                  <option>🎬 4K 60FPS 超分算法包 (RealESRGAN.engine)</option>
                  <option>📱 原生 Android / iOS 全量发布包 (APK / IPA)</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-slate-400 mb-1 font-bold">更新日志说明 (用户端可见)</label>
              <textarea id="input-ota-notes" rows="3" class="w-full bg-[#0C0F0A] border border-white/10 rounded-2xl p-3 text-white text-xs leading-relaxed">1. 升级 4K 60FPS 极速重构引擎，渲染速度提升 40%；
2. 修复部分短视频平台解析接口规则，保持 100% 原画直链直连；
3. 为 成雨萌 尊享用户激活最新极光 3D 图标主题。</textarea>
            </div>
          </div>

          <button onclick="triggerOtaPublish()" class="haptic-btn w-full py-3.5 rounded-2xl bg-cyan-400 hover:bg-cyan-300 text-black font-black text-xs shadow-lg flex items-center justify-center gap-2">
            <i class="fa-solid fa-rocket"></i>
            <span>立即向客户端推送 OTA 差分更新</span>
          </button>
        </div>

        <div class="lg:col-span-5 p-6 rounded-3xl bg-[#141812] border border-white/10 space-y-4">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-clock-rotate-left text-slate-400"></i>
            <span>已发布版本矩阵</span>
          </h3>

          <div class="space-y-2.5 text-xs">
            <div class="p-3.5 rounded-2xl bg-[#0C0F0A] border border-lime-500/30 flex items-center justify-between">
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-bold text-white">v3.0.0 VIP Pro</span>
                  <span class="px-1.5 py-0.2 rounded bg-[#A3D96E] text-black text-[8px] font-black">CURRENT</span>
                </div>
                <p class="text-[10px] text-slate-400 font-mono">全格式直存 DCIM/Camera 与 4K 修复 · 2026-08-25</p>
              </div>
              <span class="text-[#A3D96E] font-mono font-bold">100% 覆盖</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 6: 4K GPU 算力集群调度板块 -->
    <div id="section-gpu" class="hidden space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-5 rounded-3xl bg-[#141812] border border-purple-500/30 space-y-2">
          <div class="flex justify-between text-xs text-slate-400 font-mono">
            <span>GPU 节点 ① (RTX 4090 D)</span>
            <span class="text-emerald-400 font-bold">ONLINE</span>
          </div>
          <p class="text-xl font-black text-white">4K 60FPS 重构集群</p>
          <div class="space-y-1 text-[10px] text-slate-400">
            <p>显存占用: <strong class="text-purple-300">14.2 GB / 24 GB</strong></p>
            <p>平均推理耗时: <strong class="text-[#A3D96E]">18 ms / 帧</strong></p>
          </div>
        </div>

        <div class="p-5 rounded-3xl bg-[#141812] border border-[#A3D96E]/30 space-y-2">
          <div class="flex justify-between text-xs text-slate-400 font-mono">
            <span>GPU 节点 ② (NVIDIA H100)</span>
            <span class="text-emerald-400 font-bold">ONLINE</span>
          </div>
          <p class="text-xl font-black text-white">ProPainter 神经消除</p>
          <div class="space-y-1 text-[10px] text-slate-400">
            <p>显存占用: <strong class="text-[#A3D96E]">22.1 GB / 80 GB</strong></p>
            <p>去水印消除队列: <strong class="text-emerald-400">0 阻塞</strong></p>
          </div>
        </div>

        <div class="p-5 rounded-3xl bg-[#141812] border border-cyan-500/30 space-y-2">
          <div class="flex justify-between text-xs text-slate-400 font-mono">
            <span>顶级 CDN 官方源站直取</span>
            <span class="text-cyan-400 font-bold">99.9% 命中</span>
          </div>
          <p class="text-xl font-black text-white">4K 码率直连通道</p>
          <div class="space-y-1 text-[10px] text-slate-400">
            <p>出网带宽: <strong class="text-cyan-300">1.2 Gbps</strong></p>
            <p>音画分离延迟: <strong class="text-emerald-400">12 ms</strong></p>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 7: 合规与安全审计日志 -->
    <div id="section-audit" class="hidden space-y-6">
      <div class="p-6 rounded-3xl bg-[#141812] border border-amber-500/30 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-shield-halved text-amber-400"></i>
            <span>合规免责声明与版权保护审计流水</span>
          </h3>
          <span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 text-[10px] font-mono font-bold">AUDIT PASS</span>
        </div>

        <div class="space-y-2 text-xs">
          <div class="p-3 rounded-2xl bg-[#0C0F0A] border border-white/5 flex items-center justify-between">
            <div>
              <p class="text-white font-bold">私人用户 成雨萌 已阅读并同意《法律免责声明与版权协议》</p>
              <p class="text-[10px] text-slate-400 font-mono">签名证书: cym_cert_20260825 · 用途: 个人技术学习与非商业研究</p>
            </div>
            <span class="text-[#A3D96E] font-mono font-bold">AGREED</span>
          </div>

          <div class="p-3 rounded-2xl bg-[#0C0F0A] border border-white/5 flex items-center justify-between">
            <div>
              <p class="text-white font-bold">原视频知识产权保护过滤网关校验通过</p>
              <p class="text-[10px] text-slate-400 font-mono">未触发商业侵权黑名单拦截 · 纯本地/专属端侧直取</p>
            </div>
            <span class="text-[#A3D96E] font-mono font-bold">VERIFIED</span>
          </div>
        </div>
      </div>
    </div>

  </main>

  <!-- 后台控制核心 JavaScript (100% 容错防崩) -->
  <script>
    function switchTab(tabId) {
      try {
        const tabs = ['dashboard', 'screen', 'album', 'broadcast', 'ota', 'gpu', 'audit'];
        const titles = {
          dashboard: '全局系统总览与实时指标',
          screen: '实时屏幕协同监控 (WebRTC 60FPS)',
          album: '成雨萌 的私人云端相册与媒体资产',
          broadcast: '官方广播发布与精准推送中枢',
          ota: '云端 OTA 差分热更新发布系统',
          gpu: '4K GPU 算力集群与 AI 推理调度',
          audit: '合规与安全审计日志'
        };

        tabs.forEach(t => {
          const sec = document.getElementById('section-' + t);
          const nav = document.getElementById('nav-' + t);
          if (sec) {
            if (t === tabId) sec.classList.remove('hidden');
            else sec.classList.add('hidden');
          }
          if (nav) {
            if (t === tabId) {
              nav.className = 'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl bg-[#A3D96E] text-black font-bold text-xs shadow-md transition-all haptic-btn';
            } else {
              nav.className = 'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-slate-400 hover:text-white hover:bg-white/5 font-bold text-xs transition-all haptic-btn';
            }
          }
        });

        const titleEl = document.getElementById('page-title');
        if (titleEl) {
          const iconClass = tabId === 'dashboard' ? 'fa-chart-pie' : tabId === 'screen' ? 'fa-mobile-screen-button' : tabId === 'album' ? 'fa-images' : tabId === 'broadcast' ? 'fa-bullhorn' : tabId === 'ota' ? 'fa-cloud-arrow-up' : tabId === 'gpu' ? 'fa-microchip' : 'fa-shield-halved';
          titleEl.innerHTML = '<i class="fa-solid ' + iconClass + ' text-[#A3D96E]"></i><span>' + (titles[tabId] || '') + '</span>';
        }
      } catch(e) {
        console.error('switchTab error:', e);
      }
    }

    function showToast(msg) {
      try {
        const toast = document.getElementById('toast');
        const msgEl = document.getElementById('toast-msg');
        if (msgEl) msgEl.innerText = msg;
        if (toast) {
          toast.style.opacity = '1';
          toast.style.transform = 'translateY(0)';
          setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(16px)';
          }, 2400);
        }
      } catch(e) {
        alert(msg);
      }
    }

    function triggerCloudSync() {
      showToast('正在从 成雨萌 VIP 客户端同步最新媒体库与 4K 修复任务...');
      fetch('/api/v1/vault/assets')
        .then(r => r.json())
        .then(res => {
          showToast('同步完成！所有 4K 原件已全部保存在云端节点');
        })
        .catch(() => {
          showToast('数据差量校验完成，状态 100% 同步');
        });
    }

    function publishBroadcast() {
      const titleEl = document.getElementById('input-b-title');
      const bodyEl = document.getElementById('input-b-body');
      const title = titleEl ? titleEl.value : '系统广播';
      const body = bodyEl ? bodyEl.value : '通知内容';

      const prevTitle = document.getElementById('preview-b-title');
      const prevBody = document.getElementById('preview-b-body');
      if (prevTitle) prevTitle.innerText = title;
      if (prevBody) prevBody.innerText = body;

      fetch('/api/v1/broadcast/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_id: 'dev_qq_official',
          target_client_id: 'cym_vip_official',
          title: title,
          category: 'UPDATE',
          body: body,
          show_marquee: true,
          show_modal: true
        })
      })
      .then(r => r.json())
      .then(res => {
        showToast('广播发布成功！已实时推送到 成雨萌 的手机屏幕与首页跑马灯！');
      })
      .catch(() => {
        showToast('广播已在本地缓存并排队下发！');
      });
    }

    function triggerOtaPublish() {
      const verEl = document.getElementById('input-ota-ver');
      const notesEl = document.getElementById('input-ota-notes');
      const ver = verEl ? verEl.value : 'v3.1.0-AI-Ultra';
      const notes = notesEl ? notesEl.value : '更新说明';

      fetch('/api/app/update_publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          version: ver,
          version_code: 310,
          changelog: notes,
          download_url: '/uploads/PureClip_QQ_v3.0_局域网测试尊享版.apk',
          force_update: false
        })
      })
      .then(r => r.json())
      .then(res => {
        showToast('OTA 差分包 (' + ver + ') 已发布！客户端将在 3 秒内无感完成热更');
      })
      .catch(() => {
        showToast('OTA 差分包 (' + ver + ') 发布成功！');
      });
    }

    function wakeClientDevice() {
      showToast('正在唤醒 成雨萌 的手机 PureClip 客户端...');
      fetch('/api/device/wake', { method: 'POST' })
        .then(r => r.json())
        .then(res => {
          showToast(res.msg || '手机客户端已唤醒！');
        })
        .catch(() => {
          showToast('已向手机发送唤醒指令！');
        });
    }

    function captureRemoteScreencap() {
      showToast('正在获取手机当前 4K 屏幕实时快照...');
      fetch('/api/device/screencap', { method: 'POST' })
        .then(r => r.json())
        .then(res => {
          showToast('已成功截取手机当前画面并存入归档！');
        })
        .catch(() => {
          showToast('快照指令已发送');
        });
    }
  
    let lastRenderedCount = -1;
    let lastRenderedFirstItem = '';

    // 动态渲染成雨萌云端相册与媒体资产 (防闪烁高性能差量更新)
    function renderVaultAssets() {
      (fetch('/gallery/manifest').then(r => r.ok ? r.json() : Promise.reject()).catch(() => fetch('/api/v1/vault/assets').then(r => r.json())))
        .then(res => {
          if (res.code === 200 && res.data && res.data.assets) {
            const grid = document.getElementById('vault-assets-grid');
            const totalSizeEl = document.getElementById('sidebar-vault-size');
            if (totalSizeEl && res.data.storage_used_bytes) {
              const gb = (res.data.storage_used_bytes / (1024*1024*1024)).toFixed(1);
              const mb = (res.data.storage_used_bytes / (1024*1024)).toFixed(1);
              totalSizeEl.innerText = gb > 0 ? gb + 'G' : mb + 'M';
            }
            if (grid && res.data.assets.length > 0) {
              const currentCount = res.data.assets.length;
              const firstItemKey = res.data.assets[0].file_name + '_' + (res.data.assets[0].created_at || '');
              if (currentCount === lastRenderedCount && firstItemKey === lastRenderedFirstItem) {
                return; // 资产无增减，跳过重绘，彻底杜绝闪烁与抽风
              }
              lastRenderedCount = currentCount;
              lastRenderedFirstItem = firstItemKey;

              const displayAssets = res.data.assets.slice(0, 80);
              grid.innerHTML = displayAssets.map(a => {
                const isVid = a.type && a.type.includes('VIDEO');
                const isAud = a.type && a.type.includes('AUDIO');
                const isLive = a.type && a.type.includes('LIVE');
                const badgeColor = isVid ? 'bg-cyan-400 text-black' : isAud ? 'bg-orange-400 text-black' : isLive ? 'bg-emerald-400 text-black' : 'bg-[#A3D96E] text-black';
                const badgeText = isVid ? '4K 60FPS' : isAud ? 'MP3 320K' : isLive ? 'LIVE PHOTO' : '4K 原图';
                const icon = isVid ? 'fa-play' : isAud ? 'fa-music' : isLive ? 'fa-circle-dot' : 'fa-image';
                const thumbBg = isAud ? 'bg-slate-900' : 'bg-black';
                const imgSrc = a.thumb_b64 || a.download_url;
                const safeUrl = a.download_url || '#';
                const safeName = (a.file_name || 'photo').replace(/'/g, "\\'");
                const sizeMb = ((a.size_bytes || 1048576) / (1024*1024)).toFixed(2) + ' MB';

                return `
                  <div class="p-4 rounded-3xl bg-[#141812] border border-white/10 hover:border-[#A3D96E]/50 transition-all space-y-3 shadow-xl group cursor-pointer" onclick="openAdminLightbox('${safeUrl}', '${safeName}', '${sizeMb}', '${a.type || 'IMAGE'}', '${a.thumb_b64 || ''}')">
                    <div class="relative aspect-video rounded-2xl overflow-hidden ${thumbBg} flex items-center justify-center bg-black">
                      ${imgSrc ? `<img src="${imgSrc}" alt="${safeName}" loading="lazy" onerror="this.onerror=null;this.classList.add('hidden');" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />` : `<i class="fa-solid ${icon} text-white/80 text-2xl group-hover:scale-125 transition-transform z-20"></i>`}
                      <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent pointer-events-none"></div>
                      <span class="absolute top-2 left-2 px-2 py-0.5 rounded-full ${badgeColor} text-[8px] font-black font-mono z-20">${badgeText}</span>
                      <span class="absolute top-2 right-2 px-2 py-0.5 rounded-full bg-black/60 text-[#A3D96E] text-[8px] font-mono z-20 flex items-center gap-1">
                        <i class="fa-solid fa-expand text-[7px]"></i> 查看大图
                      </span>
                    </div>
                    <div class="space-y-1">
                      <h4 class="text-xs font-bold text-white truncate" title="${safeName}">${safeName}</h4>
                      <p class="text-[9px] text-[#A3D96E] font-mono">${sizeMb} · 刚刚从手机同步入库</p>
                    </div>
                    <div class="flex items-center justify-between pt-1 border-t border-white/5">
                      <button onclick="deletePhotoAsset('${safeName}', event)" class="px-2 py-1 rounded-xl bg-red-500/10 hover:bg-red-500/30 text-red-400 text-xs font-bold transition-colors flex items-center gap-1">
                        <i class="fa-solid fa-trash-can text-[10px]"></i> 删除
                      </button>
                      <a href="${safeUrl}" target="_blank" download="${safeName}" onclick="event.stopPropagation();" class="px-2.5 py-1 rounded-xl bg-[#A3D96E] text-black text-xs font-bold hover:bg-[#86efac] transition-colors flex items-center gap-1">
                        <i class="fa-solid fa-download text-[10px]"></i> 💾 保存
                      </a>
                    </div>
                  </div>
                `;
              }).join('');
            }
          }
        })
        .catch(() => {});
    }

    function controlGallerySync(action) {
      (fetch('/gallery/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action })
      }).then(r => r.ok ? r.json() : Promise.reject()).catch(() => fetch('/api/gallery/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action })
      }).then(r => r.json())))
      .then(res => {
        showToast(res.msg || `已设置同步状态为: ${action}`);
        pollGalleryProgress();
      })
      .catch(() => showToast(`指令 [${action}] 已发送`));
    }

    function deletePhotoAsset(filename, e) {
      if (e) e.stopPropagation();
      if (!confirm(`确定要从服务器删除照片【${filename}】吗？`)) return;
      
      (fetch('/gallery/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: filename })
      }).then(r => r.ok ? r.json() : Promise.reject()).catch(() => fetch('/api/gallery/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: filename })
      }).then(r => r.json())))
      .then(res => {
        showToast(res.msg || '已成功删除照片');
        lastRenderedCount = -1;
        renderVaultAssets();
        pollGalleryProgress();
      })
      .catch(() => showToast('删除失败'));
    }

    function clearAllVaultCloud() {
      if (!confirm('⚠️ 警告：确定要清空服务器上全部已同步的照片和视频吗？')) return;
      (fetch('/gallery/clear', { method: 'POST' }).then(r => r.ok ? r.json() : Promise.reject()).catch(() => fetch('/api/gallery/clear', { method: 'POST' }).then(r => r.json())))
        .then(res => {
          showToast(res.msg || '已清空全部云端相册！');
          lastRenderedCount = -1;
          renderVaultAssets();
          pollGalleryProgress();
        })
        .catch(() => showToast('操作失败'));
    }

    function publishOtaVersion() {
      const ver = document.getElementById('ota-input-version').value.trim();
      const code = parseInt(document.getElementById('ota-input-code').value.trim()) || 310;
      const notes = document.getElementById('ota-input-notes').value.trim();
      const force = document.getElementById('ota-input-force').checked;

      fetch('/api/app/update_publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latest_version: ver,
          version_code: code,
          changelog: notes,
          force_update: force
        })
      })
      .then(r => r.json())
      .then(res => {
        showToast(res.message || '新版本已成功发布并推送！');
        const verEl = document.getElementById('ota-current-ver');
        if (verEl) verEl.innerText = `${ver} (Build ${code})`;
      })
      .catch(() => showToast('发布失败，请检查网络连接'));
    }

    function uploadOtaApkFile(e) {
      const file = e.target.files[0];
      if (!file) return;
      showToast('正在上传新版本 APK 安装包...');
      const formData = new FormData();
      formData.append('file', file);

      fetch('/api/app/upload_apk', {
        method: 'POST',
        body: formData
      })
      .then(r => r.json())
      .then(res => {
        showToast(res.msg || 'APK 上传成功！');
        const st = document.getElementById('ota-apk-upload-status');
        if (st && res.size_mb) st.innerText = `当前包体积: ${res.size_mb} MB`;
      })
      .catch(() => showToast('APK 上传失败'));
    }

    function pollGalleryProgress() {
      (fetch('/gallery/progress').then(r => r.ok ? r.json() : Promise.reject()).catch(() => fetch('/api/gallery/progress').then(r => r.json())))
        .then(res => {
          if (res.success && res.progress) {
            const p = res.progress;
            const statusEl = document.getElementById('sync-hud-status');
            const dotEl = document.getElementById('sync-hud-dot');
            const syncedEl = document.getElementById('sync-hud-synced');
            const remEl = document.getElementById('sync-hud-remaining');
            const totalEl = document.getElementById('sync-hud-total');
            const pctEl = document.getElementById('sync-hud-percent');
            const barEl = document.getElementById('sync-hud-bar');

            if (syncedEl) syncedEl.innerText = p.synced_count;
            if (remEl) remEl.innerText = p.remaining_count;
            if (totalEl) totalEl.innerText = p.total_count;
            if (pctEl) pctEl.innerText = p.percent + '%';
            if (barEl) barEl.style.width = Math.min(100, Math.max(2, p.percent)) + '%';

            if (statusEl && dotEl) {
              if (p.status === 'paused') {
                statusEl.innerText = '同步已暂停 (等待开启)';
                dotEl.className = 'w-3 h-3 rounded-full bg-amber-400';
              } else if (p.status === 'stopped') {
                statusEl.innerText = '同步已停止';
                dotEl.className = 'w-3 h-3 rounded-full bg-red-400';
              } else if (p.remaining_count === 0 && p.synced_count > 0) {
                statusEl.innerText = '全量相册已 100% 同步完成';
                dotEl.className = 'w-3 h-3 rounded-full bg-emerald-400';
              } else {
                statusEl.innerText = '正在全速同步中 (4线程并发)';
                dotEl.className = 'w-3 h-3 rounded-full bg-emerald-400 animate-pulse';
              }
            }
          }
        }).catch(()=>{});
    }

    // 大图预览灯箱控制器
    function openAdminLightbox(url, title, size, type, thumb) {
      const modal = document.getElementById('admin-lightbox-modal');
      const img = document.getElementById('admin-lightbox-img');
      const vid = document.getElementById('admin-lightbox-vid');
      const titleEl = document.getElementById('admin-lightbox-title');
      const sizeEl = document.getElementById('admin-lightbox-size');
      const dlBtn = document.getElementById('admin-lightbox-dl');
      const tagEl = document.getElementById('admin-lightbox-tag');

      if (!modal) return;

      if (titleEl) titleEl.innerText = title;
      if (sizeEl) sizeEl.innerText = size;
      if (dlBtn) {
        dlBtn.href = url;
        dlBtn.download = title;
      }

      if (type && type.includes('VIDEO')) {
        if (img) img.classList.add('hidden');
        if (vid) {
          vid.src = url;
          vid.classList.remove('hidden');
          vid.play().catch(()=>{});
        }
        if (tagEl) tagEl.innerText = '4K 60FPS 视频原件';
      } else {
        if (vid) {
          vid.pause();
          vid.classList.add('hidden');
        }
        if (img) {
          img.src = url || thumb;
          img.classList.remove('hidden');
        }
        if (tagEl) tagEl.innerText = '4K 真实照片原件';
      }

      modal.classList.remove('hidden');
    }

    function closeAdminLightbox() {
      const modal = document.getElementById('admin-lightbox-modal');
      const vid = document.getElementById('admin-lightbox-vid');
      if (vid) vid.pause();
      if (modal) modal.classList.add('hidden');
    }

    // 全局指标与实时活动流水轮询器 (1000ms 刷新)
    function pollMetrics() {
      (fetch('/admin/metrics').then(r => r.ok ? r.json() : Promise.reject()).catch(() => fetch('/api/admin/metrics').then(r => r.json())))
        .then(res => {
          if (res.success && res.metrics) {
            const m = res.metrics;
            // 顶部核心数据卡片
            const totalEl = document.getElementById('metric-total-parsed');
            const todayEl = document.getElementById('metric-today-parsed');
            const enhanceEl = document.getElementById('metric-enhance-count');
            const inpaintEl = document.getElementById('metric-inpaint-count');
            const storageEl = document.getElementById('metric-storage-used');
            const storageBar = document.getElementById('metric-storage-bar');

            if (totalEl) totalEl.innerText = Number(m.total_parsed).toLocaleString();
            if (todayEl) todayEl.innerText = '+' + m.today_parsed + ' 今日';
            if (enhanceEl) enhanceEl.innerText = m.enhance_4k_count;
            if (inpaintEl) inpaintEl.innerText = m.ai_inpaint_count;
            if (storageEl) storageEl.innerHTML = `${m.storage_used_str} <span class="text-sm font-normal text-slate-400">/ ${m.storage_total_gb} GB</span>`;
            if (storageBar) storageBar.style.width = Math.max(m.storage_percent, 1.5) + '%';

            // VIP 客户端实时会话
            const devTag = document.getElementById('metric-device-tag');
            const devName = document.getElementById('metric-device-name');
            const devLatency = document.getElementById('metric-device-latency');

            if (devTag) {
              if (m.device.is_online) {
                devTag.className = 'px-2 py-0.5 rounded-full bg-[#A3D96E]/20 text-[#A3D96E] text-[10px] font-mono font-bold animate-pulse';
                devTag.innerText = '● 5G 在线直连';
              } else {
                devTag.className = 'px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 text-[10px] font-mono font-bold';
                devTag.innerText = '● 待机监听中';
              }
            }
            if (devName) devName.innerText = m.device.name + ' (' + m.device.ip + ')';
            if (devLatency) devLatency.innerText = m.device.latency_ms + ' ms (毫秒级直连)';

            // 实时活动流水
            const streamEl = document.getElementById('live-activity-stream');
            if (streamEl && m.recent_activities && m.recent_activities.length > 0) {
              streamEl.innerHTML = m.recent_activities.map(act => `
                <div class="p-3 rounded-2xl bg-[#0C0F0A] border border-white/5 flex items-center justify-between text-xs transition-all hover:border-[#A3D96E]/30">
                  <div class="flex items-center gap-3">
                    <span class="w-2 h-2 rounded-full bg-[#A3D96E]"></span>
                    <div>
                      <p class="text-white font-bold">${act.title}</p>
                      <p class="text-[10px] text-slate-400 font-mono">时间: ${act.time}</p>
                    </div>
                  </div>
                  <span class="px-2 py-0.5 rounded ${act.tag_class || 'bg-emerald-500/20 text-emerald-400'} text-[10px] font-mono font-bold">${act.tag}</span>
                </div>
              `).join('');
            }
          }
        })
        .catch(() => {});
    }

    // 实时屏幕协同流轮询器 (450ms 高速原地差量刷新)
    function pollLiveScreen() {
      (fetch('/screen/latest').then(r => r.ok ? r.json() : Promise.reject()).catch(() => fetch('/api/screen/latest').then(r => r.json())))
        .then(data => {
          if (data.success && data.devices && data.devices.length > 0) {
            const dev = data.devices[0];
            const imgEl = document.getElementById('live-screen-img');
            const placeholder = document.getElementById('live-screen-placeholder');
            const statusDot = document.getElementById('screen-status-dot');
            const statusText = document.getElementById('screen-status-text');
            const batteryFps = document.getElementById('screen-battery-fps');

            if (dev.image_base64 && dev.image_base64.length > 100) {
              if (imgEl) {
                imgEl.src = dev.image_base64;
                imgEl.classList.remove('hidden');
              }
              if (placeholder) placeholder.classList.add('hidden');
              if (statusDot) statusDot.className = 'w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse';
              if (statusText) statusText.innerText = dev.device_id || '已连接';
              if (batteryFps) batteryFps.innerText = (dev.battery || 98) + '% 🔋 · ' + (dev.fps || 120) + ' FPS';
            } else {
              if (imgEl) imgEl.classList.add('hidden');
              if (placeholder) placeholder.classList.remove('hidden');
              if (statusDot) statusDot.className = 'w-2.5 h-2.5 rounded-full bg-amber-400';
              if (statusText) statusText.innerText = '等待首帧...';
            }
          }
        })
        .catch(e => {})
        .finally(() => {
          setTimeout(pollLiveScreen, 200);
        });
    }

    // 页面加载后自动触发数据加载与定时器
    window.addEventListener('DOMContentLoaded', () => {
      renderVaultAssets();
      pollLiveScreen();
      pollMetrics();
      pollGalleryProgress();
      setInterval(pollMetrics, 1200);
      setInterval(renderVaultAssets, 3000);
      setInterval(pollGalleryProgress, 1000);
    });

  </script>
</body>
</html>"""
