const spinnerLoaderInit = () => {
  const spinnerWrapper = document.createElement("div");
  const spinner = document.createElement("div");
  spinnerWrapper.id = "spinnerWrapper";
  spinnerWrapper.className = "b-spinner-wrapper";
  spinner.id = "spinner";
  spinner.className = "b-spinner";
  spinner.innerHTML = `<div class="spinner-border" role="status">
  <span class="visually-hidden">Loading...</span>
</div>`
  // inject nodes into DOM
  spinnerWrapper.appendChild(spinner);
  document.body.prepend(spinnerWrapper);
}

const showMessageScript = (text, severity = "danger") => {
  const escapeHtml = (html) => {
    return html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }
  const messageWrapper = document.getElementById("messageWrapper");
  if (!messageWrapper) throw new Error(`Can't find message wrapper!`);
  const message = `<div class="alert alert-${escapeHtml(severity)} alert-dismissible fade show" role="alert">
  ${escapeHtml(text)}
  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>`
  // append html markup to the message wrapper
  messageWrapper.innerHTML = message;
}

