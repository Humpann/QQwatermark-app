ADMIN_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QQ定制 · 云端相册管理与 AI 偏好画像大屏 (IP & 手机型号分批管理)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body {
            background: linear-gradient(135deg, #0a0e1a 0%, #15182d 50%, #0a0e1a 100%);
            min-height: 100vh;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
        }
        .glass-card {
            background: rgba(22, 27, 46, 0.78);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.08);
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
    </style>
</head>
<body class="p-4 md:p-8 flex flex-col items-center">

    <!-- 顶部导航栏 -->
    <header class="w-full max-w-6xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 py-4 border-b border-slate-800/80 mb-6">
        <div class="flex items-center space-x-3">
            <div class="w-11 h-11 rounded-2xl rainbow-badge flex items-center justify-center shadow-lg shadow-indigo-500/25 shrink-0">
                <i data-lucide="sparkles" class="w-6 h-6 text-slate-950 font-black"></i>
            </div>
            <div>
                <h1 class="text-xl font-extrabold tracking-tight text-white flex items-center space-x-2">
                    <span>QQ定制 · 云端相册管理后台</span>
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">IP & 型号分批</span>
                </h1>
                <p class="text-xs text-slate-400 mt-0.5">按客户端 IP / 手机型号分批管理 · 多选批量删除 · 一键全量清空 · AI 喜好雷达</p>
            </div>
        </div>

        <div class="flex items-center space-x-3 self-end sm:self-auto">
            <span class="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-xs">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse mr-2"></span>
                <span id="live-status">云端服务在线 (4s实时同步)</span>
            </span>
            <button onclick="loadDashboardData()" class="px-3.5 py-1.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-xs font-bold flex items-center space-x-1.5 border border-slate-700 transition active:scale-95">
                <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-sky-400"></i>
                <span>刷新</span>
            </button>
        </div>
    </header>

    <!-- 主体容器 -->
    <main class="w-full max-w-6xl space-y-6">

        <!-- 1. 核心数据指标看板 (KPI Capsules) -->
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
                <p class="text-[11px] text-slate-400 mt-2" id="stat-ip-subtext">支持按设备/IP独立审查</p>
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

        <!-- 2. 按 IP 与 手机型号分批管理卡片 (Batch Filter Tabs) -->
        <div class="glass-card rounded-3xl p-5 shadow-xl space-y-3">
            <div class="flex items-center justify-between border-b border-slate-800 pb-2.5">
                <div class="flex items-center space-x-2">
                    <i data-lucide="layers" class="w-4 h-4 text-sky-400"></i>
                    <h2 class="text-sm font-extrabold text-white">按客户端 IP 或 手机型号分批筛选</h2>
                </div>
                <span class="text-[11px] text-slate-400">点击标签切换相册批次</span>
            </div>

            <!-- 手机型号批次标签 -->
            <div class="space-y-1.5">
                <div class="text-[11px] font-bold text-slate-400 flex items-center space-x-1">
                    <i data-lucide="smartphone" class="w-3 h-3 text-amber-400"></i>
                    <span>📱 手机型号批次:</span>
                </div>
                <div id="device-tabs-container" class="flex flex-wrap gap-2">
                    <!-- 动态注入设备型号标签 -->
                </div>
            </div>

            <!-- 客户端 IP 批次标签 -->
            <div class="space-y-1.5 pt-2 border-t border-slate-800/60">
                <div class="text-[11px] font-bold text-slate-400 flex items-center space-x-1">
                    <i data-lucide="network" class="w-3 h-3 text-sky-400"></i>
                    <span>🌐 客户端 IP 批次:</span>
                </div>
                <div id="ip-tabs-container" class="flex flex-wrap gap-2">
                    <!-- 动态注入IP标签 -->
                </div>
            </div>
        </div>

        <!-- 3. AI 喜好雷达与分类分布图 -->
        <div class="glass-card rounded-3xl p-6 shadow-xl space-y-4">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <div class="flex items-center space-x-2">
                    <i data-lucide="pie-chart" class="w-4 h-4 text-indigo-400"></i>
                    <h2 class="text-sm font-extrabold text-white">AI 偏好细分统计与分类雷达</h2>
                </div>
                <span class="text-[11px] text-slate-400">自动场景聚类</span>
            </div>

            <div id="category-bars" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <!-- 动态填充分类进度条 -->
            </div>
        </div>

        <!-- 4. 云端相册管理画廊 + 批量删除/一键删除操作栏 (Media Manager) -->
        <div class="glass-card rounded-3xl p-6 shadow-xl space-y-5">
            
            <!-- 顶部操作工具栏 -->
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

                <!-- 批量与一键删除控制按钮组 -->
                <div class="flex items-center space-x-2 flex-wrap gap-y-2">
                    <button onclick="toggleSelectAll()" class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition active:scale-95 flex items-center space-x-1.5">
                        <i data-lucide="check-square" class="w-3.5 h-3.5 text-indigo-400"></i>
                        <span id="select-all-text">全选</span>
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
            <div id="photo-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3.5 min-h-[240px]">
                <div class="col-span-full py-16 text-center text-slate-400 text-xs flex flex-col items-center justify-center space-y-2">
                    <i data-lucide="cloud-off" class="w-8 h-8 text-slate-600"></i>
                    <span>暂无云端数据或该批次下暂无相片</span>
                </div>
            </div>
        </div>

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
                <div id="lightbox-info" class="truncate space-y-0.5">
                    <!-- Meta Info -->
                </div>
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
        let batchFilterType = 'all'; // 'all', 'ip', 'device'
        let batchFilterValue = 'all';
        let currentFilter = 'all';
        let selectedFiles = new Set();

        async function loadDashboardData() {
            try {
                const res = await fetch('/api/gallery/analytics');
                const data = await res.json();
                
                if (data && data.success) {
                    allItems = data.recent_items || [];
                    
                    // 1. 设备型号分组渲染
                    const deviceGroups = data.device_groups || [];
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

                    // 2. IP 分组渲染
                    const ipGroups = data.ip_groups || [];
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

                    // 3. 核心指标更新
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

                    // 4. AI 偏好进度条渲染
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
                console.error('Failed to load analytics', e);
            }
            lucide.createIcons();
        }

        function setBatchFilter(type, value) {
            batchFilterType = type;
            batchFilterValue = value;
            selectedFiles.clear();
            updateSelectionUi();
            loadDashboardData();
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

        function renderPhotoGrid() {
            const grid = document.getElementById('photo-grid');
            let filtered = getFilteredBatchItems();
            if (currentFilter !== 'all') {
                filtered = filtered.filter(item => item.category === currentFilter);
            }

            if (filtered.length === 0) {
                grid.innerHTML = `
                    <div class="col-span-full py-16 text-center text-slate-400 text-xs flex flex-col items-center justify-center space-y-2">
                        <i data-lucide="folder-x" class="w-8 h-8 text-slate-600"></i>
                        <span>当前批次/分类下暂无相片数据</span>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            grid.innerHTML = filtered.map(item => {
                const isChecked = selectedFiles.has(item.filename);
                return `
                    <div class="group relative aspect-square rounded-2xl overflow-hidden bg-slate-900 border ${isChecked ? 'border-indigo-500 ring-2 ring-indigo-500/50' : 'border-slate-800 hover:border-indigo-500/40'} transition shadow-lg">
                        <img src="/uploads/${item.filename}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300 cursor-pointer" onclick="openLightbox('/uploads/${item.filename}', '${item.filename}', '${item.category_name || '日常'}', '${item.size_kb || 0} KB', '${item.ip || '未知'}', '${item.device_id || '设备'}')" loading="lazy" alt="${item.filename}">
                        
                        <!-- 复选框 (用于选择删除) -->
                        <div class="absolute top-2 right-2 z-10">
                            <input type="checkbox" ${isChecked ? 'checked' : ''} onchange="toggleItemSelection('${item.filename}', this.checked)" class="custom-checkbox shadow-md">
                        </div>

                        <!-- 标签胶囊 (AI分类 & 设备型号) -->
                        <div class="absolute top-2 left-2 z-10 flex flex-col space-y-1">
                            <span class="px-2 py-0.5 rounded-md bg-slate-950/85 backdrop-blur-md text-[9px] font-extrabold text-sky-300 border border-white/10 shadow-sm w-fit">
                                ${item.category_name || '相片'}
                            </span>
                            <span class="px-1.5 py-0.5 rounded bg-indigo-950/80 text-[8px] font-bold text-amber-300 w-fit">
                                ${item.device_id || '设备'}
                            </span>
                        </div>

                        <!-- 快捷单张删除按钮 (悬浮出现) -->
                        <div class="absolute bottom-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition">
                            <button onclick="deleteSinglePhoto('${item.filename}')" title="删除此照片" class="w-7 h-7 rounded-xl bg-rose-600/90 hover:bg-rose-600 text-white flex items-center justify-center shadow-lg active:scale-90 transition">
                                <i data-lucide="trash" class="w-3.5 h-3.5"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');

            lucide.createIcons();
            updateSelectionUi();
        }

        function toggleItemSelection(filename, isChecked) {
            if (isChecked) {
                selectedFiles.add(filename);
            } else {
                selectedFiles.delete(filename);
            }
            updateSelectionUi();
        }

        function toggleSelectAll() {
            let filtered = getFilteredBatchItems();
            if (currentFilter !== 'all') {
                filtered = filtered.filter(item => item.category === currentFilter);
            }

            if (selectedFiles.size >= filtered.length && filtered.length > 0) {
                selectedFiles.clear();
            } else {
                filtered.forEach(item => selectedFiles.add(item.filename));
            }
            renderPhotoGrid();
        }

        function updateSelectionUi() {
            const count = selectedFiles.size;
            const batchBtn = document.getElementById('batch-delete-btn');
            const badge = document.getElementById('selected-counter-badge');
            const selectAllText = document.getElementById('select-all-text');

            if (count > 0) {
                batchBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                batchBtn.removeAttribute('disabled');
                batchBtn.classList.add('bg-rose-600', 'text-white');
                document.getElementById('batch-delete-text').innerText = `批量删除所选 (${count})`;
                badge.classList.remove('hidden');
                badge.innerText = `已选 ${count} 张`;
                selectAllText.innerText = "取消全选";
            } else {
                batchBtn.classList.add('opacity-50', 'cursor-not-allowed');
                batchBtn.setAttribute('disabled', 'true');
                batchBtn.classList.remove('bg-rose-600', 'text-white');
                document.getElementById('batch-delete-text').innerText = `批量删除所选 (0)`;
                badge.classList.add('hidden');
                selectAllText.innerText = "全选";
            }
        }

        // 1. 单张删除
        async function deleteSinglePhoto(filename) {
            if (!confirm(`确定要删除相片 [${filename}] 吗？删除后不可恢复。`)) return;
            try {
                const res = await fetch('/api/gallery/delete_single', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: filename })
                });
                const data = await res.json();
                if (data.success) {
                    selectedFiles.delete(filename);
                    loadDashboardData();
                } else {
                    alert("删除失败: " + data.message);
                }
            } catch(e) {
                alert("网络请求异常: " + e.message);
            }
        }

        // 2. 选择批量删除
        async function deleteSelectedBatch() {
            if (selectedFiles.size === 0) return;
            const count = selectedFiles.size;
            if (!confirm(`确定要彻底删除已选中的 ${count} 张相片吗？`)) return;

            try {
                const res = await fetch('/api/gallery/delete_batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filenames: Array.from(selectedFiles) })
                });
                const data = await res.json();
                if (data.success) {
                    selectedFiles.clear();
                    alert(`成功删除 ${data.deleted_count} 张相片！`);
                    loadDashboardData();
                } else {
                    alert("批量删除失败: " + data.message);
                }
            } catch(e) {
                alert("批量删除请求异常: " + e.message);
            }
        }

        // 3. 一键清空当前批次
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

            if (!confirm(`⚠️ 高危操作确认：\n\n您确定要一键清空 ${label} 吗？此操作将彻底删除磁盘物理文件！`)) return;

            try {
                const res = await fetch('/api/gallery/delete_all', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.success) {
                    selectedFiles.clear();
                    alert(`🎉 已成功清空 ${data.deleted_count} 张相片！`);
                    loadDashboardData();
                } else {
                    alert("清空失败: " + data.message);
                }
            } catch(e) {
                alert("请求异常: " + e.message);
            }
        }

        function openLightbox(url, name, cat, size, ip, device) {
            const modal = document.getElementById('lightbox-modal');
            const img = document.getElementById('lightbox-img');
            const info = document.getElementById('lightbox-info');
            const dlBtn = document.getElementById('lightbox-download-btn');
            const delBtn = document.getElementById('lightbox-delete-btn');

            img.src = url;
            dlBtn.href = url;
            delBtn.onclick = () => {
                closeLightbox();
                deleteSinglePhoto(name);
            };

            info.innerHTML = `
                <div>文件名: <b class="text-white">${name}</b></div>
                <div class="text-[11px] text-slate-400">手机型号: <b class="text-amber-300">${device}</b> · 来源 IP: <b class="text-sky-300">${ip}</b> · AI 分类: <b class="text-purple-400">${cat}</b> · 大小: <b>${size}</b></div>
            `;
            modal.classList.remove('hidden');
            setTimeout(() => modal.classList.remove('opacity-0'), 10);
            lucide.createIcons();
        }

        function closeLightbox() {
            const modal = document.getElementById('lightbox-modal');
            modal.classList.add('opacity-0');
            setTimeout(() => modal.classList.add('hidden'), 300);
        }

        // Init & Auto-poll
        loadDashboardData();
        setInterval(loadDashboardData, 4000);
    </script>
</body>
</html>
"""
