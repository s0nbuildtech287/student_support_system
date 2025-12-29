// Settings Page Navigation
document.querySelectorAll('.settings-nav-item').forEach(item => {
  item.addEventListener('click', (e) => {
    e.preventDefault();
    
    // Remove active class from all items
    document.querySelectorAll('.settings-nav-item').forEach(i => {
      i.classList.remove('active');
    });
    
    // Add active class to clicked item
    item.classList.add('active');
    
    // Hide all sections
    document.querySelectorAll('.settings-section').forEach(section => {
      section.classList.remove('active');
    });
    
    // Show selected section
    const sectionId = item.getAttribute('data-section');
    document.getElementById(sectionId).classList.add('active');
  });
});
