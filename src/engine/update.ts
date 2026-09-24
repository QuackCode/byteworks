// GitHub Pages lets browsers keep a copy of the page for 10 minutes, so after an update some
// players would keep getting the old game. On start-up we ask the server which build is current
// (version.json is never cached) and, if ours is older, reload on a fresh URL the cache hasn't seen.

declare const __BUILD_ID__: string;   // stamped in by vite.config.ts at build time

/** The URL to reload on if this page is out of date, or null if it's fine (or we already tried). */
export function freshUrl(href: string, currentId: string, latestId: string): string | null {
  if (!latestId || latestId === currentId) return null;
  const url = new URL(href);
  if (url.searchParams.get("v") === latestId) return null;   // already reloaded once: don't loop
  url.searchParams.set("v", latestId);
  return url.toString();
}

/** The address without our ?v= marker, or null if there's nothing to tidy. */
export function cleanUrl(href: string): string | null {
  const url = new URL(href);
  if (!url.searchParams.has("v")) return null;
  url.searchParams.delete("v");
  return url.toString();
}

export async function reloadIfOutdated(): Promise<void> {
  const href = location.href;                  // read before tidying: the ?v= marker is the loop guard
  const tidy = cleanUrl(href);
  if (tidy) history.replaceState(null, "", tidy);
  try {
    const res = await fetch(`./version.json?t=${Date.now()}`, { cache: "no-store" });
    if (!res.ok) return;                       // dev server: there's no version.json
    const { id } = await res.json();
    const target = freshUrl(href, __BUILD_ID__, id);
    if (target) location.replace(target);
  } catch {
    /* offline: just carry on with the copy we have */
  }
}
