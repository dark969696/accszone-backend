<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DigiZone - Secure Master Admin Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen p-4 sm:p-6 flex items-center justify-center">

    <!-- شاشة تسجيل دخول الأدمن السرية -->
    <div id="authOverlay" class="max-w-md w-full bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl text-center">
        <div class="mb-6">
            <div class="w-12 h-12 bg-blue-600/20 text-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-3 text-xl">
                <i class="fa-solid fa-shield-halved"></i>
            </div>
            <h2 class="text-xl font-bold text-white">Admin Authentication</h2>
            <p class="text-xs text-slate-400 mt-1">Enter your admin secret key to access control panel.</p>
        </div>
        <form id="authForm" onsubmit="verifyAdmin(event)" class="space-y-4">
            <input type="password" id="adminSecretInput" placeholder="Enter Admin Secret..." class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500 text-center" required>
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl text-sm transition shadow-lg shadow-blue-600/20">
                Access Master Dashboard
            </button>
        </form>
        <div class="mt-4">
            <a href="index.html" class="text-xs text-slate-400 hover:text-white transition">← Return to Store</a>
        </div>
    </div>

    <!-- لوحة التحكم الرئيسية الكاملة (مخفية لحين إدخال كلمة المرور) -->
    <div id="adminPanel" class="max-w-5xl w-full space-y-6 hidden">
        
        <!-- Top Header & Tabs Navigation -->
        <div class="flex flex-col md:flex-row justify-between items-center bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl gap-4">
            <h1 class="text-xl font-bold text-white"><i class="fa-solid fa-shield-halved text-blue-500 mr-2"></i> Master Admin Control Panel</h1>
            
            <div class="flex flex-wrap items-center gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
                <button onclick="switchTab('inventory')" id="tabInvBtn" class="px-3.5 py-2 rounded-lg text-xs font-bold transition bg-blue-600 text-white shadow-lg">
                    <i class="fa-solid fa-boxes-stacked mr-1"></i> Inventory & Prices
                </button>
                <button onclick="switchTab('deposits')" id="tabDepBtn" class="px-3.5 py-2 rounded-lg text-xs font-bold transition text-slate-400 hover:text-white">
                    <i class="fa-solid fa-wallet mr-1"></i> Deposits
                </button>
                <button onclick="switchTab('purchases')" id="tabPurBtn" class="px-3.5 py-2 rounded-lg text-xs font-bold transition text-slate-400 hover:text-white">
                    <i class="fa-solid fa-bag-shopping mr-1"></i> Purchases
                </button>
            </div>

            <div class="flex gap-2">
                <a href="index.html" class="text-xs bg-slate-800 text-slate-300 px-3 py-2 rounded-lg border border-slate-700 transition hover:bg-slate-700">Store</a>
                <button onclick="logoutAdmin()" class="text-xs bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white px-3 py-2 rounded-lg border border-red-500/30 transition">Logout</button>
            </div>
        </div>

        <!-- TAB 1: Inventory & Prices Section -->
        <div id="inventorySection" class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="space-y-6">
                <!-- Add Account Form -->
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
                    <h3 class="font-bold text-sm mb-4 pb-2 border-b border-slate-800 text-slate-200">Add New Account</h3>
                    <form id="addForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Product ID:</label>
                            <input type="number" id="product_id" value="1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500" required>
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Account Data:</label>
                            <textarea id="account_data" rows="3" placeholder="user@email.com | pass" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500" required></textarea>
                        </div>
                        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-xl text-xs transition shadow-lg shadow-blue-600/20">
                            Add to Inventory
                        </button>
                    </form>
                    <p id="resultMsg" class="mt-3 text-center text-xs font-semibold"></p>
                </div>

                <!-- Update Price Form -->
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
                    <h3 class="font-bold text-sm mb-4 pb-2 border-b border-slate-800 text-slate-200">Update Product Price</h3>
                    <form id="priceForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Product ID:</label>
                            <input type="number" id="price_product_id" value="1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500" required>
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">New Price ($):</label>
                            <input type="number" step="0.01" id="new_price" placeholder="2.50" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500" required>
                        </div>
                        <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 rounded-xl text-xs transition shadow-lg shadow-emerald-600/20">
                            Update Price
                        </button>
                    </form>
                    <p id="priceMsg" class="mt-3 text-center text-xs font-semibold"></p>
                </div>
            </div>

            <!-- Accounts Table View -->
            <div class="md:col-span-2 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl h-fit">
                <div class="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
                    <h3 class="font-bold text-sm text-slate-200">Current Inventory Database</h3>
                    <button onclick="loadAccounts()" class="text-xs bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 transition">Refresh List 🔄</button>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="text-slate-400 border-b border-slate-800">
                                <th class="pb-3">ID</th>
                                <th class="pb-3">Account Data</th>
                                <th class="pb-3">Status</th>
                                <th class="pb-3 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="accountsTableBody" class="divide-y divide-slate-800 text-slate-300">
                            <tr><td colspan="4" class="py-4 text-center text-slate-500">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- TAB 2: Pending Deposits Section -->
        <div id="depositsSection" class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4 hidden">
            <h3 class="font-bold text-base text-white flex items-center"><i class="fa-solid fa-wallet text-amber-400 mr-2"></i> Pending Deposit Requests</h3>
            <div id="depositsList" class="space-y-3">
                <p class="text-xs text-slate-500">Loading pending deposits...</p>
            </div>
        </div>

        <!-- TAB 3: Product Purchases Section -->
        <div id="purchasesSection" class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4 hidden">
            <h3 class="font-bold text-base text-white flex items-center"><i class="fa-solid fa-bag-shopping text-emerald-400 mr-2"></i> Product Purchases History</h3>
            <div id="purchasesList" class="space-y-3">
                <p class="text-xs text-slate-500">Loading purchases history...</p>
            </div>
        </div>

    </div>

    <script>
        const API_URL = "https://digizone-kb46.onrender.com";
        let currentAdminSecret = sessionStorage.getItem("digizone_admin_secret") || "";

        if (currentAdminSecret) {
            validateAndOpenPanel(currentAdminSecret);
        }

        async function verifyAdmin(e) {
            e.preventDefault();
            let secret = document.getElementById('adminSecretInput').value;
            validateAndOpenPanel(secret);
        }

        async function validateAndOpenPanel(secret) {
            try {
                let res = await fetch(`${API_URL}/get-pending-deposits?admin_secret=${secret}`);
                if (res.ok) {
                    currentAdminSecret = secret;
                    sessionStorage.setItem("digizone_admin_secret", secret);
                    document.getElementById('authOverlay').classList.add('hidden');
                    document.getElementById('adminPanel').classList.remove('hidden');
                    loadAccounts();
                } else {
                    alert("❌ كلمة السر غير صحيحة!");
                    sessionStorage.removeItem("digizone_admin_secret");
                }
            } catch (err) {
                alert("❌ خطأ في الاتصال بالخادم!");
            }
        }

        function logoutAdmin() {
            sessionStorage.removeItem("digizone_admin_secret");
            location.reload();
        }

        function switchTab(tabName) {
            let invSec = document.getElementById('inventorySection');
            let depSec = document.getElementById('depositsSection');
            let purSec = document.getElementById('purchasesSection');
            
            let invBtn = document.getElementById('tabInvBtn');
            let depBtn = document.getElementById('tabDepBtn');
            let purBtn = document.getElementById('tabPurBtn');

            invSec.classList.add('hidden');
            depSec.classList.add('hidden');
            purSec.classList.add('hidden');

            invBtn.className = "px-3.5 py-2 rounded-lg text-xs font-bold transition text-slate-400 hover:text-white";
            depBtn.className = "px-3.5 py-2 rounded-lg text-xs font-bold transition text-slate-400 hover:text-white";
            purBtn.className = "px-3.5 py-2 rounded-lg text-xs font-bold transition text-slate-400 hover:text-white";

            if (tabName === 'inventory') {
                invSec.classList.remove('hidden');
                invBtn.className = "px-3.5 py-2 rounded-lg text-xs font-bold transition bg-blue-600 text-white shadow-lg";
                loadAccounts();
            } else if (tabName === 'deposits') {
                depSec.classList.remove('hidden');
                depBtn.className = "px-3.5 py-2 rounded-lg text-xs font-bold transition bg-blue-600 text-white shadow-lg";
                fetchPendingDeposits();
            } else if (tabName === 'purchases') {
                purSec.classList.remove('hidden');
                purBtn.className = "px-3.5 py-2 rounded-lg text-xs font-bold transition bg-blue-600 text-white shadow-lg";
                fetchAllPurchases();
            }
        }

        async function loadAccounts() {
            let tbody = document.getElementById('accountsTableBody');
            tbody.innerHTML = `<tr><td colspan="4" class="py-4 text-center text-slate-500">Loading...</td></tr>`;
            try {
                let res = await fetch(`${API_URL}/get-all-accounts`);
                let data = await res.json();
                if(res.ok && data.accounts && data.accounts.length > 0) {
                    tbody.innerHTML = "";
                    data.accounts.forEach(acc => {
                        let statusBadge = acc.is_sold 
                            ? `<span class="bg-red-500/10 text-red-400 px-2 py-0.5 rounded-md border border-red-500/20 font-medium">Sold ❌</span>`
                            : `<span class="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-md border border-emerald-500/20 font-medium">Available ✅</span>`;
                    
                        tbody.innerHTML += `
                            <tr class="hover:bg-slate-800/50">
                                <td class="py-3 font-mono">${acc.id}</td>
                                <td class="py-3 font-mono text-slate-200 max-w-xs truncate">${acc.account_data}</td>
                                <td class="py-3">${statusBadge}</td>
                                <td class="py-3 text-center">
                                    <button onclick="deleteAccount(${acc.id})" class="bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white px-3 py-1 rounded-lg border border-red-500/30 transition text-xs">Delete</button>
                                </td>
                            </tr>
                        `;
                    });
                } else {
                    tbody.innerHTML = `<tr><td colspan="4" class="py-4 text-center text-slate-500">No accounts added yet.</td></tr>`;
                }
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="4" class="py-4 text-center text-red-400">Server connection error</td></tr>`;
            }
        }

        async function deleteAccount(accountId) {
            if (!confirm(`Delete account ID #${accountId}?`)) return;
            try {
                let res = await fetch(`${API_URL}/delete-account`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account_id: accountId, admin_secret: currentAdminSecret })
                });
                let data = await res.json();
                if (res.ok) {
                    alert("✅ " + data.message);
                    loadAccounts();
                } else {
                    alert("❌ " + (data.detail || "Deletion error"));
                }
            } catch (err) {
                alert("❌ Server connection error");
            }
        }

        document.getElementById('addForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            let productId = document.getElementById('product_id').value;
            let accountData = document.getElementById('account_data').value;
            let msg = document.getElementById('resultMsg');
            msg.innerText = "Adding...";
            msg.className = "mt-3 text-center text-xs font-semibold text-slate-400";

            try {
                let response = await fetch(`${API_URL}/add-account`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: parseInt(productId), account_data: accountData, admin_secret: currentAdminSecret })
                });
                let data = await response.json();
                if (response.ok) {
                    msg.className = "mt-3 text-center text-xs font-semibold text-emerald-400";
                    msg.innerText = "✅ " + data.message;
                    document.getElementById('account_data').value = "";
                    loadAccounts();
                } else {
                    msg.className = "mt-3 text-center text-xs font-semibold text-red-400";
                    msg.innerText = "❌ " + (data.detail || "Error");
                }
            } catch (err) {
                msg.className = "mt-3 text-center text-xs font-semibold text-red-400";
                msg.innerText = "❌ Server connection error";
            }
        });

        document.getElementById('priceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            let productId = document.getElementById('price_product_id').value;
            let newPrice = document.getElementById('new_price').value;
            let msg = document.getElementById('priceMsg');
            msg.innerText = "Updating price...";
            msg.className = "mt-3 text-center text-xs font-semibold text-slate-400";

            try {
                let response = await fetch(`${API_URL}/update-product-price`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: parseInt(productId), new_price: parseFloat(newPrice), admin_secret: currentAdminSecret })
                });
                let data = await response.json();
                if (response.ok) {
                    msg.className = "mt-3 text-center text-xs font-semibold text-emerald-400";
                    msg.innerText = "✅ " + (data.message || "Price updated successfully");
                } else {
                    msg.className = "mt-3 text-center text-xs font-semibold text-red-400";
                    msg.innerText = "❌ " + (data.detail || "Update error");
                }
            } catch (err) {
                msg.className = "mt-3 text-center text-xs font-semibold text-red-400";
                msg.innerText = "❌ Server connection error";
            }
        });

        async function fetchPendingDeposits() {
            let container = document.getElementById('depositsList');
            try {
                let res = await fetch(`${API_URL}/get-pending-deposits?admin_secret=${currentAdminSecret}`);
                let data = await res.json();
                if (res.ok && data.deposits && data.deposits.length > 0) {
                    container.innerHTML = data.deposits.map(d => `
                        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 flex justify-between items-center text-xs">
                            <div class="space-y-1">
                                <p class="text-white font-bold">Customer: ${d.customer_name} (${d.customer_email})</p>
                                <p class="text-emerald-400 font-bold text-sm">Amount: $${d.amount}</p>
                                <p class="text-slate-400 font-mono">TXID: ${d.txid}</p>
                            </div>
                            <button onclick="approveDeposit(${d.order_id})" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-4 py-2.5 rounded-xl transition shadow-lg">
                                Approve & Credit
                            </button>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = `<p class="text-xs text-slate-500">No pending deposits found.</p>`;
                }
            } catch (err) {
                container.innerHTML = `<p class="text-xs text-red-500">Error loading deposits.</p>`;
            }
        }

        async function approveDeposit(orderId) {
            if (!confirm("Are you sure you want to approve this deposit and credit the user's balance?")) return;
            try {
                let res = await fetch(`${API_URL}/approve-deposit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ order_id: orderId, admin_secret: currentAdminSecret })
                });
                let data = await res.json();
                if (res.ok) {
                    alert("✅ " + data.message);
                    fetchPendingDeposits();
                } else {
                    alert("❌ " + (data.detail || "Approval failed"));
                }
            } catch (err) {
                alert("❌ Server connection error");
            }
        }

        async function fetchAllPurchases() {
            let container = document.getElementById('purchasesList');
            try {
                let res = await fetch(`${API_URL}/get-all-purchases?admin_secret=${currentAdminSecret}`);
                let data = await res.json();
                if (res.ok && data.purchases && data.purchases.length > 0) {
                    container.innerHTML = data.purchases.map(p => `
                        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
                            <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                                <span class="text-white font-bold">Order #${p.order_id} — ${p.customer_name} (${p.customer_email})</span>
                                <span class="text-emerald-400 font-bold">Paid: $${p.total_amount}</span>
                            </div>
                            <div>
                                <span class="text-slate-400 block mb-1">Delivered Account Details:</span>
                                <textarea readonly class="w-full bg-slate-900 border border-slate-800 rounded p-2 text-blue-400 font-mono" rows="2">${p.account_details}</textarea>
                            </div>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = `<p class="text-xs text-slate-500">No product purchases recorded yet.</p>`;
                }
            } catch (err) {
                container.innerHTML = `<p class="text-xs text-red-500">Error loading purchases.</p>`;
            }
        }
    </script>
</body>
</html>
