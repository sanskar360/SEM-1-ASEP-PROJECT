// Random bubble sizes
const bubbles = document.querySelectorAll('.bubble');

bubbles.forEach(b => {
  let size = Math.random() * 50 + 20;
  b.style.width = size + "px";
  b.style.height = size + "px";
});

//Address Form

document.addEventListener("DOMContentLoaded", function () {

  const openbtn = document.getElementById("openFormBtn");
  const form = document.getElementById("addressForm");
  const cancelBtn = document.getElementById("cancelBtn");

  if (openbtn && form && cancelBtn) {

    openbtn.addEventListener("click", () => {
      form.classList.remove("hidden");
      openbtn.style.display = "none";
    });

    cancelBtn.addEventListener("click", () => {
      form.classList.add("hidden");
      openbtn.style.display = "block";
    });

  }

});

// document.getElementById("hamburger").onclick = function () {
//   const menu = document.getElementById("navLinks");

//   if (menu.classList.contains("active")) {
//     menu.classList.remove("active");
//     this.textContent = "☰";
//   } else {
//     menu.classList.add("active");
//     this.textContent = "✖";
//   }
// };

function selectService(service_id) {
  window.location.href = `/select_address?service_id=${service_id}`;
  console.log("clicked", service_id);
}

document.addEventListener("DOMContentLoaded", function () {

  let selectedAddressId = null;

  window.selectAddress = function (element, id) {
    console.log("Selected:", id);

    document.querySelectorAll(".address-card").forEach(card => {
      card.classList.remove("selected");
    });

    element.classList.add("selected");
    selectedAddressId = id;

    const btn = document.getElementById("nextBtn");
    btn.disabled = false;
    btn.classList.add("active");
  };

  document.getElementById("nextBtn").onclick = function () {

    console.log("Next clicked");

    if (!selectedAddressId) {
      alert("Please select address");
      return;
    }

    const service_id = new URLSearchParams(window.location.search).get("service_id");

    console.log("service_id:", service_id);
    console.log("address_id:", selectedAddressId);

    window.location.href =
      `/vendors?service_id=${service_id}&address_id=${selectedAddressId}`;
  };

});
function loadVendors(){
  window.location.href = "/vendors"
}

function goBack() {
  window.history.back();
}

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("searchInput");
  const cards = document.querySelectorAll(".vendor-card");
  const noResult = document.getElementById("noResult");

  input.addEventListener("input", () => {
    const value = input.value.toLowerCase();
    let visible = 0;

    cards.forEach(card =>{
      const name = card.dataset.name.toLowerCase();

      if(name.includes(value)){
        card.style.display = "block";
        visible++;
      } else{
        card.style.display = "none";
      }
    });

    noResult.style.display = visible === 0 ? "block" : "none";
  });
})

document.getElementById("searchBtn").onclick = function () {
document.getElementById("searchInput").dispatchEvent(new Event("input"));
};

function selectVendor(vendor_id) {
  const params = new URLSearchParams(window.location.search);

  const service_id = params.get("service_id");
  const address_id = params.get("address_id");

  window.location.href = `/add_orders/${service_id}/${address_id}/${vendor_id}`;
}

function changeQty(btn, change) {

  const row = btn.closest(".item-row");
  const qtyEl = row.querySelector(".qty");
  const qtyInput = row.querySelector(".qty-input");

  let qty = parseInt(qtyEl.textContent);
  qty = Math.max(0, qty + change);

  qtyEl.textContent = qty;
  qtyInput.value = qty;

  updateTotal();
}


function updateTotal() {

  let total = 0;

  document.querySelectorAll(".item-row").forEach(row => {

    const price = parseFloat(row.dataset.price);
    const qty = parseInt(row.querySelector(".qty").textContent);

    total += price * qty;
  });

  document.getElementById("total").textContent = total;
}