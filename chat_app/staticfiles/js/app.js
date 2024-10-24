
// Select all elements with the class referenced
const slideElements = document.querySelectorAll('.slide');
const appearElements = document.querySelectorAll('.appear');

// Set transition delay for each element
slideElements.forEach((el, index) => {
  el.style.transitionDelay = `${index * 0.5}s`; // Adjust the multiplier as needed
});


// Create an Intersection Observer
const observer = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('show');
      //observer.unobserve(entry.target); // Optional: Unobserve after revealing
    }  else {
      entry.target.classList.remove('show');
    }
  });
}, {
  threshold: 0.1 // Adjust the threshold as needed
});

// Start observing each element
slideElements.forEach(el => observer.observe(el));
appearElements.forEach(el => observer.observe(el));
