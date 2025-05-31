(function () {
  const sessionId = localStorage.getItem("session_id") || crypto.randomUUID();
  localStorage.setItem("session_id", sessionId);
  const baseUrl1 = window.location.origin;
  function sendTracking(eventType, metadata = {}) {
    fetch(`${baseUrl1}/track`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        event_type: eventType,
        url: window.location.href,
        referrer: document.referrer,
        metadata,
        email: localStorage.getItem("user_email") || null,
      }),
    });
  }

  // Page view
  sendTracking("page_view");

  // Click tracking
  document.addEventListener("click", function (e) {
    const el = e.target;
    sendTracking("click", {
      element: el.tagName,
      id: el.id,
      class: el.className,
      text: el.innerText?.slice(0, 100),
    });
  });

  // Scroll tracking
  let scrollDepthSent = false;
  window.addEventListener("scroll", () => {
    const scrolled = window.scrollY + window.innerHeight;
    const totalHeight = document.body.scrollHeight;
    const scrollPercent = (scrolled / totalHeight) * 100;
    if (!scrollDepthSent && scrollPercent > 80) {
      scrollDepthSent = true;
      sendTracking("scroll_depth", { percent: Math.round(scrollPercent) });
    }
  });

  // Time on page
  const start = Date.now();
  window.addEventListener("beforeunload", () => {
    const duration = Math.floor((Date.now() - start) / 1000);
    sendTracking("time_on_page", { duration });
  });
})();
