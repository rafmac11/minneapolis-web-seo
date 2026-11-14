/* Contact form: posts leads straight to the WebLeadsNow CRM quote webhook. */
(function () {
  var form = document.getElementById("lead-form");
  if (!form) return;
  var status = form.querySelector(".lf-status");
  var btn = form.querySelector("button[type=submit]");
  var f = form.elements;

  function say(msg, isError) {
    status.textContent = msg;
    status.className = "lf-status" + (isError ? " is-error" : "");
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (f.website_url && f.website_url.value) return; // honeypot: bots fill hidden field
    if (!form.checkValidity()) { form.reportValidity(); return; }

    var data = new URLSearchParams();
    var full = f.name.value.trim();
    var parts = full.split(/\s+/);
    data.append("name", full);
    data.append("first_name", parts[0] || "");
    data.append("last_name", parts.slice(1).join(" "));
    data.append("email", f.email.value.trim());
    data.append("phone", f.phone.value.trim());
    data.append("company", f.company.value.trim());
    data.append("website", f.website.value.trim());
    data.append("service", f.service.value);
    data.append("message", f.message.value.trim());
    data.append("source", "seo4web.pro");
    data.append("page_url", location.href);
    data.append("referrer", document.referrer || "");

    btn.disabled = true;
    say("Sending…", false);

    // A urlencoded POST is a CORS "simple request": no preflight, so the CRM
    // receives it whatever CORS headers it returns. no-cors means we cannot read
    // the reply, so a resolved fetch is treated as delivered; only a network
    // failure rejects.
    fetch(form.action, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: data.toString()
    }).then(function () {
      window.location.href = "/thank-you/";
    }).catch(function () {
      btn.disabled = false;
      say("We couldn't send that. Please try again, or call (612) 230-0815.", true);
    });
  });
})();
