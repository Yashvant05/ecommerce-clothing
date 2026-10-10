document.addEventListener('DOMContentLoaded', function () {
  // 1. Add quick search placeholder enhancement
  const searchInput = document.getElementById('searchbar');
  if (searchInput) {
    searchInput.placeholder = "Type to search records... (Press '/' to focus)";
    
    // Keyboard shortcut '/' to instantly focus search
    document.addEventListener('keydown', function(e) {
      if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
    });
  }

  // 2. Automatically fade out Django success messages after 4 seconds
  const successMsgs = document.querySelectorAll('.messagelist li.success');
  successMsgs.forEach(msg => {
    setTimeout(() => {
      msg.style.transition = "opacity 0.5s ease";
      msg.style.opacity = "0";
      setTimeout(() => msg.remove(), 500);
    }, 4000);
  });
});