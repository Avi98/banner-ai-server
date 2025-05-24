() => {
  const headers = {};
  document.querySelectorAll("h1, h2, h3, h4, h5, h6").forEach((header) => {
    headers[header.tagName] = header.innerText;
  });
  return headers;
}
