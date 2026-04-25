const API = "http://localhost:8000/api";

let CURRENT_USER = null;

// =========================
// 🔍 LOAD MOVIES
// =========================
function loadMovies() {
    const q = document.getElementById("search").value || "";
    const genre = document.getElementById("genre").value || "";

    const container = document.getElementById("movies");
    container.innerHTML = "<p>Loading...</p>";

    fetch(`${API}/movies/?search=${q}&genre=${genre}`)
        .then(res => res.json())
        .then(data => {
            const movies = data.results || data;
            display("movies", movies);
        })
        .catch(err => {
            console.error(err);
            container.innerHTML = "<p>Failed to load movies</p>";
        });
}

// =========================
// 🔥 TRENDING
// =========================
function loadTrending() {
    fetch(`${API}/movies/trending/`)
        .then(res => res.json())
        .then(data => display("trending", data))
        .catch(err => {
            console.error(err);
            alert("Failed to load trending");
        });
}

// =========================
// ⭐ RECOMMENDATIONS
// =========================
function loadRecommendations() {
    const mood = document.getElementById("mood").value || "";

    const container = document.getElementById("movies");
    container.innerHTML = "<p>Loading recommendations...</p>";

    fetch(`${API}/movies/recommendations/?mood=${mood}`)
        .then(res => res.json())
        .then(data => {
            const movies = data.results || data;
            display("movies", movies);
        })
        .catch(err => {
            console.error(err);
            container.innerHTML = "<p>Failed to load recommendations</p>";
        });
}

// =========================
// 🎬 DISPLAY MOVIES
// =========================
function display(id, movies) {
    const container = document.getElementById(id);
    container.innerHTML = "";

    if (!movies || movies.length === 0) {
        container.innerHTML = "<p>No movies found.</p>";
        return;
    }

    movies.forEach(m => {
        const poster = m.poster && m.poster.trim() !== ""
            ? m.poster
            : "https://via.placeholder.com/300x450?text=No+Image";

        const genres = m.genres
            ? m.genres.map(g => g.name).join(", ")
            : "";

        const rating = Number(m.avg_rating || 0).toFixed(1);

        const card = document.createElement("div");
        card.className = "card";

        card.innerHTML = `
            <img src="${poster}">
            <div class="card-info">
                <p class="title">${m.title}</p>
                <small>${genres}</small>
                <small><i class="bi bi-star-fill"></i> ${rating}</small>
                <small><i class="bi bi-fire"></i> ${m.popularity ?? 0}</small>
                
                ${m.match_score ? `<small><i class="bi bi-lightning-fill"></i> Match: ${m.match_score}</small>` : ""}
            </div>
        `;

        card.onclick = () => showDetails(m);
        container.appendChild(card);
    });
}
// =========================
// 📄 DETAILS MODAL
// =========================
function showDetails(movie) {
    const modal = document.getElementById("modal");
    const body = document.getElementById("modal-body");

    const poster = movie.poster || "https://via.placeholder.com/300x450";

    body.innerHTML = `
        <h2>${movie.title}</h2>
        <img src="${poster}" style="width:200px;">
        <p>${movie.description}</p>
        <p><i class="bi bi-star-fill"></i> ${(Number(movie.avg_rating || 0)).toFixed(1)}</p>

        <div class="stars" data-id="${movie.id}">
            <span class="star" data-value="1">☆</span>
            <span class="star" data-value="2">☆</span>
            <span class="star" data-value="3">☆</span>
            <span class="star" data-value="4">☆</span>
            <span class="star" data-value="5">☆</span>
        </div>

        <button class="btn btn-outline-light" onclick="addToWatchlist(${movie.id})">
            <i class="bi bi-heart"></i> Watchlist
        </button>

        <button class="btn btn-outline-light" onclick="loadSimilar(${movie.id}); closeModal()">
            <i class="bi bi-collection-play"></i> Similar
        </button>
    `;

    modal.classList.remove("hidden");
}

// =========================
// ⭐ STAR RATING CLICK
// =========================
document.addEventListener("click", function(e) {
    if (e.target.classList.contains("star")) {
        const rating = parseInt(e.target.dataset.value);
        const movieId = parseInt(e.target.parentElement.dataset.id);

        rateMovie(movieId, rating);

        const stars = e.target.parentElement.querySelectorAll(".star");
        stars.forEach((s, i) => {
            s.textContent = i < rating ? "⭐" : "☆";
        });
    }
});

// =========================
// ⭐ RATE MOVIE (FIXED)
// =========================
function rateMovie(movieId, score) {
    if (!CURRENT_USER) {
        alert("Please login first");
        return;
    }

    fetch(`${API}/ratings/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Username": CURRENT_USER
        },
        body: JSON.stringify({
            movie: movieId,
            score: score
        })
    })
    .then(async res => {
        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
            if (data.non_field_errors) {
                alert("You already rated this movie");
            } else {
                alert("Failed to rate movie");
            }
            throw new Error("Rating failed");
        }

        alert("Rating submitted ⭐");
        return data;
    })
    .catch(err => console.error(err));
}

// =========================
// ❤️ WATCHLIST (FIXED)
// =========================
function addToWatchlist(movieId) {
    if (!CURRENT_USER) {
        alert("Please login first");
        return;
    }

    fetch(`${API}/watchlist/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Username": CURRENT_USER
        },
        body: JSON.stringify({ movie_id: movieId })
    })
    .then(async res => {
        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
            alert("Already in watchlist or error");
            throw new Error("Watchlist error");
        }

        return data;
    })
    .then(() => {
        alert("Added to watchlist ❤️");
        loadWatchlist();
    })
    .catch(err => console.error(err));
}

// =========================
// ❌ REMOVE FROM WATCHLIST
// =========================
function removeFromWatchlist(id) {
    fetch(`${API}/watchlist/${id}/`, {
        method: "DELETE",
        headers: {
            "X-Username": CURRENT_USER
        }
    })
    .then(() => {
        alert("Removed from watchlist");
        loadWatchlist();
    })
    .catch(err => console.error(err));
}

// =========================
// 📂 WATCHLIST
// =========================
function loadWatchlist() {
    const container = document.getElementById("watchlist");
    container.innerHTML = "<p>Loading...</p>";

    if (!CURRENT_USER) {
        container.innerHTML = "<p>Please login first.</p>";
        return;
    }

    fetch(`${API}/watchlist/`, {
        headers: {
            "X-Username": CURRENT_USER
        }
    })
    .then(res => res.json())
    .then(data => {
        if (!data.length) {
            container.innerHTML = "<p>No items in watchlist.</p>";
            return;
        }

        container.innerHTML = "";

        data.forEach(w => {
            const m = w.movie;

            const div = document.createElement("div");
            div.className = "card";

            div.innerHTML = `
                <img src="${m.poster || 'https://via.placeholder.com/300x450'}">
                
                <div class="card-info">
                    <p class="title">${m.title}</p>

                    <button class="btn btn-sm btn-danger mt-2"
                        onclick="removeFromWatchlist(${w.id})">
                        Remove
                    </button>
                </div>
            `;

            container.appendChild(div);
        });
    })
    .catch(err => {
        console.error(err);
        container.innerHTML = "<p style='color:red'>Error loading watchlist</p>";
    });
}

// =========================
// 🎬 SIMILAR MOVIES
// =========================
function loadSimilar(id) {
    fetch(`${API}/movies/${id}/similar/`)
        .then(res => res.json())
        .then(data => display("movies", data))
        .catch(err => {
            console.error(err);
            alert("Failed to load similar movies");
        });
}

// =========================
// 🔐 LOGIN
// =========================
function login() {
    const username = document.getElementById("username").value;

    if (!username.trim()) {
        alert("Enter username");
        return;
    }

    CURRENT_USER = username;
    localStorage.setItem("user", username);

    alert("Logged in as " + username);
}

// =========================
// ❌ CLOSE MODAL
// =========================
document.getElementById("modal").addEventListener("click", function(e) {
    if (e.target.id === "modal") {
        closeModal();
    }
});

function closeModal() {
    document.getElementById("modal").classList.add("hidden");
}

// =========================
// 🚀 INIT
// =========================
window.onload = function() {
    document.getElementById("search").addEventListener("keyup", e => {
        if (e.key === "Enter") loadMovies();
    });

    CURRENT_USER = localStorage.getItem("user");

    if (CURRENT_USER) {
        document.getElementById("username").value = CURRENT_USER;
    }

    loadHero();
    loadTrending();
    loadMovies();
};

// =========================
// 🎬 HERO
// =========================
function loadHero() {
    fetch(`${API}/movies/`)
        .then(res => res.json())
        .then(data => {
            const movies = data.results || data;

            if (!movies.length) return;

            const random = movies[Math.floor(Math.random() * movies.length)];
            const bg = random.poster || "https://via.placeholder.com/800x300";

            document.getElementById("hero").style.backgroundImage = `url(${bg})`;
            document.getElementById("hero-title").innerText = random.title;
            document.getElementById("hero-desc").innerText =
                (random.description || "").slice(0, 120) + "...";
        });
}
