// api/feed.js  -- Node/Next-compatible serverless handler (works on localhost & Vercel Node runtimes)
// Usage (local): http://localhost:3000/api/feed?type=genshin  or ?type=hsr
// Node 18+ provides global fetch & AbortController.

export default async function handler(req, res) {
  // Simple logger for local debugging
  const log = (...args) => {
    if (typeof console !== "undefined") console.log("[/api/feed]", ...args);
  };

  // send helper for consistent responses
  const sendJSON = (obj, status = 200) => {
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.status(status).send(JSON.stringify(obj));
  };

  const sendText = (txt, status = 200) => {
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.status(status).send(txt);
  };

  try {
    // robust URL parsing: req.url may be absolute or path-only
    let urlObj;
    try {
      urlObj = new URL(req.url); // works if absolute
    } catch (e) {
      const hostHeader = req.headers && (req.headers.host || req.headers.get && req.headers.get("host"));
      const host = hostHeader || "localhost:3000";
      const base = host.includes("://") ? host : `http://${host}`;
      urlObj = new URL(req.url, base);
    }

    const type = (urlObj.searchParams.get("type") || "").toLowerCase();
    if (!["hsr", "genshin"].includes(type)) {
      return sendJSON(
        {
          ok: false,
          message: "Provide ?type=hsr or ?type=genshin",
          example: "/api/feed?type=hsr",
        },
        400
      );
    }

    const CONFIG = {
      hsr: {
        label: "Honkai: Star Rail (id)",
        linkBase: "https://hsr.hoyoverse.com/id-id/news",
        api:
          "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/113fe6d3b4514cdd/getContentList?iPage=1&iPageSize=20&sLangKey=id-id&isPreview=0&iChanId=248",
      },
      genshin: {
        label: "Genshin Impact (id)",
        linkBase: "https://genshin.hoyoverse.com/id/news",
        api:
          "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/a1b1f9d3315447cc/getContentList?iAppId=32&iChanId=395&iPageSize=20&iPage=1&sLangKey=id-id",
      },
    };

    const conf = CONFIG[type];

    // Abortable fetch with timeout to avoid "eternal loading"
    const FETCH_TIMEOUT_MS = 10000; // 10 seconds
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

    let upstreamResp;
    try {
      upstreamResp = await fetch(conf.api, {
        headers: {
          Accept: "application/json, text/plain, */*",
          Referer: conf.linkBase,
          "User-Agent": "Mozilla/5.0 (compatible; feed-builder/1.0)",
        },
        signal: controller.signal,
      });
    } catch (fetchErr) {
      clearTimeout(timeoutId);
      log("fetch error:", fetchErr && fetchErr.message ? fetchErr.message : fetchErr);
      // If aborted, give specific message
      if (fetchErr && fetchErr.name === "AbortError") {
        return sendJSON({ ok: false, message: "Upstream fetch timed out (10s)" }, 504);
      }
      return sendJSON({ ok: false, message: "Upstream fetch failed", detail: String(fetchErr) }, 502);
    }
    clearTimeout(timeoutId);

    if (!upstreamResp.ok) {
      log("upstream non-ok", upstreamResp.status, upstreamResp.statusText);
      return sendJSON({ ok: false, message: "Upstream returned non-OK", status: upstreamResp.status }, 502);
    }

    let json;
    try {
      json = await upstreamResp.json();
    } catch (e) {
      log("json parse error", e);
      return sendJSON({ ok: false, message: "Failed to parse upstream JSON" }, 502);
    }

    const posts = json && json.data && Array.isArray(json.data.list) ? json.data.list : [];

    // helpers
    function escapeXml(s) {
      if (!s) return "";
      return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&apos;");
    }

    function parseDateToRfc822(dtStr) {
      if (!dtStr) return new Date().toUTCString();
      try {
        const iso = dtStr.replace(" ", "T") + "Z";
        const d = new Date(iso);
        if (isNaN(d.getTime())) return new Date().toUTCString();
        return d.toUTCString();
      } catch (e) {
        return new Date().toUTCString();
      }
    }

    function extractImageUrl(item) {
      if (!item) return null;
      try {
        let ext = item.sExt;
        if (typeof ext === "string" && ext.trim()) ext = JSON.parse(ext);
        if (ext && typeof ext === "object") {
          if (Array.isArray(ext["news-poster"]) && ext["news-poster"][0] && ext["news-poster"][0].url)
            return ext["news-poster"][0].url;
          if (Array.isArray(ext.banner) && ext.banner[0] && ext.banner[0].url) return ext.banner[0].url;
          if (Array.isArray(ext.value) && ext.value[0] && ext.value[0].url) return ext.value[0].url;
          if (Array.isArray(ext["news_poster"]) && ext["news_poster"][0] && ext["news_poster"][0].url)
            return ext["news_poster"][0].url;
        }
      } catch (e) {
        // ignore parse error
      }
      if (item.sContent && typeof item.sContent === "string") {
        const m = item.sContent.match(/<img[^>]+src=(?:["'])([^"']+)(?:["'])/i);
        if (m) return m[1];
      }
      return null;
    }

    // Build RSS
    const now = new Date().toUTCString();
    const itemsXml = posts
      .map((p) => {
        const id =
          p && (p.iInfoId !== undefined && p.iInfoId !== null) ? String(p.iInfoId) : Math.random().toString(36).slice(2);
        const title = escapeXml(p.sTitle || p.title || "No title");
        const intro = p.sIntro || "";
        const pubDate = parseDateToRfc822(p.dtStartTime || p.dtCreateTime);
        const link = p.sUrl && p.sUrl.trim() ? p.sUrl : `${conf.linkBase}/${id}`;
        const imageUrl = extractImageUrl(p);

        let descriptionCdata = "<![CDATA[";
        if (imageUrl) descriptionCdata += `<img src="${imageUrl}" alt="${escapeXml(p.sTitle || "")}" /><br/><br/>`;
        if (intro) {
          descriptionCdata += intro;
        } else if (p.sContent) {
          const text = p.sContent.replace(/<[^>]+>/g, "").trim();
          descriptionCdata += text.slice(0, 600) + (text.length > 600 ? "…" : "");
        }
        descriptionCdata += `<br/><br/>Read more: <a href="${link}">${link}</a>`;
        descriptionCdata += "]]>";

        const enclosure = imageUrl ? `<enclosure url="${escapeXml(imageUrl)}" type="image/*" />` : "";

        return `
      <item>
        <title>${title}</title>
        <link>${escapeXml(link)}</link>
        <guid isPermaLink="false">${escapeXml(id)}</guid>
        <description>${descriptionCdata}</description>
        ${enclosure}
        <pubDate>${escapeXml(pubDate)}</pubDate>
      </item>`;
      })
      .join("\n");

    const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escapeXml(conf.label)} feed</title>
    <link>${escapeXml(conf.linkBase)}</link>
    <description>${escapeXml(conf.label)} feed</description>
    <lastBuildDate>${now}</lastBuildDate>
    ${itemsXml}
  </channel>
</rss>`;

    res.setHeader("Content-Type", "application/rss+xml; charset=utf-8");
    res.setHeader("Cache-Control", "no-cache, no-store, max-age=0");
    return res.status(200).send(rss);
  } catch (err) {
    console.error("[/api/feed] internal error:", err);
    return sendText("Internal error", 500);
  }
}
