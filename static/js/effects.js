document.addEventListener("DOMContentLoaded", () => {
    const car = document.getElementById("parallax-car");
    const navWrapper = document.getElementById("car-nav-wrapper");
    const particleCanvas = document.getElementById("particle-canvas");

    // ---------- Directional car movement based on nav position ----------
    // Maps each page URL to a position in the nav order (left to right).
    // Moving to a LATER item (further right in the menu) -> car drifts BACKWARD (away).
    // Moving to an EARLIER item (further left in the menu) -> car drifts FORWARD (closer).
    if (navWrapper) {
        const routeIndexMap = [
            { path: "/", index: 0 },
            { path: "/scan", index: 1 },
            { path: "/vehicles", index: 2 },
            { path: "/vehicles/register", index: 3 },
            { path: "/scan-history", index: 4 },
            { path: "/face/setup", index: 5 },
        ];

        const currentPath = window.location.pathname;
        let match = routeIndexMap.find(r => r.path === currentPath);
        let currentIndex = match ? match.index : 0;

        const storedIndex = sessionStorage.getItem("navCarIndex");
        const previousIndex = storedIndex !== null ? parseInt(storedIndex, 10) : currentIndex;
        const direction = currentIndex - previousIndex;

        let targetX = 0;
        let targetScale = 1;

        if (direction > 0) {
            // Moved right in the nav -> car moves backward/away
            targetX = 130;
            targetScale = 0.86;
        } else if (direction < 0) {
            // Moved left in the nav -> car moves forward/closer
            targetX = -130;
            targetScale = 1.14;
        }

        // Apply on next frame so the CSS transition animates smoothly
        requestAnimationFrame(() => {
            navWrapper.style.transform = `translateX(${targetX}px) scale(${targetScale})`;
        });

        sessionStorage.setItem("navCarIndex", currentIndex);
    }

    // ---------- Parallax car on scroll (independent of nav movement) ----------
    if (car) {
        window.addEventListener("scroll", () => {
            const scrollY = window.scrollY;
            const translateX = -(scrollY * 0.15);
            const translateY = -(scrollY * 0.05);
            const rotate = scrollY * 0.01;
            car.style.transform = `translate(${translateX}px, ${translateY}px) rotate(${rotate}deg)`;
        });
    }

    // ---------- Animated particle background ----------
    if (particleCanvas) {
        const ctx = particleCanvas.getContext("2d");
        let width, height, particles = [];
        const PARTICLE_COUNT = 60;

        function resize() {
            width = particleCanvas.width = window.innerWidth;
            height = particleCanvas.height = document.body.scrollHeight;
        }
        window.addEventListener("resize", resize);
        resize();

        function createParticles() {
            particles = [];
            for (let i = 0; i < PARTICLE_COUNT; i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    r: Math.random() * 1.6 + 0.4,
                    speed: Math.random() * 0.3 + 0.05,
                    drift: Math.random() * 0.4 - 0.2,
                    opacity: Math.random() * 0.5 + 0.15,
                });
            }
        }
        createParticles();

        function animate() {
            ctx.clearRect(0, 0, width, height);
            for (const p of particles) {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(250, 204, 21, ${p.opacity})`;
                ctx.fill();
                p.y -= p.speed;
                p.x += p.drift;
                if (p.y < -10) {
                    p.y = height + 10;
                    p.x = Math.random() * width;
                }
            }
            requestAnimationFrame(animate);
        }
        animate();
    }

    // ---------- Fade-in on load for main content ----------
    const container = document.querySelector(".container");
    if (container) {
        container.style.opacity = "0";
        container.style.transform = "translateY(16px)";
        requestAnimationFrame(() => {
            container.style.transition = "opacity 0.6s ease, transform 0.6s ease";
            container.style.opacity = "1";
            container.style.transform = "translateY(0)";
        });
    }
});