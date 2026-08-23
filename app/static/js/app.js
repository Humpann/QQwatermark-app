/**
 * OmniMedia Pro - Frontend Logic & Vue Application
 */
const { createApp, ref, computed, onMounted, nextTick } = Vue;

const app = createApp({
    setup() {
        // Tab state: 'single' | 'batch'
        const currentTab = ref('single');
        
        // Inputs
        const inputUrl = ref('');
        const batchText = ref('');
        const isParsing = ref(false);
        const parseProgress = ref('');
        
        // Single Parse Result
        const currentResult = ref(null);
        const selectedQuality = ref(null);
        
        // Batch Parse Results
        const batchResults = ref([]);
        const isBatchPacking = ref(false);
        
        // LAN Info & Modal
        const showLanModal = ref(false);
        const lanInfo = ref({
            primary_ip: '127.0.0.1',
            all_ips: ['127.0.0.1'],
            port: 8888,
            lan_url: 'http://127.0.0.1:8888',
            qr_code: ''
        });
        
        // History & Drawer
        const showHistoryDrawer = ref(false);
        const historyList = ref([]);
        
        // Lightbox Gallery
        const lightboxOpen = ref(false);
        const lightboxIndex = ref(0);
        const lightboxImages = ref([]);
        
        // Toast System
        const toast = ref({
            show: false,
            message: '',
            type: 'info' // 'success' | 'error' | 'info'
        });
        let toastTimer = null;

        const showToast = (message, type = 'info', duration = 3000) => {
            if (toastTimer) clearTimeout(toastTimer);
            toast.value = { show: true, message, type };
            toastTimer = setTimeout(() => {
                toast.value.show = false;
            }, duration);
        };

        // Fetch LAN Info on mount
        const fetchLanInfo = async () => {
            try {
                const res = await fetch('/api/lan-info');
                if (res.ok) {
                    lanInfo.value = await res.json();
                }
            } catch (err) {
                console.error('Failed to load LAN info:', err);
            }
        };

        // Load History from LocalStorage
        const loadHistory = () => {
            try {
                const saved = localStorage.getItem('omnimedia_history');
                if (saved) {
                    historyList.value = JSON.parse(saved);
                }
            } catch (e) {
                console.error('Failed to parse history:', e);
            }
        };

        const saveHistory = (result) => {
            if (!result || !result.success) return;
            // Remove existing duplicate
            historyList.value = historyList.value.filter(item => item.item_id !== result.item_id || item.platform !== result.platform);
            // Prepend new item
            historyList.value.unshift({
                ...result,
                savedAt: new Date().toLocaleString()
            });
            // Keep max 50 items
            if (historyList.value.length > 50) {
                historyList.value = historyList.value.slice(0, 50);
            }
            localStorage.setItem('omnimedia_history', JSON.stringify(historyList.value));
        };

        const clearHistory = () => {
            historyList.value = [];
            localStorage.removeItem('omnimedia_history');
            showToast('历史记录已清空', 'info');
        };

        // Auto paste from clipboard
        const pasteClipboard = async () => {
            try {
                if (navigator.clipboard && navigator.clipboard.readText) {
                    const text = await navigator.clipboard.readText();
                    if (text) {
                        if (currentTab.value === 'single') {
                            inputUrl.value = text;
                        } else {
                            batchText.value = text;
                        }
                        showToast('已从剪贴板粘贴内容', 'success');
                    } else {
                        showToast('剪贴板中无内容', 'info');
                    }
                } else {
                    showToast('浏览器限制访问剪贴板，请手动按 Ctrl+V 粘贴', 'info');
                }
            } catch (err) {
                showToast('无法读取剪贴板，请手动粘贴', 'info');
            }
        };

        // Parse Single URL
        const handleSingleParse = async () => {
            const raw = inputUrl.value.trim();
            if (!raw) {
                showToast('请输入或粘贴视频/图集分享链接', 'error');
                return;
            }

            isParsing.value = true;
            parseProgress.value = '正在解析内容元数据...';
            currentResult.value = null;

            try {
                const res = await fetch('/api/parse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: raw })
                });

                const data = await res.json();
                if (res.ok && data.success) {
                    currentResult.value = data;
                    // Set default quality
                    if (data.video_qualities && data.video_qualities.length > 0) {
                        selectedQuality.value = data.video_qualities[0];
                    } else {
                        selectedQuality.value = null;
                    }
                    saveHistory(data);
                    showToast(`解析成功: ${data.title.slice(0, 20)}...`, 'success');
                    // Scroll to result smoothly
                    nextTick(() => {
                        const el = document.getElementById('parse-result-view');
                        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    });
                } else {
                    showToast(data.error_message || '解析失败，请检查链接是否有效', 'error', 4500);
                }
            } catch (err) {
                showToast(`请求异常: ${err.message}`, 'error');
            } finally {
                isParsing.value = false;
                parseProgress.value = '';
            }
        };

        // Batch Parse
        const handleBatchParse = async () => {
            const raw = batchText.value.trim();
            if (!raw) {
                showToast('请粘贴包含多个链接的文本内容', 'error');
                return;
            }

            isParsing.value = true;
            parseProgress.value = '正在提取链接并并发解析中...';
            batchResults.value = [];

            try {
                const res = await fetch('/api/batch-parse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: raw })
                });

                const data = await res.json();
                if (res.ok && data.results) {
                    batchResults.value = data.results;
                    const successCount = data.results.filter(r => r.success).length;
                    showToast(`批量解析完成：成功 ${successCount} / ${data.total} 个`, 'success');
                    // Save successful ones to history
                    data.results.filter(r => r.success).forEach(r => saveHistory(r));
                } else {
                    showToast(data.detail || '批量解析失败', 'error');
                }
            } catch (err) {
                showToast(`批量请求失败: ${err.message}`, 'error');
            } finally {
                isParsing.value = false;
                parseProgress.value = '';
            }
        };

        // Stream URL helper (bypasses 403)
        const getStreamUrl = (url) => {
            if (!url) return '';
            return `/api/proxy/stream?url=${encodeURIComponent(url)}`;
        };

        // Download single media file with safe attachment naming
        const triggerDownload = (url, customName = 'download') => {
            if (!url) {
                showToast('下载地址无效', 'error');
                return;
            }
            const cleanTitle = (customName || 'media').replace(/[\\/:*?"<>|]/g, '_').slice(0, 50);
            const downloadUrl = `/api/proxy/download?url=${encodeURIComponent(url)}&filename=${encodeURIComponent(cleanTitle)}`;
            
            // Create hidden anchor to trigger download
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.setAttribute('download', cleanTitle);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showToast('已开始下载...', 'info');
        };

        // Download all images in album as ZIP
        const downloadAlbumZip = async (result) => {
            if (!result || (!result.images.length && !result.live_photos.length)) {
                showToast('没有可打包的媒体文件', 'error');
                return;
            }

            isBatchPacking.value = true;
            showToast('正在为您打包并生成 ZIP 压缩包，请稍候...', 'info', 5000);

            try {
                const items = [];
                const prefix = `[${result.platform_name}]_${result.author.nickname || '作品'}`;

                if (result.media_type === 'live_photo' && result.live_photos.length > 0) {
                    result.live_photos.forEach((lp, idx) => {
                        const num = String(idx + 1).padStart(2, '0');
                        if (lp.image_url) {
                            items.push({
                                url: lp.image_url,
                                name: `${num}_静态原图.jpg`
                            });
                        }
                        if (lp.video_url) {
                            items.push({
                                url: lp.video_url,
                                name: `${num}_实况动态视频.mp4`
                            });
                        }
                    });
                } else if (result.images.length > 0) {
                    result.images.forEach((imgUrl, idx) => {
                        const num = String(idx + 1).padStart(2, '0');
                        items.push({
                            url: imgUrl,
                            name: `${num}_原图.jpg`
                        });
                    });
                }

                if (result.music_url) {
                    items.push({
                        url: result.music_url,
                        name: `背景原声音频_${result.music_title || 'BGM'}.mp3`
                    });
                }

                const res = await fetch('/api/proxy/zip', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title: `${prefix}_${result.title.slice(0, 30)}`,
                        items: items
                    })
                });

                if (res.ok) {
                    const blob = await res.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    link.download = `${prefix}_打包合集.zip`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(downloadUrl);
                    showToast('ZIP 打包下载完成！', 'success');
                } else {
                    showToast('打包下载失败，请尝试单独下载', 'error');
                }
            } catch (err) {
                showToast(`打包出错: ${err.message}`, 'error');
            } finally {
                isBatchPacking.value = false;
            }
        };

        // Copy direct link to clipboard
        const copyToClipboard = (text) => {
            if (!text) return;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(() => {
                    showToast('链接已复制到剪贴板', 'success');
                }).catch(() => {
                    fallbackCopy(text);
                });
            } else {
                fallbackCopy(text);
            }
        };

        const fallbackCopy = (text) => {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                showToast('链接已复制到剪贴板', 'success');
            } catch (err) {
                showToast('复制失败，请手动复制', 'error');
            }
            document.body.removeChild(textArea);
        };

        // Open item from history
        const openFromHistory = (item) => {
            currentResult.value = item;
            if (item.video_qualities && item.video_qualities.length > 0) {
                selectedQuality.value = item.video_qualities[0];
            } else {
                selectedQuality.value = null;
            }
            showHistoryDrawer.value = false;
            currentTab.value = 'single';
            nextTick(() => {
                const el = document.getElementById('parse-result-view');
                if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        };

        // Lightbox Gallery functions
        const openLightbox = (images, index = 0) => {
            lightboxImages.value = images;
            lightboxIndex.value = index;
            lightboxOpen.value = true;
        };

        const closeLightbox = () => {
            lightboxOpen.value = false;
        };

        const prevLightbox = () => {
            if (lightboxIndex.value > 0) {
                lightboxIndex.value--;
            } else {
                lightboxIndex.value = lightboxImages.value.length - 1;
            }
        };

        const nextLightbox = () => {
            if (lightboxIndex.value < lightboxImages.value.length - 1) {
                lightboxIndex.value++;
            } else {
                lightboxIndex.value = 0;
            }
        };

        // Interactive Live Photo Hover / Press Controller
        const activeLiveIndex = ref(null);
        const handleLivePhotoStart = (index, videoEl) => {
            activeLiveIndex.value = index;
            if (videoEl) {
                videoEl.currentTime = 0;
                videoEl.play().catch(() => {});
            }
        };
        const handleLivePhotoEnd = (index, videoEl) => {
            if (activeLiveIndex.value === index) {
                activeLiveIndex.value = null;
                if (videoEl) {
                    videoEl.pause();
                    videoEl.currentTime = 0;
                }
            }
        };

        // Lifecycle hooks
        onMounted(() => {
            fetchLanInfo();
            loadHistory();

            // Keyboard navigation for lightbox
            window.addEventListener('keydown', (e) => {
                if (!lightboxOpen.value) return;
                if (e.key === 'Escape') closeLightbox();
                if (e.key === 'ArrowLeft') prevLightbox();
                if (e.key === 'ArrowRight') nextLightbox();
            });
        });

        return {
            currentTab,
            inputUrl,
            batchText,
            isParsing,
            parseProgress,
            currentResult,
            selectedQuality,
            batchResults,
            isBatchPacking,
            showLanModal,
            lanInfo,
            showHistoryDrawer,
            historyList,
            lightboxOpen,
            lightboxIndex,
            lightboxImages,
            toast,
            showToast,
            pasteClipboard,
            handleSingleParse,
            handleBatchParse,
            getStreamUrl,
            triggerDownload,
            downloadAlbumZip,
            copyToClipboard,
            openFromHistory,
            clearHistory,
            openLightbox,
            closeLightbox,
            prevLightbox,
            nextLightbox,
            activeLiveIndex,
            handleLivePhotoStart,
            handleLivePhotoEnd
        };
    }
});

app.mount('#app');
