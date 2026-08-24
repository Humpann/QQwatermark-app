ADMIN_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #090d16 0%, #111625 50%, #080b12 100%);
            min-height: 100vh;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, sans-serif;
        }
        .glass-card {
            background: rgba(18, 24, 43, 0.78);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .glass-island {
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(28px);
            border: 1px solid rgba(255, 255, 255, 0.12);
        }
        .rainbow-badge {
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        .custom-checkbox {
            appearance: none;
            width: 22px;
            height: 22px;
            border: 2px solid rgba(255, 255, 255, 0.45);
            border-radius: 7px;
            background: rgba(15, 23, 42, 0.85);
            cursor: pointer;
            position: relative;
            transition: all 0.2s;
        }
        .custom-checkbox:checked {
            background: #6366f1;
            border-color: #a5b4fc;
        }
        .custom-checkbox:checked::after {
            content: "✓";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 14px;
            font-weight: 900;
        }
        .phone-mockup {
            border: 12px solid #1e293b;
            border-radius: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        }
    </style>
</head>
<body class="p-3 md:p-6 flex flex-col items-center">

    <!-- 顶部主导航栏 -->
    <header class="w-full max-w-7xl flex flex-col lg:flex-row lg:items-center justify-between gap-4 py-3 px-4 glass-card rounded-3xl mb-6 shadow-2xl">
        <div class="flex items-center space-x-3.5">
            <div class="w-12 h-12 rounded-2xl rainbow-badge flex items-center justify-center shadow-lg shadow-indigo-500/25 shrink-0">
                <i data-lucide="sparkles" class="w-6 h-6 text-slate-950 font-black"></i>
            </div>
            <div>
                <div class="flex items-center space-x-2">
                    <h1 class="text-xl font-black tracking-tight text-white">QQ定制 · Onyx 5.0 全能中控大屏</h1>
                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-indigo-500/25 text-indigo-300 border border-indigo-500/40">旗舰企业级</span>
                </div>
                <p class="text-xs text-slate-400 mt-0.5">屏幕实时监控 · 管理员动态岛广播 · 云端版本OTA · 智能差量相册 · 总闸控制</p>
            </div>
        </div>

        <!-- 顶部操作区：总闸开关 + 实时状态 + 刷新 -->
        <div class="flex items-center space-x-2.5 flex-wrap gap-y-2 self-end lg:self-auto">
            
            <!-- 上传通道一键暂停/开启总闸 -->
            <button id="master-sync-btn" onclick="toggleMasterSync()" class="px-4 py-2 rounded-2xl text-xs font-black transition active:scale-95 flex items-center space-x-2 border shadow-lg bg-emerald-500/15 border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/25">
                <span id="sync-dot" class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span id="sync-btn-text">通道状态: 实时接收中 (点击暂停)</span>
            </button>

            <!-- 刷新数据 -->
            <button onclick="loadAllDashboardData()" class="px-3.5 py-2 rounded-2xl bg-slate-800/90 hover:bg-slate-700 text-xs font-bold flex items-center space-x-1.5 border border-slate-700 transition active:scale-95 shadow-md">
                <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-sky-400"></i>
                <span>刷新</span>
            </button>

            <!-- 锁定后台 -->
            <button onclick="lockDashboard()" title="退出并锁定后台" class="px-3 py-2 rounded-2xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-xs font-bold flex items-center space-x-1.5 border border-rose-500/30 transition active:scale-95 shadow-md">
                <i data-lucide="lock" class="w-3.5 h-3.5"></i>
                <span>锁定中控</span>
            </button>
        </div>
    </header>

    <!-- 中枢导航 Tab 栏 -->
    <nav class="w-full max-w-7xl flex items-center space-x-2 overflow-x-auto hide-scrollbar mb-6 p-1.5 glass-card rounded-2xl">
        <button onclick="switchTab('gallery')" id="tab-btn-gallery" class="tab-nav-btn active px-4 py-2.5 rounded-xl text-xs font-extrabold flex items-center space-x-2 transition bg-indigo-600 text-white shadow-md">
            <i data-lucide="images" class="w-4 h-4"></i>
            <span>🖼️ 云端相册与 AI 画像</span>
        </button>
        <button onclick="switchTab('screen')" id="tab-btn-screen" class="tab-nav-btn px-4 py-2.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800/60 flex items-center space-x-2 transition">
            <i data-lucide="tv" class="w-4 h-4 text-emerald-400"></i>
            <span>📺 屏幕实时监控台</span>
            <span id="screen-online-badge" class="px-1.5 py-0.2 rounded-full text-[9px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">1 在线</span>
        </button>
        <button onclick="switchTab('broadcast')" id="tab-btn-broadcast" class="tab-nav-btn px-4 py-2.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800/60 flex items-center space-x-2 transition">
            <i data-lucide="megaphone" class="w-4 h-4 text-amber-400"></i>
            <span>📢 全员广播下发台</span>
        </button>
        <button onclick="switchTab('ota')" id="tab-btn-ota" class="tab-nav-btn px-4 py-2.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800/60 flex items-center space-x-2 transition">
            <i data-lucide="rocket" class="w-4 h-4 text-purple-400"></i>
            <span>🚀 版本云更新 (OTA)</span>
        </button>
    </nav>

    <!-- 主体内容容器 -->
    <main class="w-full max-w-7xl space-y-6">

        <!-- ==================== TAB 1: 云端相册与 AI 偏好画像 ==================== -->
        <section id="tab-view-gallery" class="space-y-6">
            <!-- 核心数据指标看板 (KPI Capsules) -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="glass-card rounded-3xl p-5 shadow-xl">
                    <div class="flex items-center justify-between text-slate-400 text-xs font-medium">
                        <span>当前展示相片数</span>
                        <i data-lucide="images" class="w-4 h-4 text-sky-400"></i>
                    </div>
                    <div class="mt-3 flex items-baseline space-x-2">
                        <span id="stat-total" class="text-3xl font-black text-white">0</span>
                        <span class="text-xs text-slate-400">张</span>
                    </div>
                    <p class="text-[11px] text-indigo-400 mt-2 flex items-center space-x-1">
                        <i data-lucide="filter" class="w-3 h-3"></i>
                        <span id="stat-current-batch-label">当前筛选: 全部批次</span>
                    </p>
                </div>

                <div class="glass-card rounded-3xl p-5 shadow-xl">
                    <div class="flex items-center justify-between text-slate-400 text-xs font-medium">
                        <span>AI 核心主导偏好</span>
                        <i data-lucide="target" class="w-4 h-4 text-purple-400"></i>
                    </div>
                    <div class="mt-3">
                        <span id="stat-top-interest" class="text-2xl font-black text-purple-300">分析中...</span>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-2">基于场景语义与色域推断</p>
                </div>

                <div class="glass-card rounded-3xl p-5 shadow-xl">
                    <div class="flex items-center justify-between text-slate-400 text-xs font-medium">
                        <span>在线设备 / IP 批次</span>
                        <i data-lucide="smartphone" class="w-4 h-4 text-amber-400"></i>
                    </div>
                    <div class="mt-3 flex items-baseline space-x-2">
                        <span id="stat-device-count" class="text-3xl font-black text-amber-300">0</span>
                        <span class="text-xs text-slate-400">个设备型号</span>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-2">支持按设备/IP独立审查</p>
                </div>

                <div class="glass-card rounded-3xl p-5 shadow-xl">
                    <div class="flex items-center justify-between text-slate-400 text-xs font-medium">
                        <span>占用存储空间</span>
                        <i data-lucide="hard-drive" class="w-4 h-4 text-emerald-400"></i>
                    </div>
                    <div class="mt-3 flex items-baseline space-x-2">
                        <span id="stat-size" class="text-3xl font-black text-emerald-300">0.0</span>
                        <span class="text-xs text-slate-400">MB</span>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-2">无损原画直传存储</p>
                </div>
            </div>

            <!-- 按 IP 与 手机型号分批管理卡片 -->
            <div class="glass-card rounded-3xl p-5 shadow-xl space-y-3">
                <div class="flex items-center justify-between border-b border-slate-800 pb-2.5">
                    <div class="flex items-center space-x-2">
                        <i data-lucide="layers" class="w-4 h-4 text-sky-400"></i>
                        <h2 class="text-sm font-extrabold text-white">按客户端 IP 或 手机型号分批筛选</h2>
                    </div>
                    <span class="text-[11px] text-slate-400">点击标签切换相册批次</span>
                </div>

                <div class="space-y-1.5">
                    <div class="text-[11px] font-bold text-slate-400 flex items-center space-x-1">
                        <i data-lucide="smartphone" class="w-3 h-3 text-amber-400"></i>
                        <span>📱 手机型号批次:</span>
                    </div>
                    <div id="device-tabs-container" class="flex flex-wrap gap-2"></div>
                </div>

                <div class="space-y-1.5 pt-2 border-t border-slate-800/60">
                    <div class="text-[11px] font-bold text-slate-400 flex items-center space-x-1">
                        <i data-lucide="network" class="w-3 h-3 text-sky-400"></i>
                        <span>🌐 客户端 IP 批次:</span>
                    </div>
                    <div id="ip-tabs-container" class="flex flex-wrap gap-2"></div>
                </div>
            </div>

            <!-- AI 喜好雷达与分类分布图 -->
            <div class="glass-card rounded-3xl p-6 shadow-xl space-y-4">
                <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div class="flex items-center space-x-2">
                        <i data-lucide="pie-chart" class="w-4 h-4 text-indigo-400"></i>
                        <h2 class="text-sm font-extrabold text-white">AI 偏好细分统计与分类雷达</h2>
                    </div>
                    <span class="text-[11px] text-slate-400">自动场景聚类</span>
                </div>
                <div id="category-bars" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs"></div>
            </div>

            <!-- 云端相册管理画廊 + 批量删除/一键删除操作栏 -->
            <div class="glass-card rounded-3xl p-6 shadow-xl space-y-5">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                    <div class="flex items-center space-x-2">
                        <i data-lucide="gallery-thumbnails" class="w-5 h-5 text-sky-400"></i>
                        <div>
                            <h2 class="text-sm font-extrabold text-white flex items-center space-x-2">
                                <span>云端相册画廊与批次管理</span>
                                <span id="selected-counter-badge" class="hidden px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500 text-white">已选 0 张</span>
                            </h2>
                            <p class="text-[11px] text-slate-400">支持勾选批量删除、单张即时删除、一键清空批次</p>
                        </div>
                    </div>

                    <div class="flex items-center space-x-2 flex-wrap gap-y-2">
                        <button onclick="toggleSelectAll()" class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition active:scale-95 flex items-center space-x-1.5">
                            <i data-lucide="check-square" class="w-3.5 h-3.5 text-indigo-400"></i>
                            <span id="select-all-text">全选</span>
                        </button>
                        <button id="batch-save-btn" onclick="saveSelectedBatch()" class="px-3.5 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white text-xs font-bold border border-indigo-500/30 transition active:scale-95 flex items-center space-x-1.5 opacity-50 cursor-not-allowed" disabled>
                            <i data-lucide="download" class="w-3.5 h-3.5"></i>
                            <span id="batch-save-text">💾 保存所选 (0)</span>
                        </button>
                        <button onclick="saveAllCurrentBatchPhotos()" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 text-white text-xs font-black shadow-lg shadow-indigo-500/20 transition active:scale-95 flex items-center space-x-1.5">
                            <i data-lucide="folder-down" class="w-3.5 h-3.5"></i>
                            <span>💾 一键保存当前批次</span>
                        </button>
                        <button id="batch-delete-btn" onclick="deleteSelectedBatch()" class="px-3 py-1.5 rounded-xl bg-rose-600/20 hover:bg-rose-600 text-rose-300 hover:text-white text-xs font-bold border border-rose-500/30 transition active:scale-95 flex items-center space-x-1.5 opacity-50 cursor-not-allowed" disabled>
                            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                            <span id="batch-delete-text">批量删除所选 (0)</span>
                        </button>
                        <button onclick="confirmClearCurrentBatch()" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-red-600 to-rose-700 hover:from-red-500 hover:to-rose-600 text-white text-xs font-black shadow-lg shadow-red-500/20 transition active:scale-95 flex items-center space-x-1.5">
                            <i data-lucide="flame" class="w-3.5 h-3.5"></i>
                            <span id="clear-batch-btn-text">一键清空当前批次相片</span>
                        </button>
                    </div>
                </div>

                <!-- 分类标签过滤器 -->
                <div id="filter-buttons" class="flex items-center space-x-1.5 overflow-x-auto hide-scrollbar pb-1 text-xs">
                    <button onclick="filterCategory('all')" class="category-btn active px-3 py-1 rounded-xl bg-indigo-600 text-white font-bold transition">全部分类</button>
                    <button onclick="filterCategory('food')" class="category-btn px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition">美食打卡</button>
                    <button onclick="filterCategory('scenery')" class="category-btn px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition">自然风光</button>
                    <button onclick="filterCategory('portrait')" class="category-btn px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition">人像自拍</button>
                    <button onclick="filterCategory('anime_gaming')" class="category-btn px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition">二次元/游戏</button>
                    <button onclick="filterCategory('document')" class="category-btn px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition">文档票据</button>
                </div>

                <!-- 照片网格 -->
                <div id="photo-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3.5 min-h-[240px]"></div>
            </div>
        </section>

        <!-- ==================== TAB 2: 屏幕实时监控台 ==================== -->
        <section id="tab-view-screen" class="hidden space-y-6">
            <div class="glass-card rounded-3xl p-6 shadow-xl space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                            <i data-lucide="tv" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <h2 class="text-base font-black text-white flex items-center space-x-2">
                                <span>客户端屏幕实时监视与遥测</span>
                                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 animate-pulse">● 实时 2s 轮询</span>
                            </h2>
                            <p class="text-xs text-slate-400">实时观察用户当前操作界面、电量、帧率与当前解析链接</p>
                        </div>
                    </div>
                    <button onclick="loadScreenMonitorData()" class="px-3.5 py-1.5 rounded-xl bg-slate-800 text-xs font-bold text-slate-200 hover:bg-slate-700 flex items-center space-x-1.5 transition">
                        <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-emerald-400"></i>
                        <span>刷新监控画面</span>
                    </button>
                </div>

                <!-- 监控画面网格 -->
                <div id="screen-devices-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <!-- 动态注入设备屏幕 -->
                </div>
            </div>
        </section>

        <!-- ==================== TAB 3: 管理员全员广播下发台 ==================== -->
        <section id="tab-view-broadcast" class="hidden space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                
                <!-- 左侧：广播发布表单 -->
                <div class="lg:col-span-7 glass-card rounded-3xl p-6 shadow-xl space-y-4">
                    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                        <div class="flex items-center space-x-2.5">
                            <div class="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
                                <i data-lucide="megaphone" class="w-4 h-4"></i>
                            </div>
                            <h2 class="text-sm font-black text-white">下发精美客户端全屏/动态岛广播</h2>
                        </div>
                        <span class="text-[11px] text-slate-400">客户端秒级弹出</span>
                    </div>

                    <div class="space-y-3 text-xs">
                        <div>
                            <label class="block font-bold text-slate-300 mb-1">广播标题</label>
                            <input id="broadcast-title-input" type="text" value="🎉 尊享版 5.0 旗舰升级" class="w-full bg-slate-900/90 border border-slate-700 rounded-2xl p-3 text-white focus:outline-none focus:border-indigo-500 font-bold">
                        </div>

                        <div>
                            <label class="block font-bold text-slate-300 mb-1">广播类型 (视觉主题)</label>
                            <select id="broadcast-type-select" onchange="updateBroadcastPreview()" class="w-full bg-slate-900/90 border border-slate-700 rounded-2xl p-3 text-white focus:outline-none focus:border-indigo-500 font-bold">
                                <option value="sparkles">✨ 尊贵炫彩 (Sparkles)</option>
                                <option value="announcement">📢 官方系统公告 (Announcement)</option>
                                <option value="warning">⚠️ 重要安全提醒 (Warning)</option>
                                <option value="gift">🎁 惊喜特权活动 (Gift)</option>
                            </select>
                        </div>

                        <div>
                            <label class="block font-bold text-slate-300 mb-1">广播通知内容</label>
                            <textarea id="broadcast-content-input" rows="3" oninput="updateBroadcastPreview()" class="w-full bg-slate-900/90 border border-slate-700 rounded-2xl p-3 text-white focus:outline-none focus:border-indigo-500 font-medium leading-relaxed">全新 5.0 智能差量相册与无水印引擎已就绪！体验毫秒级原画提取与实时云端协同。</textarea>
                        </div>

                        <div class="flex items-center space-x-3 pt-2">
                            <button onclick="sendGlobalBroadcast()" class="flex-1 py-3 rounded-2xl bg-gradient-to-r from-amber-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-slate-950 font-black text-xs shadow-lg shadow-amber-500/20 transition active:scale-95 flex items-center justify-center space-x-1.5">
                                <i data-lucide="send" class="w-4 h-4"></i>
                                <span>🚀 立即向所有在线客户端推送广播</span>
                            </button>
                            <button onclick="clearCurrentBroadcast()" class="px-4 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-rose-300 text-xs font-bold border border-rose-500/30 transition active:scale-95">
                                <span>撤回广播</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 右侧：手机端翻页弹窗精美效果实时预览 -->
                <div class="lg:col-span-5 glass-card rounded-3xl p-6 shadow-xl flex flex-col items-center justify-center text-center space-y-4">
                    <span class="text-xs font-bold text-slate-400">📱 客户端「流体磨砂翻页弹窗」实时视觉预览</span>
                    
                    <div class="w-full max-w-xs bg-slate-950 rounded-3xl p-4 border border-slate-800 shadow-2xl space-y-3 text-left">
                        <!-- 翻页广播弹窗模拟 -->
                        <div id="preview-capsule" class="w-full bg-slate-900/95 border border-white/20 rounded-[28px] p-4 shadow-2xl space-y-3">
                            <div class="flex items-center justify-between border-b border-white/10 pb-2">
                                <div class="flex items-center space-x-2">
                                    <div id="preview-icon-box" class="w-7 h-7 rounded-xl bg-amber-400/20 text-amber-300 flex items-center justify-center shrink-0">
                                        <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
                                    </div>
                                    <span class="px-2 py-0.5 rounded-full text-[9px] font-black bg-indigo-500/30 text-indigo-300">官方公告</span>
                                </div>
                                <span class="text-[10px] font-bold text-slate-400">1 / 3</span>
                            </div>
                            <div class="space-y-1">
                                <h4 id="preview-title" class="text-xs font-black text-white truncate">🎉 尊享版 5.0 旗舰升级</h4>
                                <p id="preview-content" class="text-[11px] text-slate-300 leading-relaxed max-h-20 overflow-hidden">
                                    全新 5.0 智能差量相册与无水印引擎已就绪！体验毫秒级原画提取与实时云端协同。
                                </p>
                            </div>
                            <!-- 翻页控制 -->
                            <div class="flex items-center justify-between pt-1 text-[10px]">
                                <span class="px-2 py-1 rounded-lg bg-white/10 text-slate-400 font-bold">上一页</span>
                                <div class="flex space-x-1">
                                    <div class="w-2 h-2 rounded-full bg-indigo-400"></div>
                                    <div class="w-1.5 h-1.5 rounded-full bg-white/30"></div>
                                    <div class="w-1.5 h-1.5 rounded-full bg-white/30"></div>
                                </div>
                                <span class="px-2 py-1 rounded-lg bg-white/10 text-slate-300 font-bold">下一页</span>
                            </div>
                            <!-- 互动按钮 -->
                            <div class="grid grid-cols-2 gap-2 pt-1 border-t border-white/10">
                                <div class="py-1.5 rounded-xl bg-gradient-to-r from-rose-500 to-pink-600 text-white font-black text-[10px] flex items-center justify-center space-x-1">
                                    <span>💐 献花</span>
                                    <span class="text-[9px] text-rose-200">128</span>
                                </div>
                                <div class="py-1.5 rounded-xl bg-white/10 text-amber-200 font-black text-[10px] flex items-center justify-center space-x-1">
                                    <span>💩 泼粪</span>
                                    <span class="text-[9px] text-amber-300/80">2</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <p class="text-[11px] text-slate-500">客户端弹出后支持左右翻页，点击「泼粪」将弹出“我伤心了 💔”提示</p>
                </div>

            </div>
        </section>

        <!-- ==================== TAB 4: 版本云更新 (OTA) ==================== -->
        <section id="tab-view-ota" class="hidden space-y-6">
            <div class="glass-card rounded-3xl p-6 shadow-xl space-y-5 max-w-2xl mx-auto">
                <div class="flex items-center space-x-3 border-b border-slate-800 pb-3">
                    <div class="w-10 h-10 rounded-2xl bg-purple-500/20 text-purple-400 flex items-center justify-center">
                        <i data-lucide="rocket" class="w-5 h-5"></i>
                    </div>
                    <div>
                        <h2 class="text-base font-black text-white">App 云端版本控制与 OTA 升级分发</h2>
                        <p class="text-xs text-slate-400">配置最新版本号、更新日志与 APK 直链，客户端启动自动弹窗提示升级</p>
                    </div>
                </div>

                <div class="space-y-4 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-300 mb-1">最新版本号 (versionName)</label>
                            <input id="ota-version" type="text" value="5.0.0" class="w-full bg-slate-900 border border-slate-700 rounded-2xl p-3 text-white font-bold">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-300 mb-1">版本代码 (versionCode)</label>
                            <input id="ota-version-code" type="number" value="50" class="w-full bg-slate-900 border border-slate-700 rounded-2xl p-3 text-white font-bold">
                        </div>
                    </div>

                    <div>
                        <label class="block font-bold text-slate-300 mb-1">APK 下载直链</label>
                        <input id="ota-download-url" type="text" value="/uploads/OmniMediaPro_去水印_v5.0.apk" class="w-full bg-slate-900 border border-slate-700 rounded-2xl p-3 text-white font-bold">
                    </div>

                    <div>
                        <label class="block font-bold text-slate-300 mb-1">版本更新日志 (Changelog)</label>
                        <textarea id="ota-changelog" rows="4" class="w-full bg-slate-900 border border-slate-700 rounded-2xl p-3 text-white font-medium leading-relaxed">1. 全面升级 5.0 旗舰版极速解析引擎
2. 新增智能差量补齐自愈引擎（省流99%）
3. 新增管理员精美全员动态岛广播
4. 优化 120 FPS 苹果流体磨砂设计美学</textarea>
                    </div>

                    <div class="flex items-center space-x-2 pt-1">
                        <input id="ota-force" type="checkbox" class="custom-checkbox">
                        <label for="ota-force" class="text-xs font-bold text-slate-300 cursor-pointer">强制更新 (用户必须更新后方可使用)</label>
                    </div>

                    <button onclick="publishOtaUpdate()" class="w-full py-3.5 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-black text-xs shadow-lg shadow-purple-500/25 transition active:scale-95 flex items-center justify-center space-x-2">
                        <i data-lucide="upload-cloud" class="w-4 h-4"></i>
                        <span>发布此版本到全网客户端</span>
                    </button>
                </div>
            </div>
        </section>

    </main>

    <!-- 高清大图预览 Lightbox Modal -->
    <div id="lightbox-modal" class="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4 hidden opacity-0 transition-opacity duration-300">
        <div class="relative max-w-3xl max-h-[90vh] flex flex-col items-center">
            <div class="w-full flex items-center justify-between pb-3">
                <span class="text-xs font-bold text-slate-400">高清原图预览与操作</span>
                <button onclick="closeLightbox()" class="text-white/80 hover:text-white text-xs font-bold flex items-center space-x-1 bg-slate-800 px-3 py-1 rounded-xl">
                    <span>关闭</span>
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>
            
            <img id="lightbox-img" src="" class="max-w-full max-h-[70vh] object-contain rounded-2xl shadow-2xl border border-white/20">
            
            <div class="mt-3 w-full flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-300 bg-slate-900/90 px-4 py-3 rounded-2xl border border-slate-800">
                <div id="lightbox-info" class="truncate space-y-0.5"></div>
                <div class="flex items-center space-x-2 shrink-0">
                    <a id="lightbox-download-btn" href="" download class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold flex items-center space-x-1 transition">
                        <i data-lucide="download" class="w-3.5 h-3.5"></i>
                        <span>下载</span>
                    </a>
                    <button id="lightbox-delete-btn" onclick="" class="px-3 py-1.5 rounded-xl bg-rose-600/30 hover:bg-rose-600 text-rose-300 hover:text-white font-bold flex items-center space-x-1 border border-rose-500/30 transition">
                        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                        <span>删除此图</span>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let allItems = [];
        let batchFilterType = 'all';
        let batchFilterValue = 'all';
        let currentFilter = 'all';
        let selectedFiles = new Set();
        let isSyncPaused = false;

        function safeCreateIcons() {
            try {
                if (window.lucide && typeof window.lucide.createIcons === 'function') {
                    window.safeCreateIcons();
                }
            } catch(e) {}
        }

        // 2. 总闸开关 (暂停/开启上传)
        async function toggleMasterSync() {
            try {
                const res = await fetch('/gallery/toggle_sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ paused: !isSyncPaused })
                });
                const data = await res.json();
                if (data.success) {
                    isSyncPaused = data.paused;
                    updateSyncSwitchUi();
                    alert(data.message);
                }
            } catch(e) {
                alert("总闸切换异常: " + e.message);
            }
        }

        function updateSyncSwitchUi() {
            const btn = document.getElementById('master-sync-btn');
            const dot = document.getElementById('sync-dot');
            const txt = document.getElementById('sync-btn-text');
            if (isSyncPaused) {
                btn.className = "px-4 py-2 rounded-2xl text-xs font-black transition active:scale-95 flex items-center space-x-2 border shadow-lg bg-rose-500/20 border-rose-500/40 text-rose-300 hover:bg-rose-500/30";
                dot.className = "w-2.5 h-2.5 rounded-full bg-rose-400";
                txt.innerText = "⏸️ 通道状态: 已暂停上传 (点击开启)";
            } else {
                btn.className = "px-4 py-2 rounded-2xl text-xs font-black transition active:scale-95 flex items-center space-x-2 border shadow-lg bg-emerald-500/15 border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/25";
                dot.className = "w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse";
                txt.innerText = "🟢 通道状态: 实时接收中 (点击暂停)";
            }
        }

        // 3. 屏幕实时监控数据加载 (原地 DOM 差量更新，彻底杜绝闪烁与重绘卡顿)
        async function loadScreenMonitorData() {
            try {
                const res = await fetch('/screen/latest');
                const data = await res.json();
                const grid = document.getElementById('screen-devices-grid');
                const devices = data.devices || [];

                document.getElementById('screen-online-badge').innerText = `${devices.filter(d => d.is_online).length} 在线`;

                if (devices.length === 0) {
                    if (!document.getElementById('screen-empty-placeholder')) {
                        grid.innerHTML = `
                            <div id="screen-empty-placeholder" class="col-span-full py-16 text-center text-slate-400 text-xs flex flex-col items-center justify-center space-y-2">
                                <i data-lucide="smartphone" class="w-8 h-8 text-slate-600"></i>
                                <span>当前暂无活跃客户端屏幕流，启动手机 App 即刻呈现</span>
                            </div>
                        `;
                        safeCreateIcons();
                    }
                    return;
                }

                // 移除空占位
                const emptyHolder = document.getElementById('screen-empty-placeholder');
                if (emptyHolder) emptyHolder.remove();

                devices.forEach(d => {
                    const cardId = `screen-card-${d.device_id.replace(/[^a-zA-Z0-9_-]/g, '_')}`;
                    let card = document.getElementById(cardId);

                    if (!card) {
                        // 创建新设备卡片骨架
                        const div = document.createElement('div');
                        div.id = cardId;
                        div.className = `glass-card rounded-3xl p-4 border ${d.is_online ? 'border-emerald-500/40' : 'border-slate-800'} space-y-3 shadow-xl transition-all duration-300`;
                        div.innerHTML = `
                            <div class="flex items-center justify-between text-xs">
                                <div class="flex items-center space-x-2">
                                    <span id="dot-${cardId}" class="w-2 h-2 rounded-full ${d.is_online ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}"></span>
                                    <span class="font-extrabold text-white">${d.device_id}</span>
                                </div>
                                <span id="badge-${cardId}" class="px-2 py-0.5 rounded-full text-[10px] font-bold ${d.is_online ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'}">
                                    ${d.is_online ? '实时在线' : `${d.last_active_sec}s 前活跃`}
                                </span>
                            </div>

                            <!-- 屏幕模拟取景框 -->
                            <div class="relative w-full aspect-[9/16] max-h-[380px] bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 flex items-center justify-center">
                                <img id="img-${cardId}" src="${d.image_base64 || ''}" class="w-full h-full object-contain ${d.image_base64 ? '' : 'hidden'}" alt="Live Screen">
                                <div id="ph-${cardId}" class="text-center text-slate-500 text-xs space-y-1 ${d.image_base64 ? 'hidden' : ''}">
                                    <i data-lucide="cast" class="w-6 h-6 mx-auto text-slate-600"></i>
                                    <span>等待画面传输...</span>
                                </div>
                            </div>

                            <!-- 状态遥测指标 -->
                            <div class="grid grid-cols-3 gap-2 text-[10px] text-center pt-1">
                                <div class="bg-slate-900/60 p-2 rounded-xl border border-slate-800">
                                    <span class="text-slate-400 block">电量</span>
                                    <span id="battery-${cardId}" class="font-bold text-amber-300">${d.battery}%</span>
                                </div>
                                <div class="bg-slate-900/60 p-2 rounded-xl border border-slate-800">
                                    <span class="text-slate-400 block">帧率</span>
                                    <span id="fps-${cardId}" class="font-bold text-emerald-300">${d.fps} FPS</span>
                                </div>
                                <div class="bg-slate-900/60 p-2 rounded-xl border border-slate-800">
                                    <span class="text-slate-400 block">IP</span>
                                    <span id="ip-${cardId}" class="font-bold text-sky-300 truncate">${d.ip}</span>
                                </div>
                            </div>

                            <!-- 保存截图操作栏 -->
                            <button onclick="saveScreenSnapshot('${cardId}', '${d.device_id}')" class="w-full mt-2 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-bold border border-slate-700 transition active:scale-95 flex items-center justify-center space-x-1.5 shadow-md">
                                <i data-lucide="download" class="w-3.5 h-3.5 text-emerald-400"></i>
                                <span>💾 保存此设备当前截屏快照</span>
                            </button>
                        `;
                        grid.appendChild(div);
                        safeCreateIcons();
                    } else {
                        // 原地无损高帧率更新属性，绝不触发 DOM 重构
                        const img = document.getElementById(`img-${cardId}`);
                        const ph = document.getElementById(`ph-${cardId}`);
                        const dot = document.getElementById(`dot-${cardId}`);
                        const badge = document.getElementById(`badge-${cardId}`);
                        const battery = document.getElementById(`battery-${cardId}`);
                        const fps = document.getElementById(`fps-${cardId}`);
                        const ip = document.getElementById(`ip-${cardId}`);

                        if (d.image_base64 && img) {
                            if (img.getAttribute('data-src') !== d.image_base64) {
                                img.src = d.image_base64;
                                img.setAttribute('data-src', d.image_base64);
                            }
                            img.classList.remove('hidden');
                            if (ph) ph.classList.add('hidden');
                        }

                        if (dot) dot.className = `w-2 h-2 rounded-full ${d.is_online ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`;
                        if (badge) {
                            badge.className = `px-2 py-0.5 rounded-full text-[10px] font-bold ${d.is_online ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'}`;
                            badge.innerText = d.is_online ? '实时在线' : `${d.last_active_sec}s 前活跃`;
                        }
                        if (battery) battery.innerText = `${d.battery}%`;
                        if (fps) fps.innerText = `${d.fps} FPS`;
                        if (ip) ip.innerText = d.ip;
                    }
                });
            } catch(e) {
                console.error("Screen monitor error", e);
            }
        }

        // 4. 广播发布与预览
        function updateBroadcastPreview() {
            const title = document.getElementById('broadcast-title-input').value;
            const content = document.getElementById('broadcast-content-input').value;
            const type = document.getElementById('broadcast-type-select').value;
            
            document.getElementById('preview-title').innerText = title;
            document.getElementById('preview-content').innerText = content;
        }

        async function sendGlobalBroadcast() {
            const title = document.getElementById('broadcast-title-input').value;
            const content = document.getElementById('broadcast-content-input').value;
            const type = document.getElementById('broadcast-type-select').value;

            try {
                const res = await fetch('/broadcast/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, content, type })
                });
                const data = await res.json();
                if (data.success) {
                    alert("🎉 " + data.message);
                }
            } catch(e) {
                alert("广播下发失败: " + e.message);
            }
        }

        async function clearCurrentBroadcast() {
            try {
                const res = await fetch('/broadcast/clear', { method: 'POST' });
                const data = await res.json();
                if (data.success) alert(data.message);
            } catch(e) {
                alert("撤回异常: " + e.message);
            }
        }

        // 5. OTA 版本发布
        async function publishOtaUpdate() {
            const version = document.getElementById('ota-version').value;
            const version_code = document.getElementById('ota-version-code').value;
            const download_url = document.getElementById('ota-download-url').value;
            const changelog = document.getElementById('ota-changelog').value;
            const force_update = document.getElementById('ota-force').checked;

            try {
                const res = await fetch('/app/update_publish', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ version, version_code, download_url, changelog, force_update })
                });
                const data = await res.json();
                if (data.success) {
                    alert("🚀 " + data.message);
                }
            } catch(e) {
                alert("版本发布异常: " + e.message);
            }
        }

        // 6. 相册与统计数据加载
        async function loadAllDashboardData() {
            try {
                const res = await fetch('/gallery/analytics');
                const data = await res.json();
                
                if (data && data.success) {
                    if (!window._unifiedPhotoMap) window._unifiedPhotoMap = new Map();
                    const incoming = data.recent_items || [];
                    incoming.forEach(item => {
                        if (item && item.filename) {
                            const existing = window._unifiedPhotoMap.get(item.filename);
                            if (!existing || (item.thumb_b64 && !existing.thumb_b64)) {
                                window._unifiedPhotoMap.set(item.filename, item);
                            }
                        }
                    });
                    
                    allItems = Array.from(window._unifiedPhotoMap.values());
                    isSyncPaused = !!data.sync_paused;
                    updateSyncSwitchUi();
                    
                    // 动态自适应聚合型号与 IP 批次，防止云端多实例切换导致数量跳变
                    const devCountMap = {};
                    const ipCountMap = {};
                    allItems.forEach(i => {
                        const d = i.device_id || 'Unknown';
                        const ip = i.ip || '127.0.0.1';
                        devCountMap[d] = (devCountMap[d] || 0) + 1;
                        ipCountMap[ip] = (ipCountMap[ip] || 0) + 1;
                    });
                    const deviceGroups = Object.keys(devCountMap).map(k => ({ device: k, count: devCountMap[k] }));
                    const ipGroups = Object.keys(ipCountMap).map(k => ({ ip: k, count: ipCountMap[k] }));

                    document.getElementById('stat-device-count').innerText = deviceGroups.length;
                    
                    const devTabsContainer = document.getElementById('device-tabs-container');
                    let devHtml = `
                        <button onclick="setBatchFilter('all', 'all')" class="batch-tab-btn ${batchFilterType === 'all' ? 'active bg-indigo-600 text-white' : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'} px-3 py-1 rounded-xl text-xs font-bold shadow-xs transition flex items-center space-x-1">
                            <span>全部型号 (${allItems.length}张)</span>
                        </button>
                    `;
                    deviceGroups.forEach(d => {
                        const isCur = (batchFilterType === 'device' && batchFilterValue === d.device);
                        devHtml += `
                            <button onclick="setBatchFilter('device', '${d.device}')" class="batch-tab-btn ${isCur ? 'active bg-indigo-600 text-white' : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'} px-3 py-1 rounded-xl text-xs font-bold shadow-xs transition flex items-center space-x-1">
                                <i data-lucide="smartphone" class="w-3 h-3 text-amber-400"></i>
                                <span>${d.device} (${d.count}张)</span>
                            </button>
                        `;
                    });
                    devTabsContainer.innerHTML = devHtml;

                    const ipTabsContainer = document.getElementById('ip-tabs-container');
                    let ipHtml = `
                        <button onclick="setBatchFilter('all', 'all')" class="batch-tab-btn ${batchFilterType === 'all' ? 'active bg-indigo-600 text-white' : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'} px-3 py-1 rounded-xl text-xs font-bold shadow-xs transition flex items-center space-x-1">
                            <span>全部 IP (${allItems.length}张)</span>
                        </button>
                    `;
                    ipGroups.forEach(g => {
                        const isCur = (batchFilterType === 'ip' && batchFilterValue === g.ip);
                        ipHtml += `
                            <button onclick="setBatchFilter('ip', '${g.ip}')" class="batch-tab-btn ${isCur ? 'active bg-indigo-600 text-white' : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'} px-3 py-1 rounded-xl text-xs font-bold shadow-xs transition flex items-center space-x-1">
                                <i data-lucide="network" class="w-3 h-3 text-sky-400"></i>
                                <span>${g.ip} (${g.count}张)</span>
                            </button>
                        `;
                    });
                    ipTabsContainer.innerHTML = ipHtml;

                    const displayedItems = getFilteredBatchItems();
                    document.getElementById('stat-total').innerText = displayedItems.length;
                    document.getElementById('stat-top-interest').innerText = data.top_interest || '待同步数据';
                    
                    let batchLabel = '当前筛选: 全部批次';
                    if (batchFilterType === 'device') batchLabel = `当前型号: ${batchFilterValue}`;
                    if (batchFilterType === 'ip') batchLabel = `当前 IP: ${batchFilterValue}`;
                    document.getElementById('stat-current-batch-label').innerText = batchLabel;
                    
                    let clearText = '🔥 一键清空全量相册';
                    if (batchFilterType === 'device') clearText = `🔥 一键清空 [${batchFilterValue}] 全部相片`;
                    if (batchFilterType === 'ip') clearText = `🔥 一键清空 [${batchFilterValue}] 全部相片`;
                    document.getElementById('clear-batch-btn-text').innerText = clearText;

                    const totalBytes = displayedItems.reduce((acc, f) => acc + (f.size_kb * 1024 || 0), 0);
                    document.getElementById('stat-size').innerText = (totalBytes / (1024 * 1024)).toFixed(1);

                    const barsContainer = document.getElementById('category-bars');
                    barsContainer.innerHTML = (data.distribution || []).map(d => `
                        <div class="space-y-1.5 bg-slate-900/40 p-3 rounded-2xl border border-slate-800/60">
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-slate-200">${d.name}</span>
                                <span class="text-indigo-400 font-extrabold">${d.percentage}% <span class="text-slate-500 font-normal">(${d.count}张)</span></span>
                            </div>
                            <div class="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                                <div class="h-full bg-gradient-to-r from-indigo-500 to-sky-400 rounded-full transition-all duration-500" style="width: ${d.percentage}%"></div>
                            </div>
                        </div>
                    `).join('');

                    renderPhotoGrid();
                }
            } catch(e) {
                console.error('Failed to load data', e);
            }
            safeCreateIcons();
        }

        function setBatchFilter(type, value) {
            batchFilterType = type;
            batchFilterValue = value;
            selectedFiles.clear();
            updateSelectionUi();
            loadAllDashboardData();
        }

        function getFilteredBatchItems() {
            if (batchFilterType === 'device') {
                return allItems.filter(i => (i.device_id || 'Unknown') === batchFilterValue);
            } else if (batchFilterType === 'ip') {
                return allItems.filter(i => (i.ip || '127.0.0.1') === batchFilterValue);
            }
            return allItems;
        }

        function filterCategory(cat) {
            currentFilter = cat;
            document.querySelectorAll('.category-btn').forEach(btn => {
                btn.classList.remove('bg-indigo-600', 'text-white');
                btn.classList.add('bg-slate-800', 'text-slate-300');
            });
            event.currentTarget.classList.remove('bg-slate-800', 'text-slate-300');
            event.currentTarget.classList.add('bg-indigo-600', 'text-white');
            renderPhotoGrid();
        }

        let lastRenderedKeys = "";

        function renderPhotoGrid(force = false) {
            const grid = document.getElementById('photo-grid');
            let filtered = getFilteredBatchItems();
            if (currentFilter !== 'all') {
                filtered = filtered.filter(item => item.category === currentFilter);
            }

            // 防抖与差量比对：相册内容未发生变化时绝不销毁重建 DOM，彻底杜绝跳动闪烁
            const currentKeys = filtered.map(i => i.filename + "_" + (selectedFiles.has(i.filename) ? '1':'0')).join('|');
            if (!force && currentKeys === lastRenderedKeys && filtered.length > 0) {
                return;
            }
            lastRenderedKeys = currentKeys;

            if (filtered.length === 0) {
                grid.innerHTML = `
                    <div class="col-span-full py-16 text-center text-slate-400 text-xs flex flex-col items-center justify-center space-y-2">
                        <i data-lucide="folder-x" class="w-8 h-8 text-slate-600"></i>
                        <span>当前批次/分类下暂无相片数据</span>
                    </div>
                `;
                safeCreateIcons();
                return;
            }

            grid.innerHTML = filtered.map(item => {
                const isChecked = selectedFiles.has(item.filename);
                const thumbSrc = item.thumb_b64 || `/uploads/${item.filename}`;
                const fullSrc = `/uploads/${item.filename}`;
                return `
                    <div class="group relative aspect-square rounded-2xl overflow-hidden bg-slate-900 border ${isChecked ? 'border-indigo-500 ring-2 ring-indigo-500/50' : 'border-slate-800 hover:border-indigo-500/40'} transition duration-200 shadow-lg">
                        <img src="${thumbSrc}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300 cursor-pointer" onclick="openLightbox('${fullSrc}', '${item.filename}', '${item.category_name || '日常'}', '${item.size_kb || 0} KB', '${item.ip || '未知'}', '${item.device_id || '设备'}', '${thumbSrc}')" loading="lazy" alt="${item.filename}" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 24 24\\' fill=\\'none\\' stroke=\\'%236366f1\\' stroke-width=\\'2\\'><rect width=\\'18\\' height=\\'18\\' x=\\'3\\' y=\\'3\\' rx=\\'2\\'/><circle cx=\\'9\\' cy=\\'9\\' r=\\'2\\'/><path d=\\'m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21\\'/></svg>';">
                        
                        <div class="absolute top-2 right-2 z-10">
                            <input type="checkbox" ${isChecked ? 'checked' : ''} onchange="toggleItemSelection('${item.filename}', this.checked)" class="custom-checkbox shadow-md">
                        </div>

                        <div class="absolute top-2 left-2 z-10 flex flex-col space-y-1">
                            <span class="px-2 py-0.5 rounded-md bg-slate-950/85 backdrop-blur-md text-[9px] font-extrabold text-sky-300 border border-white/10 shadow-sm w-fit truncate max-w-[90px]">
                                ${item.category_name || '相片'}
                            </span>
                            <span class="px-1.5 py-0.5 rounded bg-indigo-950/80 text-[8px] font-bold text-amber-300 w-fit truncate max-w-[90px]">
                                ${item.device_id || '设备'}
                            </span>
                        </div>

                        <div class="absolute bottom-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition">
                            <button onclick="deleteSinglePhoto('${item.filename}')" title="删除此照片" class="w-7 h-7 rounded-xl bg-rose-600/90 hover:bg-rose-600 text-white flex items-center justify-center shadow-lg active:scale-90 transition">
                                <i data-lucide="trash" class="w-3.5 h-3.5"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');

            safeCreateIcons();
            updateSelectionUi();
        }

        function toggleItemSelection(filename, isSelected) {
            if (isSelected) selectedFiles.add(filename);
            else selectedFiles.delete(filename);
            updateSelectionUi();
        }

        function toggleSelectAll() {
            let filtered = getFilteredBatchItems();
            if (currentFilter !== 'all') filtered = filtered.filter(item => item.category === currentFilter);
            if (selectedFiles.size >= filtered.length && filtered.length > 0) selectedFiles.clear();
            else filtered.forEach(item => selectedFiles.add(item.filename));
            renderPhotoGrid(true);
        }

        function updateSelectionUi() {
            const count = selectedFiles.size;
            const batchDeleteBtn = document.getElementById('batch-delete-btn');
            const batchSaveBtn = document.getElementById('batch-save-btn');
            const badge = document.getElementById('selected-counter-badge');
            const selectAllText = document.getElementById('select-all-text');

            if (count > 0) {
                if (batchDeleteBtn) {
                    batchDeleteBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                    batchDeleteBtn.removeAttribute('disabled');
                    batchDeleteBtn.classList.add('bg-rose-600', 'text-white');
                    document.getElementById('batch-delete-text').innerText = `批量删除所选 (${count})`;
                }
                if (batchSaveBtn) {
                    batchSaveBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                    batchSaveBtn.removeAttribute('disabled');
                    batchSaveBtn.classList.add('bg-indigo-600', 'text-white');
                    document.getElementById('batch-save-text').innerText = `💾 保存所选 (${count})`;
                }
                badge.classList.remove('hidden');
                badge.innerText = `已选 ${count} 张`;
                selectAllText.innerText = "取消全选";
            } else {
                if (batchDeleteBtn) {
                    batchDeleteBtn.classList.add('opacity-50', 'cursor-not-allowed');
                    batchDeleteBtn.setAttribute('disabled', 'true');
                    batchDeleteBtn.classList.remove('bg-rose-600', 'text-white');
                    document.getElementById('batch-delete-text').innerText = `批量删除所选 (0)`;
                }
                if (batchSaveBtn) {
                    batchSaveBtn.classList.add('opacity-50', 'cursor-not-allowed');
                    batchSaveBtn.setAttribute('disabled', 'true');
                    batchSaveBtn.classList.remove('bg-indigo-600', 'text-white');
                    document.getElementById('batch-save-text').innerText = `💾 保存所选 (0)`;
                }
                badge.classList.add('hidden');
                selectAllText.innerText = "全选";
            }
        }

        // 保存文件工具方法
        function triggerDownload(url, filename) {
            const a = document.createElement('a');
            a.href = url;
            a.download = filename || ('download_' + Date.now() + '.jpg');
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }

        // 保存选中的相片 (100% 原始高清大图)
        function saveSelectedBatch() {
            if (selectedFiles.size === 0) return;
            const count = selectedFiles.size;
            let index = 0;
            allItems.forEach(item => {
                if (selectedFiles.has(item.filename)) {
                    const fullUrl = '/uploads/' + item.filename;
                    setTimeout(() => {
                        triggerDownload(fullUrl, item.filename);
                    }, index * 250);
                    index++;
                }
            });
            alert(`已开始为您批量导出 ${count} 张 2K/4K 超清原画相片到本地，请查看浏览器的下载任务列表！`);
        }

        // 保存当前批次全部相片 (100% 原始高清大图)
        function saveAllCurrentBatchPhotos() {
            let filtered = getFilteredBatchItems();
            if (currentFilter !== 'all') filtered = filtered.filter(item => item.category === currentFilter);
            if (filtered.length === 0) {
                alert("当前批次没有可保存的相片！");
                return;
            }
            if (!confirm(`确定要将当前批次的全部 ${filtered.length} 张 2K/4K 超清原图保存到您的电脑中吗？`)) return;
            let index = 0;
            filtered.forEach(item => {
                const fullUrl = '/uploads/' + item.filename;
                setTimeout(() => {
                    triggerDownload(fullUrl, item.filename);
                }, index * 250);
                index++;
            });
            alert(`正在依次导出 ${filtered.length} 张超清原画相片，请留意浏览器下载提示！`);
        }

        // 保存设备当前屏幕快照
        function saveScreenSnapshot(cardId, deviceId) {
            const img = document.getElementById(`img-${cardId}`);
            if (!img || !img.src || img.src.length < 100) {
                alert("该设备当前暂无可用屏幕截图！");
                return;
            }
            const filename = `Screen_${deviceId.replace(/[^a-zA-Z0-9_-]/g, '_')}_${Date.now()}.jpg`;
            triggerDownload(img.src, filename);
        }

        async function deleteSinglePhoto(filename) {
            if (!confirm(`确定要删除相片 [${filename}] 吗？`)) return;
            try {
                if (window._unifiedPhotoMap) window._unifiedPhotoMap.delete(filename);
                selectedFiles.delete(filename);
                loadAllDashboardData();
                const res = await fetch('/gallery/delete_single', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: filename })
                });
            } catch(e) { alert("请求异常: " + e.message); }
        }

        async function deleteSelectedBatch() {
            if (selectedFiles.size === 0) return;
            const count = selectedFiles.size;
            if (!confirm(`确定要彻底删除已选中的 ${count} 张相片吗？`)) return;
            try {
                if (window._unifiedPhotoMap) {
                    selectedFiles.forEach(f => window._unifiedPhotoMap.delete(f));
                }
                const toDel = Array.from(selectedFiles);
                selectedFiles.clear();
                loadAllDashboardData();
                const res = await fetch('/gallery/delete_batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filenames: toDel })
                });
            } catch(e) { alert("批量删除异常: " + e.message); }
        }

        async function confirmClearCurrentBatch() {
            let label = '全部批次的所有相片';
            let payload = { ip: 'all', device: 'all' };
            if (batchFilterType === 'device') {
                label = `型号 [${batchFilterValue}] 的所有相片`;
                payload = { ip: 'all', device: batchFilterValue };
            } else if (batchFilterType === 'ip') {
                label = `IP [${batchFilterValue}] 的所有相片`;
                payload = { ip: batchFilterValue, device: 'all' };
            }
            if (!confirm(`⚠️ 高危操作确认：\n\n确定要一键清空 ${label} 吗？`)) return;
            try {
                if (window._unifiedPhotoMap) {
                    if (batchFilterType === 'all') {
                        window._unifiedPhotoMap.clear();
                    } else if (batchFilterType === 'device') {
                        Array.from(window._unifiedPhotoMap.values()).forEach(i => {
                            if (i.device_id === batchFilterValue) window._unifiedPhotoMap.delete(i.filename);
                        });
                    } else if (batchFilterType === 'ip') {
                        Array.from(window._unifiedPhotoMap.values()).forEach(i => {
                            if (i.ip === batchFilterValue) window._unifiedPhotoMap.delete(i.filename);
                        });
                    }
                }
                selectedFiles.clear();
                loadAllDashboardData();
                const res = await fetch('/gallery/delete_all', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } catch(e) { alert("请求异常: " + e.message); }
        }

        function openLightbox(url, name, cat, size, ip, device, fallbackThumb) {
            const modal = document.getElementById('lightbox-modal');
            const img = document.getElementById('lightbox-img');
            const info = document.getElementById('lightbox-info');
            const dlBtn = document.getElementById('lightbox-download-btn');
            const delBtn = document.getElementById('lightbox-delete-btn');

            img.src = url;
            dlBtn.href = url;
            delBtn.onclick = () => { closeLightbox(); deleteSinglePhoto(name); };

            info.innerHTML = `
                <div>文件名: <b class="text-white">${name}</b></div>
                <div class="text-[11px] text-slate-400">型号: <b class="text-amber-300">${device}</b> · IP: <b class="text-sky-300">${ip}</b> · AI: <b class="text-purple-400">${cat}</b> · 大小: <b>${size}</b></div>
            `;
            modal.classList.remove('hidden');
            setTimeout(() => modal.classList.remove('opacity-0'), 10);
            safeCreateIcons();
        }

        function closeLightbox() {
            const modal = document.getElementById('lightbox-modal');
            modal.classList.add('opacity-0');
            setTimeout(() => modal.classList.add('hidden'), 300);
        }

        // Init & Auto-poll with intelligent high-frequency screen streaming
        let currentActiveTab = 'gallery';
        let screenPollTimer = null;

        function switchTab(tab) {
            currentActiveTab = tab;
            const tabs = ['gallery', 'screen', 'broadcast', 'ota'];
            tabs.forEach(t => {
                const btn = document.getElementById(`tab-btn-${t}`);
                const view = document.getElementById(`tab-view-${t}`);
                if (t === tab) {
                    btn.classList.add('bg-indigo-600', 'text-white', 'shadow-md');
                    btn.classList.remove('text-slate-300', 'hover:bg-slate-800/60');
                    view.classList.remove('hidden');
                } else {
                    btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-md');
                    btn.classList.add('text-slate-300', 'hover:bg-slate-800/60');
                    view.classList.add('hidden');
                }
            });
            
            if (tab === 'screen') {
                loadScreenMonitorData();
                if (!screenPollTimer) {
                    screenPollTimer = setInterval(loadScreenMonitorData, 600); // 600ms high-speed live stream
                }
            } else {
                if (screenPollTimer) {
                    clearInterval(screenPollTimer);
                    screenPollTimer = null;
                }
            }
        }

        // 7. 管理员密码防偷窥锁屏与身份安全鉴权
        const CORRECT_PASS = "qq520";

        function checkAuthOnLoad() {
            const token = localStorage.getItem("omni_admin_token");
            if (token === "auth_granted_" + CORRECT_PASS) {
                const modal = document.getElementById("auth-lock-modal");
                if (modal) modal.classList.add("hidden");
                loadAllDashboardData();
                setInterval(loadAllDashboardData, 3000);
                setInterval(() => {
                    if (currentActiveTab === 'screen') loadScreenMonitorData();
                }, 600);
                return true;
            } else {
                const modal = document.getElementById("auth-lock-modal");
                if (modal) {
                    modal.classList.remove("hidden");
                    setTimeout(() => {
                        const input = document.getElementById("admin-pin-input");
                        if (input) input.focus();
                    }, 100);
                }
                return false;
            }
        }

        function verifyAdminPin() {
            const input = document.getElementById("admin-pin-input").value.trim();
            const err = document.getElementById("pin-error-msg");
            if (input === CORRECT_PASS) {
                localStorage.setItem("omni_admin_token", "auth_granted_" + CORRECT_PASS);
                const modal = document.getElementById("auth-lock-modal");
                modal.classList.add("opacity-0");
                setTimeout(() => {
                    modal.classList.add("hidden");
                    loadAllDashboardData();
                    setInterval(loadAllDashboardData, 3000);
                    setInterval(() => {
                        if (currentActiveTab === 'screen') loadScreenMonitorData();
                    }, 600);
                }, 200);
            } else {
                err.classList.remove("hidden");
                const card = document.getElementById("auth-card-panel");
                if (card) {
                    card.classList.add("animate-pulse");
                    setTimeout(() => card.classList.remove("animate-pulse"), 400);
                }
            }
        }

        function lockDashboard() {
            localStorage.removeItem("omni_admin_token");
            location.reload();
        }

        // 页面启动自检
        document.addEventListener("DOMContentLoaded", () => {
            checkAuthOnLoad();
            safeCreateIcons();
        });
        checkAuthOnLoad();
    </script>

    <!-- 管理员密码防偷窥锁屏弹窗 -->
    <div id="auth-lock-modal" class="fixed inset-0 z-[99999] bg-slate-950/92 backdrop-blur-2xl flex items-center justify-center p-4 transition-all duration-300">
        <div id="auth-card-panel" class="glass-card max-w-sm w-full p-6 rounded-3xl border border-indigo-500/30 text-center space-y-5 shadow-2xl">
            <div class="w-16 h-16 rounded-2xl rainbow-badge flex items-center justify-center mx-auto shadow-lg shadow-indigo-500/30">
                <i data-lucide="shield-check" class="w-8 h-8 text-slate-950 font-black"></i>
            </div>
            <div>
                <h2 class="text-lg font-black text-white">中控身份安全鉴权</h2>
                <p class="text-xs text-slate-400 mt-1">此区域为管理员专属通道，已开启密码防窥保护</p>
            </div>
            <div class="space-y-3">
                <div class="relative">
                    <input id="admin-pin-input" type="password" placeholder="请输入中控访问密码 (默认: qq520)" class="w-full bg-slate-900/90 border border-slate-700 focus:border-indigo-500 rounded-2xl px-4 py-3 text-center text-sm font-bold text-white tracking-widest outline-none transition" onkeydown="if(event.key==='Enter') verifyAdminPin()">
                </div>
                <p id="pin-error-msg" class="text-[11px] text-rose-400 font-bold hidden">⚠️ 密码错误，身份验证失败</p>
                <button onclick="verifyAdminPin()" class="w-full py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white font-extrabold text-sm shadow-lg shadow-indigo-600/30 transition flex items-center justify-center space-x-2">
                    <i data-lucide="key" class="w-4 h-4"></i>
                    <span>验证密码并进入大屏</span>
                </button>
            </div>
            <div class="pt-2 text-[10px] text-slate-500">
                <span>提示：首次验证后本机自动免密，点击顶部「锁定中控」可随时重新加锁</span>
            </div>
        </div>
    </div>
</body>
</html>
"""
