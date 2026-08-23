ADMIN_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QQ定制 · 云端相册管理与 AI 偏好画像大屏</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            min-height: 100vh;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
        }
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .rainbow-badge {
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="p-4 md:p-8 flex flex-col items-center">

    <!-- 顶部导航栏 -->
    <header class="w-full max-w-6xl flex items-center justify-between py-4 border-b border-slate-800/80 mb-6">
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-2xl rainbow-badge flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <i data-lucide="sparkles" class="w-5 h-5 text-slate-950 font-black"></i>
            </div>
            <div>
                <h1 class="text-xl font-extrabold tracking-tight text-white flex items-center space-x-2">
                    <span>QQ定制 · 云端相册与 AI 偏好分析中心</span>
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">Admin Pro</span>
                </h1>
                <p class="text-xs text-slate-400 mt-0.5">多端协同相册管理 · AI 视觉特征与场景喜好自动聚类</p>
            </div>
        </div>

        <div class="flex items-center space-x-3">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse mr-1.5"></span>
                <span id="live-status">云端服务运行中</span>
            </span>
            <button onclick="loadDashboardData()" class="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold flex items-center space-x-1.5 border border-slate-700 transition active:scale-95">
                <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-sky-400"></i>
                <span>刷新数据</span>
            </button>
        </div>
    </header>

    <!-- 主体容器 -->
    <main class="w-full max-w-6xl space-y-6">

        <!-- 1. 四大核心指标数据胶囊 (KPI Capsules) -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="glass-card rounded-3xl p-5 shadow-xl">
                <div class="flex items-center justify-between text-slate-400 text-xs font-medium">
                    <span>全量同步相片总数</span>
                    <i data-lucide="images" class="w-4 h-4 text-sky-400"></i>
                </div>
                <div class="mt-3 flex items-baseline space-x-2">
                    <span id="stat-total" class="text-3xl font-black text-white">0</span>
                    <span class="text-xs text-slate-400">张</span>
                </div>
                <p class="text-[11px] text-emerald-400 mt-2 flex items-center space-x-1">
                    <i data-lucide="trending-up" class="w-3 h-3"></i>
                    <span>已完成 100% 自动特征推断</span>
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
                <p class="text-[11px] text-slate-400 mt-2">基于场景语义与色彩聚类</p>
            </div>

            <div class="glass-card rounded-3xl p-5 shadow-xl">
                <div class="flex items-center justify-between text-slate-400 text-xs font-medium">
                    <span>关联活跃设备</span>
                    <i data-lucide="smartphone" class="w-4 h-4 text-amber-400"></i>
                </div>
                <div class="mt-3">
                    <span id="stat-device" class="text-xl font-bold text-amber-300 truncate block">Redmi / Android 14</span>
                </div>
                <p class="text-[11px] text-slate-400 mt-2">端云安全双向通信</p>
            </div>

            <div class="glass-card rounded-3xl p-5 shadow-xl">
                <div class="flex items-center justify-between text-slate-400 text-xs font-medium">
                    <span>云端存储占用</span>
                    <i data-lucide="hard-drive" class="w-4 h-4 text-emerald-400"></i>
                </div>
                <div class="mt-3 flex items-baseline space-x-2">
                    <span id="stat-size" class="text-3xl font-black text-emerald-300">0.0</span>
                    <span class="text-xs text-slate-400">MB</span>
                </div>
                <p class="text-[11px] text-slate-400 mt-2">无损原画直传存储</p>
            </div>
        </div>

        <!-- 2. AI 喜好雷达与分类分布图 -->
        <div class="glass-card rounded-3xl p-6 shadow-xl space-y-4">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <div class="flex items-center space-x-2">
                    <i data-lucide="pie-chart" class="w-4 h-4 text-indigo-400"></i>
                    <h2 class="text-sm font-extrabold text-white">AI 偏好细分统计与分类雷达</h2>
                </div>
                <span class="text-[11px] text-slate-400">实时动态更新</span>
            </div>

            <div id="category-bars" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <!-- 动态填充分类进度条 -->
            </div>
        </div>

        <!-- 3. 云端相册图片瀑布流画廊 (Media Vault) -->
        <div class="glass-card rounded-3xl p-6 shadow-xl space-y-4">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                <div class="flex items-center space-x-2">
                    <i data-lucide="gallery-thumbnails" class="w-5 h-5 text-sky-400"></i>
                    <div>
                        <h2 class="text-sm font-extrabold text-white">云端全量相册画廊</h2>
                        <p class="text-[11px] text-slate-400">点击任意图片可查看高清原图与 AI 分析元数据</p>
                    </div>
                </div>

                <!-- 分类筛选器 -->
                <div id="filter-buttons" class="flex items-center space-x-1.5 overflow-x-auto hide-scrollbar pb-1 text-xs">
                    <button onclick="filterCategory('all')" class="category-btn active px-3 py-1 rounded-xl bg-indigo-600 text-white font-bold transition">全部</button>
                    <button onclick="filterCategory('food')" class="category-btn px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition">美食打卡</button>
                    <button onclick="filterCategory('scenery')" class="category-btn px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition">自然风光</button>
                    <button onclick="filterCategory('portrait')" class="category-btn px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition">人像自拍</button>
                    <button onclick="filterCategory('anime_gaming')" class="category-btn px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition">二次元/游戏</button>
                    <button onclick="filterCategory('document')" class="category-btn px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 font-medium transition">文档票据</button>
                </div>
            </div>

            <!-- 照片网格 -->
            <div id="photo-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 min-h-[220px]">
                <div class="col-span-full py-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center space-y-2">
                    <i data-lucide="cloud-off" class="w-8 h-8 text-slate-600"></i>
                    <span>暂无云端同步数据，请在手机 App 开启全量同步</span>
                </div>
            </div>
        </div>

    </main>

    <!-- 高清大图预览 Lightbox Modal -->
    <div id="lightbox-modal" class="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 hidden opacity-0 transition-opacity duration-300">
        <div class="relative max-w-3xl max-h-[90vh] flex flex-col items-center">
            <button onclick="closeLightbox()" class="absolute -top-10 right-0 text-white/80 hover:text-white text-sm font-bold flex items-center space-x-1">
                <span>关闭</span>
                <i data-lucide="x" class="w-5 h-5"></i>
            </button>
            <img id="lightbox-img" src="" class="max-w-full max-h-[75vh] object-contain rounded-2xl shadow-2xl border border-white/20">
            <div id="lightbox-info" class="mt-3 text-center text-xs text-slate-300 bg-slate-900/80 px-4 py-2 rounded-xl border border-slate-800">
                <!-- Meta Info -->
            </div>
        </div>
    </div>

    <script>
        let allItems = [];
        let currentFilter = 'all';

        async function loadDashboardData() {
            try {
                const res = await fetch('/api/gallery/analytics');
                const data = await res.json();
                
                if (data && data.success) {
                    document.getElementById('stat-total').innerText = data.total_analyzed || 0;
                    document.getElementById('stat-top-interest').innerText = data.top_interest || '待同步数据';
                    
                    // Render Category Progress Bars
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

                    // Fetch full files list
                    const listRes = await fetch('/api/gallery/list');
                    const listData = await listRes.json();
                    
                    if (listData && listData.files) {
                        allItems = (data.recent_items || []).length > 0 ? data.recent_items : listData.files.map(f => ({
                            filename: f.name,
                            category: 'general',
                            category_name: '生活日常',
                            size_kb: Math.round(f.size / 1024),
                            url: f.url
                        }));

                        const totalBytes = listData.files.reduce((acc, f) => acc + (f.size || 0), 0);
                        document.getElementById('stat-size').innerText = (totalBytes / (1024 * 1024)).toFixed(1);

                        if (allItems.length > 0 && allItems[0].device_id) {
                            document.getElementById('stat-device').innerText = allItems[0].device_id;
                        }

                        renderPhotoGrid();
                    }
                }
            } catch(e) {
                console.error('Failed to load analytics', e);
            }
            lucide.createIcons();
        }

        function renderPhotoGrid() {
            const grid = document.getElementById('photo-grid');
            const filtered = currentFilter === 'all' ? allItems : allItems.filter(item => item.category === currentFilter);

            if (filtered.length === 0) {
                grid.innerHTML = `
                    <div class="col-span-full py-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center space-y-2">
                        <i data-lucide="folder-x" class="w-8 h-8 text-slate-600"></i>
                        <span>该分类下暂无图片</span>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            grid.innerHTML = filtered.map(item => `
                <div onclick="openLightbox('/uploads/${item.filename}', '${item.filename}', '${item.category_name || '日常'}', '${item.size_kb || 0} KB')" class="group relative aspect-square rounded-2xl overflow-hidden bg-slate-900 border border-slate-800 hover:border-indigo-500/50 cursor-pointer transition shadow-lg">
                    <img src="/uploads/${item.filename}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" loading="lazy" alt="${item.filename}">
                    
                    <!-- AI 标签胶囊 -->
                    <div class="absolute top-1.5 left-1.5 px-2 py-0.5 rounded-md bg-slate-950/80 backdrop-blur-md text-[9px] font-extrabold text-sky-300 border border-white/10 shadow-sm">
                        ${item.category_name || '相片'}
                    </div>

                    <!-- 悬浮查看 -->
                    <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center space-x-2">
                        <span class="w-8 h-8 rounded-full bg-white/90 text-slate-950 flex items-center justify-center shadow-md">
                            <i data-lucide="maximize-2" class="w-4 h-4"></i>
                        </span>
                    </div>
                </div>
            `).join('');

            lucide.createIcons();
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

        function openLightbox(url, name, cat, size) {
            const modal = document.getElementById('lightbox-modal');
            const img = document.getElementById('lightbox-img');
            const info = document.getElementById('lightbox-info');
            img.src = url;
            info.innerHTML = `<span>文件名: <b class="text-white">${name}</b></span> · <span>AI 分类: <b class="text-purple-400">${cat}</b></span> · <span>大小: <b>${size}</b></span>`;
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
