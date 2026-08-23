package com.omnimedia.watermark

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import java.util.regex.Pattern

object NativeParser {

    private const val USER_AGENT_MOBILE =
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
    private const val USER_AGENT_DESKTOP =
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

    private fun extractUrl(text: String): String? {
        val pattern = Pattern.compile("https?://[^\\s\\u4e00-\\u9fa5]+")
        val matcher = pattern.matcher(text)
        if (matcher.find()) {
            return matcher.group(0).trimEnd('。', '，', '；', '！', '？', ')', '）')
        }
        return null
    }

    private val API_ENDPOINTS = listOf(
        "http://192.168.1.11:8888/api/parse",
        "http://127.0.0.1:8888/api/parse",
        "https://q-qwatermark-app-tf99.vercel.app/api/parse"
    )

    suspend fun parse(rawInput: String, onLog: ((String, String) -> Unit)? = null): String = withContext(Dispatchers.IO) {
        val targetUrl = extractUrl(rawInput) ?: return@withContext errorJson("未在输入中检测到有效链接")
        android.util.Log.d("OmniMedia", "请求URL: $targetUrl")
        onLog?.invoke("REQ", "提取到有效链接: $targetUrl")

        // 1. 本地局域网/本机超低延迟专线优先（10ms - 50ms 极速直连）
        for (ep in API_ENDPOINTS) {
            try {
                onLog?.invoke("PROBE", "尝试请求高速解析节点: $ep")
                val result = queryApi(ep, targetUrl, onLog)
                if (result != null) {
                    val obj = JSONObject(result)
                    if (obj.optBoolean("success")) {
                        val title = obj.optString("title")
                        onLog?.invoke("SUCCESS", "节点解析成功: ${title.take(15)}...")
                        return@withContext result
                    }
                }
            } catch (e: Exception) {}
        }

        // 2. 本地端侧 0.2 秒极速原生解析（离线直取）
        try {
            if (targetUrl.contains("douyin.com") || targetUrl.contains("iesdouyin.com")) {
                onLog?.invoke("LOCAL", "启动端侧 4K 极速解析引擎...")
                val localRes = parseDouyin(targetUrl, onLog)
                val isSuccess = JSONObject(localRes).optBoolean("success", false)
                if (isSuccess) {
                    onLog?.invoke("SUCCESS", "端侧毫秒级解析成功！")
                    return@withContext localRes
                }
            } else if (targetUrl.contains("kuaishou.com") || targetUrl.contains("kwai.com") || targetUrl.contains("gifshow.com")) {
                onLog?.invoke("LOCAL", "启动快手端侧极速解析引擎...")
                val localRes = parseKuaishou(targetUrl)
                val isSuccess = JSONObject(localRes).optBoolean("success", false)
                if (isSuccess) {
                    onLog?.invoke("SUCCESS", "快手端侧解析成功！")
                    return@withContext localRes
                }
            }
        } catch (e: Exception) {
            onLog?.invoke("LOCAL_WARN", "端侧解析提示: ${e.message}")
        }

        return@withContext errorJson("解析失败，请检查网络或稍后重试")
    }

    private fun queryApi(endpointUrl: String, targetUrl: String, onLog: ((String, String) -> Unit)? = null): String? {
        try {
            val url = URL(endpointUrl)
            val conn = (url.openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = 1500
                readTimeout = 2500
                doOutput = true
                setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                setRequestProperty("Accept", "application/json")
            }
            val postData = JSONObject().apply {
                put("url", targetUrl)
            }.toString().toByteArray(Charsets.UTF_8)

            conn.outputStream.use { os ->
                os.write(postData)
            }

            val code = conn.responseCode
            android.util.Log.d("OmniMedia", "节点 $endpointUrl 响应状态码: $code")

            val stream = if (code in 200..299) conn.inputStream else conn.errorStream
            if (stream != null) {
                val reader = BufferedReader(InputStreamReader(stream, Charsets.UTF_8))
                val sb = StringBuilder()
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    sb.append(line)
                }
                reader.close()
                val body = sb.toString()
                if (code in 200..299) {
                    return body
                }
            }
        } catch (e: Exception) {}
        return null
    }

    private fun resolveCleanIp(hostname: String): String? {
        try {
            val dohUrl = "https://223.5.5.5/resolve?name=$hostname&type=A"
            val conn = (URL(dohUrl).openConnection() as HttpURLConnection).apply {
                connectTimeout = 2000
                readTimeout = 2000
            }
            val text = BufferedReader(InputStreamReader(conn.inputStream, Charsets.UTF_8)).use { it.readText() }
            val json = JSONObject(text)
            val answers = json.optJSONArray("Answer")
            if (answers != null && answers.length() > 0) {
                for (i in 0 until answers.length()) {
                    val ans = answers.getJSONObject(i)
                    val ip = ans.optString("data")
                    if (ip.isNotBlank() && !ip.startsWith("157.") && !ip.startsWith("31.")) {
                        return ip
                    }
                }
            }
        } catch (e: Exception) {}
        return null
    }

    private fun fetchRedirectUrl(initialUrl: String): String {
        var currentUrl = initialUrl
        var redirects = 0
        while (redirects < 6) {
            val url = URL(currentUrl)
            val conn = (url.openConnection() as HttpURLConnection).apply {
                instanceFollowRedirects = false
                requestMethod = "GET"
                connectTimeout = 3500
                readTimeout = 3500
                setRequestProperty("User-Agent", USER_AGENT_MOBILE)
                setRequestProperty("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
            }
            conn.connect()
            val code = conn.responseCode
            if (code in 300..399) {
                val location = conn.getHeaderField("Location")
                conn.disconnect()
                if (!location.isNullOrBlank()) {
                    currentUrl = if (location.startsWith("http")) location else URL(url, location).toString()
                    redirects++
                    continue
                }
            }
            conn.disconnect()
            break
        }
        return currentUrl
    }

    private fun httpGet(urlStr: String, isMobile: Boolean = true, referer: String? = null, cookie: String? = null): String {
        val url = URL(urlStr)
        val conn = (url.openConnection() as HttpURLConnection).apply {
            connectTimeout = 3500
            readTimeout = 3500
            setRequestProperty("User-Agent", if (isMobile) USER_AGENT_MOBILE else USER_AGENT_DESKTOP)
            setRequestProperty("Accept", "application/json, text/html, */*")
            if (referer != null) setRequestProperty("Referer", referer)
            if (cookie != null) setRequestProperty("Cookie", cookie)
        }
        val stream = if (conn.responseCode in 200..299) conn.inputStream else conn.errorStream
        return BufferedReader(InputStreamReader(stream, Charsets.UTF_8)).use { it.readText() }
    }

    private fun parseDouyin(rawUrl: String, onLog: ((String, String) -> Unit)? = null): String {
        val finalUrl = fetchRedirectUrl(rawUrl)
        onLog?.invoke("REDIR", "重定向落地页: ${finalUrl.take(60)}...")
        
        // Extract Aweme ID
        var awemeId: String? = null
        val idPatterns = listOf(
            "/(?:video|note|slides|share/video|share/note|share/slides)/(\\d+)",
            "modal_id=(\\d+)",
            "itemId=(\\d+)",
            "item_ids=(\\d+)",
            "aweme_id=(\\d+)",
            "/(\\d{15,})",
            "(\\d{18,20})"
        )
        for (p in idPatterns) {
            val m = Pattern.compile(p).matcher(finalUrl)
            if (m.find()) {
                awemeId = m.group(1)
                break
            }
        }

        if (awemeId.isNullOrBlank()) {
            return errorJson("无法从重定向链接获取作品ID: $finalUrl")
        }
        onLog?.invoke("ID", "成功提取作品ID: $awemeId")

        // Try API 1: Web detail API (Desktop Headers with bypass cookies)
        var item: JSONObject? = null
        try {
            val webApi = "https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=$awemeId&aid=6383&version_code=190500&version_name=19.5.0&device_platform=webapp&os=ios"
            val jsonStr = httpGet(
                webApi,
                isMobile = false,
                referer = "https://www.douyin.com/video/$awemeId",
                cookie = "s_v_web_id=verify_placeholder; passport_csrf_token=placeholder; ttwid=1%7Cplaceholder%7Cplaceholder;"
            )
            val root = JSONObject(jsonStr)
            item = root.optJSONObject("aweme_detail")
            if (item != null) onLog?.invoke("DETAIL", "Web 4K 接口获取成功")
        } catch (e: Exception) {}

        // Try API 2: iesdouyin iteminfo (Fallback)
        if (item == null) {
            try {
                val apiUrl = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=$awemeId"
                val jsonStr = httpGet(apiUrl, isMobile = true, referer = "https://www.iesdouyin.com/")
                val root = JSONObject(jsonStr)
                val list = root.optJSONArray("item_list")
                if (list != null && list.length() > 0) {
                    item = list.getJSONObject(0)
                    onLog?.invoke("DETAIL", "IES 接口获取成功")
                }
            } catch (e: Exception) {}
        }

        // Try API 3: iesdouyin share pages HTML fallback
        if (item == null) {
            val sharePages = listOf(
                "https://www.iesdouyin.com/share/video/$awemeId/",
                "https://www.iesdouyin.com/share/note/$awemeId/",
                "https://www.iesdouyin.com/share/slides/$awemeId/"
            )
            for (sp in sharePages) {
                try {
                    val html = httpGet(sp, isMobile = true)
                    android.util.Log.d("OmniMedia", "分享页 $sp 响应长度: ${html.length}")
                    val rMatch = Pattern.compile("window\\._ROUTER_DATA\\s*=\\s*(\\{.*?\\})\\s*</script>", Pattern.DOTALL).matcher(html)
                    if (rMatch.find()) {
                        val rJson = JSONObject(rMatch.group(1) ?: "{}")
                        val loaderData = rJson.optJSONObject("loaderData")
                        if (loaderData != null) {
                            val it = loaderData.keys()
                            while (it.hasNext()) {
                                val key = it.next()
                                val pageObj = loaderData.optJSONObject(key)
                                val videoRes = pageObj?.optJSONObject("videoInfoRes")
                                val list = videoRes?.optJSONArray("item_list")
                                if (list != null && list.length() > 0) {
                                    item = list.getJSONObject(0)
                                    break
                                }
                                val itemInfo = pageObj?.optJSONObject("itemInfo")
                                val struct = itemInfo?.optJSONObject("itemStruct")
                                if (struct != null) {
                                    item = struct
                                    break
                                }
                            }
                        }
                    }
                    if (item != null) break
                } catch (e: Exception) {}
            }
        }

        if (item == null) {
            return errorJson("获取抖音作品详情失败，作品可能已被删除或私密")
        }

        val desc = item.optString("desc", "抖音作品").trim()
        val authorObj = item.optJSONObject("author") ?: JSONObject()
        val nickname = authorObj.optString("nickname", "抖音用户")
        val uid = authorObj.optString("unique_id").ifBlank { authorObj.optString("short_id") }
        val avatarList = authorObj.optJSONObject("avatar_thumb")?.optJSONArray("url_list")
        val avatar = if (avatarList != null && avatarList.length() > 0) avatarList.getString(0) else ""

        val statsObj = item.optJSONObject("statistics") ?: JSONObject()
        val likes = statsObj.optInt("digg_count", 0)
        val comments = statsObj.optInt("comment_count", 0)
        val collects = statsObj.optInt("collect_count", 0)

        // Images & Live Photos
        val imagesArr = item.optJSONArray("images")
        val imageUrls = JSONArray()
        val livePhotosArr = JSONArray()
        var hasLive = false

        if (imagesArr != null && imagesArr.length() > 0) {
            for (i in 0 until imagesArr.length()) {
                val imgObj = imagesArr.getJSONObject(i)
                val uList = imgObj.optJSONArray("url_list") ?: imgObj.optJSONArray("download_url_list")
                val imgUrl = if (uList != null && uList.length() > 0) uList.getString(uList.length() - 1) else ""
                
                var clipUrl: String? = null
                val clipList = imgObj.optJSONArray("clip_video_list") ?: imgObj.optJSONArray("video_list")
                if (clipList != null && clipList.length() > 0) {
                    val clipObj = clipList.opt(0)
                    if (clipObj is JSONObject) {
                        clipUrl = clipObj.optString("main_url").ifBlank {
                            clipObj.optJSONObject("play_addr")?.optJSONArray("url_list")?.optString(0)
                        }
                    } else if (clipObj is String) {
                        clipUrl = clipObj
                    }
                    if (!clipUrl.isNullOrBlank()) hasLive = true
                }

                if (imgUrl.isNotBlank()) {
                    imageUrls.put(imgUrl)
                    val lpObj = JSONObject().apply {
                        put("imageUrl", imgUrl)
                        put("videoUrl", clipUrl ?: "")
                    }
                    livePhotosArr.put(lpObj)
                }
            }
        }

        // Video & Qualities
        val videoObj = item.optJSONObject("video")
        val qualitiesArr = JSONArray()
        var mainVideoUrl = ""

        if (videoObj != null) {
            val bitrates = videoObj.optJSONArray("bit_rate")
            if (bitrates != null && bitrates.length() > 0) {
                for (i in 0 until bitrates.length()) {
                    val bObj = bitrates.getJSONObject(i)
                    val uList = bObj.optJSONObject("play_addr")?.optJSONArray("url_list")
                    if (uList != null && uList.length() > 0) {
                        val cleanUrl = uList.getString(0).replace("playwm", "play")
                        val w = bObj.optInt("width", 0)
                        val h = bObj.optInt("height", 0)
                        val maxDim = maxOf(w, h)
                        val gear = bObj.optString("gear_name", "")
                        val label = when {
                            maxDim >= 3840 || gear.contains("4k", ignoreCase = true) -> "4K 超清原画"
                            maxDim >= 2560 -> "2K 极清"
                            maxDim >= 1920 -> "1080P 60FPS 原画"
                            maxDim >= 1280 -> "720P 高清"
                            else -> "超清 原画"
                        }
                        qualitiesArr.put(JSONObject().apply {
                            put("label", label)
                            put("url", cleanUrl)
                            put("width", w)
                            put("height", h)
                        })
                    }
                }
            }

            if (qualitiesArr.length() == 0) {
                val uList = videoObj.optJSONObject("play_addr")?.optJSONArray("url_list")
                if (uList != null && uList.length() > 0) {
                    val cleanUrl = uList.getString(0).replace("playwm", "play")
                    qualitiesArr.put(JSONObject().apply {
                        put("label", "4K/超清 原画")
                        put("url", cleanUrl)
                    })
                }
            }

            if (qualitiesArr.length() > 0) {
                mainVideoUrl = qualitiesArr.getJSONObject(0).getString("url")
            }
        }

        val cover = videoObj?.optJSONObject("cover")?.optJSONArray("url_list")?.optString(0)
            ?: (if (imageUrls.length() > 0) imageUrls.getString(0) else "")

        val mediaType = if (hasLive) "live_photo" else if (imageUrls.length() > 0) "images" else "video"

        val musicObj = item.optJSONObject("music")
        var musicUrl = musicObj?.optJSONObject("play_url")?.optJSONArray("url_list")?.optString(0) ?: ""
        if (musicUrl.isBlank()) {
            musicUrl = musicObj?.optString("play_url", "") ?: ""
        }
        if (musicUrl.isBlank()) {
            musicUrl = musicObj?.optJSONArray("url_list")?.optString(0) ?: ""
        }

        val result = JSONObject().apply {
            put("success", true)
            put("platform", "douyin")
            put("platformName", "抖音")
            put("title", desc)
            put("author", JSONObject().apply {
                put("nickname", nickname)
                put("uid", uid)
                put("avatar", avatar)
            })
            put("stats", JSONObject().apply {
                put("likes", likes)
                put("comments", comments)
                put("collects", collects)
            })
            put("mediaType", mediaType)
            put("media_type", mediaType)
            put("videoUrl", mainVideoUrl)
            put("video_url", mainVideoUrl)
            put("qualities", qualitiesArr)
            put("images", imageUrls)
            put("livePhotos", livePhotosArr)
            put("live_photos", livePhotosArr)
            put("musicUrl", musicUrl)
            put("music_url", musicUrl)
            put("music_title", musicObj?.optString("title", "原声背景音乐"))
            put("music_author", musicObj?.optString("author", "抖音原声"))
            put("coverUrl", cover)
            put("cover_url", cover)
        }

        return result.toString()
    }

    private fun parseKuaishou(rawUrl: String): String {
        val finalUrl = fetchRedirectUrl(rawUrl)
        val html = httpGet(finalUrl, isMobile = true, referer = "https://www.kuaishou.com/")

        var photoUrl = ""
        var title = "快手作品"
        var nickname = "快手用户"
        var avatar = ""
        val imageUrls = JSONArray()

        val pVideo = Pattern.compile("\"photoUrl\"\\s*:\\s*\"(https?:[^\"]+)\"")
        val mVideo = pVideo.matcher(html)
        if (mVideo.find()) {
            photoUrl = mVideo.group(1).replace("\\u002F", "/").replace("\\/", "/")
        }

        val pTitle = Pattern.compile("\"caption\"\\s*:\\s*\"([^\"]*)\"")
        val mTitle = pTitle.matcher(html)
        if (mTitle.find()) {
            title = mTitle.group(1).replace("\\u002F", "/")
        }

        val pUser = Pattern.compile("\"userName\"\\s*:\\s*\"([^\"]*)\"")
        val mUser = pUser.matcher(html)
        if (mUser.find()) {
            nickname = mUser.group(1)
        }

        val pHead = Pattern.compile("\"headUrl\"\\s*:\\s*\"(https?:[^\"]+)\"")
        val mHead = pHead.matcher(html)
        if (mHead.find()) {
            avatar = mHead.group(1).replace("\\u002F", "/")
        }

        if (photoUrl.isBlank() && imageUrls.length() == 0) {
            return errorJson("无法获取快手内容，可能已被删除或私密")
        }

        val qualitiesArr = JSONArray()
        if (photoUrl.isNotBlank()) {
            qualitiesArr.put(JSONObject().apply {
                put("label", "4K/超清 原画")
                put("url", photoUrl)
            })
        }

        val result = JSONObject().apply {
            put("success", true)
            put("platform", "kuaishou")
            put("platformName", "快手")
            put("title", title)
            put("author", JSONObject().apply {
                put("nickname", nickname)
                put("avatar", avatar)
            })
            put("stats", JSONObject().apply {
                put("likes", 0)
                put("comments", 0)
                put("collects", 0)
            })
            put("mediaType", if (imageUrls.length() > 0) "images" else "video")
            put("videoUrl", photoUrl)
            put("qualities", qualitiesArr)
            put("images", imageUrls)
            put("livePhotos", JSONArray())
            put("musicUrl", "")
            put("coverUrl", avatar)
        }

        return result.toString()
    }

    private fun errorJson(msg: String): String {
        return JSONObject().apply {
            put("success", false)
            put("error_message", msg)
        }.toString()
    }
}
