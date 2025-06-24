let blocklist = new Set();
let legitDomains = [];
let suspiciousTlds = [];

async function fetchBlocklists() {
  try {
    // Fetch OpenPhish blocklist
    const openphish = await (await fetch("https://openphish.com/feed.txt")).text();
    blocklist = new Set(openphish.split("\n").filter(url => url));
    
    // Fetch PhishTank blocklist
    const phishtank = await (await fetch("http://data.phishtank.com/data/online-valid.json")).json();
    phishtank.forEach(entry => blocklist.add(entry.url));
    
    // Fetch local config files
    legitDomains = (await (await fetch(chrome.runtime.getURL("legit_domains.txt"))).text()).split("\n").filter(d => d);
    suspiciousTlds = (await (await fetch(chrome.runtime.getURL("suspicious_tlds.txt"))).text()).split("\n").filter(t => t);
  } catch (e) {
    console.error("Error fetching blocklists/configs:", e);
  }
}

function checkTyposquatting(domain) {
  for (let legit of legitDomains) {
    let dist = 0;
    for (let i = 0; i < Math.min(domain.length, legit.length); i++) {
      if (domain[i] !== legit[i]) dist++;
    }
    if (dist < 3 && dist > 0) return `Typosquatting detected: Similar to ${legit}`;
  }
  return "";
}

function checkHomoglyph(url) {
  const normalized = url.normalize("NFKC").toLowerCase();
  if (normalized !== url.toLowerCase()) return "Homoglyph detected: Unicode characters used.";
  
  const homoglyphs = [
    ["а", "a"], // Cyrillic 'a'
    ["ο", "o"], // Greek 'omicron'
    ["і", "i"]  // Cyrillic 'i'
  ];
  for (let [spoof, legit] of homoglyphs) {
    if (url.toLowerCase().includes(spoof)) return `Homoglyph detected: '${spoof}' mimics '${legit}'.`;
  }
  return "";
}

function checkSuspiciousTld(url) {
  const tld = url.split(".").pop().toLowerCase();
  return suspiciousTlds.includes(tld) ? "Suspicious TLD detected." : "";
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.url) {
    let result = "";
    if (blocklist.has(request.url)) {
      result = "Phishing detected: URL in blocklist.";
    } else if (checkTyposquatting(request.url.split("/")[2] || "")) {
      result = checkTyposquatting(request.url.split("/")[2] || "");
    } else if (checkHomoglyph(request.url)) {
      result = checkHomoglyph(request.url);
    } else if (checkSuspiciousTld(request.url)) {
      result = checkSuspiciousTld(request.url);
    } else {
      result = "Uncertain. Open in Browserling sandbox?";
    }
    sendResponse({
      result,
      sandboxUrl: `https://www.browserling.com/browse/chrome/100/${encodeURIComponent(request.url)}`
    });
  }
  return true;
});

fetchBlocklists();
setInterval(fetchBlocklists, 3600000);