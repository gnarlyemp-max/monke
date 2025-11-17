// api/feed.js
export const config = { runtime: "edge" };

/**
 * Config for each feed.
 * - genshin: uses the genshin API you provided
 * - hsr: uses the hsr API you provided
 *
 * Both configured for Indonesian (id-id) and pageSize 20 by default (you can change).
 */
const FEEDS = {
  genshin: {
    label: "Genshin Impact (id)",
    apiBase:
      "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/a1b1f9d3315447cc/getContentList",
    // query params (note some endpoints use iAppId vs iPage)
    qs: {
      iAppId: "32",
      iChanId: "395",
      iPageSize: "20",
      iPage: "1",
      sLangKey: "id-id"
    },
    linkBase: "https://genshin.hoyoverse.com/id/news",
    safeHeadersReferer: "https://genshin.hoyoverse.com/"
  },
  hsr: {
    label: "Honkai: Star Rail (id)",
    apiBase:
      "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/113fe6d3b4514cdd/getContentList",
    qs: {
      iPage: "1",
      iPageSize: "20",
      sLangKey: "id-id",
      isPreview: "0",
      iChanId: "248"
    },
    linkBase: "https://www.hoyoverse.com/hsr/news",
    safeHeadersReferer: "https://www.hoyoverse.com/"
  }
};

export default async function handler(req) {
  try {
    const url = new URL(req.url);
    // prefer ?game=genshin or path like /genshin.xml via rewrite
    const gameParam =
      (url.searchParams.get("game") ||
        url.pathname.split("/").pop().replace(".xml", ""))?.toLowerCase() ||
      "genshin";

    const cfg = FEEDS[gameParam];
    if (!cfg) return new Response(`Unknown feed "${gameParam}"`, { status: 404 });

    // Build query string (we'll allow single-page fetch; change page size above)
    const qs = new URLSearchParams(cfg.qs).toString();
    const apiUrl = `${cfg.apiBase}?${qs}`;

    const headers = {
      accept: "application/json, text/plain, */*",
      referer: cfg.safeHeadersReferer,
      origin: new URL(cfg.safeHeadersReferer).origin,
      "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    };

    const resp = await fetch(apiUrl, { headers });
    if (!resp.ok) {
      console.error("Upstream fetch failed", resp.status, await resp.text());
      return new Response("Upstream fetch failed", { status: 502 });
    }

    const j = await resp.json();
    if (!j || j.retcode !== 0 || !j.data) {
      console.warn("Upstream returned no data or non-zero retcode", j);
    }
    const posts = Array.isArray(j?.data?.list) ? j.data.list : [];

    // Build RSS
    const now = new Date().toUTCString();
    const channelTitle = `${cfg.label} feed`;
    const linkBase = cfg.linkBase || "";

    const itemsXml = posts
      .map((p) => {
        const id = String(p.iInfoId ?? hashFallback(p.sTitle, p.dtStartTime));
        const title = escapeXml(p.sTitle ?? "No title");
        const intro = p.sIntro ?? "";
        const introSafe = safeCData(intro);
        const pubDate = parseDateToRfc822(p.dtStartTime) ?? new Date().toUTCString();
        const link = p.sUrl && p.sUrl.length ? p.sUrl : `${linkBase}/detail/${id}`;

        // banner from sExt if available
        let descHtml = introSafe;
        if (p.sExt) {
          try {
            const ext = JSON.parse(p.sExt);
            const mediaKey = ext.banner ? "banner" : ext.value ? "value" : null;
            if (mediaKey && Array.isArray(ext[mediaKey]) && ext[mediaKey].length) {
              const bannerUrl = ext[mediaKey][0].url;
              descHtml = `<img src="${escapeXml(bannerUrl)}" alt="banner"/><br/>${descHtml}`;
            }
          } catch (e) {
            // ignore malformed sExt
          }
        }

        return `
<item>
  <title>${title}</title>
  <link>${escapeXml(link)}</link>
  <guid isPermaLink="false">${escapeXml(id)}</guid>
  <description><![CDATA[${descHtml}]]></description>
  <pubDate>${escapeXml(pubDate)}</pubDate>
</item>`;
      })
      .join("\n");

    const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escapeXml(channelTitle)}</title>
    <link>${escapeXml(linkBase)}</link>
    <description>${escapeXml(channelTitle)}</description>
    <lastBuildDate>${escapeXml(now)}</lastBuildDate>
    ${itemsXml}
  </channel>
</rss>`;

    return new Response(rss, {
      status: 200,
      headers: {
        "Content-Type": "application/rss+xml; charset=utf-8",
        "Cache-Control": "no-cache, no-store, max-age=0"
      }
    });
  } catch (err) {
    console.error("Internal error", err);
    return new Response("Internal error", { status: 500 });
  }
}

/* Helpers */
function escapeXml(s) {
  if (s == null) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}
function safeCData(s) {
  if (s == null) return "";
  return String(s).replace(/]]>/g, "]]]]><![CDATA[>");
}
function parseDateToRfc822(dtStr) {
  if (!dtStr) return null;
  try {
    // upstream appears to use "YYYY-MM-DD HH:MM:SS"
    const iso = dtStr.replace(" ", "T") + "Z";
    const d = new Date(iso);
    if (isNaN(d)) return null;
    return d.toUTCString();
  } catch (e) {
    return null;
  }
}
function hashFallback(title = "", date = "") {
  const s = `${title}||${date}`;
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return "h" + Math.abs(h).toString(36);
}
