// api/feed.js  (for Vercel / Node 18+)
// Usage:
//   /api/feed?type=hsr
//   /api/feed?type=genshin
// You can rewrite /hsr.xml -> /api/feed?type=hsr and /genshin.xml -> /api/feed?type=genshin

export default async function handler(req) {
  try {
    // --- robust URL parsing: some runtimes give req.url as path only ---
    let urlObj;
    try {
      // try absolute (works in some runtimes)
      urlObj = new URL(req.url);
    } catch (e) {
      // fallback: build using Host header or VERCEL_URL
      const host =
        (req.headers && (req.headers.get ? req.headers.get("host") : req.headers.host)) ||
        process.env.VERCEL_URL ||
        "monke-five.vercel.app";
      const base = host.includes("://") ? host : `https://${host}`;
      urlObj = new URL(req.url, base);
    }
    const type = (urlObj.searchParams.get("type") || "").toLowerCase();

    if (!["hsr", "genshin"].includes(type)) {
      return new Response(
        JSON.stringify({
          ok: false,
          message: "Provide ?type=hsr or ?type=genshin",
          example: "/api/feed?type=hsr",
        }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // ===== CONFIG =====
    const CONFIG = {
      hsr: {
        label: "Honkai: Star Rail (id)",
        linkBase: "https://www.hoyoverse.com/hsr/news",
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

    // fetch upstream
    const resp = await fetch(conf.api, {
      headers: {
        Accept: "application/json, text/plain, */*",
        Referer: conf.linkBase,
        "User-Agent": "Mozilla/5.0 (compatible; feed-builder/1.0)",
      },
    });

    if (!resp.ok) {
      return new Response("Upstream fetch failed", { status: 502 });
    }

    const json = await resp.json();
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
      // dtStr like "YYYY-MM-DD HH:MM:SS" -> try to parse as UTC-ish
      try {
        const iso = dtStr.replace(" ", "T") + "Z";
        const d = new Date(iso);
        if (isNaN(d.getTime())) return new Date().toUTCString();
        return d.toUTCString();
      } catch (e) {
        return new Date().toUTCString();
      }
    }

    // image extraction (works for HSR and Genshin patterns)
    function extractImageUrl(item) {
      if (!item) return null;

      // Try parsing sExt if it's a JSON string
      try {
        let ext = item.sExt;
        if (typeof ext === "string" && ext.trim()) ext = JSON.parse(ext);
        if (ext && typeof ext === "object") {
          // HSR often uses news-poster
          if (Array.isArray(ext["news-poster"]) && ext["news-poster"][0] && ext["news-poster"][0].url) {
            return ext["news-poster"][0].url;
          }
          // common: banner
          if (Array.isArray(ext.banner) && ext.banner[0] && ext.banner[0].url) {
            return ext.banner[0].url;
          }
          // fallback: value
          if (Array.isArray(ext.value) && ext.value[0] && ext.value[0].url) {
            return ext.value[0].url;
          }
          // news-poster sometimes under news-poster or news_poster variants
          if (Array.isArray(ext["news_poster"]) && ext["news_poster"][0] && ext["news_poster"][0].url) {
            return ext["news_poster"][0].url;
          }
        }
      } catch (e) {
        // ignore parse error
      }

      // fallback: find first <img src="..."> in sContent
      if (item.sContent && typeof item.sContent === "string") {
        const m = item.sContent.match(/<img[^>]+src=(?:["'])([^"']+)(?:["'])/i);
        if (m) return m[1];
      }

      return null;
    }

    // Build RSS items
    const now = new Date().toUTCString();
    const itemsXml = posts
      .map((p) => {
        const id =
          p && (p.iInfoId !== undefined && p.iInfoId !== null)
            ? String(p.iInfoId)
            : Math.random().toString(36).slice(2);
        const title = escapeXml(p.sTitle || p.title || "No title");
        const intro = p.sIntro || "";
        const pubDate = parseDateToRfc822(p.dtStartTime || p.dtCreateTime);
        const link = p.sUrl && p.sUrl.trim() ? p.sUrl : `${conf.linkBase}/detail/${id}`;

        const imageUrl = extractImageUrl(p);

        let descriptionCdata = "<![CDATA[";
        if (imageUrl) {
          // include image tag
          descriptionCdata += `<img src="${imageUrl}" alt="${escapeXml(p.sTitle || "")}" /><br/><br/>`;
        }
        if (intro) {
          descriptionCdata += intro;
        } else if (p.sContent) {
          // strip tags and take a short excerpt
          const text = p.sContent.replace(/<[^>]+>/g, "").trim();
          descriptionCdata += text.slice(0, 600) + (text.length > 600 ? "…" : "");
        } else {
          descriptionCdata += "";
        }
        descriptionCdata += `<br/><br/>Read more: <a href="${link}">${link}</a>`;
        descriptionCdata += "]]>";

        // Choose a reasonable mime fallback if image exists (we don't know exact type)
        const enclosure =
          imageUrl ? `<enclosure url="${escapeXml(imageUrl)}" type="image/*" />` : "";

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

    return new Response(rss, {
      status: 200,
      headers: {
        "Content-Type": "application/rss+xml; charset=utf-8",
        "Cache-Control": "no-cache, no-store, max-age=0",
      },
    });
  } catch (err) {
    console.error(err);
    return new Response("Internal error", { status: 500 });
  }
}
