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

  const nextBtn = document.getElementById("nextBtn");

  if (nextBtn) {
    nextBtn.onclick = function () {

      console.log("Next clicked");

      if (!selectedAddressId) {
        alert("Please select address");
        return;
      }

      const service_id = new URLSearchParams(window.location.search).get("service_id");

      window.location.href =
        `/vendors?service_id=${service_id}&address_id=${selectedAddressId}`;
    };
  }

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

  if (!input || !noResult) return;   // 🔥 IMPORTANT

  input.addEventListener("input", () => {
    const value = input.value.toLowerCase();
    let visible = 0;

    cards.forEach(card => {
      const name = card.dataset.name.toLowerCase();

      if (name.includes(value)) {
        card.style.display = "block";
        visible++;
      } else {
        card.style.display = "none";
      }
    });

    noResult.style.display = visible === 0 ? "block" : "none";
  });

});

const searchBtn = document.getElementById("searchBtn");

if (searchBtn) {
  searchBtn.onclick = function () {
    const input = document.getElementById("searchInput");
    if (input) {
      input.dispatchEvent(new Event("input"));
    }
  };
}

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

function openSidebar() {
    document.getElementById('adminSidebar').classList.add('open');
    document.getElementById('sidebarOverlay').classList.add('open');
}
function closeSidebar() {
    document.getElementById('adminSidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('open');
}
/* ── Add Modal ── */
function openAddModal() { document.getElementById('addModal').classList.add('show'); }
function closeAddModal() { document.getElementById('addModal').classList.remove('show'); }

function assignDelivery(order_id) {

  const select = document.getElementById("db_" + order_id);
  const delivery_boy_id = select.value;

  if (!delivery_boy_id) {
    alert("Please select delivery boy");
    return;
  }

  fetch("/assign_delivery", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      order_id: order_id,
      delivery_boy_id: delivery_boy_id
    })
  })
  .then(res => res.json())
  .then(data => {
    alert("Assigned successfully!");
  });
}

document.addEventListener("DOMContentLoaded", function () {

  const form = document.getElementById("addDeliveryForm");

  if (!form) return;   // 🔥 prevents crash on other pages

  form.addEventListener("submit", function (e) {

    e.preventDefault();

    const name = document.getElementById("newName").value.trim();
    const phone = document.getElementById("newPhone").value.trim();
    const status = document.getElementById("newStatus").value;

    if (!name || !phone) {
      alert("Please fill all fields");
      return;
    }

    if (!/^\d{10}$/.test(phone)) {
      alert("Enter valid 10-digit phone number");
      return;
    }

    fetch("/add_delivery_boy", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: name,
        phone: phone,
        status: status
      })
    })
    .then(res => res.json())
    .then(data => {
      alert("Delivery boy added!");
      location.reload();
    });

  });

});

console.log(document.getElementById("addDeliveryForm"));

function deactivate(btn, code) {

  fetch("/toggle_delivery_status", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ code: code })
  })
  .then(res => res.json())
  .then(data => {

    if (data.status === "success") {

      // 🔥 update UI instantly
      const card = btn.closest(".delivery-card");
      const badge = card.querySelector(".badge");

      if (data.new_status === "inactive") {
        badge.textContent = "Inactive";
        badge.classList.remove("badge-active");
        badge.classList.add("badge-inactive");

        btn.textContent = "Activate";
      } else {
        badge.textContent = "Active";
        badge.classList.remove("badge-inactive");
        badge.classList.add("badge-active");

        btn.textContent = "Deactivate";
      }
    }

  });
}

// ========================
// EDIT USER
// ========================
function openEditUser(id, role, status) {

  const modal = document.getElementById("editModal");
  if (!modal) return;

  const idInput = document.getElementById("editUserId");
  const roleInput = document.getElementById("editRole");
  const statusInput = document.getElementById("editStatus");

  if (idInput) idInput.value = id;
  if (roleInput) roleInput.value = role;
  if (statusInput) statusInput.value = status;

  modal.style.display = "flex";
}

function closeEditModal() {
  const modal = document.getElementById("editModal");
  if (modal) modal.style.display = "none";
}

function updateUser() {

  const idInput = document.getElementById("editUserId");
  const roleInput = document.getElementById("editRole");
  const statusInput = document.getElementById("editStatus");

  if (!idInput || !roleInput || !statusInput) return;

  const id = idInput.value;
  const role = roleInput.value;
  const status = statusInput.value;

  fetch("/update_user", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ id, role, status })
  })
  .then(res => res.json())
  .then(data => {

    if (data.status === "success") {
      alert("User updated successfully");
      closeEditModal();
      location.reload();
    } else {
      alert("Update failed");
    }

  })
  .catch(() => alert("Something went wrong"));
}


// ========================
// DELETE USER
// ========================
function confirmDelete(id, name) {

  const modal = document.getElementById("deleteModal");
  const text = document.getElementById("deleteText");
  const hidden = document.getElementById("deleteUserId");

  if (!modal || !text || !hidden) return;

  hidden.value = id;
  text.innerText = `Are you sure you want to delete ${name}?`;

  modal.style.display = "flex";
}

function closeDeleteModal() {
  const modal = document.getElementById("deleteModal");
  if (modal) modal.style.display = "none";
}

function deleteUser() {

  const hidden = document.getElementById("deleteUserId");
  if (!hidden) return;

  const id = hidden.value;

  fetch("/delete_user", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ id })
  })
  .then(res => res.json())
  .then(data => {

    if (data.status === "success") {
      alert("User deleted successfully");
      closeDeleteModal();
      location.reload();
    } else {
      alert("Delete failed");
    }

  })
  .catch(() => alert("Something went wrong"));
}

function filterTable(input, tableId) {
            const filter = input.value.toLowerCase();
            const rows = document.getElementById(tableId).querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.style.display = row.textContent.toLowerCase().includes(filter) ? '' : 'none';
            });
        }

// vendors_panel

function loadDashboardStats() {
  fetch("/api/dashboard_stats")
    .then(res => res.json())
    .then(data => {
      document.getElementById("newTodayCount").textContent = data.new_today;
      document.getElementById("acceptedCount").textContent = data.accepted;
      document.getElementById("rejectedCount").textContent = data.rejected;
    });
}

function updateIncomingBadge() {
  const rows = document.querySelectorAll('#incomingTable tbody tr');
  const count = rows.length;

  const badge = document.getElementById('incomingBadge');

  if (!badge) return; // safety check

  badge.textContent = count;

  if (count === 0) {
    badge.style.display = 'none';
  } else {
    badge.style.display = 'inline-block';
  }
}

function acceptOrder(btn, id) {
  const row = btn.closest('tr');

  row.style.opacity = '.5';
  row.style.pointerEvents = 'none';

  fetch("/accept_order", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      order_id: id.replace('#VV-', '')   // clean ID
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      setTimeout(() => {
        row.remove();
        updateIncomingBadge();
        loadDashboardStats();   // 🔥 ADD THIS
        showToast(`Order ${id} accepted ✅ — moved to Processing`);
      }, 400);
    }
  })
  .catch(() => {
    row.style.opacity = '1';
    row.style.pointerEvents = 'auto';
    showToast("Something went wrong ❌");
  });
}

function rejectOrder(btn, id) {
  const row = btn.closest('tr');

  row.style.opacity = '.5';
  row.style.pointerEvents = 'none';

  fetch("/reject_order", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      order_id: id.replace('#VV-', '')
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      setTimeout(() => {
        row.remove();
       updateIncomingBadge();
       loadDashboardStats();   // 🔥 ADD THIS
        showToast(`Order ${id} rejected ❌`);
      }, 400);
    }
  })
  .catch(() => {
    row.style.opacity = '1';
    row.style.pointerEvents = 'auto';
    showToast("Something went wrong ❌");
  });
}

window.onload = function () {
  loadPendingOrders();
  loadDashboardStats();
};

function loadPendingOrders() {
  fetch("/api/pending_orders")
    .then(res => res.json())
    .then(data => {
      const tbody = document.querySelector("#incomingTable tbody");
      tbody.innerHTML = "";

      data.forEach(order => {
        const row = `
          <tr>
            <td><span class="order-id-text">#VV-${order.id}</span></td>
            <td>${order.user}</td>
            <td>${order.service}</td>
            <td>${order.pickup_date}</td>
            <td>${order.payment}</td>
            <td>₹${order.amount}</td>
            <td>
              <div class="action-btns">
                <button class="btn-accept" onclick="acceptOrder(this,'#VV-${order.id}')">✅ Accept</button>
                <button class="btn-reject" onclick="rejectOrder(this,'#VV-${order.id}')">❌ Reject</button>
              </div>
            </td>
          </tr>
        `;
        tbody.innerHTML += row;
      });

      updateIncomingBadge(); // update count
    });
}