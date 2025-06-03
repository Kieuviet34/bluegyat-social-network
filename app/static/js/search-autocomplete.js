if (!window.__SEARCH_AUTOCOMPLETE_LOADED__) {
  window.__SEARCH_AUTOCOMPLETE_LOADED__ = true;
  // Autocomplete for username search
  const searchInput = document.getElementById('search-user');
  const suggestionsBox = document.getElementById('search-suggestions');

  if (searchInput && suggestionsBox) {
    let debounceTimeout;
    searchInput.addEventListener('input', function () {
      clearTimeout(debounceTimeout);
      const query = this.value.trim();
      if (!query) {
        suggestionsBox.classList.remove('show');
        suggestionsBox.innerHTML = '';
        return;
      }
      debounceTimeout = setTimeout(() => {
        fetch(`/search/users?q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(users => {
            if (!Array.isArray(users) || users.length === 0) {
              suggestionsBox.classList.remove('show');
              suggestionsBox.innerHTML = '';
              return;
            }
            suggestionsBox.innerHTML = users.map(user => `
              <button type="button" class="dropdown-item d-flex align-items-center" data-username="${user.username}">
                <img src="${user.avatar_url}" alt="avatar" class="rounded-circle me-2" style="width:32px;height:32px;object-fit:cover;">
                <span>${user.username}</span>
              </button>
            `).join('');
            suggestionsBox.classList.add('show');
          }).catch(err => {
            suggestionsBox.classList.remove('show');
            suggestionsBox.innerHTML = '';
          });
      }, 200);
    });

    suggestionsBox.addEventListener('click', function (e) {
      const btn = e.target.closest('button[data-username]');
      if (btn) {
        searchInput.value = btn.dataset.username;
        suggestionsBox.classList.remove('show');
        suggestionsBox.innerHTML = '';
        // Optionally submit the form or redirect to user profile
        // searchInput.form.submit();
      }
    });

    document.addEventListener('click', function (e) {
      if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
        suggestionsBox.classList.remove('show');
        suggestionsBox.innerHTML = '';
      }
    });
  }
}
