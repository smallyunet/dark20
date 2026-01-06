document.addEventListener('DOMContentLoaded', () => {
    const copyBtn = document.getElementById('copy-btn');
    const addressInput = document.getElementById('doge-address');
    const toast = document.getElementById('toast');
    const balanceDisplay = document.getElementById('balance-display');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const txList = document.getElementById('tx-list');
    const totalBurnedEl = document.getElementById('total-burned');
    const totalTxsEl = document.getElementById('total-txs');
    const largestBurnEl = document.getElementById('largest-burn');

    const DEAD_ADDRESS = "DDogepartyxxxxxxxxxxxxxxxxxxw1dfzr";
    let lastKnownBalance = 0;
    let knownTxHashes = new Set();
    let isFirstLoad = true;

    // ═══════════════════════════════════════════════════════════════
    // STARFIELD BACKGROUND
    // ═══════════════════════════════════════════════════════════════
    const starfieldCanvas = document.getElementById('starfield');
    const starfieldCtx = starfieldCanvas.getContext('2d');
    let stars = [];

    function initStarfield() {
        const dpr = window.devicePixelRatio || 1;
        starfieldCanvas.width = window.innerWidth * dpr;
        starfieldCanvas.height = window.innerHeight * dpr;
        starfieldCanvas.style.width = window.innerWidth + 'px';
        starfieldCanvas.style.height = window.innerHeight + 'px';
        starfieldCtx.scale(dpr, dpr);
        
        stars = [];
        const numStars = Math.floor((window.innerWidth * window.innerHeight) / 8000);

        for (let i = 0; i < numStars; i++) {
            stars.push({
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                radius: Math.random() * 1.5,
                opacity: Math.random() * 0.8 + 0.2,
                twinkleSpeed: Math.random() * 0.02 + 0.005,
                speed: Math.random() * 0.5 + 0.1 // Movement speed
            });
        }
    }

    function animateStarfield() {
        starfieldCtx.fillStyle = '#050505';
        starfieldCtx.fillRect(0, 0, window.innerWidth, window.innerHeight); // Use logical size for rect

        stars.forEach(star => {
            star.opacity += star.twinkleSpeed;
            if (star.opacity > 1 || star.opacity < 0.2) {
                star.twinkleSpeed *= -1;
            }

            // Gravity Pull Effect
            const centerX = window.innerWidth / 2;
            const centerY = window.innerHeight / 2;
            const dx = star.x - centerX;
            const dy = star.y - centerY;
            star.x -= dx * 0.002 * star.speed; // Pull x towards center
            star.y -= dy * 0.002 * star.speed; // Pull y towards center

            // Reset if too close to center
            const distCheck = Math.sqrt(dx * dx + dy * dy);
            if (distCheck < 50) {
                star.x = Math.random() * window.innerWidth;
                star.y = Math.random() * window.innerHeight;
                star.opacity = 0;
            }

            starfieldCtx.beginPath();
            starfieldCtx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
            starfieldCtx.fillStyle = `rgba(255, 255, 255, ${star.opacity})`;
            starfieldCtx.fill();
        });

        requestAnimationFrame(animateStarfield);
    }

    initStarfield();
    animateStarfield();
    window.addEventListener('resize', initStarfield);

    // ═══════════════════════════════════════════════════════════════
    // BLACK HOLE PARTICLE ABSORPTION
    // ═══════════════════════════════════════════════════════════════
    const bhCanvas = document.getElementById('blackhole-canvas');
    const bhCtx = bhCanvas.getContext('2d');
    let particles = [];

    function initBlackhole() {
        const dpr = window.devicePixelRatio || 1;
        // Logical Size is fixed at 400x400 for CSS
        bhCanvas.width = 400 * dpr;
        bhCanvas.height = 400 * dpr;
        bhCanvas.style.width = '400px';
        bhCanvas.style.height = '400px';
        bhCtx.scale(dpr, dpr);
    }

    function createParticle() {
        const angle = Math.random() * Math.PI * 2;
        const distance = 180 + Math.random() * 50;
        return {
            // Logic relative to center 200,200
            x: 200 + Math.cos(angle) * distance,
            y: 200 + Math.sin(angle) * distance,
            angle: angle,
            distance: distance,
            speed: 0.3 + Math.random() * 0.5,
            size: 1 + Math.random() * 2,
            color: Math.random() > 0.5 ?
                `rgba(255, ${150 + Math.random() * 100}, 50, ` :
                `rgba(${200 + Math.random() * 55}, ${200 + Math.random() * 55}, 255, `
        };
    }

    function animateBlackhole() {
        bhCtx.clearRect(0, 0, 400, 400); // Clear logical area

        // Add new particles
        if (particles.length < 50 && Math.random() > 0.9) {
            particles.push(createParticle());
        }

        // Update and draw particles
        particles = particles.filter(p => {
            // Spiral inward
            p.distance -= p.speed;
            p.angle += (0.02 + (200 - p.distance) * 0.0003);

            p.x = 200 + Math.cos(p.angle) * p.distance;
            p.y = 200 + Math.sin(p.angle) * p.distance;

            if (p.distance < 30) return false; // Absorbed

            // Fade as approaching center
            const opacity = Math.min(1, (p.distance - 30) / 100);

            bhCtx.beginPath();
            bhCtx.arc(p.x, p.y, p.size * (p.distance / 200), 0, Math.PI * 2);
            bhCtx.fillStyle = p.color + opacity + ')';
            bhCtx.fill();

            // Glow effect
            bhCtx.beginPath();
            bhCtx.arc(p.x, p.y, p.size * 2 * (p.distance / 200), 0, Math.PI * 2);
            bhCtx.fillStyle = p.color + (opacity * 0.3) + ')';
            bhCtx.fill();

            return true;
        });

        requestAnimationFrame(animateBlackhole);
    }

    initBlackhole();
    animateBlackhole();

    // ═══════════════════════════════════════════════════════════════
    // CELEBRATION PARTICLES (BIG BANG)
    // ═══════════════════════════════════════════════════════════════
    const celebCanvas = document.getElementById('celebration-canvas');
    const celebCtx = celebCanvas.getContext('2d');
    let celebParticles = [];

    function initCelebration() {
        const dpr = window.devicePixelRatio || 1;
        celebCanvas.width = window.innerWidth * dpr;
        celebCanvas.height = window.innerHeight * dpr;
        celebCanvas.style.width = window.innerWidth + 'px';
        celebCanvas.style.height = window.innerHeight + 'px';
        celebCtx.scale(dpr, dpr);
    }

    function triggerCelebration() {
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2; // Center of screen/blackhole

        for (let i = 0; i < 150; i++) {
            const angle = Math.random() * Math.PI * 2;
            // Exponential speed distribution for explosion feel
            const speed = Math.pow(Math.random(), 3) * 20 + 2; 
            
            celebParticles.push({
                x: centerX,
                y: centerY,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                size: 2 + Math.random() * 4,
                color: ['#ffd700', '#ff00c1', '#00fff9', '#ffffff'][Math.floor(Math.random() * 4)],
                life: 1.0,
                decay: 0.01 + Math.random() * 0.02,
                friction: 0.96 // Air resistance
            });
        }
    }

    function animateCelebration() {
        celebCtx.clearRect(0, 0, window.innerWidth, window.innerHeight); // Use logical

        celebParticles = celebParticles.filter(p => {
            p.x += p.vx;
            p.y += p.vy;
            
            // Physics
            p.vx *= p.friction;
            p.vy *= p.friction;
            p.life -= p.decay;

            if (p.life <= 0) return false;

            celebCtx.beginPath();
            celebCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            celebCtx.fillStyle = p.color;
            celebCtx.globalAlpha = p.life;
            celebCtx.fill();
            celebCtx.globalAlpha = 1;

            return true;
        });

        if (celebParticles.length > 0) {
            requestAnimationFrame(animateCelebration);
        } else {
            celebCtx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        }
    }

    initCelebration();
    window.addEventListener('resize', initCelebration);

    // ═══════════════════════════════════════════════════════════════
    // COPY FUNCTIONALITY
    // ═══════════════════════════════════════════════════════════════
    const qrBtn = document.getElementById('qr-btn');
    const qrContainer = document.getElementById('qr-container');

    function copyToClipboard() {
        addressInput.select();
        addressInput.setSelectionRange(0, 99999);

        navigator.clipboard.writeText(addressInput.value).then(() => {
            showToast();
        }).catch(err => {
            try {
                document.execCommand('copy');
                showToast();
            } catch (e) {
                console.error('Copy failed', e);
            }
        });
    }

    function showToast() {
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 2000);
    }

    function toggleQR() {
        if (qrContainer.style.display === 'none') {
            qrContainer.style.display = 'block';
            qrBtn.innerText = 'Hide QR Code';
        } else {
            qrContainer.style.display = 'none';
            qrBtn.innerText = 'Show QR Code';
        }
    }

    copyBtn.addEventListener('click', copyToClipboard);
    addressInput.addEventListener('click', copyToClipboard);
    qrBtn.addEventListener('click', toggleQR);

    // ═══════════════════════════════════════════════════════════════
    // API DATA FETCHING
    // ═══════════════════════════════════════════════════════════════
    const CACHE_KEY = 'dark20_doge_balance';
    const TX_CACHE_KEY = 'dark20_doge_txs';

    // Load Cache Immediately
    const cachedBalance = localStorage.getItem(CACHE_KEY);
    if (cachedBalance) {
        const b = parseFloat(cachedBalance);
        if (!isNaN(b)) {
            lastKnownBalance = b;
            const formatted = b.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
            balanceDisplay.innerText = `${formatted} DOGE`;
            totalBurnedEl.innerText = `${formatted}`;
            statusText.innerText = "Synchronizing Node...";
        }
    }

    async function fetchAddressData() {
        try {
            // Using BlockCypher for detailed data
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000);

            const response = await fetch(
                `https://api.blockcypher.com/v1/doge/main/addrs/${DEAD_ADDRESS}?limit=10`,
                { signal: controller.signal }
            );
            clearTimeout(timeoutId);

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();

            // Update balance
            const balance = data.final_balance / 100000000;
            updateBalance(balance);

            // Update stats
            updateStats(data);

            // Update transaction history
            if (data.txrefs) {
                updateTransactions(data.txrefs);
            }

        } catch (e) {
            console.warn("Primary API failed, trying fallback:", e);
            // Fallback to Chain.so
            try {
                const response = await fetch(`https://chain.so/api/v2/get_address_balance/DOGE/${DEAD_ADDRESS}`);
                const data = await response.json();
                const balance = parseFloat(data.data.confirmed_balance);
                updateBalance(balance);
            } catch (e2) {
                console.warn("All APIs failed:", e2);
                if (!statusDot.classList.contains('live')) {
                    statusText.innerText = "Network Error (Retrying...)";
                }
            }
        }
    }

    function updateBalance(balance) {
        const formatted = balance.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 });

        // Check for new burn
        if (lastKnownBalance > 0 && balance > lastKnownBalance) {
            const diff = balance - lastKnownBalance;
            console.log(`New burn detected! +${diff} DOGE`);

            // Trigger celebration
            triggerCelebration();
            animateCelebration();

            // Animate balance
            balanceDisplay.classList.add('new-burn');
            setTimeout(() => balanceDisplay.classList.remove('new-burn'), 1000);

            // Animate stats
            totalBurnedEl.classList.add('animating');
            setTimeout(() => totalBurnedEl.classList.remove('animating'), 500);
        }

        lastKnownBalance = balance;
        balanceDisplay.innerText = `${formatted} DOGE`;
        totalBurnedEl.innerText = `${formatted}`;

        // Update Supply Stats
        updateSupplyStats(balance);

        statusDot.classList.add('live');
        statusText.innerText = "Live Network Data";

        localStorage.setItem(CACHE_KEY, balance);
    }

    function updateStats(data) {
        // Total transactions
        const txCount = data.n_tx || 0;
        totalTxsEl.innerText = txCount.toLocaleString();

        // Find largest burn from available txrefs
        if (data.txrefs && data.txrefs.length > 0) {
            const received = data.txrefs.filter(tx => tx.tx_input_n === -1);
            if (received.length > 0) {
                const largest = Math.max(...received.map(tx => tx.value));
                const largestFormatted = (largest / 100000000).toLocaleString('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 2
                });
                largestBurnEl.innerText = `${largestFormatted} DOGE`;
            }
        }
    }

    function updateTransactions(txrefs) {
        // Filter to only received transactions
        const received = txrefs.filter(tx => tx.tx_input_n === -1);
        if (received.length === 0) return;

        let html = '';
        let newTxFound = false;

        // First pass: identify which hashes are new
        const incomingHashes = new Set(received.map(tx => tx.tx_hash));

        // If it's not the first load, check if we have unseen hashes
        if (!isFirstLoad) {
            for (let hash of incomingHashes) {
                if (!knownTxHashes.has(hash)) {
                    newTxFound = true;
                    break;
                }
            }
        }

        // Update known hashes
        // We add them all now so the display loop knows they are "known"
        // But for the "new-tx" class, we only apply it if !isFirstLoad

        received.forEach((tx, index) => {
            const amount = (tx.value / 100000000).toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 4
            });
            const time = timeAgo(new Date(tx.confirmed));
            const hashShort = tx.tx_hash.substring(0, 8) + '...' + tx.tx_hash.substring(tx.tx_hash.length - 6);

            const isNew = !knownTxHashes.has(tx.tx_hash) && !isFirstLoad;
            knownTxHashes.add(tx.tx_hash);

            html += `
                <div class="tx-item ${isNew ? 'new-tx' : ''}">
                    <div>
                        <span class="tx-amount">${amount} DOGE</span>
                        <span class="tx-message"> entered the void</span>
                        <div class="tx-hash">
                            <a href="https://dogechain.info/tx/${tx.tx_hash}" target="_blank" rel="noopener">${hashShort}</a>
                        </div>
                    </div>
                    <span class="tx-time">${time}</span>
                </div>
            `;
        });

        txList.innerHTML = html;

        // Trigger celebration only if new tx found AND not first load
        if (newTxFound && !isFirstLoad) {
            triggerCelebration();
            animateCelebration();
        }

        isFirstLoad = false;
    }

    function timeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);

        if (seconds < 60) return 'just now';
        if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
        if (seconds < 86400) return Math.floor(seconds / 3600) + 'h ago';
        if (seconds < 2592000) return Math.floor(seconds / 86400) + 'd ago';
        if (seconds < 31536000) return Math.floor(seconds / 2592000) + 'mo ago';
        return Math.floor(seconds / 31536000) + 'y ago';
    }

    function updateSupplyStats(burnedAmount) {
        // Estimate DOGE Supply
        // 2024 Base: ~143B. Increases ~5B/year (~10k per minute)
        const now = new Date();
        const baseDate = new Date('2024-01-01T00:00:00Z');
        const secondsSinceBase = (now - baseDate) / 1000;
        const coinsPerSecond = 10000 / 60; // 10k per block (1 min)
        const baseSupply = 142400000000;

        const currentSupply = baseSupply + (secondsSinceBase * coinsPerSecond);

        const percent = (burnedAmount / currentSupply) * 100;

        // Update DOM
        document.getElementById('supply-percent').innerText = percent.toFixed(8) + '%';
        document.getElementById('progress-fill').style.width = Math.min(percent * 10, 100) + '%'; // Scale x10 for visibility if needed, or keeping accurate?
        // Actually keep it accurate but visual representation might need help if it's very small.
        // 1.8B / 144B is > 1%. It will be visible.

        document.getElementById('progress-fill').style.width = percent + '%';

        document.getElementById('supply-burned').innerText = (burnedAmount / 1000000000).toFixed(4) + 'B Burned';
        document.getElementById('supply-total').innerText = 'Total: ' + (currentSupply / 1000000000).toFixed(2) + 'B';
    }

    // Initial fetch
    fetchAddressData();

    // Poll every 30 seconds
    setInterval(fetchAddressData, 30000);
});
