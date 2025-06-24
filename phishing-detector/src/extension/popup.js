chrome.runtime.sendMessage({ url: window.location.href }, response => {
  document.getElementById("result").textContent = response.result || "Error analyzing URL.";
  if (response.result && response.result.includes("Uncertain")) {
    const sandboxButton = document.getElementById("sandbox");
    sandboxButton.style.display = "block";
    sandboxButton.onclick = () => window.open(response.sandboxUrl, "_blank");
  }
});