// Random bubble sizes
const bubbles = document.querySelectorAll('.bubble');

bubbles.forEach(b => {
  let size = Math.random() * 50 + 20;
  b.style.width = size + "px";
  b.style.height = size + "px";
});

//Address Form

const openbtn = document.getElementById("openFormBtn");
const form = document.getElementById("addressForm");
const cancleBtn = document.getElementById("cancelBtn");

openbtn.addEventListener("click", () => {
  form.classList.remove("hidden");
  openbtn.style.display = "none";
});

cancleBtn.addEventListener("click", () => {
  form.classList.add("hidden");
  openbtn.style.display = "block";
});

document.getElementById("hamburger").onclick = function () {
  const menu = document.getElementById("navLinks");

  if (menu.classList.contains("active")) {
    menu.classList.remove("active");
    this.textContent = "☰";
  } else {
    menu.classList.add("active");
    this.textContent = "✖";
  }
};