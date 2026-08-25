package com.omnimedia.watermark

import android.annotation.SuppressLint
import android.content.Context
import android.os.Handler
import android.os.Looper
import android.webkit.*
import org.json.JSONArray
import org.json.JSONObject
import java.net.URLDecoder
import java.util.regex.Pattern

object HeadlessParser {

    private var headlessWebView: WebView? = null
    private val mainHandler = Handler(Looper.getMainLooper())
    private var isParsing = false
    private var parseCallback: ((String) -> Unit)? = null
    private var timeoutRunnable: Runnable? = null

    @SuppressLint("SetJavaScriptEnabled")
    fun init(context: Context) {
        if (headlessWebView != null) return
        mainHandler.post {
            headlessWebView = WebView(context.applicationContext).apply {
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.databaseEnabled = true
                settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                settings.mediaPlaybackRequiresUserGesture = false
                settings.userAgentString =
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
            }
        }
    }

    fun parse(context: Context, rawInput: String, onResult: (String) -> Unit) {
        mainHandler.post {
            init(context)
            parseCallback = onResult
            isParsing = true

            val targetUrl = extractUrl(rawInput)
            if (targetUrl == null) {
                returnResult(createErrorJson("未在输入中检测到有效链接"))
                return@post
            }

            // Set 12-second safety timeout
            timeoutRunnable?.let { mainHandler.removeCallbacks(it) }
            timeoutRunnable = Runnable {
                if (isParsing) {
                    returnResult(createErrorJson("解析超时，请检查网络连接"))
                }
            }
            mainHandler.postDelayed(timeoutRunnable!!, 12000)

            val wv = headlessWebView ?: return@post
            wv.stopLoading()

            wv.webViewClient = object : WebViewClient() {

                override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? {
                    val reqUrl = request?.url?.toString() ?: return super.shouldInterceptRequest(view, request)

                    // Intercept Douyin / Kuaishou media stream requests
                    if (isParsing && (reqUrl.contains("video/tos") || reqUrl.contains("playwm") || reqUrl.contains("aweme.snssdk.com/aweme/v1/play") || reqUrl.contains(".yximgs.com") || reqUrl.contains("kuaishou.com/rest/wd/photo/info"))) {
                        val cleanVideoUrl = reqUrl.replace("playwm", "play")
                        mainHandler.post {
                            val res = JSONObject().apply {
                                put("success", true)
                                put("platform", if (reqUrl.contains("kuaishou")) "kuaishou" else "douyin")
                                put("platform_name", if (reqUrl.contains("kuaishou")) "快手" else "抖音")
                                put("media_type", "video")
                                put("title", "4K 无损提取作品")
                                put("video_url", cleanVideoUrl)
                                put("cover_url", "")
                                put("images", JSONArray())
                                put("live_photos", JSONArray())
                                put("qualities", JSONArray().apply {
                                    put(JSONObject().apply {
                                        put("label", "4K 超清原画")
                                        put("url", cleanVideoUrl)
                                    })
                                })
                            }
                            returnResult(res.toString())
                        }
                    }
                    return super.shouldInterceptRequest(view, request)
                }

                override fun onPageFinished(view: WebView?, url: String?) {
                    super.onPageFinished(view, url)
                    if (!isParsing) return

                    // Schedule polling extraction attempts to reliably catch DOM when WAF JS challenge finishes
                    val attempts = listOf(500L, 1200L, 2200L, 3500L, 5000L)
                    attempts.forEach { delayMs ->
                        mainHandler.postDelayed({
                            if (!isParsing) return@postDelayed
                            executeJsExtraction(wv)
                        }, delayMs)
                    }
                }
            }

            wv.loadUrl(targetUrl)
        }
    }

    private fun executeJsExtraction(wv: WebView) {
        val jsExtract = """
            (function() {
                try {
                    var routerData = window._ROUTER_DATA || window._SSR_DATA || window.RENDER_DATA || window.__INITIAL_DATA__;
                    var title = document.title || '4K 提取作品';
                    var videoSrc = '';
                    var images = [];
                    var livePhotos = [];
                    var coverUrl = '';

                    // 1. Extract from Router / SSR Data
                    if (routerData && routerData.loaderData) {
                        for (var k in routerData.loaderData) {
                            var v = routerData.loaderData[k];
                            // Video item
                            if (v && v.videoInfoRes && v.videoInfoRes.item_list && v.videoInfoRes.item_list.length > 0) {
                                var it = v.videoInfoRes.item_list[0];
                                title = it.desc || title;
                                if (it.video && it.video.cover && it.video.cover.url_list) {
                                    coverUrl = it.video.cover.url_list[0];
                                }
                                if (it.video && it.video.play_addr && it.video.play_addr.url_list && it.video.play_addr.url_list.length > 0) {
                                    videoSrc = it.video.play_addr.url_list[0].replace('playwm', 'play');
                                }
                                if (it.images && it.images.length > 0) {
                                    it.images.forEach(function(im) {
                                        if (im.url_list && im.url_list.length > 0) {
                                            var u = im.url_list[im.url_list.length - 1];
                                            if (!images.includes(u)) images.push(u);
                                        }
                                    });
                                }
                            }
                            // Slides / Note item
                            if (v && v.itemInfo && v.itemInfo.itemStruct) {
                                var it = v.itemInfo.itemStruct;
                                title = it.desc || title;
                                if (it.video && it.video.play_addr && it.video.play_addr.url_list) {
                                    videoSrc = it.video.play_addr.url_list[0].replace('playwm', 'play');
                                }
                                if (it.images && it.images.length > 0) {
                                    it.images.forEach(function(im) {
                                        if (im.url_list && im.url_list.length > 0) {
                                            var u = im.url_list[im.url_list.length - 1];
                                            if (!images.includes(u)) images.push(u);
                                        }
                                    });
                                }
                            }
                        }
                    }

                    // 2. DOM fallback
                    if (!videoSrc) {
                        var video = document.querySelector('video');
                        if (video) {
                            videoSrc = video.src || (video.querySelector('source') ? video.querySelector('source').src : '');
                        }
                    }

                    if (images.length === 0 && !videoSrc) {
                        var imgElements = Array.from(document.querySelectorAll('img'));
                        imgElements.forEach(function(img) {
                            var s = img.src;
                            if (s && s.startsWith('http') && !s.includes('logo') && !s.includes('avatar') && !s.includes('icon') && !s.includes('data:')) {
                                if (!images.includes(s)) images.push(s);
                            }
                        });
                    }

                    if (videoSrc || images.length > 0) {
                        var isKwai = location.hostname.includes('kuaishou') || location.hostname.includes('kwai');
                        return JSON.stringify({
                            success: true,
                            platform: isKwai ? 'kuaishou' : 'douyin',
                            platform_name: isKwai ? '快手' : '抖音',
                            media_type: (images.length > 0 && !videoSrc) ? 'images' : 'video',
                            title: title,
                            cover_url: coverUrl || (images.length > 0 ? images[0] : ''),
                            video_url: videoSrc ? videoSrc.replace('playwm', 'play') : '',
                            images: images,
                            live_photos: images.map(function(im, idx){ return { index: idx + 1, image_url: im, video_url: '' }; }),
                            qualities: videoSrc ? [{ label: '4K 超清原画', url: videoSrc.replace('playwm', 'play') }] : []
                        });
                    }
                } catch(e) {}
                return '';
            })();
        """.trimIndent()

        wv.evaluateJavascript(jsExtract) { evalRes ->
            if (!isParsing) return@evaluateJavascript
            if (evalRes != null && evalRes != "null" && evalRes != "\"\"" && evalRes.length > 15) {
                var cleanJson = evalRes
                if (cleanJson.startsWith("\"") && cleanJson.endsWith("\"")) {
                    try {
                        cleanJson = JSONObject(cleanJson).toString()
                    } catch (e: Exception) {
                        cleanJson = cleanJson.substring(1, cleanJson.length - 1)
                            .replace("\\\"", "\"")
                            .replace("\\\\", "\\")
                            .replace("\\n", "\n")
                            .replace("\\u002F", "/")
                    }
                }
                returnResult(cleanJson)
            }
        }
    }

    private fun returnResult(jsonResult: String) {
        if (!isParsing) return
        isParsing = false
        timeoutRunnable?.let { mainHandler.removeCallbacks(it) }
        parseCallback?.invoke(jsonResult)
    }

    private fun createErrorJson(msg: String): String {
        return JSONObject().apply {
            put("success", false)
            put("error_message", msg)
        }.toString()
    }

    private fun extractUrl(text: String): String? {
        val pattern = Pattern.compile("https?://[^\\s\\u4e00-\\u9fa5]+")
        val matcher = pattern.matcher(text)
        if (matcher.find()) {
            return matcher.group(0).trimEnd('。', '，', '；', '！', '？', ')', '）')
        }
        return null
    }
}
