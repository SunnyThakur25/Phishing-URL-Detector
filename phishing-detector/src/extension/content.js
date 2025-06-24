chrome.runtime.sendMessage({ url: window.location.href }, response => {
  if (response.result) {
    chrome.runtime.sendMessage({ result: response.result, sandboxUrl: response.sandboxUrl });
  }
});

// Scan links on page
document.querySelectorAll("a").forEach(link => {
  const url = link.href;
  if (url) {
    chrome.runtime.sendMessage({ url }, response => {
      if (response.result && response.result.includes("Phishing")) {
        link.style.backgroundColor = "#ffcccc";
        link.title = response.result;
      }
    });
  }
});