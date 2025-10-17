document.addEventListener("DOMContentLoaded", () => {
    // State management
    const state = {
        likedCards: new Set(),
        bookmarkedCards: new Set(),
        currentUser: null,
        allLinks: [],
        searchResults: [],
        isSearching: false,
        currentFilterState: false
    };

    // DOM Elements
    const addLinkModal = document.getElementById('addLinkModal');
    const signupModal = document.getElementById('signupModal');
    const loginModal = document.getElementById('loginModal');
    const toast = document.getElementById('toast');

    // Search Elements
    let searchModal;
    let searchInput;
    let searchResultsContainer;

    // Initialize all functionality
    function initializeApp() {
        initSearch();
        initContentFilter();
        loadInitialFilterState();
        loadAllLinks();
        setupEventListeners();
    }

    function setupEventListeners() {
        // Modal openers
        document.getElementById('addLinkBtn')?.addEventListener('click', () => openModal(addLinkModal));
        document.getElementById('addLinkSidebarBtn')?.addEventListener('click', () => openModal(addLinkModal));
        document.getElementById('addLinkHeroBtn')?.addEventListener('click', () => openModal(addLinkModal));
        document.getElementById('signupBtn')?.addEventListener('click', () => openModal(signupModal));
        document.getElementById('loginBtn')?.addEventListener('click', () => openModal(loginModal));
        document.getElementById('getStartedBtn')?.addEventListener('click', () => openModal(signupModal));

        // Search button
        document.getElementById('searchBtn')?.addEventListener('click', () => {
            if (searchModal) {
                openModal(searchModal);
            } else {
                filterCards(searchInput?.value || '');
            }
        });

        // Modal closers
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                closeModal(modal);
            });
        });

        document.getElementById('cancelAddLink')?.addEventListener('click', () => closeModal(addLinkModal));
        document.getElementById('cancelSignup')?.addEventListener('click', () => closeModal(signupModal));
        document.getElementById('cancelLogin')?.addEventListener('click', () => closeModal(loginModal));

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                closeModal(e.target);
            }
        });

        // Form submissions
        setupFormSubmissions();

        // Newsletter subscription
        document.getElementById('subscribeBtn')?.addEventListener('click', handleNewsletterSubscription);

        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                showToast(`Navigating to ${page} page`, 'info');

                // Update active nav link
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // View All buttons
        document.querySelectorAll('.view-all-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const category = e.target.closest('.category-block')?.getAttribute('data-category');
                if (category) {
                    showToast(`Viewing all ${category} content`, 'info');
                }
            });
        });

        // Category Filter
        document.querySelectorAll('.filter-option').forEach(option => {
            option.addEventListener('click', handleCategoryFilter);
        });

        // Slider functionality
        initSliders();

        // Card interactions
        initCardInteractions();
    }

    function setupFormSubmissions() {
        document.getElementById('addLinkForm')?.addEventListener('submit', handleAddLink);
        document.getElementById('signupForm')?.addEventListener('submit', handleSignup);
        document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    }

    // ==================== FORM HANDLERS ====================
    async function handleAddLink(e) {
        e.preventDefault();

        const isSensitive = document.getElementById('linkSensitive').checked;

        const formData = {
            title: document.getElementById('linkTitle').value,
            url: document.getElementById('linkUrl').value,
            description: document.getElementById('linkDescription').value,
            image_url: document.getElementById('linkImage').value,
            category_id: document.getElementById('linkCategory').value,
            is_sensitive: isSensitive
        };

        try {
            const response = await fetch('/api/links', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                showToast('Link shared successfully!', 'success');
                closeModal(addLinkModal);
                document.getElementById('addLinkForm').reset();
                // Reset sensitive toggle
                document.getElementById('linkSensitive').checked = false;
                // Refresh page after a delay to show new link
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast(result.message || 'Failed to share link', 'error');
            }
        } catch (error) {
            console.error('Add link error:', error);
            showToast('Network error', 'error');
        }
    }

    async function handleSignup(e) {
        e.preventDefault();

        const formData = {
            username: document.getElementById('signupUsername').value,
            email: document.getElementById('signupEmail').value,
            password: document.getElementById('signupPassword').value,
            full_name: document.getElementById('signupName').value
        };

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                showToast('Account created successfully!', 'success');
                closeModal(signupModal);
                document.getElementById('signupForm').reset();
                // Refresh page to update user state
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast(result.message || 'Registration failed', 'error');
            }
        } catch (error) {
            console.error('Signup error:', error);
            showToast('Network error', 'error');
        }
    }

    async function handleLogin(e) {
        e.preventDefault();

        const formData = {
            username: document.getElementById('loginUsername').value,
            password: document.getElementById('loginPassword').value
        };

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                showToast('Login successful!', 'success');
                closeModal(loginModal);
                document.getElementById('loginForm').reset();
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast(result.message || 'Login failed', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            showToast('Network error', 'error');
        }
    }

    function handleNewsletterSubscription() {
        const email = document.getElementById('newsletterEmail').value;
        if (email && validateEmail(email)) {
            showToast('Thanks for subscribing!', 'success');
            document.getElementById('newsletterEmail').value = '';
        } else {
            showToast('Please enter a valid email address', 'error');
        }
    }

    function handleCategoryFilter(e) {
        // Remove active class from all options
        document.querySelectorAll('.filter-option').forEach(opt => opt.classList.remove('active'));
        // Add active class to clicked option
        e.currentTarget.classList.add('active');

        const category = e.currentTarget.getAttribute('data-category');
        if (category === 'all') {
            document.querySelectorAll('.category-block').forEach(block => {
                block.style.display = 'block';
            });
        } else {
            document.querySelectorAll('.category-block').forEach(block => {
                if (block.getAttribute('data-category') === category) {
                    block.style.display = 'block';
                } else {
                    block.style.display = 'none';
                }
            });
        }

        const categoryName = e.currentTarget.querySelector('span').textContent;
        showToast(`Filtering by: ${categoryName}`, 'info');
    }

    // ==================== SLIDER FUNCTIONALITY ====================
    function initSliders() {
        document.querySelectorAll('.slider-container').forEach(slider => {
            const leftBtn = slider.querySelector('.arrow.left');
            const rightBtn = slider.querySelector('.arrow.right');
            const wrapper = slider.querySelector('.cards-wrapper');

            if (!wrapper) return;

            const scrollAmount = 300;

            leftBtn?.addEventListener('click', () => {
                wrapper.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
            });

            rightBtn?.addEventListener('click', () => {
                wrapper.scrollBy({ left: scrollAmount, behavior: 'smooth' });
            });

            // Hide arrows when at the edges
            const updateArrows = () => {
                const scrollLeft = wrapper.scrollLeft;
                const scrollWidth = wrapper.scrollWidth;
                const clientWidth = wrapper.clientWidth;

                if (leftBtn) {
                    leftBtn.style.display = scrollLeft <= 10 ? 'none' : 'flex';
                }
                if (rightBtn) {
                    rightBtn.style.display = scrollLeft + clientWidth >= scrollWidth - 10 ? 'none' : 'flex';
                }
            };

            wrapper.addEventListener('scroll', updateArrows);
            updateArrows();
        });
    }

    // ==================== CARD INTERACTIONS ====================
    function initCardInteractions() {
        // Use event delegation for dynamic cards
        document.addEventListener('click', async (e) => {
            // Like button
            if (e.target.closest('.like-btn')) {
                await handleLikeClick(e);
            }
            // Bookmark button
            else if (e.target.closest('.bookmark-btn')) {
                await handleBookmarkClick(e);
            }
            // Card click (excluding buttons)
            else if (e.target.closest('.card') &&
                !e.target.closest('.like-btn') &&
                !e.target.closest('.bookmark-btn')) {
                handleCardClick(e);
            }
        });
    }

    async function handleLikeClick(e) {
        e.stopPropagation();
        const likeBtn = e.target.closest('.like-btn');
        const card = likeBtn.closest('.card');
        const icon = likeBtn.querySelector('i');
        const cardId = card.getAttribute('data-id');

        if (!cardId) {
            console.error('Card ID not found');
            return;
        }

        try {
            const isLiked = likeBtn.classList.contains('liked');
            const endpoint = `/api/links/${cardId}/${isLiked ? 'unlike' : 'like'}`;

            const response = await fetch(endpoint, { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                if (isLiked) {
                    likeBtn.classList.remove('liked');
                    icon?.classList.replace('fas', 'far');
                    updateLikeCount(card, -1);
                    showToast('Removed from liked items', 'info');
                } else {
                    likeBtn.classList.add('liked');
                    icon?.classList.replace('far', 'fas');
                    updateLikeCount(card, 1);
                    showToast('Added to liked items', 'success');
                }
            } else {
                showToast(result.message || 'Action failed', 'error');
            }
        } catch (error) {
            console.error('Like error:', error);
            showToast('Network error', 'error');
        }
    }

    async function handleBookmarkClick(e) {
        e.stopPropagation();
        const bookmarkBtn = e.target.closest('.bookmark-btn');
        const card = bookmarkBtn.closest('.card');
        const icon = bookmarkBtn.querySelector('i');
        const cardId = card.getAttribute('data-id');

        if (!cardId) {
            console.error('Card ID not found');
            return;
        }

        try {
            const isBookmarked = bookmarkBtn.classList.contains('bookmarked');
            const endpoint = `/api/links/${cardId}/${isBookmarked ? 'unbookmark' : 'bookmark'}`;

            const response = await fetch(endpoint, { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                if (isBookmarked) {
                    bookmarkBtn.classList.remove('bookmarked');
                    icon?.classList.replace('fas', 'far');
                    showToast('Removed from bookmarks', 'info');
                } else {
                    bookmarkBtn.classList.add('bookmarked');
                    icon?.classList.replace('far', 'fas');
                    showToast('Added to bookmarks', 'success');
                }
            } else {
                showToast(result.message || 'Action failed', 'error');
            }
        } catch (error) {
            console.error('Bookmark error:', error);
            showToast('Network error', 'error');
        }
    }

    function handleCardClick(e) {
        const card = e.target.closest('.card');
        if (!card) return;

        const title = card.querySelector('h3')?.textContent || 'Link';
        const url = card.dataset.url;

        showToast(`Opening: ${title}`, 'info');

        if (url) {
            setTimeout(() => {
                window.open(url, '_blank');
            }, 600);
        }
    }


    function updateLikeCount(card, change) {
        const metaText = card.querySelector('.card-meta span');
        if (metaText) {
            const currentText = metaText.textContent;
            const currentLikes = parseInt(currentText.match(/\d+/)) || 0;
            const newLikes = Math.max(0, currentLikes + change);
            metaText.textContent = currentText.replace(/\d+ likes/, `${newLikes} likes`);
        }
    }

    // ==================== SEARCH FUNCTIONALITY ====================
    function initSearch() {
        searchModal = document.getElementById('searchModal');
        searchInput = document.getElementById('searchInput');
        searchResultsContainer = document.getElementById('searchResults');

        // Live search as you type
        searchInput?.addEventListener('input', (e) => {
            filterCards(e.target.value);
        });

        // Search on Enter key
        searchInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                filterCards(e.target.value);
            }
        });
    }

    function filterCards(term) {
        const lowerTerm = term.toLowerCase().trim();
        const cards = document.querySelectorAll('.card');
        let found = false;

        cards.forEach(card => {
            const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
            const description = card.querySelector('p')?.textContent.toLowerCase() || '';
            const category = card.closest('.category-block')?.getAttribute('data-category') || '';

            const matches = title.includes(lowerTerm) ||
                description.includes(lowerTerm) ||
                category.includes(lowerTerm);

            if (matches) {
                card.style.display = 'flex';
                found = true;

                // Highlight matching text
                highlightText(card, lowerTerm);
            } else {
                card.style.display = 'none';
                removeHighlights(card);
            }
        });

        // Update category visibility
        updateCategoryVisibility();

        if (term.length > 0) {
            if (!found) {
                showToast('No results found', 'error');
            } else {
                showToast(`Showing results for: "${term}"`, 'success');
            }
        } else {
            // Reset all cards when search is empty
            cards.forEach(card => {
                card.style.display = 'flex';
                removeHighlights(card);
            });
            updateCategoryVisibility();
        }
    }

    function highlightText(card, term) {
        if (!term) return;

        const title = card.querySelector('h3');
        const description = card.querySelector('p');

        [title, description].forEach(element => {
            if (element) {
                const text = element.textContent;
                const regex = new RegExp(`(${term})`, 'gi');
                const highlighted = text.replace(regex, '<mark>$1</mark>');
                element.innerHTML = highlighted;
            }
        });
    }

    function removeHighlights(card) {
        const title = card.querySelector('h3');
        const description = card.querySelector('p');

        [title, description].forEach(element => {
            if (element) {
                element.innerHTML = element.textContent;
            }
        });
    }

    function showSearchPlaceholder() {
        if (searchResultsContainer) {
            searchResultsContainer.innerHTML = '<p class="search-placeholder">Start typing to search...</p>';
        }
    }

    // ==================== CONTENT FILTER FUNCTIONALITY ====================
    function initContentFilter() {
        // Create filter toggle button
        const filterToggle = document.createElement('button');
        filterToggle.id = 'contentFilterToggle';
        filterToggle.className = 'btn btn-outline';
        filterToggle.innerHTML = '<i class="fas fa-eye"></i> Hide Sensitive Content';
        filterToggle.style.marginLeft = '10px';

        // Add to user actions
        const userActions = document.querySelector('.user-actions');
        if (userActions) {
            userActions.appendChild(filterToggle);
        }

        // Toggle event
        filterToggle.addEventListener('click', () => {
            const currentState = localStorage.getItem('contentFilterEnabled') === 'true';
            const newState = !currentState;

            // If user is trying to SHOW sensitive content (turning filter OFF), show warning
            if (currentState === true && newState === false) {
                showSensitiveContentWarning(newState);
            } else {
                // If hiding sensitive content (turning filter ON), proceed normally
                updateFilterState(newState);
                localStorage.setItem('contentFilterEnabled', newState.toString());
                updateServerFilterPreference(newState);

                showToast(
                    newState ? 'Sensitive content hidden' : 'Sensitive content shown',
                    'info'
                );
            }
        });
    }

    function showSensitiveContentWarning(newState) {
        // Create warning modal
        const warningModal = document.createElement('div');
        warningModal.className = 'modal';
        warningModal.id = 'warningModal';
        warningModal.innerHTML = `
        <div class="modal-content" style="max-width: 400px;">
            <div class="modal-header">
                <h2><i class="fas fa-exclamation-triangle" style="color: #ffc107;"></i> Sensitive Content Warning</h2>
                <button class="close-modal">&times;</button>
            </div>
            <div style="padding: 1rem 0;">
                <p style="margin-bottom: 1rem; line-height: 1.5;">
                    You are about to view content that may be sensitive or disturbing to some users.
                </p>
                <div style="background: var(--light-gray); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="margin: 0; font-size: 0.9rem; color: var(--gray);">
                        <strong>This content may include:</strong><br>
                        • Graphic or disturbing imagery<br>
                        • Mature themes<br>
                        • Strong language<br>
                        • Other potentially offensive material
                    </p>
                </div>
                <p style="font-size: 0.9rem; color: var(--gray);">
                    Are you sure you want to proceed?
                </p>
                <p style="font-size: 1.1rem; color: var(--gray);">
                    Refresh the page after selecting.
                </p>
            </div>
            <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
                <button id="cancelWarning" class="btn btn-outline" style="flex: 1; color: var(--dark); border-color: var(--light-gray);">
                    Cancel
                </button>
                <button id="confirmShowSensitive" class="btn btn-primary" style="flex: 1;">
                    <i class="fas fa-eye"></i> Show Content
                </button>
            </div>
        </div>
    `;

        document.body.appendChild(warningModal);

        // Show the modal
        warningModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        // Event listeners for the warning modal
        const closeModal = warningModal.querySelector('.close-modal');
        const cancelBtn = warningModal.querySelector('#cancelWarning');
        const confirmBtn = warningModal.querySelector('#confirmShowSensitive');

        const closeWarningModal = () => {
            warningModal.style.display = 'none';
            document.body.style.overflow = 'auto';
            document.body.removeChild(warningModal);
        };

        closeModal.addEventListener('click', closeWarningModal);
        cancelBtn.addEventListener('click', closeWarningModal);

        confirmBtn.addEventListener('click', () => {
            // User confirmed - show sensitive content
            updateFilterState(newState);
            localStorage.setItem('contentFilterEnabled', newState.toString());
            updateServerFilterPreference(newState);

            showToast('Sensitive content is now visible', 'info');
            closeWarningModal();
        });

        // Close modal when clicking outside
        warningModal.addEventListener('click', (e) => {
            if (e.target === warningModal) {
                closeWarningModal();
            }
        });

        // Close modal with Escape key
        const handleEscapeKey = (e) => {
            if (e.key === 'Escape') {
                closeWarningModal();
                document.removeEventListener('keydown', handleEscapeKey);
            }
        };
        document.addEventListener('keydown', handleEscapeKey);
    }

    function updateFilterState(enabled) {
        const toggle = document.getElementById('contentFilterToggle');
        if (!toggle) return;

        state.currentFilterState = enabled;

        if (enabled) {
            toggle.innerHTML = '<i class="fas fa-eye-slash"></i> Show Sensitive Content';
            toggle.classList.add('filter-active');
            document.body.classList.add('content-filter-enabled');
        } else {
            toggle.innerHTML = '<i class="fas fa-eye"></i> Hide Sensitive Content';
            toggle.classList.remove('filter-active');
            document.body.classList.remove('content-filter-enabled');
        }

        // Apply filtering to content
        filterSensitiveContent(enabled);
    }

    function filterSensitiveContent(enabled) {
        const sensitiveCards = document.querySelectorAll('.card[data-sensitive="true"]');

        sensitiveCards.forEach(card => {
            if (enabled) {
                // Hide the entire card when filter is enabled
                card.style.display = 'none';
            } else {
                // Show the entire card when filter is disabled
                card.style.display = 'flex';
            }
        });

        // Update category visibility
        updateCategoryVisibility();
    }

    function updateCategoryVisibility() {
        document.querySelectorAll('.category-block').forEach(block => {
            const visibleCards = block.querySelectorAll('.card[style*="display: flex"], .card:not([style])');
            if (visibleCards.length === 0) {
                block.style.display = 'none';
            } else {
                block.style.display = 'block';
            }
        });
    }

    // Update server-side filter preference
    async function updateServerFilterPreference(showSensitive) {
        try {
            const response = await fetch('/api/filter/preference', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    show_sensitive: !showSensitive // Invert because we're tracking "filter enabled" not "show sensitive"
                })
            });

            const result = await response.json();
            if (!result.success) {
                console.error('Failed to update filter preference:', result.message);
            }
        } catch (error) {
            console.error('Error updating filter preference:', error);
        }
    }

    // Load initial filter state from server
    async function loadInitialFilterState() {
        try {
            // Check if we have a stored preference
            const storedPreference = localStorage.getItem('contentFilterEnabled');
            if (storedPreference !== null) {
                const filterEnabled = storedPreference === 'true';
                updateFilterState(filterEnabled);
            } else {
                // Default to showing sensitive content (filter disabled)
                updateFilterState(false);
                localStorage.setItem('contentFilterEnabled', 'false');
            }
        } catch (error) {
            console.error('Error loading filter state:', error);
            // Default to showing sensitive content
            updateFilterState(false);
            localStorage.setItem('contentFilterEnabled', 'false');
        }
    }

    // ==================== HELPER FUNCTIONS ====================
    function openModal(modal) {
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';

            // Focus on first input if it's a form modal
            if (modal === searchModal) {
                setTimeout(() => searchInput?.focus(), 100);
            } else if (modal === loginModal) {
                setTimeout(() => document.getElementById('loginUsername')?.focus(), 100);
            } else if (modal === signupModal) {
                setTimeout(() => document.getElementById('signupName')?.focus(), 100);
            } else if (modal === addLinkModal) {
                setTimeout(() => document.getElementById('linkTitle')?.focus(), 100);
            }
        }
    }

    function closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';

            // Clear search when closing search modal
            if (modal === searchModal) {
                searchInput.value = '';
                showSearchPlaceholder();
            }
        }
    }

    function showToast(message, type = 'info') {
        if (!toast) return;

        toast.textContent = message;
        toast.className = 'toast show';

        // Set background color based on type
        if (type === 'success') {
            toast.style.backgroundColor = '#28a745';
        } else if (type === 'error') {
            toast.style.backgroundColor = '#dc3545';
        } else if (type === 'info') {
            toast.style.backgroundColor = '#17a2b8';
        } else {
            toast.style.backgroundColor = 'var(--dark)';
        }

        // Hide after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function loadAllLinks() {
        // This would typically fetch links from your API
        console.log('Loading all links...');
        // Implementation would go here
    }

    // Initialize the application
    initializeApp();
});