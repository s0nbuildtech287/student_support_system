// User Avatar Dropdown
const userAvatarBtn = document.getElementById('userAvatarBtn');
const userDropdown = document.getElementById('userDropdown');

if (userAvatarBtn && userDropdown) {
  userAvatarBtn.addEventListener('click', () => {
    userDropdown.classList.toggle('show');
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!userAvatarBtn.contains(e.target)) {
      userDropdown.classList.remove('show');
    }
  });
}
