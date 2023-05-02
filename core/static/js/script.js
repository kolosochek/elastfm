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