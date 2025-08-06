// document.addEventListener('DOMContentLoaded', function () {
//   const titleBlock = document.querySelector('.sub-tool-container-item.title');
//   const formBlock = document.querySelector('.sub-tool-container-item.file-form');

//   titleBlock.addEventListener('click', function () {
//     const isVisible = formBlock.style.display === 'block';
//     formBlock.style.display = isVisible ? 'none' : 'block';
//   });
// });

window.onload = function() {
    var popup = document.getElementById('error-popup');
    if (popup) popup.style.display = 'flex';
};