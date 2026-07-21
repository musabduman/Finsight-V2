document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked button
            btn.classList.add('active');

            // Show corresponding content
            const tabId = btn.getAttribute('data-tab');
            const tabContent = document.getElementById(tabId);
            if (tabContent) {
                tabContent.classList.add('active');
            }
        });
    });

    // Get buttons
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const chatbotBtn = document.getElementById('chatbotBtn');
    const contactForm = document.getElementById('contactForm');
    const profileForm = document.getElementById('profileForm');

    // Login button click
    if (loginBtn) {
        loginBtn.addEventListener('click', function() {
            alert('Giriş yapma özelliği yakında kullanılabilir olacak.');
            // In a real app, you would redirect to a login page or show a modal
        });
    }

    // Signup button click
    if (signupBtn) {
        signupBtn.addEventListener('click', function() {
            alert('Kayıt olma özelliği yakında kullanılabilir olacak.');
            // In a real app, you would redirect to a signup page or show a modal
        });
    }

    // Chatbot button click (Pro feature warning)
    if (chatbotBtn) {
        chatbotBtn.addEventListener('click', function() {
            alert('Bu özellik sadece Pro planda mevcuttur. Lütfen pro plana abone olabilirsiniz.');
        });
    }

    // Contact form submission
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent actual form submission
            
            // Get form values
            const name = this.querySelector('input[placeholder="Adınız"]').value;
            const email = this.querySelector('input[placeholder="E-posta Adresiniz"]').value;
            const message = this.querySelector('textarea[placeholder="Mesajınız"]').value;
            
            // Simple validation
            if (name && email && message) {
                alert('Mesajınız gönderildi. Teşekkür ederiz, ' + name + '!');
                this.reset(); // Reset form
            } else {
                alert('Lütfen tüm alanları doldurun.');
            }
        });
    }

    // Profile form submission
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent actual form submission
            
            // Get form values
            const fullName = this.querySelector('#fullName').value;
            const email = this.querySelector('#email').value;
            const phone = this.querySelector('#phone').value;
            const bio = this.querySelector('#bio').value;
            
            // Simple validation
            if (fullName && email) {
                alert('Profiliniz güncellendi, ' + fullName + '!');
                this.reset(); // Reset form
            } else {
                alert('Lütfen zorunlu alanları doldurun.');
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});